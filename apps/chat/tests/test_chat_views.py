"""Tests para sa chat views — throttle, sources passthrough, auto-learn gating."""

from datetime import timedelta
from unittest import mock

from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.chat import presence
from apps.chat.models import Conversation
from apps.core.models import ActivityLog
from apps.users.models import User


class ChatSendViewTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username='tester', email='tester@example.com', password='test-pass-123',
        )
        self.client.force_login(self.user)

    def _post(self, message='hello world how are you'):
        return self.client.post(reverse('chat:send'), {'message': message})

    @mock.patch('apps.chat.services.ai.answer_question')
    def test_sources_returned_in_response(self, answer):
        answer.return_value = {
            'reply': 'Sagot mula KB.',
            'engine': 'KNIGHT v1.0',
            'sources': [{'title': 'Car Pass', 'url': '', 'type': 'kb'}],
        }
        res = self._post()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.json()['sources'],
            [{'title': 'Car Pass', 'url': '', 'type': 'kb'}],
        )

    def test_empty_message_returns_400(self):
        res = self._post(message='')
        self.assertEqual(res.status_code, 400)

    @override_settings(CHAT_MAX_PER_MINUTE=2)
    @mock.patch('apps.chat.services.ai.answer_question')
    def test_rate_limit_returns_429(self, answer):
        answer.return_value = {'reply': 'ok', 'engine': 'K', 'sources': []}
        first = self._post('first message here')
        second = self._post('second message here')
        third = self._post('third message here')
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(third.status_code, 429)

    @mock.patch('apps.chat.services.ai.auto_learn')
    @mock.patch('apps.chat.services.ai.answer_question')
    def test_non_staff_does_not_auto_learn(self, answer, auto_learn):
        answer.return_value = {'reply': 'ok', 'engine': 'K', 'sources': []}
        self._post('some kcc fact message here')
        self.assertFalse(auto_learn.called)

    @mock.patch('apps.chat.services.ai.auto_learn')
    @mock.patch('apps.chat.services.ai.answer_question')
    def test_staff_auto_learn_called(self, answer, auto_learn):
        staff = User.objects.create_user(
            username='staffy', email='staff@example.com', password='test-pass-123', is_staff=True,
        )
        self.client.force_login(staff)
        answer.return_value = {'reply': 'ok', 'engine': 'K', 'sources': []}
        auto_learn.return_value = []
        self._post('some kcc fact message here')
        self.assertTrue(auto_learn.called)


class ChatAuthTests(TestCase):
    @mock.patch('apps.chat.services.ai.answer_question')
    def test_public_visitor_can_chat_without_login(self, answer):
        """Public chat is open — no account needed, conversation is session-bound."""
        answer.return_value = {'reply': 'ok', 'engine': 'K', 'sources': []}
        res = self.client.post(
            reverse('chat:send'), {'message': 'hi there friend', 'newchat': '1'}
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['conversation_token'])


