def announcement(request):
    """Active announcements: sidebar card + read-only list for every visitor."""
    from .models import Announcement
    try:
        items = list(Announcement.objects.filter(is_active=True).order_by('-created_at')[:10])
    except Exception:
        return {}

    data = {
        'sidebar_announcement': items[0] if items else None,
        'sidebar_announcements': items,
    }

    # Admin sidebar badge: every announcement (active + archived), not just
    # the 10 active ones the public card shows.
    user = getattr(request, 'user', None)
    if user is not None and user.is_authenticated and user.is_superuser:
        try:
            data['announcements_count'] = Announcement.objects.count()
        except Exception:
            data['announcements_count'] = len(items)

    return data


def chat_sessions(request):
    """Saved chats for the sidebar on EVERY page (not just /chat/).

    Without this, leaving the chat page (e.g. clicking Announcements) made the
    session list render as "No sessions yet." until the user pressed New chat.
    Anonymous visitors only get a list once their browser session exists, so we
    never create session rows just by browsing.
    """
    from apps.chat.models import Conversation
    items = []
    try:
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated:
            items = list(
                Conversation.objects.filter(user=user).order_by('-updated_at')[:50]
            )
        else:
            # Guests never see a session list: their chat is ephemeral and gets
            # deleted when the tab closes, so nothing is exposed or countable.
            items = []
    except Exception:
        return {}
    return {'sessions': items}


def tickets(request):
    """Open ticket badge for the admin sidebar only."""
    user = getattr(request, 'user', None)
    if user is not None and user.is_authenticated and user.is_superuser:
        from .models import Ticket
        return {'open_tickets_count': Ticket.objects.filter(status=Ticket.STATUS_OPEN).count()}
    return {}
