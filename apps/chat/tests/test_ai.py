"""Unit tests para sa KNIGHT AI service (network mocked — walang tunay na API calls)."""

import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import requests
from django.test import SimpleTestCase, override_settings

from apps.chat.services import ai


class FakeResponse:
    def __init__(self, payload=None, status=200, headers=None, text=''):
        self._payload = payload if payload is not None else {}
        self.status_code = status
        self.headers = headers or {}
        self.text = text

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f'{self.status_code}', response=self)


def _chat_ok_payload(content='Hello from KNIGHT'):
    return {
        'choices': [{'message': {'content': content}}],
        'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15},
    }


class NeedsResearchTests(SimpleTestCase):
    def test_empty_kb_always_researches(self):
        self.assertTrue(ai.needs_research('ano ang enrollment process', []))

    def test_kb_hit_without_hints_skips_web(self):
        item = ai.KItem(title='Registrar', content='Office hours 8am-5pm', source='t.txt', category='General')
        self.assertFalse(ai.needs_research('saan ang registrar office', [item]))

    def test_kb_hit_with_freshness_hint_researches(self):
        item = ai.KItem(title='Registrar', content='Office hours 8am-5pm', source='t.txt', category='General')
        self.assertTrue(ai.needs_research('may bagong announcement ba', [item]))


class RetryTests(SimpleTestCase):
    @override_settings(AI_RETRY_ATTEMPTS=1, AI_RETRY_BACKOFF=0.0)
    def test_transient_error_retried_then_succeeds(self):
        calls = {'n': 0}

        def fake_post(*args, **kwargs):
            calls['n'] += 1
            if calls['n'] == 1:
                raise requests.ConnectTimeout('temporary')
            return FakeResponse(_chat_ok_payload('ok after retry'))

        with mock.patch.object(ai.requests, 'post', side_effect=fake_post), \
                mock.patch.object(ai.time, 'sleep'), \
                mock.patch.object(ai, '_record_usage'):
            out = ai._chat_openai('http://x', 'key', 'm', 'sys', [], 'hi')
        self.assertEqual(out, 'ok after retry')
        self.assertEqual(calls['n'], 2)

    @override_settings(AI_RETRY_ATTEMPTS=2, AI_RETRY_BACKOFF=0.0)
    def test_non_transient_error_not_retried(self):
        calls = {'n': 0}

        def fake_post(*args, **kwargs):
            calls['n'] += 1
            return FakeResponse({}, status=400)

        with mock.patch.object(ai.requests, 'post', side_effect=fake_post), \
                mock.patch.object(ai.time, 'sleep'):
            with self.assertRaises(ai.AIUnavailable):
                ai._chat_openai('http://x', 'key', 'm', 'sys', [], 'hi')
        self.assertEqual(calls['n'], 1)

    @override_settings(AI_RETRY_ATTEMPTS=1, AI_RETRY_BACKOFF=0.0)
    def test_transient_exhausted_raises_unavailable(self):
        def fake_post(*args, **kwargs):
            raise requests.ConnectTimeout('still down')

        with mock.patch.object(ai.requests, 'post', side_effect=fake_post), \
                mock.patch.object(ai.time, 'sleep'):
            with self.assertRaises(ai.AIUnavailable):
                ai._chat_openai('http://x', 'key', 'm', 'sys', [], 'hi')


class WebSaveGateTests(SimpleTestCase):
    def _run_answer(self, web_save):
        web = [{
            'title': 'KCC FB Post',
            'snippet': 'The KCC enrollment for 2026 is now open for all students.',
            'url': 'https://example.com/post',
        }]
        with override_settings(AI_WEB_SAVE_FACTS=web_save, GEMINI_API_KEY=''), \
                mock.patch.object(ai, '_load_knowledge', return_value=[]), \
                mock.patch.object(ai, 'web_search', return_value=web), \
                mock.patch.object(ai, 'chat', return_value=('web answer', 'KNIGHT v1.0')), \
                mock.patch.object(ai, 'remember') as remember_mock:
            result = ai.answer_question('latest KCC enrollment update please')
        return result, remember_mock

    def test_flag_off_does_not_save(self):
        result, remember_mock = self._run_answer(False)
        self.assertFalse(remember_mock.called)
        self.assertEqual(result['sources'][0]['url'], 'https://example.com/post')

    def test_flag_on_saves(self):
        result, remember_mock = self._run_answer(True)
        self.assertTrue(remember_mock.called)


