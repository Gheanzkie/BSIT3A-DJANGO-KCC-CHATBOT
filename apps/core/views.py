from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from .activity import log_activity
from .models import ActivityLog, Announcement, AnnouncementImage, Ticket

User = get_user_model()

INVALID_LOGIN_MESSAGE = 'Invalid email or password.'
LOCKOUT_MESSAGE = 'Too many failed attempts. Please try again in a few minutes.'
REPORT_LIMIT_MESSAGE = 'Too many reports submitted. Please try again later.'
GENERIC_EXISTS_MESSAGE = 'That username or email is already in use.'


def _client_ip(request):
    # REMOTE_ADDR only — X-Forwarded-For is client-controlled unless behind a trusted proxy.
    return request.META.get('REMOTE_ADDR', '')


def _is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def _is_superuser(user):
    return user.is_authenticated and user.is_superuser


def _drop_anonymous_conversations(request, anon_key):
    """Public chats stay ephemeral: they are NOT merged into the account on login.

    Registered users only see conversations saved while signed in.
    """
    if anon_key:
        from apps.chat.models import Conversation
        Conversation.objects.filter(user__isnull=True, session_key=anon_key).delete()


@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard') if request.user.is_superuser else redirect('chat:page')

    if request.method == 'GET':
        return render(request, 'auth/login.html')

    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '')
    ip = _client_ip(request)
    ajax = _is_ajax(request)

    # Rate limiting: per ip+account (targeted) and per ip (spray). See settings.LOGIN_*.
    account_key = f'kcc:login_fail:{ip}:{email.lower()}'
    ip_key = f'kcc:login_fail_ip:{ip}'
    if (cache.get(account_key, 0) >= settings.LOGIN_MAX_ATTEMPTS or
            cache.get(ip_key, 0) >= settings.LOGIN_MAX_ATTEMPTS_PER_IP):
        if ajax:
            return JsonResponse({'ok': False, 'error': LOCKOUT_MESSAGE}, status=429)
        messages.error(request, LOCKOUT_MESSAGE)
        return render(request, 'auth/login.html')

    user = authenticate(request, username=email, password=password)

    if user is not None:
        cache.delete(account_key)
        anon_key = request.session.session_key
        login(request, user)
        _drop_anonymous_conversations(request, anon_key)
        log_activity(request, 'login', user=user)
        if ajax:
            return JsonResponse({'ok': True, 'redirect': '/home/' if user.is_superuser else '/chat/'})
        return redirect('dashboard') if user.is_superuser else redirect('chat:page')

    cache.set(account_key, cache.get(account_key, 0) + 1, settings.LOGIN_LOCKOUT_SECONDS)
    cache.set(ip_key, cache.get(ip_key, 0) + 1, settings.LOGIN_LOCKOUT_SECONDS)
    if ajax:
        return JsonResponse({'ok': False, 'error': INVALID_LOGIN_MESSAGE}, status=400)
    messages.error(request, INVALID_LOGIN_MESSAGE)
    return render(request, 'auth/login.html')


@require_http_methods(['GET', 'POST'])
def register_view(request):
    """Create an account from the floating register modal; auto-login on success."""
    if request.user.is_authenticated:
        return redirect('chat:page')

    if request.method == 'GET':
        return redirect('login')

    ajax = _is_ajax(request)
    ip = _client_ip(request)
    reg_key = f'kcc:register_try:{ip}'
    if cache.get(reg_key, 0) >= settings.REGISTER_MAX_ATTEMPTS:
        message = 'Too many registration attempts. Please try again later.'
        if ajax:
            return JsonResponse({'ok': False, 'error': message}, status=429)
        messages.error(request, message)
        return redirect('login')
    cache.set(reg_key, cache.get(reg_key, 0) + 1, settings.REGISTER_WINDOW_SECONDS)

    username = request.POST.get('username', '').strip()
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '')
    confirm = request.POST.get('confirm_password', '')

    error = None
    if not username:
        error = 'Username is required.'
    elif not email:
        error = 'Email is required.'
    elif not password or len(password) < 8:
        error = 'Password must be at least 8 characters.'
    elif password != confirm:
        error = 'Passwords do not match.'
    else:
        try:
            validate_email(email)
            validate_password(password)
        except ValidationError as exc:
            error = ' '.join(exc.messages)
        if error is None and (User.objects.filter(username=username).exists()
                              or User.objects.filter(email=email).exists()):
            error = GENERIC_EXISTS_MESSAGE

    if error is not None:
        if ajax:
            return JsonResponse({'ok': False, 'error': error}, status=400)
        messages.error(request, error)
        return redirect('login')

    user = User.objects.create_user(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
    )
    anon_key = request.session.session_key
    login(request, user)
    _drop_anonymous_conversations(request, anon_key)
    log_activity(request, 'register', user=user)

    if ajax:
        return JsonResponse({'ok': True, 'redirect': '/chat/'})
    return redirect('chat:page')


