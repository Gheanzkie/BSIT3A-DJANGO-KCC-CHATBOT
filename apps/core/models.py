from django.conf import settings
from django.db import models


class Ticket(models.Model):
    """Report/ticket sent by a visitor or a logged-in user to the admin."""

    STATUS_OPEN = 'open'
    STATUS_RESOLVED = 'resolved'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_RESOLVED, 'Resolved'),
    ]
    CATEGORY_CHOICES = [
        ('bug', 'Bug / Error'),
        ('content', 'Wrong answer / content'),
        ('account', 'Account / login'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets',
    )
    session_key = models.CharField(max_length=64, blank=True, default='')
    name = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'#{self.pk} [{self.category}] {self.status}'

class ActivityLog(models.Model):
    """""Every request that reaches the app: page opens, module opens, auth events."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_logs',
    )
    session_key = models.CharField(max_length=64, blank=True, default='')
    action = models.CharField(max_length=120, blank=True, default='')
    method = models.CharField(max_length=10, blank=True, default='')
    path = models.CharField(max_length=255, blank=True, default='')
    status_code = models.PositiveSmallIntegerField(null=True, blank=True)
    ip = models.CharField(max_length=45, blank=True, default='')
    user_agent = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.created_at:%Y-%m-%d %H:%M} {self.method} {self.path}'

class Announcement(models.Model):
    """""Admin announcements shown in the sidebar for every visitor."""

    title = models.CharField(max_length=140, blank=True, default='')
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='announcements',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title or self.message[:40]

class AnnouncementImage(models.Model):
    """""One of the pictures attached to an announcement."""

    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name='images',
    )
    image = models.ImageField(upload_to='announcements/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.image.name