class ChatTokenUrlTests(TestCase):
    """Chat URLs use an opaque token and are scoped to the owning visitor."""

    def setUp(self):
        cache.clear()

    def _start_public_chat(self):
        with mock.patch('apps.chat.services.ai.answer_question') as answer:
            answer.return_value = {'reply': 'ok', 'engine': 'K', 'sources': []}
            res = self.client.post(
                reverse('chat:send'), {'message': 'hello there', 'newchat': '1'}
            )
        self.assertEqual(res.status_code, 200)
        return res.json()['conversation_token']

    def test_public_chat_opens_with_token_same_browser(self):
        token = self._start_public_chat()
        self.assertNotEqual(token, str(Conversation.objects.get(token=token).pk))
        res = self.client.get(reverse('chat:session', args=[token]))
        # The sid never stays in the address bar; the chat URL is always /chat/.
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res['Location'], '/chat/')
        # Guests get a fresh chat page per tab; the tab restores from sessionStorage.
        self.assertContains(self.client.get('/chat/'), 'Kumusta')
        hist = self.client.post(reverse('chat:history'), {'token': token}).json()
        self.assertEqual(hist['messages'][0]['content'], 'hello there')

    def test_token_not_reachable_from_another_device(self):
        token = self._start_public_chat()
        res = Client().get(reverse('chat:session', args=[token]))
        self.assertEqual(res.status_code, 404)

    def test_numeric_id_url_does_not_expose_public_chat(self):
        token = self._start_public_chat()
        pk = Conversation.objects.get(token=token).pk
        res = self.client.get(f'/chat/{pk}/')
        self.assertEqual(res.status_code, 404)

    def test_registered_user_keeps_own_chat(self):
        user = User.objects.create_user(
            username='tokuser', email='tokuser@example.com', password='TestPass!2345'
        )
        self.client.force_login(user)
        with mock.patch('apps.chat.services.ai.answer_question') as answer:
            answer.return_value = {'reply': 'ok', 'engine': 'K', 'sources': []}
            res = self.client.post(
                reverse('chat:send'), {'message': 'registered hello', 'newchat': '1'}
            )
        token = res.json()['conversation_token']
        opened = self.client.get(reverse('chat:session', args=[token]))
        self.assertEqual(opened.status_code, 302)
        self.assertEqual(opened['Location'], '/chat/')
        self.assertContains(self.client.get('/chat/'), 'registered hello')

    def test_registered_user_cannot_open_another_users_chat(self):
        owner = User.objects.create_user(
            username='owner1', email='owner1@example.com', password='TestPass!2345'
        )
        self.client.force_login(owner)
        with mock.patch('apps.chat.services.ai.answer_question') as answer:
            answer.return_value = {'reply': 'ok', 'engine': 'K', 'sources': []}
            res = self.client.post(
                reverse('chat:send'), {'message': 'private hello', 'newchat': '1'}
            )
        token = res.json()['conversation_token']
        self.client.logout()

        intruder = User.objects.create_user(
            username='intruder', email='intruder@example.com', password='TestPass!2345'
        )
        self.client.force_login(intruder)
        self.assertEqual(self.client.get(reverse('chat:session', args=[token])).status_code, 404)


class ChatLifecycleTests(TestCase):
    """Closed tab -> anonymous chats are deleted; activity logs survive."""

    def setUp(self):
        cache.clear()

    def _start_public_chat(self):
        with mock.patch('apps.chat.services.ai.answer_question') as answer:
            answer.return_value = {'reply': 'ok', 'engine': 'K', 'sources': []}
            res = self.client.post(
                reverse('chat:send'), {'message': 'hello there', 'newchat': '1'}
            )
        self.assertEqual(res.status_code, 200)
        return res.json()['conversation_token']

    def test_leave_beacon_marks_public_chat_as_closing(self):
        token = self._start_public_chat()
        res = self.client.post(reverse('chat:leave'))
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(Conversation.objects.get(token=token).closing_at)

    def test_returning_visitor_cancels_pending_deletion(self):
        token = self._start_public_chat()
        self.client.post(reverse('chat:leave'))
        self.client.get(reverse('chat:page'))  # any request clears the mark
        self.assertIsNone(Conversation.objects.get(token=token).closing_at)

    def test_purge_deletes_closed_chat_and_keeps_activity_logs(self):
        token = self._start_public_chat()
        self.assertTrue(ActivityLog.objects.filter(action='chat').exists())

        self.client.post(reverse('chat:leave'))
        Conversation.objects.filter(token=token).update(
            closing_at=timezone.now() - timedelta(seconds=120)
        )
        presence.purge_expired_anonymous(force=True)

        self.assertFalse(Conversation.objects.filter(token=token).exists())
        self.assertTrue(ActivityLog.objects.filter(action='chat').exists())

    def test_registered_user_chats_are_never_marked(self):
        user = User.objects.create_user(
            username='keepuser', email='keepuser@example.com', password='TestPass!2345'
        )
        self.client.force_login(user)
        with mock.patch('apps.chat.services.ai.answer_question') as answer:
            answer.return_value = {'reply': 'ok', 'engine': 'K', 'sources': []}
            res = self.client.post(
                reverse('chat:send'), {'message': 'registered hello', 'newchat': '1'}
            )
        token = res.json()['conversation_token']
        self.client.post(reverse('chat:leave'))
        self.assertIsNone(Conversation.objects.get(token=token).closing_at)