class SourcesFormatTests(SimpleTestCase):
    def test_combined_sources_have_titles_urls_and_types(self):
        item = ai.KItem(title='Car Pass', content='Go to HR office.', source='a.txt', category='General')
        web = [{'title': 'FB Update', 'snippet': 'x', 'url': 'https://fb.example/p/1'}]
        with mock.patch.object(ai, 'correct_prompt', side_effect=lambda q, **kw: q), \
                mock.patch.object(ai, '_retrieve', return_value=[item]), \
                mock.patch.object(ai, 'web_search', return_value=web), \
                mock.patch.object(ai, 'chat', return_value=('combined', 'KNIGHT v1.0')):
            result = ai.answer_question('may bagong update ba tungkol sa car pass')
        types = [s['type'] for s in result['sources']]
        self.assertNotIn('kb', types)  # KB chips hindi na ipinapadala
        self.assertIn('web', types)
        web_src = [s for s in result['sources'] if s['type'] == 'web'][0]
        self.assertEqual(web_src['url'], 'https://fb.example/p/1')

    def test_kb_only_answer_has_no_sources(self):
        item = ai.KItem(title='Car Pass', content='Go to HR office.', source='a.txt', category='General')
        with mock.patch.object(ai, '_retrieve', return_value=[item]), \
                mock.patch.object(ai, 'chat', return_value=('kb answer', 'KNIGHT v1.0')):
            result = ai.answer_question('saan ako kukuha ng car pass')
        self.assertEqual(result['sources'], [])


