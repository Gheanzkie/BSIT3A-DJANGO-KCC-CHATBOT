import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Conversation, Message
from .services import ai

logger = logging.getLogger(__name__)

MSG_NOT_CONFIGURED = (
    'The KNIGHT AI engines are not configured yet. Please ask the administrator '
    'to add GROQ_API_KEY and GEMINI_API_KEY to .env and restart the server.'
)
MSG_UNAVAILABLE = (
    'Sorry — the KNIGHT engines cannot be reached right now (network or rate limit). '
    'Please try again in a few seconds.'
)
MSG_ERROR = 'There was an error with the KNIGHT engine. Please try again.'

# Chat-based teaching — admin/staff accounts can add knowledge by typing a prefix.
TEACH_PREFIXES = ('tandaan:', 'remember:', 'idagdag:', 'add info:')


def _ensure_session_key(request):
    """Anonymous visitors get a server-side session that owns their conversations."""
    if request.session.session_key is None:
        request.session.create()
    return request.session.session_key


def _purge_anonymous_sessions():
    """Delete public chats whose browser session is gone/expired.

    Anonymous chats are per browser session: expired session rows are removed,
    conversations no longer backed by a live session are deleted, and anything
    older than 24h is dropped so public data never accumulates.
    """
    try:
        now = timezone.now()
        Session.objects.filter(expire_date__lt=now).delete()
        live_keys = Session.objects.values_list('session_key', flat=True)
        Conversation.objects.filter(user__isnull=True).filter(
            Q(session_key='')
            | ~Q(session_key__in=live_keys)
            | Q(updated_at__lt=now - timedelta(hours=24))
        ).delete()
    except Exception:
        logger.exception('Anonymous session cleanup failed')


def _sessions(request):
    if request.user.is_authenticated:
        return Conversation.objects.filter(user=request.user).order_by('-updated_at')
    return Conversation.objects.filter(
        user__isnull=True,
        session_key=_ensure_session_key(request),
    ).order_by('-updated_at')


def _new_conversation(request):
    if request.user.is_authenticated:
        return Conversation.objects.create(user=request.user)
    return Conversation.objects.create(user=None, session_key=_ensure_session_key(request))


def _resolve_conversation(request, conv_id, new_chat=False):
    """Conversation para sa send: bagong chat mula welcome (new_chat), pinili (kung
    sarili), kundi latest, kundi bago."""
    if new_chat:
        return _new_conversation(request)
    conversation = None
    if conv_id and conv_id.isdigit():
        conversation = _sessions(request).filter(pk=int(conv_id)).first()
    if conversation is None:
        conversation = _sessions(request).first()
    if conversation is None:
        conversation = _new_conversation(request)
    return conversation


def _rate_key(request):
    if request.user.is_authenticated:
        return f'kcc:chat_min:user:{request.user.pk}'
    return f'kcc:chat_min:anon:{_ensure_session_key(request)}'


def chat_page(request, pk=None):
    _purge_anonymous_sessions()
    sessions = _sessions(request)
    if pk is not None:
        conversation = get_object_or_404(sessions, pk=pk)
    else:
        # Welcome state muna — walang auto-load ng latest conversation.
        conversation = None
    context = {
        'sessions': sessions,
        'current_conversation_id': conversation.pk if conversation else None,
        'chat_messages': conversation.messages.all() if conversation else [],
        'primary_name': settings.AI_PRIMARY_NAME,
        'fallback_name': settings.AI_FALLBACK_NAME,
        'ai_configured': bool(settings.GROQ_API_KEY or settings.GEMINI_API_KEY),
        'engine_choices': Conversation.ENGINE_CHOICES,
        'language_choices': Conversation.LANGUAGE_CHOICES,
        'engine_preference': conversation.engine_preference if conversation else 'primary',
        'language_preference': conversation.language if conversation else 'auto',
    }
    return render(request, 'chat/chat.html', context)


@require_POST
def chat_new(request):
    """Bagong chat = welcome screen. Ang conversation ay gagawin lang sa unang mensahe."""
    return redirect('chat:page')


@require_POST
def chat_delete(request, pk):
    conversation = get_object_or_404(_sessions(request), pk=pk)
    conversation.delete()
    return redirect('chat:page')


