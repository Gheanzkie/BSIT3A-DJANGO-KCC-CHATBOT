"""Ephemeral lifecycle for public (anonymous) chats.

When a visitor closes the tab/browser the page fires a small beacon. The
visitor's anonymous conversations are marked with ``closing_at``; any later
request from the same browser session clears the mark (the visitor came back).
A purge — piggy-backed on normal requests and debounced — removes the chats and
the stale Django session row once the grace period has passed.

``ActivityLog`` rows are NEVER touched: audit history keeps working after the
chat data is gone.
"""

import logging
from datetime import timedelta

from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone

from .models import Conversation

logger = logging.getLogger(__name__)

PURGE_LOCK_KEY = 'kcc:chat:purge_lock'
CLOSING_SESSION_KEY = 'kcc_chat_closing'


def _grace_seconds():
    from django.conf import settings
    return int(getattr(settings, 'ANON_CHAT_CLOSE_GRACE_SECONDS', 20))


def _purge_interval():
    from django.conf import settings
    return int(getattr(settings, 'ANON_CHAT_PURGE_INTERVAL_SECONDS', 60))


def mark_closing(request, session_key, token=None):
    """Flag this tab's public chat as closed (tab/browser gone).

    With a per-tab ``token`` only that conversation is flagged, so closing one
    tab never deletes the chat another tab is still using.
    """
    if not session_key:
        return 0
    request.session[CLOSING_SESSION_KEY] = True
    request.session.modified = True
    pending = Conversation.objects.filter(
        user__isnull=True, session_key=session_key, closing_at__isnull=True
    )
    if token:
        pending = pending.filter(token=token)
    return pending.update(closing_at=timezone.now())


def clear_closing(request, session_key):
    """Visitor came back — cancel the pending deletion for this session."""
    if not session_key:
        return 0
    if request.session.get(CLOSING_SESSION_KEY):
        request.session.pop(CLOSING_SESSION_KEY, None)
        request.session.modified = True
    return Conversation.objects.filter(
        user__isnull=True, session_key=session_key, closing_at__isnull=False
    ).update(closing_at=None)


def purge_expired_anonymous(force=False):
    """Delete closed public chats + dead session rows. Returns rows removed.

    Debounced through the cache so normal traffic triggers it at most once per
    ``ANON_CHAT_PURGE_INTERVAL_SECONDS``. Registered users' chats are untouched,
    and ActivityLog rows are never referenced here.
    """
    if not force and not cache.add(PURGE_LOCK_KEY, 1, _purge_interval()):
        return 0

    now = timezone.now()
    removed = 0
    try:
        Session.objects.filter(expire_date__lt=now).delete()

        closed = Conversation.objects.filter(
            user__isnull=True,
            closing_at__isnull=False,
            closing_at__lt=now - timedelta(seconds=_grace_seconds()),
        )
        closed_keys = list(
            closed.exclude(session_key='').values_list('session_key', flat=True).distinct()
        )
        removed, _ = closed.delete()
        if closed_keys:
            Session.objects.filter(session_key__in=closed_keys).delete()

        # Legacy leftovers: no live session, blank key, or older than 24h.
        live_keys = Session.objects.values_list('session_key', flat=True)
        legacy, _ = Conversation.objects.filter(user__isnull=True).filter(
            Q(session_key='')
            | ~Q(session_key__in=live_keys)
            | Q(updated_at__lt=now - timedelta(hours=24))
        ).delete()
        removed += legacy
    except Exception:
        logger.exception('Anonymous chat purge failed')
    return removed
