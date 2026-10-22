from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.users.models import User


@login_required(login_url='login')
@require_POST
def profile_update(request):
    user = request.user
    username = request.POST.get('username', '').strip()
    email = request.POST.get('email', '').strip()
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()

    error = None
    if not username:
        error = 'Username is required.'
    elif not email:
        error = 'Email is required.'
    elif User.objects.filter(username=username).exclude(pk=user.pk).exists():
        error = 'That username is already taken.'
    elif User.objects.filter(email=email).exclude(pk=user.pk).exists():
        error = 'That email is already in use.'

    if error:
        return JsonResponse({'ok': False, 'error': error}, status=400)

    user.username = username
    user.email = email
    user.first_name = first_name
    user.last_name = last_name
    user.save(update_fields=['username', 'email', 'first_name', 'last_name'])

    return JsonResponse({
        'ok': True,
        'message': 'Profile updated.',
        'user': {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        },
    })


@login_required(login_url='login')
@require_POST
def password_change(request):
    current = request.POST.get('current_password', '')
    new = request.POST.get('new_password', '')
    confirm = request.POST.get('confirm_password', '')

    if not request.user.check_password(current):
        error = 'Current password is incorrect.'
    elif len(new) < 8:
        error = 'New password must be at least 8 characters.'
    elif new != confirm:
        error = 'New passwords do not match.'
    else:
        error = None
        request.user.set_password(new)
        request.user.save(update_fields=['password'])
        update_session_auth_hash(request, request.user)

    if error:
        return JsonResponse({'ok': False, 'error': error}, status=400)
    return JsonResponse({'ok': True, 'message': 'Password changed.'})