class RootChatUrlTests(TestCase):
    """The address bar only ever shows the site root — sessions still work."""

    def setUp(self):
        cache.clear()

    def test_root_renders_public_landing(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Start Chatting')

    def test_chat_url_renders_chat(self):
        res = self.client.get(reverse('chat:page'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Kumusta')

    @mock.patch('apps.chat.services.ai.answer_question')
    def test_send_keeps_url_at_root_and_session_works(self, answer):
        answer.return_value = {'reply': 'ok', 'engine': 'K', 'sources': []}
        res = self.client.post(
            reverse('chat:send'), {'message': 'hi from root', 'newchat': '1'}
        )
        self.assertEqual(res.status_code, 200)
        token = res.json()['conversation_token']
        # The tab token restores its own chat; a plain page load stays fresh.
        hist = self.client.post(reverse('chat:history'), {'token': token}).json()
        self.assertEqual(hist['messages'][0]['content'], 'hi from root')
        self.assertContains(self.client.get('/chat/'), 'Kumusta')

    @mock.patch('apps.chat.services.ai.answer_question')
    def test_open_endpoint_redirects_to_root(self, answer):
        answer.return_value = {'reply': 'ok', 'engine': 'K', 'sources': []}
        token = self.client.post(
            reverse('chat:send'), {'message': 'open via post', 'newchat': '1'}
        ).json()['conversation_token']
        self.client.post(reverse('chat:new'))

        res = self.client.post(reverse('chat:open'), {'token': token})
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res['Location'], '/chat/')
        hist = self.client.post(reverse('chat:history'), {'token': token}).json()
        self.assertEqual(hist['messages'][0]['content'], 'open via post')

    def test_new_chat_clears_selection(self):
        with mock.patch('apps.chat.services.ai.answer_question') as answer:
            answer.return_value = {'reply': 'ok', 'engine': 'K', 'sources': []}
            self.client.post(
                reverse('chat:send'), {'message': 'first chat', 'newchat': '1'}
            )
        token = self.client.post(
            reverse('chat:send'), {'message': 'first chat', 'newchat': '1'}
        ).json()['conversation_token']
        self.client.post(reverse('chat:new'))
        page = self.client.get('/chat/')
        # A guest's chat page is always the welcome state; the previous chat is
        # only reachable through this tab's own sessionStorage token.
        self.assertContains(page, 'Kumusta')
        self.assertFalse(page.context['chat_messages'])
        self.assertTrue(Conversation.objects.filter(token=token).exists())


class LandingFlowTests(TestCase):
    """Landing page first, then the chat; guests never see a session list."""

    def setUp(self):
        cache.clear()

    def test_root_shows_landing_before_chat(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Start Chatting')

    def test_start_chat_renders_chat_at_chat_url(self):
        res = self.client.get(reverse('chat:page'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Kumusta')

    @mock.patch('apps.chat.services.ai.answer_question')
    def test_guest_sessions_are_not_listed(self, answer):
        answer.return_value = {'reply': 'ok', 'engine': 'K', 'sources': []}
        self.client.post(reverse('chat:send'), {'message': 'guest secret one', 'newchat': '1'})
        self.client.post(reverse('chat:send'), {'message': 'guest secret two', 'newchat': '1'})
        page = self.client.get('/chat/')
        self.assertEqual(list(page.context['sessions']), [])
        self.assertNotContains(page, 'Recent')

    @mock.patch('apps.chat.services.ai.answer_question')
    def test_registered_user_sees_own_sessions(self, answer):
        answer.return_value = {'reply': 'ok', 'engine': 'K', 'sources': []}
        user = User.objects.create_user(
            username='sessuser', email='sessuser@example.com', password='TestPass!2345'
        )
        self.client.force_login(user)
        self.assertContains(self.client.get('/'), 'Start Chatting')   # landing after login
        self.client.get(reverse('chat:page'))                          # Start Chatting
        self.client.post(reverse('chat:send'), {'message': 'registered secret', 'newchat': '1'})
        page = self.client.get('/chat/')
        self.assertEqual(len(page.context['sessions']), 1)
        self.assertContains(page, 'Recent')


class ChatPageTests(TestCase):
    def test_chat_page_renders(self):
        user = User.objects.create_user(
            username='pageuser', email='page@example.com', password='test-pass-123',
        )
        self.client.force_login(user)
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
