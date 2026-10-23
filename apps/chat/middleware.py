"""Chat session lifecycle.

Runs on every request:
* if a public visitor returned after a "closing" beacon, cancel the deletion;
* debounced purge of closed/expired anonymous chats + dead session rows.

Registered users are ignored, and ActivityLog rows are never deleted here.
"""

import logging

from . import presence

logger = logging.getLogger(__name__)


class ChatSessionLifecycleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            session = getattr(request, 'session', None)
            key = session.session_key if session is not None else None
            if key and not getattr(request.user, 'is_authenticated', False):
                presence.clear_closing(request, key)
            presence.purge_expired_anonymous()
        except Exception:
            logger.exception('Chat session lifecycle failed')
        return self.get_response(request)
