def announcement(request):
    """Active announcements: sidebar card + read-only list for every visitor."""
    from .models import Announcement
    try:
        items = list(Announcement.objects.filter(is_active=True).order_by('-created_at')[:10])
    except Exception:
        return {}
    return {
        'sidebar_announcement': items[0] if items else None,
        'sidebar_announcements': items,
    }


def tickets(request):
    """Open ticket badge for the admin sidebar only."""
    user = getattr(request, 'user', None)
    if user is not None and user.is_authenticated and user.is_superuser:
        from .models import Ticket
        return {'open_tickets_count': Ticket.objects.filter(status=Ticket.STATUS_OPEN).count()}
    return {}
