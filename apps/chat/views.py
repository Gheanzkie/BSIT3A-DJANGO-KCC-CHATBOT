import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from . import presence
from .models import Conversation, Message, MessageReport, Notification
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
    """Delete public chats whose browser session is gone or whose tab was closed.

    Anonymous chats are per browser session: closed tabs are flagged by the
    page beacon and removed after a short grace period, expired session rows are
    removed, and anything older than 24h is dropped so public data never
    accumulates. ActivityLog rows are intentionally left untouched.
    """
    presence.purge_expired_anonymous()


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


def _conversation_for(request, ref):
    """Resolve a conversation by its opaque URL token, scoped to the visitor.

    Anonymous visitors can only reach conversations owned by their browser
    session, so a token copied to another device resolves to nothing. Signed-in
    users are scoped to their own account; legacy numeric ids keep working for
    them so old bookmarks still open.
    """
    if not ref:
        return None
    ref = str(ref).strip()
    if not ref:
        return None
    owned = _sessions(request)
    conversation = owned.filter(token=ref).first()
    if conversation is None and request.user.is_authenticated and ref.isdigit():
        conversation = owned.filter(pk=int(ref)).first()
    return conversation


def _resolve_conversation(request, conv_ref, new_chat=False):
    """Conversation para sa send: bagong chat mula welcome (new_chat), pinili (kung
    sarili), kundi latest, kundi bago."""
    if new_chat:
        return _new_conversation(request)
    conversation = _conversation_for(request, conv_ref)
    if conversation is None:
        conversation = _sessions(request).first()
    if conversation is None:
        conversation = _new_conversation(request)
    return conversation


def _rate_key(request):
    if request.user.is_authenticated:
        return f'kcc:chat_min:user:{request.user.pk}'
    return f'kcc:chat_min:anon:{_ensure_session_key(request)}'


def _selected_token(request):
    """Conversation the visitor has open — kept in the session, never the URL."""
    return request.session.get('kcc_chat_open') or None


def chat_page(request):
    """Render the chat at the site root (/). The URL never carries a session id."""
    _purge_anonymous_sessions()
    sessions = _sessions(request)
    if request.user.is_authenticated:
        token = _selected_token(request)
        conversation = _conversation_for(request, token)
    else:
        # Guests: each tab owns its own chat. The tab token lives in the
        # browser's sessionStorage, never in the server session (which is shared
        # across tabs), so a new tab always starts fresh.
        token = None
        conversation = None
    if token and conversation is None:
        # Deleted/expired/foreign selection: drop it and show a fresh welcome.
        request.session.pop('kcc_chat_open', None)
        request.session.modified = True
    context = {
        'sessions': sessions if request.user.is_authenticated else [],
        'current_conversation_id': conversation.pk if conversation else None,
        'current_conversation_token': conversation.token if conversation else None,
        'chat_messages': conversation.messages.all() if conversation else [],
        'primary_name': settings.AI_PRIMARY_NAME,
        'fallback_name': settings.AI_FALLBACK_NAME,
        'ai_configured': bool(settings.GROQ_API_KEY or settings.GEMINI_API_KEY),
        'engine_choices': Conversation.ENGINE_CHOICES,
        'language_choices': Conversation.LANGUAGE_CHOICES,
            'engine_preference': conversation.engine_preference if conversation else 'auto',
        'language_preference': conversation.language if conversation else 'auto',
    }
    response = render(request, 'chat/chat.html', context)
    # Keep the chat out of caches, indexes and referrer headers.
    response['Cache-Control'] = 'private, no-store, max-age=0'
    response['Referrer-Policy'] = 'same-origin'
    response['X-Robots-Tag'] = 'noindex, nofollow, noarchive'
    return response


def _select_conversation(request, token):
    conversation = _conversation_for(request, token)
    if conversation is None:
        raise Http404('Chat not found')
    request.session['kcc_chat_open'] = conversation.token
    request.session['kcc_chat_started'] = True
    request.session.modified = True
    return conversation


@require_POST
def chat_open(request):
    _select_conversation(request, request.POST.get('token') or '')
    return redirect('chat:page')


def chat_open_link(request, token):
    """Old /chat/<token>/ bookmarks: select the chat, then bounce to the root URL."""
    _select_conversation(request, token)
    request.session['kcc_chat_started'] = True
    request.session.modified = True
    return redirect('chat:page')


@require_POST
def chat_new(request):
    """Bagong chat = welcome screen. Ang conversation ay gagawin lang sa unang mensahe."""
    request.session.pop('kcc_chat_open', None)
    request.session['kcc_chat_started'] = True
    request.session.modified = True
    return redirect('chat:page')


@require_POST
def chat_history(request):
    """Messages for this tab's chat (looked up by the sessionStorage token)."""
    conversation = _conversation_for(request, request.POST.get('token') or '')
    if conversation is None:
        raise Http404('Chat not found')
    return JsonResponse({
        'ok': True,
        'token': conversation.token,
        'title': conversation.title,
        'messages': [
            {'id': m.pk, 'role': m.role, 'content': m.content, 'engine': m.engine}
            for m in conversation.messages.all()
        ],
    })


