from django.conf import settings
from django.db import models

from .tokens import generate_chat_token


class Conversation(models.Model):
    """One ongoing chat thread per user (latest conversation is shown on /chat/)."""

    ENGINE_CHOICES = [
        ('primary', 'KNIGHT v1.0'),
        ('fallback', 'KNIGHT v1.2'),
    ]
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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'[{self.role}] {self.content[:50]}'