@require_POST
def logout_view(request):
    logout(request)
    return redirect('chat:page')


def _mask_key(key):
    if not key:
        return ''
    if len(key) <= 8:
        return '•' * len(key)
    return f'{key[:6]}…{key[-4:]}'


@user_passes_test(_is_superuser, login_url='login')
def home(request):
    from apps.chat.models import Conversation, Message
    from apps.chat.services import ai as ai_service

    usage = ai_service.get_usage()
    models_info = [
        {
            'slot': f'Primary — {settings.AI_PRIMARY_NAME}',
            'provider': 'Groq',
            'model': settings.AI_CHAT_MODEL_GROQ,
            'endpoint': settings.AI_PRIMARY_BASE_URL,
            'key_masked': _mask_key(settings.GROQ_API_KEY),
            'key_set': bool(settings.GROQ_API_KEY),
            'usage': usage.get('groq', {}),
        },
        {
            'slot': f'Fallback — {settings.AI_FALLBACK_NAME}',
            'provider': 'Gemini',
            'model': settings.AI_CHAT_MODEL_GEMINI,
            'endpoint': settings.AI_FALLBACK_BASE_URL,
            'key_masked': _mask_key(settings.GEMINI_API_KEY),
            'key_set': bool(settings.GEMINI_API_KEY),
            'usage': usage.get('gemini', {}),
        },
        {
            'slot': 'Embeddings',
            'provider': 'Gemini',
            'model': settings.AI_EMBED_MODEL,
            'endpoint': 'generativelanguage.googleapis.com',
            'key_masked': _mask_key(settings.GEMINI_API_KEY),
            'key_set': bool(settings.GEMINI_API_KEY),
            'usage': usage.get('embeddings', {}),
        },
    ]

    context = {
        'total_conversations': Conversation.objects.count(),
        'total_messages': Message.objects.count(),
        'open_tickets': Ticket.objects.filter(status=Ticket.STATUS_OPEN).count(),
        'models_info': models_info,
    }
    return render(request, 'home.html', context)


def welcome_view(request):
    """Public visitors land straight in the chat, ChatGPT-style."""
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('dashboard')
    return redirect('chat:page')


# ---------- HELP ----------

def help_view(request):
    return render(request, 'help.html')


# ---------- REPORT / TICKET ----------

@require_http_methods(['GET', 'POST'])
def report_view(request):
    if request.method == 'GET':
        return redirect('chat:page')

    ip = _client_ip(request)
    ajax = _is_ajax(request)
    rate_key = f'kcc:report_try:{ip}'
    if cache.get(rate_key, 0) >= 5:
        if ajax:
            return JsonResponse({'ok': False, 'error': REPORT_LIMIT_MESSAGE}, status=429)
        messages.error(request, REPORT_LIMIT_MESSAGE)
        return redirect('chat:page')
    cache.set(rate_key, cache.get(rate_key, 0) + 1, 3600)

    category = request.POST.get('category', 'other')
    if category not in dict(Ticket.CATEGORY_CHOICES):
        category = 'other'
    text = request.POST.get('message', '').strip()

    if len(text) < 5:
        if ajax:
            return JsonResponse({'ok': False, 'error': 'Please describe the problem (at least 5 characters).'}, status=400)
        messages.error(request, 'Please describe the problem (at least 5 characters).')
        return redirect('chat:page')

    ticket = Ticket.objects.create(
        user=request.user if request.user.is_authenticated else None,
        session_key=(request.session.session_key or '') if not request.user.is_authenticated else '',
        category=category,
        message=text,
    )
    if ajax:
        return JsonResponse({'ok': True, 'ticket': ticket.pk, 'message': f'Thanks! Ticket #{ticket.pk} was sent to the admin.'})
    messages.success(request, f'Thanks! Ticket #{ticket.pk} was sent to the admin.')
    return redirect('chat:page')


# ---------- ADMIN ANNOUNCEMENTS ----------

@require_http_methods(['GET', 'POST'])
def announcement_list(request):
    if request.method == 'POST':
        if not _is_superuser(request.user):
            return redirect('login')
        title = request.POST.get('title', '').strip()[:140]
        message = request.POST.get('message', '').strip()
        images = request.FILES.getlist('images')
        if not message:
            messages.error(request, 'Announcement text is required.')
        else:
            item = Announcement.objects.create(
                title=title, message=message, created_by=request.user
            )
            for image in images:
                AnnouncementImage.objects.create(announcement=item, image=image)
            from apps.chat.services import ai as chat_ai
            chat_ai.sync_announcement_knowledge(
                item.pk, item.title, item.message, item.created_at, item.is_active
            )
            messages.success(request, 'Announcement published in the sidebar.')
        return redirect('announcements')

    if _is_superuser(request.user):
        return render(request, 'announcements/list.html', {
            'announcements': Announcement.objects.all()[:100],
        })
    # Public/registered history view — active announcements only.
    return render(request, 'announcements/history.html', {
        'announcements': Announcement.objects.filter(is_active=True).order_by('-created_at')[:100],
    })


