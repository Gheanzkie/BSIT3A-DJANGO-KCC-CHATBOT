from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST

User = get_user_model()

INVALID_LOGIN_MESSAGE = 'Invalid email or password.'
LOCKOUT_MESSAGE = 'Too many failed attempts. Please try again in a few minutes.'
REGISTER_LIMIT_MESSAGE = 'Too many registration attempts. Please try again later.'
GENERIC_EXISTS_MESSAGE = 'Registration could not be completed — that username or email is already in use.'


def _landing(request):
    """Superuser -> dashboard; regular users -> dumeretso sa chat."""
    return redirect('dashboard') if request.user.is_superuser else redirect('chat:page')


def _client_ip(request):
    # REMOTE_ADDR only — X-Forwarded-For is client-controlled unless behind a trusted proxy.
    return request.META.get('REMOTE_ADDR', '')


def _validate_registration_data(data):
    errors = {}

    username = data.get('username', '').strip()
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')

    if not username:
        errors['username'] = 'Username is required.'
    elif User.objects.filter(username=username).exists():
        # Generic message — never confirm which field exists (user enumeration).
        errors['general'] = GENERIC_EXISTS_MESSAGE

    if not first_name:
        errors['first_name'] = 'First name is required.'

    if not last_name:
        errors['last_name'] = 'Last name is required.'

    if not email:
        errors['email'] = 'Email is required.'
    else:
        try:
            validate_email(email)
        except ValidationError:
            errors['email'] = 'Enter a valid email address.'
        else:
            if User.objects.filter(email=email).exists():
                errors['general'] = GENERIC_EXISTS_MESSAGE

    if not password:
        errors['password'] = 'Password is required.'
    elif len(password) < 8:
        errors['password'] = 'Password must be at least 8 characters.'
    else:
        try:
            validate_password(password)
        except ValidationError as exc:
            errors['password'] = ' '.join(exc.messages)

    if password != confirm_password:
        errors['confirm_password'] = 'Passwords do not match.'

    return errors


@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated:
        return _landing(request)

    if request.method == 'GET':
        return render(request, 'auth/login.html')

    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '')
    ip = _client_ip(request)

    # Rate limiting: per ip+account (targeted) and per ip (spray). See settings.LOGIN_*.
    account_key = f'kcc:login_fail:{ip}:{email.lower()}'
    ip_key = f'kcc:login_fail_ip:{ip}'
    if (cache.get(account_key, 0) >= settings.LOGIN_MAX_ATTEMPTS or
            cache.get(ip_key, 0) >= settings.LOGIN_MAX_ATTEMPTS_PER_IP):
        messages.error(request, LOCKOUT_MESSAGE)
        return render(request, 'auth/login.html')

    user = authenticate(request, username=email, password=password)

    if user is not None:
        cache.delete(account_key)
        login(request, user)
        return _landing(request)

    cache.set(account_key, cache.get(account_key, 0) + 1, settings.LOGIN_LOCKOUT_SECONDS)
    cache.set(ip_key, cache.get(ip_key, 0) + 1, settings.LOGIN_LOCKOUT_SECONDS)
    messages.error(request, INVALID_LOGIN_MESSAGE)
    return render(request, 'auth/login.html')


@require_POST
def logout_view(request):
    logout(request)
    return redirect('welcome')


def _mask_key(key):
    if not key:
        return ''
    if len(key) <= 8:
        return '•' * len(key)
    return f'{key[:6]}…{key[-4:]}'


@login_required(login_url='login')
def home(request):
    # Regular users: dumeretso sa chat — para sa admin lang ang dashboard.
    if not request.user.is_superuser:
        return redirect('chat:page')

    from apps.chat.services import ai as ai_service
    from apps.users.models import User
    from django.utils import timezone

    total_users = User.objects.filter(is_superuser=False).count()
    today = timezone.now().date()
    active_today = User.objects.filter(
        last_login__date=today
    ).count()

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
        'total_users': total_users,
        'total_conversations': '—',
        'total_messages': '—',
        'active_today': active_today,
        'models_info': models_info,
    }
    return render(request, 'home.html', context)


@require_http_methods(['GET', 'POST'])
def register_view(request):
    if request.user.is_authenticated:
        return _landing(request)

    if request.method == 'GET':
        return render(request, 'auth/register.html')

    # Rate limiting: cap registration POSTs per IP to slow enumeration attempts.
    ip = _client_ip(request)
    reg_key = f'kcc:register_try:{ip}'
    if cache.get(reg_key, 0) >= settings.REGISTER_MAX_ATTEMPTS:
        return render(request, 'auth/register.html', {'errors': {'general': REGISTER_LIMIT_MESSAGE}})
    cache.set(reg_key, cache.get(reg_key, 0) + 1, settings.REGISTER_WINDOW_SECONDS)

    form_data = {
        'username': request.POST.get('username', ''),
        'first_name': request.POST.get('first_name', ''),
        'last_name': request.POST.get('last_name', ''),
        'email': request.POST.get('email', ''),
        'password': request.POST.get('password', ''),
        'confirm_password': request.POST.get('confirm_password', ''),
    }

    errors = _validate_registration_data(form_data)
    if errors:
        return render(request, 'auth/register.html', {'errors': errors, 'form_data': form_data})

    user = User.objects.create_user(
        username=form_data['username'].strip(),
        first_name=form_data['first_name'].strip(),
        last_name=form_data['last_name'].strip(),
        email=form_data['email'].strip(),
        password=form_data['password'],
    )
    login(request, user)
    return _landing(request)


def welcome_view(request):
    if request.user.is_authenticated:
        return _landing(request)
    return render(request, 'welcome.html')