class UserUsageRecordingTests(SimpleTestCase):
    def test_record_user_usage_tracks_per_engine(self):
        user = SimpleNamespace(pk=7, username='user7')
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / 'usage_by_user.json'
            with mock.patch.object(ai, 'USAGE_BY_USER_FILE', target):
                ai._record_user_usage('groq', user, prompt_tokens=10, completion_tokens=5, total_tokens=15)
                ai._record_user_usage('gemini', user, total_tokens=7)
            data = json.loads(target.read_text(encoding='utf-8'))
        self.assertEqual(data['7']['username'], 'user7')
        self.assertEqual(data['7']['engines']['groq']['total_tokens'], 15)
        self.assertEqual(data['7']['engines']['gemini']['total_tokens'], 7)
        self.assertEqual(data['7']['total_tokens'], 22)

    def test_get_usage_by_user_handles_missing_file(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / 'nope.json'
            with mock.patch.object(ai, 'USAGE_BY_USER_FILE', target):
                self.assertEqual(ai.get_usage_by_user(), {})


class CorrectPromptTests(SimpleTestCase):
    def test_correct_prompt_returns_fixed_text(self):
        with mock.patch.object(ai, 'chat', return_value=('saan ang registrar office?', 'KNIGHT v1.0')):
            self.assertEqual(ai.correct_prompt('asan ang regstrar ofis?'), 'saan ang registrar office?')

    def test_correct_prompt_falls_back_on_failure(self):
        with mock.patch.object(ai, 'chat', side_effect=ai.AIUnavailable('down')):
            self.assertEqual(ai.correct_prompt('asan ang regstrar ofis?'), 'asan ang regstrar ofis?')

    def test_answer_question_uses_corrected_prompt(self):
        seen = {}

        def fake_chat(prompt, history, message, engine='auto', user=None):
            seen['msg'] = message
            return 'Sagot ni KNIGHT.', 'KNIGHT v1.0'

        def fake_correct(q, engine='auto', user=None):
            return 'saan ang registrar office'

        web = [{'title': 'KCC', 'snippet': 'Ang enrollment ay bukas para sa lahat ngayong taon.', 'url': 'https://kcc.example/enroll'}]
        with mock.patch.object(ai, 'correct_prompt', side_effect=fake_correct), \
                mock.patch.object(ai, '_retrieve', return_value=[]), \
                mock.patch.object(ai, 'web_search', return_value=web), \
                mock.patch.object(ai, 'chat', side_effect=fake_chat):
            result = ai.answer_question('asan ang regstrar ofis')
        self.assertEqual(seen['msg'], 'saan ang registrar office')
        self.assertEqual(result['reply'], 'Sagot ni KNIGHT.')


class SearchQueryTests(SimpleTestCase):
    def test_kcc_query_gets_school_context(self):
        self.assertEqual(
            ai._build_search_query('sino ang current president ng kcc ngayon'),
            'sino ang current president ng kcc ngayon Kabankalan Catholic College',
        )

    def test_query_with_kabankalan_unchanged(self):
        self.assertEqual(
            ai._build_search_query('kabankalan catholic college president'),
            'kabankalan catholic college president',
        )

    def test_generic_query_unchanged(self):
        self.assertEqual(ai._build_search_query('enrollment steps'), 'enrollment steps')


class AutoLearnNotedModeTests(SimpleTestCase):
    def test_facts_are_noted_but_not_saved(self):
        facts = [{'title': 'CMAT Dean Office', 'content': '2nd floor old building'}]
        with mock.patch.object(ai, 'chat', return_value=('extracted', 'KNIGHT v1.0')), \
                mock.patch.object(ai, '_parse_facts', return_value=facts), \
                mock.patch.object(ai, 'remember') as remember_mock:
            noted = ai.auto_learn('Ang dean office ng CMAT ay nasa 2nd floor ng old building.')
        self.assertEqual(noted, ['CMAT Dean Office'])
        self.assertFalse(remember_mock.called)


class ReasoningUpgradeTests(SimpleTestCase):
    """Per-engine reasoning effort + escalation retry (mocked, walang API calls)."""

    @override_settings(AI_REASONING_EFFORT='medium', AI_REASONING_EFFORT_PRIMARY='high',
                       AI_REASONING_EFFORT_FALLBACK='')
    def test_slot_effort_resolution(self):
        self.assertEqual(ai._slot_reasoning_effort('primary'), 'high')
        self.assertEqual(ai._slot_reasoning_effort('fallback'), 'medium')

    @override_settings(AI_REASONING_EFFORT='medium', AI_REASONING_EFFORT_PRIMARY='none')
    def test_slot_effort_none_disables_param(self):
        self.assertEqual(ai._slot_reasoning_effort('primary'), '')
        self.assertEqual(ai._slot_reasoning_effort('fallback'), 'medium')

    @override_settings(AI_MAX_OUTPUT_TOKENS=2048)
    def test_effort_sent_in_payload(self):
        captured = {}

        def fake_post(url, **kwargs):
            captured.update(kwargs['json'])
            return FakeResponse(_chat_ok_payload('ok'))

        with mock.patch.object(ai.requests, 'post', side_effect=fake_post), \
                mock.patch.object(ai, '_record_usage'):
            ai._chat_openai('http://x', 'key', 'm', 'sys', [], 'hi', effort='high')
        self.assertEqual(captured['reasoning_effort'], 'high')
        self.assertEqual(captured['max_tokens'], 2048)

    @override_settings(AI_REASONING_EFFORT='none')
    def test_effort_omitted_when_disabled(self):
        captured = {}

        def fake_post(url, **kwargs):
            captured.update(kwargs['json'])
            return FakeResponse(_chat_ok_payload('ok'))

        with mock.patch.object(ai.requests, 'post', side_effect=fake_post), \
                mock.patch.object(ai, '_record_usage'):
            ai._chat_openai('http://x', 'key', 'm', 'sys', [], 'hi')
        self.assertNotIn('reasoning_effort', captured)

    @override_settings(AI_MAX_OUTPUT_TOKENS=2048, AI_REASONING_ESCALATION_TOKENS=4096)
    def test_escalation_retry_when_reasoning_exhausts_budget(self):
        calls = {'budgets': []}

        def fake_post(url, **kwargs):
            calls['budgets'].append(kwargs['json']['max_tokens'])
            if len(calls['budgets']) == 1:
                return FakeResponse({
                    'choices': [{'message': {'content': ''}, 'finish_reason': 'length'}],
                    'usage': {'total_tokens': 2048},
                })
            return FakeResponse(_chat_ok_payload('reasoned answer'))

        with mock.patch.object(ai.requests, 'post', side_effect=fake_post), \
                mock.patch.object(ai, '_record_usage'):
            out = ai._chat_openai('http://x', 'key', 'm', 'sys', [], 'hi')
        self.assertEqual(out, 'reasoned answer')
        self.assertEqual(calls['budgets'], [2048, 4096])

    @override_settings(AI_MAX_OUTPUT_TOKENS=2048, AI_REASONING_ESCALATION_TOKENS=0)
    def test_no_escalation_when_disabled(self):
        calls = {'n': 0}

        def fake_post(url, **kwargs):
            calls['n'] += 1
            return FakeResponse({
                'choices': [{'message': {'content': ''}, 'finish_reason': 'length'}],
                'usage': {},
            })

        with mock.patch.object(ai.requests, 'post', side_effect=fake_post), \
                mock.patch.object(ai, '_record_usage'):
            with self.assertRaises(ai.AIUnavailable):
                ai._chat_openai('http://x', 'key', 'm', 'sys', [], 'hi')
        self.assertEqual(calls['n'], 1)

    def test_empty_non_length_response_not_retried(self):
        calls = {'n': 0}

        def fake_post(url, **kwargs):
            calls['n'] += 1
            return FakeResponse({
                'choices': [{'message': {'content': ''}, 'finish_reason': 'stop'}],
                'usage': {},
            })

        with mock.patch.object(ai.requests, 'post', side_effect=fake_post), \
                mock.patch.object(ai, '_record_usage'):
            with self.assertRaises(ai.AIUnavailable):
                ai._chat_openai('http://x', 'key', 'm', 'sys', [], 'hi')
        self.assertEqual(calls['n'], 1)

    def test_chat_passes_explicit_effort_to_slot(self):
        slot_mock = mock.MagicMock(return_value=('ok', 'KNIGHT v1.0'))
        with mock.patch.object(ai, '_chat_slot', slot_mock):
            out = ai.chat('sys', [], 'hi', effort='low')
        self.assertEqual(out, ('ok', 'KNIGHT v1.0'))
        self.assertEqual(slot_mock.call_args.kwargs.get('effort'), 'low')

    def test_correct_prompt_uses_low_effort(self):
        chat_mock = mock.MagicMock(return_value=('saan ang registrar office?', 'KNIGHT v1.0'))
        with mock.patch.object(ai, 'chat', chat_mock):
            ai.correct_prompt('asan ang regstrar ofis?')
        self.assertEqual(chat_mock.call_args.kwargs.get('effort'), 'low')


class SingleKnightNameTests(SimpleTestCase):
    """Isang brand lang sa chat kahit dalawang provider sa likod."""

    @override_settings(AI_NAME='KNIGHT')
    def test_knight_name_uses_ai_name(self):
        self.assertEqual(ai._knight_name(), 'KNIGHT')

    @override_settings(AI_NAME='')
    def test_knight_name_falls_back_to_knight(self):
        self.assertEqual(ai._knight_name(), 'KNIGHT')

    @override_settings(AI_NAME='KNIGHT')
    def test_both_slots_report_the_same_name(self):
        with mock.patch.object(ai, '_chat_openai', return_value='ok'):
            primary = ai._chat_slot('primary', 'sys', [], 'hi')
            fallback = ai._chat_slot('fallback', 'sys', [], 'hi')
        self.assertEqual(primary[0], fallback[0])
        self.assertEqual(primary[1], 'KNIGHT')
        self.assertEqual(fallback[1], 'KNIGHT')

    def test_conversation_choices_expose_one_model(self):
        from apps.chat.models import Conversation
        self.assertEqual([v for v, _ in Conversation.ENGINE_CHOICES], ['auto'])
        self.assertIn('primary', Conversation.ENGINE_VALUES)
        self.assertIn('fallback', Conversation.ENGINE_VALUES)


class ReasoningParamFallbackTests(SimpleTestCase):
    """Provider na tumatanggi sa reasoning_effort: i-drop at retry, hindi pumalya."""

    def _call(self, responses, effort='low'):
        calls = []

        def fake_post(url, **kwargs):
            # _post() passes the body as requests' json= keyword.
            calls.append(dict(kwargs.get('json') or {}))
            item = responses[len(calls) - 1]
            if isinstance(item, Exception):
                raise item
            return item

        with mock.patch.object(ai.requests, 'post', side_effect=fake_post), \
                mock.patch.object(ai, '_record_usage'), \
                override_settings(AI_MAX_OUTPUT_TOKENS=1024, AI_REASONING_ESCALATION_TOKENS=0):
            content = ai._chat_openai('http://x', 'key', 'm', 'sys', [], 'hi', effort=effort)
        return content, calls

    def _http_400(self, text):
        resp = FakeResponse(status=400, text=text)
        err = requests.HTTPError('400 Client Error', response=resp)
        err.response = resp
        return err

    def test_drops_reasoning_effort_and_retries_once(self):
        content, calls = self._call([
            self._http_400('{"error":{"message":"unsupported parameter: reasoning_effort"}}'),
            FakeResponse(payload=_chat_ok_payload('Sagot ni KNIGHT')),
        ])
        self.assertEqual(content, 'Sagot ni KNIGHT')
        self.assertEqual(calls[0].get('reasoning_effort'), 'low')
        self.assertNotIn('reasoning_effort', calls[1])

    def test_unrelated_400_is_not_retried(self):
        with self.assertRaises(ai.AIUnavailable):
            self._call([self._http_400('{"error":"context length exceeded"}')])

    def test_rejects_reasoning_param_detects_only_400(self):
        self.assertFalse(ai._rejects_reasoning_param(self._http_400_subclass(500)))
        self.assertTrue(ai._rejects_reasoning_param(
            self._http_400('unknown parameter reasoning_effort')))

    def _http_400_subclass(self, status):
        resp = FakeResponse(status=status, text='reasoning_effort is invalid')
        err = requests.HTTPError(f'{status}', response=resp)
        err.response = resp
        return err
