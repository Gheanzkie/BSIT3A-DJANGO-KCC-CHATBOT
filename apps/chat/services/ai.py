"""KNIGHT AI service — Groq + Gemini chat with a fallback chain.

BOTH chat engines speak the OpenAI-compatible /chat/completions format
(Groq primary, Google Gemini fallback). Nothing is hardcoded: base URL,
model name, and key all come from .env / settings.

KNOWLEDGE — file-based, walang MySQL:
  Lahat ng alam ni KNIGHT ay galing sa mga .txt file sa apps/chat/knowledge/.
  First line ng file = title; ang natitira = content. Pwede ang sub-folders
  (folder name = category). Magdagdag lang ng txt file — automatic nang
  mababasa, walang command na kailangan i-run. Ang semantic-search cache
  (knowledge/_embeddings.json) ay auto-generated at auto-refresh.

Default slots:
  Primary   (KNIGHT v1.0): AI_PRIMARY_BASE_URL  + AI_CHAT_MODEL_GROQ   + GROQ_API_KEY
  Fallback  (KNIGHT v1.2): AI_FALLBACK_BASE_URL + AI_CHAT_MODEL_GEMINI + GEMINI_API_KEY
  Embeddings             : Google Gemini (AI_EMBED_MODEL = gemini-embedding-001)

Reasoning (upgrade): AI_REASONING_EFFORT ang global default; may per-engine
overrides (AI_REASONING_EFFORT_PRIMARY / _FALLBACK — 'none' = huwag ipadala ang
param). Ang utility calls (prompt fix, auto-learn) ay 'low' pa rin para tipid sa
quota. Kapag naubos ng hidden reasoning ang output budget (empty reply,
finish_reason 'length'), isang escalation retry (AI_REASONING_ESCALATION_TOKENS)
bago sumuko sa provider.

Kung walang embedding key (o pumalya ang embeddings), keyword search pa rin
ang gagamitin — tuloy pa rin ang sagot.
"""

import hashlib
import json
import logging
import math
import random
import re
import threading
import time
from datetime import datetime

from django.utils import timezone
from pathlib import Path
from typing import NamedTuple

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = getattr(settings, 'AI_HTTP_TIMEOUT', 30)
MAX_ITEM_CHARS = 1200  # cap per knowledge item sa prompt (keep prompts small)

GEMINI_BASE = 'https://generativelanguage.googleapis.com/v1beta'  # native API — embeddings lang

# --- Usage stats (para sa dashboard): tokens + calls per engine ---
USAGE_FILE = Path(__file__).resolve().parent.parent / 'usage_stats.json'
# Per-user usage (users page): tokens + calls kada engine kada user.
USAGE_BY_USER_FILE = Path(__file__).resolve().parent.parent / 'usage_by_user.json'
_USAGE_LOCK = threading.Lock()


