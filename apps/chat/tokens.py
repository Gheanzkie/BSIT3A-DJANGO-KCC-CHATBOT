"""Public chat URL tokens.

Kept in a standalone module so the model and its migrations share the exact
same callable (Django serialises defaults by dotted path).
"""

import secrets


def generate_chat_token():
    """Opaque, unguessable handle used in chat URLs (never the DB pk).

    32 random bytes -> 43 URL-safe chars. Public visitors get a fresh token per
    conversation, and the token is additionally bound to their browser session,
    so copying the URL to another device cannot open someone else's chat.
    """
    return secrets.token_urlsafe(32)