@require_POST
def chat_delete(request, token):
    conversation = _conversation_for(request, token)
    if conversation is None:
        raise Http404('Chat not found')
    if request.session.get('kcc_chat_open') == conversation.token:
        request.session.pop('kcc_chat_open', None)
        request.session.modified = True
    conversation.delete()
    return redirect('chat:page')


@require_POST
def chat_leave(request):
    """Beacon fired when a public visitor closes the tab/browser.

    The chat is only *marked* for deletion: if the visitor comes back within the
    grace period the mark is cleared. Signed-in users are never affected, and
    ActivityLog entries stay in the database.
    """
    if request.user.is_authenticated:
        return JsonResponse({'ok': True, 'kept': True})
    presence.mark_closing(
        request, request.session.session_key,
        token=(request.POST.get('chat_token') or '').strip() or None,
    )
    return JsonResponse({'ok': True})


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
    # Remember the open chat in the session so a refresh at / keeps it.
    request.session['kcc_chat_open'] = conversation.token
    request.session['kcc_chat_started'] = True
    request.session.modified = True
    is_first_message = not conversation.messages.exists()

    # Persist the user's model choice (validated against the whitelist).
    engine_pref = request.POST.get('model') or conversation.engine_preference
    # 'auto' ang normal na daan ngayon (iisang KNIGHT). Legacy 'primary' /
    # 'fallback' ay tinatanggap pa rin para sa mga lumang conversation row.
    if engine_pref not in Conversation.ENGINE_VALUES:
        engine_pref = 'auto'
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
                saved_name = item.source.split('/')[-1]
                reply = (f'Saved to knowledge: "{item.title}" ({saved_name}). '
                         f'Ask me about it anytime!')
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
            'conversation_token': conversation.token,
            'message_id': assistant_msg.pk,
            'created_at': timezone.localtime(assistant_msg.created_at).strftime('%H:%M'),
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
        sources=sources or [],
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
        'conversation_token': conversation.token,
        'message_id': assistant_msg.pk,
        'created_at': timezone.localtime(assistant_msg.created_at).strftime('%H:%M'),
    })


# ---------- MESSAGE REPORTS (registered users) ----------

@require_POST
@login_required
def chat_report(request):
    """Registered user flags one KNIGHT reply. Snapshot is stored for the admin."""
    raw_id = (request.POST.get('message_id') or '').strip()
    reason = (request.POST.get('reason') or MessageReport.REASON_OTHER).strip()
    details = (request.POST.get('details') or '').strip()[:2000]
    if reason not in dict(MessageReport.REASON_CHOICES):
        reason = MessageReport.REASON_OTHER

    try:
        message_id = int(raw_id)
    except (TypeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Missing reply.'}, status=400)

    # Scoped: the reply must live in a conversation this account owns.
    message = (
        Message.objects.select_related('conversation')
        .filter(pk=message_id, conversation__in=_sessions(request),
                role=Message.ROLE_ASSISTANT)
        .first()
    )
    if message is None:
        return JsonResponse({'ok': False, 'error': 'Reply not found.'}, status=404)

    rate_key = f'kcc:msg_report:{request.user.pk}'
    used = cache.get(rate_key, 0)
    if used >= 10:
        return JsonResponse(
            {'ok': False, 'error': 'Too many reports. Please try again later.'},
            status=429,
        )
    cache.set(rate_key, used + 1, 3600)

    question_text = ''
    previous = (
        message.conversation.messages
        .filter(role=Message.ROLE_USER, created_at__lte=message.created_at)
        .order_by('-created_at')
        .first()
    )
    if previous:
        question_text = previous.content

    report = MessageReport.objects.create(
        message=message,
        conversation=message.conversation,
        user=request.user,
        reason=reason,
        details=details,
        question_text=question_text,
        answer_text=message.content,
        sources=message.sources or [],
        engine=message.engine or '',
    )
    return JsonResponse({
        'ok': True,
        'report_id': report.pk,
        'message': 'Salamat! Naipadala na sa admin ang report mo.',
    })


# ---------- NOTIFICATIONS (registered users) ----------

def _unread_count(user):
    return Notification.objects.filter(user=user, is_read=False).count()


@require_GET
@login_required
def notifications_list(request):
    items = Notification.objects.filter(user=request.user).order_by('-created_at')[:50]
    return JsonResponse({
        'ok': True,
        'unread': _unread_count(request.user),
        'notifications': [
            {
                'id': n.pk,
                'title': n.title,
                'body': n.body,
                'is_read': n.is_read,
                'report_id': n.report_id,
                'created_at': timezone.localtime(n.created_at).strftime('%b %d, %Y %H:%M'),
            }
            for n in items
        ],
    })


@login_required
def notifications_page(request):
    items = (
        Notification.objects.filter(user=request.user)
        .select_related('report')
        .order_by('-created_at')[:100]
    )
    return render(request, 'chat/notifications.html', {
        'notifications': items,
        'unread_count': _unread_count(request.user),
    })


@require_POST
@login_required
def notifications_mark_read(request):
    qs = Notification.objects.filter(user=request.user, is_read=False)
    raw_ids = (request.POST.get('ids') or '').strip()
    if raw_ids:
        ids = [int(x) for x in raw_ids.split(',') if x.strip().isdigit()]
        qs = qs.filter(pk__in=ids)
    updated = qs.update(is_read=True)
    return JsonResponse({'ok': True, 'updated': updated, 'unread': _unread_count(request.user)})