@user_passes_test(_is_superuser, login_url='login')
@require_http_methods(['GET', 'POST'])
def announcement_edit(request, pk):
    item = get_object_or_404(Announcement, pk=pk)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()[:140]
        message = request.POST.get('message', '').strip()
        if not message:
            messages.error(request, 'Announcement text is required.')
            return render(request, 'announcements/edit.html', {'item': item})

        item.title = title
        item.message = message
        item.is_active = request.POST.get('is_active') == 'on'
        item.save()

        remove_ids = request.POST.getlist('remove_images')
        if remove_ids:
            for picture in item.images.filter(pk__in=remove_ids):
                picture.image.delete(save=False)
                picture.delete()

        for image in request.FILES.getlist('images'):
            AnnouncementImage.objects.create(announcement=item, image=image)

        from apps.chat.services import ai as chat_ai
        chat_ai.sync_announcement_knowledge(
            item.pk, item.title, item.message, item.created_at, item.is_active
        )

        messages.success(request, 'Announcement updated.')
        return redirect('announcements')

    return render(request, 'announcements/edit.html', {'item': item})


@require_POST
@user_passes_test(_is_superuser, login_url='login')
def announcement_update(request, pk):
    item = get_object_or_404(Announcement, pk=pk)
    action = request.POST.get('action')

    from apps.chat.services import ai as chat_ai

    if action == 'toggle':
        item.is_active = not item.is_active
        item.save(update_fields=['is_active', 'updated_at'])
        chat_ai.sync_announcement_knowledge(
            item.pk, item.title, item.message, item.created_at, item.is_active
        )
        messages.success(request, 'Announcement published.' if item.is_active else 'Announcement unpublished.')
    elif action == 'delete':
        for picture in item.images.all():
            picture.image.delete(save=False)
        pk = item.pk
        item.delete()
        chat_ai.remove_announcement_knowledge(pk)
        messages.success(request, 'Announcement deleted.')

    return redirect('announcements')


# ---------- ADMIN ACTIVITY LOG ----------

@user_passes_test(_is_superuser, login_url='login')
def activity_list(request):
    query = request.GET.get('q', '').strip()
    logs = ActivityLog.objects.select_related('user').order_by('-created_at')
    if query:
        logs = logs.filter(
            Q(action__icontains=query) | Q(path__icontains=query)
            | Q(user__username__icontains=query) | Q(user__email__icontains=query)
            | Q(ip__icontains=query)
        )
    total = logs.count()
    return render(request, 'activity/list.html', {
        'logs': logs[:500],
        'query': query,
        'total_count': total,
    })


# ---------- ADMIN TICKET MODULE ----------

@user_passes_test(_is_superuser, login_url='login')
def ticket_list(request):
    active_status = request.GET.get('status', '')
    tickets = Ticket.objects.select_related('user').order_by('status', '-created_at')
    if active_status in dict(Ticket.STATUS_CHOICES):
        tickets = tickets.filter(status=active_status)
    else:
        active_status = ''

    counts = {
        Ticket.STATUS_OPEN: Ticket.objects.filter(status=Ticket.STATUS_OPEN).count(),
        Ticket.STATUS_RESOLVED: Ticket.objects.filter(status=Ticket.STATUS_RESOLVED).count(),
    }
    total = counts[Ticket.STATUS_OPEN] + counts[Ticket.STATUS_RESOLVED]

    return render(request, 'reports/list.html', {
        'tickets': tickets[:500],
        'counts': counts,
        'total_count': total,
        'active_status': active_status,
    })


@require_POST
@user_passes_test(_is_superuser, login_url='login')
def ticket_update(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    action = request.POST.get('action')

    # Done tickets are archived for the admin: no further actions, no deletion.
    if ticket.status == Ticket.STATUS_RESOLVED:
        messages.info(request, f'Ticket #{ticket.pk} is done and kept for admin.')
        return redirect('tickets')

    if action == 'resolve':
        ticket.status = Ticket.STATUS_RESOLVED
        ticket.resolved_at = timezone.now()
        ticket.save(update_fields=['status', 'resolved_at'])
        messages.success(request, f'Ticket #{ticket.pk} marked as resolved.')
    elif action == 'reopen':
        ticket.status = Ticket.STATUS_OPEN
        ticket.resolved_at = None
        ticket.save(update_fields=['status', 'resolved_at'])
        messages.success(request, f'Ticket #{ticket.pk} reopened.')
    elif action == 'delete':
        pk_value = ticket.pk
        ticket.delete()
        messages.success(request, f'Ticket #{pk_value} deleted.')

    return redirect('tickets')
