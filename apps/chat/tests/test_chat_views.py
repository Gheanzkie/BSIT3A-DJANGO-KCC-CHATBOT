"""Tests para sa chat views — throttle, sources passthrough, auto-learn gating."""

from unittest import mock

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

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
    def test_send_requires_login(self):
        res = self.client.post(reverse('chat:send'), {'message': 'hi there friend'})
        self.assertEqual(res.status_code, 302)


class ChatPageTests(TestCase):
    def test_chat_page_renders(self):
        user = User.objects.create_user(
            username='pageuser', email='page@example.com', password='test-pass-123',
        )
        self.client.force_login(user)
        res = self.client.get(reverse('chat:page'))
        self.assertEqual(res.status_code, 200)