@require_POST
def chat_send(request):
    text = (request.POST.get('message') or '').strip()
    if not text:
        return JsonResponse({'ok': False, 'error': 'Empty message.'}, status=400)
    if len(text) > 2000:
        return JsonResponse({'ok': False, 'error': 'Message is too long (max 2000 chars).'}, status=400)

    # Throttle: max CHAT_MAX_PER_MINUTE na mensahe kada visitor sa 60-second window.
    limit = getattr(settings, 'CHAT_MAX_PER_MINUTE', 20)
    rate_key = _rate_key(request)
    used = cache.get(rate_key, 0)
    if used >= limit:
        return JsonResponse(
            {'ok': False, 'error': 'Too many messages — please wait a moment and try again.'},
            status=429,
        )
    if used == 0:
        cache.set(rate_key, 1, 60)
    else:
        try:
            cache.incr(rate_key)
        except ValueError:
            cache.set(rate_key, 1, 60)

    conversation = _resolve_conversation(
        request, request.POST.get('conv'),
        new_chat=request.POST.get('newchat') == '1',
    )
    is_first_message = not conversation.messages.exists()

    # Persist the user's model choice (validated against the whitelist).
    engine_pref = request.POST.get('model') or conversation.engine_preference
    if engine_pref not in dict(Conversation.ENGINE_CHOICES):
        engine_pref = 'primary'
    conversation.engine_preference = engine_pref
    # Language: auto-detect mula sa UNANG tanong ng user — Tagalog kung may
    # Tagalog hints, English kung wala. Sinusundan ito sa lahat ng susunod na sagot.
    if is_first_message or conversation.language not in ('tl', 'en'):
        conversation.language = ai._reply_language(text, 'auto')
    lang_pref = conversation.language

    Message.objects.create(conversation=conversation, role=Message.ROLE_USER, content=text)
    if is_first_message and not conversation.title:
        conversation.title = text[:100]

    # Admin/staff-only: magdagdag ng knowledge habang nagcha-chat ("tandaan: ...").
    teach_prefix = next((p for p in TEACH_PREFIXES if text.lower().startswith(p)), None)
    if request.user.is_authenticated and request.user.is_staff and teach_prefix:
        note = text[len(teach_prefix):].strip()
        if note:
            try:
                item = ai.remember(note)
                reply = f'Added to my knowledge base: "{item.title}". Ask me about it anytime!'
            except (OSError, ValueError):
                logger.exception('Knowledge write failed')
                reply = 'I could not save the info right now — please try again.'
        else:
            reply = "Use 'remember: <info>' (or 'tandaan: <info>') followed by the info you want to add."

        assistant_msg = Message.objects.create(
            conversation=conversation,
            role=Message.ROLE_ASSISTANT,
            content=reply,
            engine='KNIGHT KB',
        )
        conversation.save()  # bump updated_at
        return JsonResponse({
            'ok': True,
            'reply': reply,
            'engine': 'KNIGHT KB',
            'sources': [],
            'conversation_id': conversation.pk,
            'created_at': assistant_msg.created_at.strftime('%H:%M'),
        })

    # Auto-learn (staff-only): bagong KCC facts mula sa staff/admin -> save sa knowledge/.
    learned = []
    if (request.user.is_authenticated and request.user.is_staff
            and getattr(settings, 'AI_AUTO_LEARN', True)):
        learned = ai.auto_learn(text, engine=engine_pref)

    # Short conversation context lang — keep prompts small (mabilis + tipid sa free tier)
    prior = list(conversation.messages.order_by('-created_at')[:settings.AI_MAX_HISTORY])
    history = [{'role': m.role, 'content': m.content} for m in reversed(prior[1:])]  # exclude the message just sent

    reply, engine, sources = None, '', []
    try:
        result = ai.answer_question(text, history, engine=engine_pref, language=lang_pref, user=request.user)
        reply, engine = result['reply'], result['engine']
        sources = result.get('sources') or []
    except ai.AIConfigError as exc:
        logger.warning('AI config error: %s', exc)
        reply = MSG_NOT_CONFIGURED
    except ai.AIUnavailable as exc:
        logger.warning('AI unavailable: %s', exc)
        reply = MSG_UNAVAILABLE
    except Exception:
        logger.exception('Unexpected AI failure')
        reply = MSG_ERROR

    if learned:
        reply = f'{reply}\n\n(Noted: {", ".join(learned[:3])}.)'

    assistant_msg = Message.objects.create(
        conversation=conversation,
        role=Message.ROLE_ASSISTANT,
        content=reply,
        engine=engine,
    )
    conversation.save()  # bump updated_at

    from apps.core.activity import log_activity
    log_activity(request, 'chat')

    return JsonResponse({
        'ok': True,
        'reply': reply,
        'engine': engine,
        'sources': sources,
        'conversation_id': conversation.pk,
        'created_at': assistant_msg.created_at.strftime('%H:%M'),
    })
