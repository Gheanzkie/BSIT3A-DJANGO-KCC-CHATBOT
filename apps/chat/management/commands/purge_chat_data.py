from pathlib import Path

from django.conf import settings
from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.chat.models import Conversation, Message, MessageReport
from apps.core.models import ActivityLog


class Command(BaseCommand):
    help = (
        'Purge chat conversation data for a clean panel demo: conversations, '
        'messages, reports, chat activity logs, browser sessions and chat photos. '
        'Keeps user accounts, knowledge base and announcements/photos.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually delete. Without it the command is a dry-run.')
        parser.add_argument('--keep-sessions', action='store_true',
                            help='Do not clear django_session rows (keeps people logged in).')
        parser.add_argument('--keep-photos', action='store_true',
                            help='Do not delete files in media/chat_uploads.')

    def handle(self, *args, **opts):
        reports = MessageReport.objects.count()
        messages = Message.objects.count()
        convos = Conversation.objects.count()
        activity = ActivityLog.objects.filter(action='chat').count()
        sessions = 0 if opts['keep_sessions'] else Session.objects.count()

        chat_dir = Path(settings.MEDIA_ROOT) / 'chat_uploads'
        files = [p for p in chat_dir.glob('*') if p.is_file()] if chat_dir.exists() else []
        if opts['keep_photos']:
            files = []

        self.stdout.write(f'MessageReport = {reports}')
        self.stdout.write(f'Message       = {messages}')
        self.stdout.write(f'Conversation  = {convos}')
        self.stdout.write(f'ActivityLog(chat) = {activity}')
        self.stdout.write(f'django_session = {sessions}')
        self.stdout.write(f'chat_uploads files = {len(files)}  ({chat_dir})')

        if not opts['yes']:
            self.stdout.write(self.style.WARNING('DRY-RUN — re-run with --yes to delete.'))
            return

        with transaction.atomic():
            MessageReport.objects.all().delete()
            Message.objects.all().delete()
            Conversation.objects.all().delete()
            ActivityLog.objects.filter(action='chat').delete()
        if not opts['keep_sessions']:
            Session.objects.all().delete()

        removed = 0
        for f in files:
            try:
                f.unlink()
                removed += 1
            except OSError:
                pass

        # Reset per-user AI usage counters (a log, not user data).
        usage = Path(settings.BASE_DIR) / 'apps' / 'chat' / 'usage_by_user.json'
        try:
            if usage.exists():
                usage.write_text('{}', encoding='utf-8')
        except OSError:
            pass

        self.stdout.write(self.style.SUCCESS(
            f'Cleaned. reports={reports} messages={messages} conversations={convos} '
            f'chat_activity={activity} sessions={sessions} photos_removed={removed}'
        ))
