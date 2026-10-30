from django.conf import settings
from django.db import models

from .tokens import generate_chat_token


class Conversation(models.Model):
    """One ongoing chat thread per user (latest conversation is shown on /chat/)."""

    # Isang KNIGHT lang ang nakikita ng user. Dalawang provider ang gumagana sa
    # likod (Groq muna, Gemini ang safety net) at awtomatiko ang paglipat kapag
    # may down o rate-limited, kaya wala nang model picker sa chat.
    ENGINE_CHOICES = [
        ('auto', 'KNIGHT'),
    ]
    # Legacy values: old conversations may still store 'primary' / 'fallback'.
    # They keep working (see services/ai.py _ENGINE_ORDER) so no saved chat breaks.
    ENGINE_VALUES = ('auto', 'primary', 'fallback')
    LANGUAGE_CHOICES = [
        ('auto', 'Auto'),
        ('tl', 'Tagalog'),
        ('en', 'English'),
    ]

    # Public chat: anonymous visitors own conversations through their session key.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_conversations',
        null=True,
        blank=True,
    )
    session_key = models.CharField(max_length=64, blank=True, default='', db_index=True)
    # Public URL handle — random, unique, never the sequential DB id.
    token = models.CharField(
        max_length=64, unique=True, editable=False, default=generate_chat_token
    )
    title = models.CharField(max_length=200, blank=True)
    # Set when a public visitor's tab/browser is closed; purge removes the chat
    # once the grace period passes. Cleared automatically if they come back.
    closing_at = models.DateTimeField(null=True, blank=True, db_index=True)
    engine_preference = models.CharField(max_length=12, choices=ENGINE_CHOICES, default='auto')
    language = models.CharField(max_length=12, choices=LANGUAGE_CHOICES, default='auto')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def save(self, *args, **kwargs):
        # Guarantee a token even for rows created without the field set.
        if not self.token:
            self.token = generate_chat_token()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user} — {self.title or "(untitled)"}'


class Message(models.Model):
    ROLE_USER = 'user'
    ROLE_ASSISTANT = 'assistant'
    ROLE_CHOICES = [(ROLE_USER, 'User'), (ROLE_ASSISTANT, 'Assistant')]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    engine = models.CharField(max_length=64, blank=True)  # e.g. 'KNIGHT v1.0'
    # Citations captured at reply time ({'title','url','type'} dicts). Stored so a
    # report can copy "saan nakuha ang info" even after the answer is old.
    sources = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'[{self.role}] {self.content[:50]}'


class MessageReport(models.Model):
    """A registered user flagging one KNIGHT reply (wrong / incomplete / etc.).

    Snapshots the answer text, the question and the citation list so the admin
    still sees exactly what the user saw, even if the conversation is purged.
    """

    REASON_WRONG = 'wrong'
    REASON_INCOMPLETE = 'incomplete'
    REASON_OUTDATED = 'outdated'
    REASON_INAPPROPRIATE = 'inappropriate'
    REASON_OTHER = 'other'
    REASON_CHOICES = [
        (REASON_WRONG, 'Maling sagot / Wrong answer'),
        (REASON_INCOMPLETE, 'Kulang ang sagot / Incomplete'),
        (REASON_OUTDATED, 'Luma na ang info / Outdated'),
        (REASON_INAPPROPRIATE, 'Hindi angkop / Inappropriate'),
        (REASON_OTHER, 'Iba pa / Other'),
    ]

    STATUS_OPEN = 'open'
    STATUS_RESOLVED = 'resolved'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_RESOLVED, 'Resolved'),
    ]

    message = models.ForeignKey(
        Message, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports'
    )
    conversation = models.ForeignKey(
        Conversation, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='message_reports'
    )
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, default=REASON_OTHER)
    details = models.TextField(blank=True, default='')

    # Snapshot of what the user was looking at.
    question_text = models.TextField(blank=True, default='')
    answer_text = models.TextField(blank=True, default='')
    sources = models.JSONField(default=list, blank=True)
    engine = models.CharField(max_length=64, blank=True, default='')

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_OPEN)
    admin_reply = models.TextField(blank=True, default='')
    replied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='answered_message_reports',
    )
    replied_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['status', '-created_at'])]

    def __str__(self):
        return f'Report #{self.pk} [{self.reason}] {self.status}'


class Notification(models.Model):
    """In-app notice for a registered user (currently: admin answered a report)."""

    KIND_REPORT_REPLY = 'report_reply'
    KIND_CHOICES = [(KIND_REPORT_REPLY, 'Admin reply to report')]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    report = models.ForeignKey(
        MessageReport, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='notifications',
    )
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default=KIND_REPORT_REPLY)
    title = models.CharField(max_length=160)
    body = models.TextField(blank=True, default='')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', 'is_read', '-created_at'])]

    def __str__(self):
        return f'Notification #{self.pk} -> {self.user_id}: {self.title[:40]}'
