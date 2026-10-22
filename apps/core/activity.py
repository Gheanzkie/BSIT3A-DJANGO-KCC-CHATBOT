"""Explicit activity logging — only login, register, and chat messages."""

from .models import ActivityLog


def log_activity(request, action, user=None):
    """Record an event. Admin (superuser) activity is never logged."""
    try:
        actor = user if user is not None else getattr(request, 'user', None)
        if actor is not None and not actor.is_authenticated:
            actor = None
        if actor is not None and actor.is_superuser:
            return None
        return ActivityLog.objects.create(
            user=actor,
            session_key=(request.session.session_key or '') if hasattr(request, 'session') else '',
            action=action[:120],
            method=request.method[:10],
            path=request.path[:255],
            status_code=200,
            ip=(request.META.get('REMOTE_ADDR', '') or '')[:45],
            user_agent=(request.META.get('HTTP_USER_AGENT', '') or '')[:255],
        )
    except Exception:
        return None