def _record_usage(kind, *, prompt_tokens=0, completion_tokens=0, total_tokens=0, items=0, rate_limit=None, latency_ms=None, user=None):
    """I-log ang isang AI call sa usage_stats.json (dashboard display)."""
    try:
        data = json.loads(USAGE_FILE.read_text(encoding='utf-8')) if USAGE_FILE.exists() else {}
    except ValueError:
        data = {}
    row = data.get(kind) or {'calls': 0, 'prompt_tokens': 0, 'completion_tokens': 0,
                             'total_tokens': 0, 'embed_items': 0}
    row['calls'] += 1
    row['prompt_tokens'] += int(prompt_tokens or 0)
    row['completion_tokens'] += int(completion_tokens or 0)
    row['total_tokens'] += int(total_tokens or 0)
    row['embed_items'] += int(items or 0)
    if latency_ms is not None:
        row['last_latency_ms'] = int(latency_ms)
    row['last_call'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if rate_limit:
        row['rate_limit'] = rate_limit
    data[kind] = row
    try:
        with _USAGE_LOCK:
            USAGE_FILE.write_text(json.dumps(data, indent=2), encoding='utf-8')
    except OSError as exc:
        logger.warning('Hindi maisulat ang usage stats: %s', exc)
    if user is not None:
        _record_user_usage(kind, user, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
                           total_tokens=total_tokens, items=items, latency_ms=latency_ms)


def get_usage():
    """Babasahin ang usage_stats.json para sa dashboard."""
    try:
        return json.loads(USAGE_FILE.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}


def _record_user_usage(kind, user, *, prompt_tokens=0, completion_tokens=0, total_tokens=0, items=0, latency_ms=None):
    """I-log ang AI call kada user sa usage_by_user.json (users page display)."""
    try:
        data = json.loads(USAGE_BY_USER_FILE.read_text(encoding='utf-8')) if USAGE_BY_USER_FILE.exists() else {}
    except ValueError:
        data = {}
    key = str(getattr(user, 'pk', '') or '')
    if not key:
        return
    row = data.get(key) or {'username': '', 'total_tokens': 0, 'engines': {}}
    row['username'] = getattr(user, 'username', '') or row.get('username', '')
    engines = row.get('engines') or {}
    eng = engines.get(kind) or {'calls': 0, 'prompt_tokens': 0, 'completion_tokens': 0,
                                'total_tokens': 0, 'embed_items': 0}
    eng['calls'] += 1
    eng['prompt_tokens'] += int(prompt_tokens or 0)
    eng['completion_tokens'] += int(completion_tokens or 0)
    eng['total_tokens'] += int(total_tokens or 0)
    eng['embed_items'] += int(items or 0)
    if latency_ms is not None:
        eng['last_latency_ms'] = int(latency_ms)
    eng['last_call'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    engines[kind] = eng
    row['engines'] = engines
    row['total_tokens'] = sum(int(e.get('total_tokens') or 0) for e in engines.values())
    data[key] = row
    try:
        with _USAGE_LOCK:
            USAGE_BY_USER_FILE.write_text(json.dumps(data, indent=2), encoding='utf-8')
    except OSError as exc:
        logger.warning('Hindi maisulat ang per-user usage stats: %s', exc)


def get_usage_by_user():
    """Babasahin ang usage_by_user.json para sa users page."""
    try:
        return json.loads(USAGE_BY_USER_FILE.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}

FALLBACK_NO_MATCH = (
    'Wala akong makitang impormasyon tungkol diyan sa KCC knowledge base. '
    'Para sa tumpak na sagot, mangyaring puntahan o kontakin ang Registrar Office.'
)
FALLBACK_NO_MATCH_EN = (
    'I could not find information about that in the KCC knowledge base. '
    'For an accurate answer, please visit or contact the Registrar Office.'
)

# Engine preference order: which provider gets tried first (the other is the safety net).
_ENGINE_ORDER = {
    'auto': ('primary', 'fallback'),
    'primary': ('primary', 'fallback'),
    'fallback': ('fallback', 'primary'),
}

_LANGUAGE_RULES = {
    'tl': 'ALWAYS answer in Tagalog (Filipino), even if the question is in English.',
    'en': 'ALWAYS answer in English, even if the question is in Tagalog.',
    'auto': "Match the user's language — Tagalog if the question is Tagalog, English if English.",
}

# --- Greeting auto-reply (file: apps/chat/replies.txt; built-in fallback sa ibaba) ---
_GREETING_CORE = {'hi', 'hello', 'helo', 'hey', 'yo', 'sup', 'uy', 'oy', 'kamusta', 'kumusta', 'musta'}
_GREETING_EXTRA = _GREETING_CORE | {
    'there', 'knight', 'sir', 'maam', 'good', 'morning', 'afternoon', 'evening',
    'day', 'magandang', 'umaga', 'hapon', 'gabi', 'araw', 'ka', 'kayo', 'po',
    'bro', 'pare', 'lods', 'guys', 'everyone', 'all', 'boss',
}
_GREETING_FILLER = {'po', 'knight', 'there', 'sir', 'maam', 'bro', 'pare', 'lods', 'boss'}

_TAGALOG_HINT_WORDS = {
    'ang', 'ng', 'sa', 'mga', 'ano', 'sino', 'paano', 'saan', 'kailan', 'bakit',
    'ba', 'po', 'ka', 'ako', 'ikaw', 'ko', 'mo', 'yung', 'ito', 'iyan',
    'pwede', 'puwede', 'kaba', 'salamat', 'kamusta', 'kumusta', 'musta',
    'magandang', 'umaga', 'hapon', 'gabi', 'lang', 'din', 'rin', 'naman',
    'pala', 'nga', 'meron', 'wala', 'hindi', 'opo', 'kayo', 'natin', 'namin', 'ninyo',
}

_GREETINGS = {
    'tl': [
        'Magandang araw! Ako si KNIGHT, ang KCC campus assistant. Paano ko kayo matutulungan ngayon?',
        'Kumusta! KNIGHT ito, ang KCC campus assistant. Anong KCC concern ang maaari kong sagutin?',
    ],
    'en': [
        'Good day! I am KNIGHT, the KCC campus assistant. How may I assist you today?',
        'Hello. This is KNIGHT, the KCC campus assistant. What KCC concern can I help you with?',
    ],
    'mix': [
        'Magandang araw! Ako si KNIGHT, ang KCC campus assistant. Ano ang maitutulong ko sa inyo ngayon?',
        'Hello. KNIGHT ito, ang KCC campus assistant. Anong KCC concern ang maaari kong sagutin?',
    ],
}

# --- Friendly small-talk replies — built-in fallback
# --- (ang ini-edit ng user ay apps/chat/replies.txt — auto-reload kapag nai-save) ---
_SMALLTALK = {
    'train': {
        'tl': [
            'Hindi ako natututo nang sarili ko. Ang KCC administration ang nagdadagdag ng impormasyon sa aking knowledge base.',
            'Ang KCC staff ang nag-a-update ng aking knowledge base. Maaari ninyong ipaalam sa admin ang nais idagdag.',
        ],
        'en': [
            'I do not learn on my own. My knowledge base is maintained by the KCC administration.',
            'My knowledge base is updated by KCC staff. Please inform an administrator about details you want added.',
        ],
    },
    'who': {
        'tl': [
            'Ako si KNIGHT, ang KCC campus assistant. Sinasagot ko ang mga tanong tungkol sa KCC: enrollment, offices, faculty, rooms, at mga proseso.',
            'KNIGHT ang pangalan ko, ang KCC campus assistant. Maaari kayong magtanong tungkol sa enrollment, offices, faculty, at mga pasilidad ng KCC.',
        ],
        'en': [
            'I am KNIGHT, the KCC campus assistant. I answer questions about KCC: enrollment, offices, faculty, rooms, and processes.',
            'My name is KNIGHT, the KCC campus assistant. You may ask about KCC enrollment, offices, faculty, and facilities.',
        ],
    },
    'capabilities': {
        'tl': [
            'Nasasagot ko ang mga tanong tungkol sa KCC: mga hakbang sa enrollment, lokasyon ng offices, faculty, rooms, fees, at mga proseso.',
            'Ang focus ko ay impormasyon tungkol sa KCC: offices at lokasyon, enrollment, faculty, rooms, at mga proseso ng paaralan. Ano ang nais ninyong malaman?',
        ],
        'en': [
            'I can answer KCC questions: enrollment steps, office locations, faculty, rooms, fees, and processes.',
            'My scope is KCC information: offices and their locations, enrollment, faculty, rooms, and school processes. What would you like to know?',
        ],
    },
    'thanks': {
        'tl': [
            'Walang anuman. Ako ay nalulugod na makatulong. May iba pa ba kayong tanong tungkol sa KCC?',
            'Walang anuman. Bumalik lamang kayo kung may kailangan pa kayong impormasyon tungkol sa KCC.',
        ],
        'en': [
            'You are welcome. I am glad to be of help. Do you have any other KCC questions?',
            'You are welcome. Please return anytime if you need more KCC information.',
        ],
    },
    'bye': {
        'tl': [
            'Paalam at ingat po. Bumalik lamang kayo kung may mga tanong pang tungkol sa KCC.',
            'Hanggang sa muli. Narito lamang ako kapag may KCC concerns kayo.',
        ],
        'en': [
            'Goodbye and take care. Please return anytime you have KCC questions.',
            'Goodbye. I will be here whenever you need KCC information.',
        ],
    },
}

# --- Editable replies file (apps/chat/replies.txt) ---
# Ang _GREETINGS at _SMALLTALK sa itaas ay built-in fallback lang. Ang sinusunod
# ni KNIGHT ay ang [section] groups sa replies.txt — pwede i-edit anumang oras,
# auto-reload kapag nai-save (walang kailangang i-restart).

REPLIES_FILE = Path(__file__).resolve().parent.parent / 'replies.txt'  # apps/chat/replies.txt
_replies_cache = {'mtime': None, 'data': {}}


def _parse_replies(path):
    """[section] groups -> {section: [lines]}. Ang '#' ay comment."""
    sections = {}
    current = None
    try:
        raw = Path(path).read_text(encoding='utf-8')
    except OSError:
        return sections
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('[') and line.endswith(']'):
            current = line[1:-1].strip().lower()
            sections.setdefault(current, [])
            continue
        if current:
            sections[current].append(line)
    return sections


def _replies():
    """Sections galing sa replies.txt — auto-reload kapag nabago ang file."""
    try:
        mtime = REPLIES_FILE.stat().st_mtime
    except OSError:
        mtime = None
    if mtime != _replies_cache['mtime']:
        _replies_cache['data'] = _parse_replies(REPLIES_FILE)
        _replies_cache['mtime'] = mtime
    return _replies_cache['data']


def _reply_variants(category, lang):
    """Variants para sa category+lang — file muna, built-in fallback kung wala."""
    variants = _replies().get(f'{category}-{lang}')
    if variants:
        return variants
    return (_SMALLTALK.get(category, {}).get(lang)
            or _SMALLTALK.get(category, {}).get('en')
            or ['Pasensya na, subukan ulit.'])


_KNIGHT_SYSTEM_TEMPLATE = """You are KNIGHT, the virtual campus assistant of KCC (Kabankalan Catholic College).

RESPONSE FORMAT (follow strictly):
1. Start with one direct sentence that answers the question. No greetings, no filler, no restating the question.
2. Add the supporting details from the context in short paragraphs. Use a bullet list ("- ") when the answer involves steps, requirements, schedules, or multiple items.
3. When the user must take action, end with one clear next step (which office to visit, or what to prepare).
4. Write in plain, professional, courteous language. No slang, no emoji, no exclamation marks.
5. Keep simple answers to 2-5 sentences. If the user asks for a full list or full text, give all of it completely - never truncate.

ACCURACY RULES:
- Answer USING ONLY the KNOWLEDGE BASE CONTEXT below.
- Think before answering: identify exactly what is asked, locate the supporting facts, and confirm that every claim is supported. If part of the question is not covered, state that plainly instead of guessing.
- If the answer is not in the context, say that the information is not available and recommend the appropriate KCC office. NEVER invent information.
- {language_rule}
- Scope: KCC campus matters only - offices, enrollment, faculty, rooms, and processes. For unrelated topics, state briefly that you can only assist with KCC-related questions.

KNOWLEDGE BASE CONTEXT:
{context}
"""

_KNIGHT_SMALLTALK_TEMPLATE = """You are KNIGHT, the virtual campus assistant of KCC (Kabankalan Catholic College).

There is NO knowledge-base context for this question. Follow these rules:
- If the question is about you (who you are, what you can do, whether you can be trained) or is small talk (thanks, praise, goodbye), reply in a professional, courteous tone in 1-3 sentences. No emoji, no slang.
- If it is about KCC but no information is available yet, state clearly that the information is not yet available, advise contacting or visiting the appropriate KCC office, and invite the user to share the details so they can be recorded. NEVER invent KCC facts or figures.
- If it is unrelated to KCC (general knowledge, coding, news, etc.), state briefly that you can only assist with KCC-related questions and invite a KCC question.
- {language_rule} Keep it short and direct: 1 to 3 sentences.
"""

_STOPWORDS = {
    'ang', 'ng', 'sa', 'na', 'at', 'ay', 'mga', 'the', 'a', 'an', 'is', 'are',
    'to', 'of', 'in', 'on', 'for', 'how', 'what', 'where', 'when', 'who',
    'paano', 'ano', 'saan', 'sino', 'kailan', 'ko', 'mo', 'namin', 'natin',
    'po', 'ba', 'yung', 'ito', 'iyan', 'doon', 'dito', 'kcc',
}


class AIConfigError(Exception):
    """Raised when the needed API key(s) are not configured."""


class AIUnavailable(Exception):
    """Raised when a provider failed (network error, rate limit, unexpected response)."""


# ---------------------------------------------------------------------------
# Low-level HTTP
# ---------------------------------------------------------------------------

def _post(url, *, headers=None, payload=None, params=None, timeout=None):
    resp = requests.post(url, headers=headers, json=payload, params=params,
                         timeout=timeout or REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp


def _is_transient(exc):
    """True kung dapat i-retry: timeout, connection error, 429, o 5xx."""
    if isinstance(exc, (requests.Timeout, requests.ConnectionError)):
        return True
    status = getattr(getattr(exc, 'response', None), 'status_code', None)
    return status in (429, 500, 502, 503, 504)


def _post_retry(url, *, headers=None, payload=None, params=None, timeout=None, attempts=None):
    """_post() na may bounded retry + exponential backoff para sa transient errors only."""
    if attempts is None:
        attempts = int(getattr(settings, 'AI_RETRY_ATTEMPTS', 2))
    backoff = float(getattr(settings, 'AI_RETRY_BACKOFF', 1.5))
    for attempt in range(attempts + 1):
        try:
            return _post(url, headers=headers, payload=payload, params=params, timeout=timeout)
        except requests.RequestException as exc:
            if attempt >= attempts or not _is_transient(exc):
                raise
            delay = backoff * (2 ** attempt) + random.uniform(0, 0.25)
            logger.info('Transient provider error (%s); retry %d/%d in %.1fs',
                        exc, attempt + 1, attempts, delay)
            time.sleep(delay)


# ---------------------------------------------------------------------------
# Embeddings (Gemini)
# ---------------------------------------------------------------------------

def embed_texts(texts):
    """Embed a list of strings via Gemini. Returns a list of vectors (list[float])."""
    key = settings.GEMINI_API_KEY
    if not key:
        raise AIConfigError('GEMINI_API_KEY is not set (needed for embeddings).')
    if not texts:
        return []

    vectors = []
    for start in range(0, len(texts), 50):  # batchEmbedContents limit-friendly
        batch = texts[start:start + 50]
        body = {
            'requests': [
                {
                    'model': f'models/{settings.AI_EMBED_MODEL}',
                    'content': {'parts': [{'text': t}]},
                }
                for t in batch
            ]
        }
        url = f'{GEMINI_BASE}/models/{settings.AI_EMBED_MODEL}:batchEmbedContents'
        t0 = time.monotonic()
        try:
            data = _post_retry(url, params={'key': key}, payload=body).json()
        except requests.RequestException as exc:
            raise AIUnavailable(f'Embedding request failed: {exc}') from exc

        batch_vectors = [item['values'] for item in data.get('embeddings', [])]
        if len(batch_vectors) != len(batch):
            raise AIUnavailable('Embedding response count mismatch.')
        vectors.extend(batch_vectors)
        _record_usage('embeddings', items=len(batch), latency_ms=(time.monotonic() - t0) * 1000)
    return vectors


def embed_text(text):
    return embed_texts([text])[0]


# ---------------------------------------------------------------------------
# Chat engines
# ---------------------------------------------------------------------------

def _normalize_effort(value):
    """Reasoning effort -> clean string. '' = huwag ipadala ang param ('none'/'off'/'-')."""
    v = (value or '').strip()
    return '' if v.lower() in ('', 'none', 'off', '-') else v


def _slot_reasoning_effort(slot):
    """Per-engine reasoning effort: AI_REASONING_EFFORT_<SLOT> kung naka-set, kundi ang global."""
    specific = getattr(settings, f'AI_REASONING_EFFORT_{slot.upper()}', '')
    if (specific or '').strip():
        return _normalize_effort(specific)
    return _normalize_effort(getattr(settings, 'AI_REASONING_EFFORT', ''))


def _chat_openai(base_url, api_key, model, system_prompt, history, user_message, usage_key='groq', user=None, effort=None, slot=None):
    """One OpenAI-compatible chat call.

    POST {base_url}/chat/completions with Bearer auth (Groq + Gemini).
    effort=None -> gamitin ang settings default; '' = huwag ipadala ang reasoning_effort.
    Kapag naubos ng hidden reasoning ang output budget (empty content, finish_reason
    'length'), i-retry isang beses ang parehong provider gamit ang
    AI_REASONING_ESCALATION_TOKENS na budget bago sumuko.
    """
    if not api_key:
        raise AIConfigError(f'API key for "{model}" is not set.')

    messages = [{'role': 'system', 'content': system_prompt}]
    messages.extend(history)
    messages.append({'role': 'user', 'content': user_message})

    if effort is None:
        effort = _normalize_effort(getattr(settings, 'AI_REASONING_EFFORT', ''))
    else:
        effort = _normalize_effort(effort)

    base_tokens = int(getattr(settings, 'AI_MAX_OUTPUT_TOKENS', 2048))
    escalation = int(getattr(settings, 'AI_REASONING_ESCALATION_TOKENS', 0) or 0)
    budgets = [base_tokens]
    if escalation > base_tokens:
        # Isang bounded retry: bigyan ng mas malaking budget ang hidden reasoning
        # bago sumuko sa provider na ito (finish_reason='length' + empty content).
        budgets.append(escalation)

    for attempt, max_tokens in enumerate(budgets):
        body = {
            'model': model,
            'messages': messages,
            'temperature': 0.2,
            'max_tokens': max_tokens,
        }
        if effort:
            body['reasoning_effort'] = effort
        t0 = time.monotonic()
        try:
            timeout = (int(getattr(settings, 'AI_HTTP_TIMEOUT_FALLBACK', 25))
                       if slot == 'fallback' else REQUEST_TIMEOUT)
            attempts = (int(getattr(settings, 'AI_RETRY_ATTEMPTS_FALLBACK', 1))
                        if slot == 'fallback' else None)
            resp = _post_retry(
                f'{base_url.rstrip("/")}/chat/completions',
                headers={'Authorization': f'Bearer {api_key}'},
                payload=body,
                timeout=timeout,
                attempts=attempts,
            )
            data = resp.json()
        except requests.RequestException as exc:
            raise AIUnavailable(f'Chat request failed ({model}): {exc}') from exc
        except ValueError as exc:
            raise AIUnavailable(f'Invalid JSON response from {model}') from exc

        usage = data.get('usage') or {}
        resp_headers = {k.lower(): v for k, v in resp.headers.items()}
        rate_limit = None
        if resp_headers.get('x-ratelimit-remaining-tokens'):
            rate_limit = {
                'remaining_tokens': resp_headers.get('x-ratelimit-remaining-tokens', ''),
                'limit_tokens': resp_headers.get('x-ratelimit-limit-tokens', ''),
                'reset': resp_headers.get('x-ratelimit-reset-tokens', ''),
            }
        _record_usage(
            usage_key,
            prompt_tokens=usage.get('prompt_tokens', 0),
            completion_tokens=usage.get('completion_tokens', 0),
            total_tokens=usage.get('total_tokens', 0),
            rate_limit=rate_limit,
            latency_ms=(time.monotonic() - t0) * 1000,
            user=user,
        )

        try:
            choice = data['choices'][0]
            content = (choice['message'].get('content') or '').strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise AIUnavailable(f'Unexpected response from {model}: {data}') from exc

        if content:
            return content

        if choice.get('finish_reason') == 'length' and attempt + 1 < len(budgets):
            logger.info('%s hit its output cap on hidden reasoning; retrying with max_tokens=%d.',
                        model, budgets[attempt + 1])
            continue
        raise AIUnavailable(f'{model} returned an empty answer (reasoning-only response).')


def _chat_slot(slot, system_prompt, history, user_message, user=None, effort=None):
    if effort is None:
        effort = _slot_reasoning_effort(slot)
    if slot == 'primary':
        return (
            _chat_openai(settings.AI_PRIMARY_BASE_URL, settings.GROQ_API_KEY,
                         settings.AI_CHAT_MODEL_GROQ, system_prompt, history, user_message,
                         usage_key='groq', user=user, effort=effort),
            settings.AI_PRIMARY_NAME,
        )
    return (
        _chat_openai(settings.AI_FALLBACK_BASE_URL, settings.GEMINI_API_KEY,
                     settings.AI_CHAT_MODEL_GEMINI, system_prompt, history, user_message,
                     usage_key='gemini', user=user, effort='', slot='fallback'),
        settings.AI_FALLBACK_NAME,
    )


_PROMPT_FIX_SYSTEM = """You are a spelling and grammar corrector for a Filipino student chatbot.
Fix the spelling, typo, at grammar ng mensahe ng user habang pinapanatili ang meaning at wika nito.
I-return LAMANG ang naitama na teksto — walang paliwanag, walang quotes, walang ibang sagot.
Kung tama na ang teksto, ibalik ito nang buo at walang babaguhin."""


def correct_prompt(message, engine='auto', user=None):
    """Model-based autocorrect ng maling prompt. Returns corrected text (o original kapag fail)."""
    original = (message or '').strip()
    if not original or len(original) < 12 or len(original) > 500:
        return original
    try:
        # Utility call: typo-fix lang — low effort, hindi ito reasoning task (tipid sa quota).
        # Run it on the fast engine when available so a slow provider is not paid twice.
        fix_engine = 'primary' if getattr(settings, 'GROQ_API_KEY', '') else engine
        fixed, _engine = chat(_PROMPT_FIX_SYSTEM, [], original, engine=fix_engine, user=user, effort='low')
    except AIUnavailable:
        return original
    fixed = (fixed or '').strip().strip('"').strip("'")
    if not fixed or len(fixed) > 500:
        return original
    return fixed


def chat(system_prompt, history, user_message, engine='auto', user=None, effort=None):
    """Try engines in preference order ('auto' | 'primary' | 'fallback'). Returns (answer, engine_name).

    effort: None = per-engine settings (AI_REASONING_EFFORT[_PRIMARY/_FALLBACK]);
    explicit 'low'/'medium'/'high' = override (hal. utility calls).
    """
    errors = []
    order = list(_ENGINE_ORDER.get(engine, _ENGINE_ORDER['auto']))
    # Short cooldown: a provider that just 503'd is skipped for a while instead of
    # making every single question wait for it first.
    healthy = [slot for slot in order if not _slot_dead(slot)]
    order = healthy or order
    for slot in order:
        try:
            reply = _chat_slot(slot, system_prompt, history, user_message, user=user, effort=effort)
            _mark_slot(slot, ok=True)
            return reply
        except (AIConfigError, AIUnavailable) as exc:
            _mark_slot(slot, ok=False)
            errors.append(f'{slot}: {exc}')
            logger.info('Engine %s failed (%s), trying next', slot, exc)
    raise AIUnavailable('; '.join(errors))


def _slot_dead(slot):
    return bool(cache.get(f'kcc:ai:dead:{slot}'))


def _mark_slot(slot, *, ok):
    key = f'kcc:ai:dead:{slot}'
    if ok:
        cache.delete(key)
    else:
        cache.set(key, 1, int(getattr(settings, 'AI_SLOT_COOLDOWN_SECONDS', 90)))


# ---------------------------------------------------------------------------
# Greeting auto-reply (no API needed)
# ---------------------------------------------------------------------------

def _is_greeting(text):
    """True kung purong greeting ang message (hi/hello/kamusta/good morning...)."""
    t = re.sub(r"[^a-z\s']", ' ', text.lower())
    words = t.split()
    if not words or len(words) > 5:
        return False
    core = [w for w in words if w not in _GREETING_FILLER]
    if not core or len(core) > 4:
        return False
    if any(w in _GREETING_CORE for w in core):
        return all(w in _GREETING_EXTRA for w in core)
    if core[0] in ('good', 'magandang') and len(core) >= 2 and core[1] in (
            'morning', 'afternoon', 'evening', 'day', 'umaga', 'hapon', 'gabi', 'araw'):
        return all(w in _GREETING_EXTRA for w in core)
    return False


def greeting_reply(text, language='auto'):
    """Canned greeting reply — 'auto' detects Tagalog from the greeting itself."""
    if language == 'auto':
        tokens = set(re.sub(r"[^a-z\s']", ' ', text.lower()).split())
        language = 'tl' if tokens & _TAGALOG_HINT_WORDS else 'mix'
    variants = _replies().get(f'greeting-{language}') or _GREETINGS.get(language, _GREETINGS['mix'])
    return random.choice(variants)


def _reply_language(text, language):
    """Language para sa canned replies: explicit choice wins; 'auto' detects from text."""
    if language in ('tl', 'en'):
        return language
    tokens = set(re.sub(r"[^a-z\s']", ' ', text.lower()).split())
    return 'tl' if tokens & _TAGALOG_HINT_WORDS else 'en'


_YOU_WORDS = {'ka', 'kaba', 'kayo', 'ikaw', 'mo', 'you', 'u'}
_QUESTION_WORDS = {
    'paano', 'saan', 'sino', 'ano', 'kailan', 'bakit', 'alin', 'magkano', 'ilan', 'nasaan',
    'what', 'how', 'where', 'who', 'when', 'why', 'which',
}

_TRAIN_HINTS_RE = re.compile(
    r"\b(trained|training|turuan|tinuturuan|matuto|natututo|nag[- ]?aaral|mag[- ]?aral|"
    r"self[\s-]?learn(ing)?|learn(ing)? from|can you learn|do you learn)\b"
)
_TRAIN_HINT2_RE = re.compile(r"\b(i[\s-]?train|mag[\s-]?train|itrain|train)\b")

_WHO_RE = re.compile(
    r"\b(sino ka( ba)?|ano ka( ba)?|who are you|what are you|sino si knight|what is knight|"
    r"introduce yourself|magpakilala|tungkol sa'?yo|about you)\b"
)

_CAPABILITY_RE = re.compile(
    r"(what can you do|what do you do|how can you help|ano ang kaya mo|anong kaya mo|"
    r"ano (ang )?(pwede|pwedeng|kaya) mo(ng)? (gawin|sagutin|tulungan)|"
    r"paano ka (makaka)?tulong|ano ang makakatulong mo|ano pwedeng itanong)"
)

_THANKS_RE = re.compile(r"\b(salamat|thank you|thank u|thanks|thankyou|ty)\b")
_BYE_RE = re.compile(r"\b(bye|good ?bye|paalam|see you|hanggang sa muli|take care|ingat)\b")


def _smalltalk_reply(text, language):
    """Canned friendly replies for common non-KB questions. Returns reply text or None."""
    if _is_greeting(text):
        return greeting_reply(text, language)

    t = re.sub(r"[^a-z\s'-]", ' ', text.lower())
    words = set(t.split())
    lang = _reply_language(text, language)

    # Train/learn questions — kailangan may "you" marker (para hindi ma-catch
    # ang campus questions tulad ng "saan ang training office").
    if (_TRAIN_HINTS_RE.search(t) or _TRAIN_HINT2_RE.search(t)) and words & _YOU_WORDS:
        return random.choice(_reply_variants('train', lang))
    if _WHO_RE.search(t):
        return random.choice(_reply_variants('who', lang))
    if _CAPABILITY_RE.search(t):
        return random.choice(_reply_variants('capabilities', lang))
    # Thanks/bye — huwag mahuli ang totoong tanong ("salamat, paano mag enroll?")
    if not words & _QUESTION_WORDS:
        if _THANKS_RE.search(t):
            return random.choice(_reply_variants('thanks', lang))
        if _BYE_RE.search(t):
            return random.choice(_reply_variants('bye', lang))
    return None


# ---------------------------------------------------------------------------
# Retrieval + the full RAG pipeline
# ---------------------------------------------------------------------------

def _cosine(a, b):
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = na = nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / math.sqrt(na * nb)


def _keywords(text):
    # Money amounts (9,000.00) are noise for keyword matching; keep grade numbers.
    text = re.sub(r'[\d,]+\.\d{2}', ' ', text.lower())
    return {w for w in re.findall(r'[a-zA-Z0-9]+', text)
            if (len(w) >= 3 or w.isdigit()) and w not in _STOPWORDS}


# ---------------------------------------------------------------------------
# Knowledge base — file-based (apps/chat/knowledge/*.txt). Walang MySQL.
# ---------------------------------------------------------------------------

KB_DIR = Path(__file__).resolve().parent.parent / 'knowledge'  # apps/chat/knowledge/
_KB_CACHE_NAME = '_embeddings.json'


class KItem(NamedTuple):
    """Isang knowledge entry na galing sa isang .txt file."""

    title: str
    content: str
    source: str    # relative path, e.g. 'hr-office.txt'
    category: str  # folder name kung nasa sub-folder; 'General' kung wala


def _load_knowledge():
    """Basahin LAHAT ng .txt files sa knowledge folder. First line = title."""
    items = []
    if not KB_DIR.is_dir():
        return items
    for path in sorted(KB_DIR.rglob('*.txt')):
        rel = path.relative_to(KB_DIR)
        if any(part.startswith(('_', '.')) for part in rel.parts):
            continue  # _README, hidden files — hindi kasama
        try:
            raw = path.read_text(encoding='utf-8').strip()
        except OSError:
            continue
        if not raw:
            continue
        lines = raw.splitlines()
        title = lines[0].lstrip('#').strip() or path.stem
        content = '\n'.join(lines[1:]).strip() or title
        folder = rel.parent.as_posix()
        items.append(KItem(
            title=title,
            content=content,
            source=rel.as_posix(),
            category='General' if folder == '.' else folder,
        ))
    return items


def _kb_fingerprint(items):
    h = hashlib.sha256()
    h.update(settings.AI_EMBED_MODEL.encode())
    for it in items:
        h.update(it.source.encode())
        h.update(it.content.encode())
    return h.hexdigest()


def _kb_embeddings(items):
    """Vectors para sa mga items — naka-cache sa knowledge/_embeddings.json.
    Auto-refresh kapag may binago, dinagdag, o tinanggal na file."""
    cache_path = KB_DIR / _KB_CACHE_NAME
    fp = _kb_fingerprint(items)
    try:
        cached = json.loads(cache_path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        cached = None
    if (isinstance(cached, dict) and cached.get('fingerprint') == fp
            and len(cached.get('vectors', [])) == len(items)):
        return cached['vectors']

    vectors = embed_texts([f'{it.title}\n{it.content[:MAX_ITEM_CHARS]}' for it in items])
    try:
        cache_path.write_text(json.dumps({'fingerprint': fp, 'vectors': vectors}), encoding='utf-8')
    except OSError as exc:
        logger.warning('Hindi maisulat ang embeddings cache: %s', exc)
    return vectors


def _retrieve(question, top_k=None, min_score=None):
    """Return the most relevant knowledge entries — galing sa knowledge/*.txt."""
    top_k = top_k or settings.AI_KB_TOP_K
    min_score = settings.AI_KB_MIN_SCORE if min_score is None else min_score

    items = _load_knowledge()
    if not items:
        return []

    # 1) Semantic search gamit ang cached embeddings (kailangan ang Gemini key)
    if settings.GEMINI_API_KEY:
        try:
            q_vec = embed_text(question)
            vectors = _kb_embeddings(items)
            scored = sorted(((_cosine(q_vec, v), it) for v, it in zip(vectors, items)),
                            key=lambda t: t[0], reverse=True)
            matched = [it for s, it in scored[:top_k] if s >= min_score]
            if matched:
                return matched
        except (AIConfigError, AIUnavailable) as exc:
            logger.warning('Semantic search failed, using keyword search: %s', exc)

    # 2) Keyword fallback — gumagana kahit walang keys, at bilang backup
    q_words = _keywords(question)
    if not q_words:
        return []
    scored = []
    for item in items:
        words = _keywords(f'{item.title} {item.content}')
        score = len(q_words & words)
        if score > 0:
            scored.append((score, item))
    scored.sort(key=lambda t: t[0], reverse=True)
    return [it for _, it in scored[:top_k]]


def _build_context(items):
    blocks = []
    for item in items:
        content = item.content[:MAX_ITEM_CHARS]
        blocks.append(f'[{item.category}] {item.title}\n{content}')
    return '\n\n---\n\n'.join(blocks)


# ---------------------------------------------------------------------------
# Chat-driven knowledge adds — writes a .txt under knowledge/
# ---------------------------------------------------------------------------

REMEMBER_SUBFOLDER = 'kcc'  # chat-added notes -> kcc/ folder (isang folder nlng, walang bagong folder)
REMEMBER_MAX_CHARS = 1200


def _remember_slug(title):
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    return (slug or 'note')[:40]


def remember(text, subfolder=REMEMBER_SUBFOLDER):
    """I-save ang info na galing sa chat bilang bagong knowledge file.

    Ang file ay awtomatikong babasahin ng _load_knowledge() (at
    nagre-refresh ang embeddings cache dahil sa fingerprint).
    """
    text = (text or '').strip()
    if not text:
        raise ValueError('Empty note.')
    text = text[:REMEMBER_MAX_CHARS]

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()] or [text]
    title = lines[0]
    rest = '\n'.join(lines[1:]) or title

    subfolder = (subfolder or '').strip().strip('/\\')
    note_dir = KB_DIR / subfolder if subfolder else KB_DIR
    note_dir.mkdir(parents=True, exist_ok=True)

    unique = hashlib.md5(text.encode('utf-8')).hexdigest()[:6]
    filename = f'note-{datetime.now().strftime("%Y%m%d-%H%M%S")}-{unique}-{_remember_slug(title)}.txt'
    (note_dir / filename).write_text(text + '\n', encoding='utf-8')

    return KItem(
        title=title,
        content=rest,
        source=f'{subfolder}/{filename}' if subfolder else filename,
        category=subfolder or 'General',
    )


# --- Announcements -> knowledge base (text only, walang images) ---

ANNOUNCEMENT_SUBFOLDER = 'announcements'


def _announcement_path(pk):
    return KB_DIR / ANNOUNCEMENT_SUBFOLDER / f'announcement-{int(pk)}.txt'


def sync_announcement_knowledge(pk, title, message, created_at=None, active=True):
    """Sync ang announcement sa knowledge base bilang text entry.

    Images are NEVER included - title + message lang. Kapag inactive o walang
    message, binubura ang entry para hindi masagot ng bot ang hindi published.
    """
    path = _announcement_path(pk)
    title = (title or '').strip() or 'KCC Announcement'
    message = (message or '').strip()

    if not active or not message:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        return None

    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = ''
    if created_at is not None:
        try:
            stamp = timezone.localtime(created_at).strftime('%B %d, %Y %I:%M %p')
        except (AttributeError, ValueError):
            stamp = str(created_at)
    header = f'{title} (KCC Announcement, {stamp})' if stamp else f'{title} (KCC Announcement)'
    path.write_text(f'{header}\n{message[:REMEMBER_MAX_CHARS]}\n', encoding='utf-8')
    return path


def remove_announcement_knowledge(pk):
    """Burahin ang announcement entry sa knowledge base."""
    try:
        _announcement_path(pk).unlink()
    except FileNotFoundError:
        pass


# --- Auto-learn: kumuha ng bagong KCC facts mula sa chat at i-save automatically ---

_AUTO_LEARN_PROMPT = """You extract factual information from a chat message for a campus knowledge base.

The message may be in Tagalog, English, or mixed. Capture ANY factual information about KCC (offices, schedules, fees, people, rooms, processes, policies) that the message states — this INCLUDES facts embedded in questions (e.g. "Diba bukas ang registrar ng 8am?" implies the registrar opens at 8am).

Reply with ONLY valid JSON:
{"facts": [{"title": "<short title in English>", "content": "<the fact in 1-3 English sentences>"}]}
Rules: max 5 facts; each content under 500 chars; write titles/content in English (translate if needed); keep names of offices/people as-is.
ONLY skip: pure greetings, thanks, goodbyes, and messages with no factual content at all. Skip uncertain statements (siguro, baka, maybe) unless stated as certain.
If there are no facts, reply with ONLY: {"facts": []}
"""


def _parse_facts(raw):
    start = raw.find('{')
    end = raw.rfind('}')
    if start == -1 or end <= start:
        return []
    try:
        data = json.loads(raw[start:end + 1])
    except ValueError:
        return []
    facts = data.get('facts')
    return facts if isinstance(facts, list) else []


def auto_learn(message, engine='primary'):
    """Kunin ang bagong KCC facts mula sa user message — (Noted) LANG, walang save sa KB.

    Returns list of noted titles ([] kung wala o pumalya).
    """
    message = (message or '').strip()
    if len(message) < 10:
        return []
    try:
        # Utility call: JSON fact extraction — low effort (tipid sa quota).
        raw, _ = chat(_AUTO_LEARN_PROMPT, [], message, engine=engine, effort='low')
    except (AIConfigError, AIUnavailable) as exc:
        logger.info('Auto-learn skipped (%s)', exc)
        return []

    facts = _parse_facts(raw)
    if not facts:
        return []

    # (Noted) mode: HUWAG nang i-save sa knowledge base — acknowledge lang ang nakuha.
    noted = []
    for fact in facts[:5]:
        if not isinstance(fact, dict):
            continue
        title = re.sub(r'\s+', ' ', str(fact.get('title') or '')).strip()[:80]
        content = re.sub(r'\s+', ' ', str(fact.get('content') or '')).strip()[:600]
        if not title or not content:
            continue
        noted.append(title)
    return noted


# ---------------------------------------------------------------------------
# Web research — kapag wala sa KB, hanapin online (DuckDuckGo) at i-save ang nahanap
# ---------------------------------------------------------------------------

WEB_SEARCH_TIMEOUT = 12

_KNIGHT_WEB_TEMPLATE = """You are KNIGHT, the virtual campus assistant of KCC (Kabankalan Catholic College).

The knowledge base had no information for this question, so LOCAL WEB RESEARCH RESULTS are provided below.

RESPONSE FORMAT (follow strictly):
1. Start with one direct sentence that answers the question.
2. Add supporting details in short paragraphs, or a bullet list ("- ") for steps, requirements, or multiple items.
3. State briefly that the information came from an online search and should be confirmed with the appropriate KCC office.
4. Write in plain, professional, courteous language. No slang, no emoji, no exclamation marks.
5. Keep simple answers to 2-5 sentences. If the user asks for a full list or full text, give all of it completely - never truncate.

ACCURACY RULES:
- Answer USING ONLY the WEB RESEARCH RESULTS below.
- Think before answering and verify every fact against the results.
- NEVER invent information beyond the results.
- {language_rule}

WEB RESEARCH RESULTS:
{context}
"""

_KNIGHT_COMBINED_TEMPLATE = """You are KNIGHT, the virtual campus assistant of KCC (Kabankalan Catholic College).

Two sources are provided: (1) the OFFICIAL KNOWLEDGE BASE CONTEXT of KCC, and (2) WEB RESEARCH RESULTS as a supplement.

RESPONSE FORMAT (follow strictly):
1. Start with one direct sentence that answers the question.
2. Add supporting details in short paragraphs, or a bullet list ("- ") for steps, requirements, or multiple items.
3. When part of the answer comes from the web results, note briefly that it came from an online search.
4. When the user must take action, end with one clear next step (which office to visit, or what to prepare).
5. Write in plain, professional, courteous language. No slang, no emoji, no exclamation marks.
6. Keep simple answers to 2-5 sentences. If the user asks for a full list or full text, give all of it completely - never truncate.

ACCURACY RULES:
- Answer by COMBINING both sources. The knowledge base always wins for KCC campus facts; web results only supplement it.
- Think before answering: identify what is asked and support every claim from the sources. If neither source covers part of the question, state that plainly instead of guessing.
- If the answer is not in either source, say that the information is not available and recommend the appropriate KCC office. NEVER invent information.
- {language_rule}

KNOWLEDGE BASE CONTEXT:
{context}

WEB RESEARCH RESULTS:
{web}
"""


def _build_search_query(query):
    """Augment ang search query para mas accurate ang results (KCC -> Kabankalan Catholic College)."""
    q = (query or '').strip()
    if re.search(r'\bkcc\b', q, re.IGNORECASE) and 'kabankalan' not in q.lower():
        q = f'{q} Kabankalan Catholic College'
    return q


def _parse_ddg_html(html):
    links = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.S)
    snippets = [re.sub(r'<[^>]+>', '', s).strip()
                for s in re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html, re.S)]
    return links, snippets


def _parse_ddg_lite(html):
    links = re.findall(r"href=\"([^\"]+)\"[^>]*class='result-link'[^>]*>(.*?)</a>", html, re.S)
    snippets = [re.sub(r'<[^>]+>', '', s).strip()
                for s in re.findall(r"class='result-snippet'[^>]*>(.*?)</td>", html, re.S)]
    return links, snippets


def web_search(query, max_results=4):
    """DuckDuckGo search (HTML + Lite fallback) — returns [{title, snippet, url}] ([] kung pumalya)."""
    query = _build_search_query(query)
    for endpoint, parser in (
        ('https://html.duckduckgo.com/html/', _parse_ddg_html),
        ('https://lite.duckduckgo.com/lite/', _parse_ddg_lite),
    ):
        try:
            resp = requests.post(
                endpoint,
                data={'q': query},
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                timeout=WEB_SEARCH_TIMEOUT,
            )
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.info('Web search failed (%s): %s', endpoint, exc)
            continue

        links, snippets = parser(resp.text)
        if not links:
            continue

        from urllib.parse import parse_qs, unquote
        results = []
        for i, (url, title) in enumerate(links[:max_results]):
            if url.startswith('//duckduckgo.com/l/') and 'uddg=' in url:
                try:
                    url = unquote(parse_qs(url.split('?', 1)[1]).get('uddg', [url])[0])
                except (ValueError, IndexError):
                    pass
            title = re.sub(r'<[^>]+>', '', title).strip()
            results.append({
                'title': title or 'Web result',
                'snippet': snippets[i] if i < len(snippets) else '',
                'url': url,
            })
        return results
    return []


def _web_context(results):
    blocks = []
    for r in results:
        block = r['title']
        if r['snippet']:
            block += f"\n{r['snippet']}"
        if r['url']:
            block += f"\n({r['url']})"
        blocks.append(block)
    return '\n\n---\n\n'.join(blocks)


def _save_web_fact(results):
    """I-save ang unang resulta ng web research sa knowledge/ (deduped)."""
    if not results:
        return None
    top = results[0]
    snippet = re.sub(r'\s+', ' ', top.get('snippet') or '').strip()
    if len(snippet) < 20:
        return None
    existing = ' '.join(f'{it.title} {it.content}'.lower() for it in _load_knowledge())
    if snippet.lower() in existing:
        return None
    title = re.sub(r'\s+', ' ', top.get('title') or 'Web Research').strip()[:80]
    content = snippet[:600]
    if top.get('url'):
        content += f"\nSource: {top['url']}"
    try:
        return remember(f'{title}\n{content}', subfolder='')
    except (OSError, ValueError):
        return None


_RESEARCH_HINTS_RE = re.compile(
    r"\b(latest|recent|recently|update[sd]?|bagong|bago|ngayon|today|current|currently|"
    r"this (week|month|year)|announcement|anunsyo|balita|news|event|upcoming|deadline|"
    r"facebook|fb|search|hanapin|online|internet)\b",
    re.IGNORECASE,
)


def needs_research(question, items):
    """Web research kailangan? Hindi na kapag may KB match at walang freshness/event hints."""
    if not items:
        return True
    return bool(_RESEARCH_HINTS_RE.search(question or ''))


def _kb_sources(items):
    return [{'title': it.title, 'url': '', 'type': 'kb'} for it in items]


def _web_sources(web):
    return [{'title': r.get('title') or '', 'url': r.get('url') or '', 'type': 'web'} for r in web]


def answer_question(question, history=None, engine='auto', language='auto', user=None):
    """Full RAG pipeline. Returns {'reply', 'engine', 'sources'}.

    engine   : 'auto' | 'primary' | 'fallback'  (provider preference order)
    language : 'auto' | 'tl' | 'en'             (reply language)
    """
    history = history or []

    # Auto-fix ng maling prompt (typos/grammar) bago sagutin — model mismo ang nag-cocorrect.
    if getattr(settings, 'AI_PROMPT_FIX', True):
        question = correct_prompt(question, engine=engine, user=user) or question

    small = _smalltalk_reply(question, language)
    if small:
        return {'reply': small, 'engine': 'KNIGHT', 'sources': []}

    items = _retrieve(question)
    web = []
    if (getattr(settings, 'AI_WEB_RESEARCH', True) and len(question.strip()) >= 10
            and needs_research(question, items)):
        web = web_search(question)

    if items and web:
        # KB match + may web results — pagsamahin ang dalawa (KB ang official, web ang supplement).
        system_prompt = _KNIGHT_COMBINED_TEMPLATE.format(
            context=_build_context(items),
            web=_web_context(web),
            language_rule=_LANGUAGE_RULES.get(language, _LANGUAGE_RULES['auto']),
        )
        reply, engine_name = chat(system_prompt, history, question, engine=engine, user=user)
        return {'reply': reply, 'engine': engine_name,
                'sources': _web_sources(web)}

    if not items:
        # Walang KB match — sagot mula sa web research kung meron, tapos small talk / scope guidance.
        if web:
            try:
                reply, engine_name = chat(
                    _KNIGHT_WEB_TEMPLATE.format(
                        language_rule=_LANGUAGE_RULES.get(language, _LANGUAGE_RULES['auto']),
                        context=_web_context(web)),
                    history, question, engine=engine, user=user)
                if getattr(settings, 'AI_WEB_SAVE_FACTS', False):
                    _save_web_fact(web)
                return {'reply': reply, 'engine': engine_name, 'sources': _web_sources(web)}
            except (AIConfigError, AIUnavailable):
                pass  # fall through sa smalltalk/canned
        try:
            reply, engine_name = chat(
                _KNIGHT_SMALLTALK_TEMPLATE.format(
                    language_rule=_LANGUAGE_RULES.get(language, _LANGUAGE_RULES['auto'])),
                history, question, engine=engine, user=user)
            return {'reply': reply, 'engine': engine_name, 'sources': []}
        except (AIConfigError, AIUnavailable) as exc:
            logger.info('Small-talk fallback engine unavailable (%s); using canned reply.', exc)
            fallback = FALLBACK_NO_MATCH_EN if language == 'en' else FALLBACK_NO_MATCH
            return {'reply': fallback, 'engine': 'KNIGHT KB', 'sources': []}

    system_prompt = _KNIGHT_SYSTEM_TEMPLATE.format(
        context=_build_context(items),
        language_rule=_LANGUAGE_RULES.get(language, _LANGUAGE_RULES['auto']),
    )
    reply, engine_name = chat(system_prompt, history, question, engine=engine, user=user)
    return {'reply': reply, 'engine': engine_name, 'sources': []}
