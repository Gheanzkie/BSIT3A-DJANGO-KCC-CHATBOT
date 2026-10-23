import secrets

from django.db import migrations, models

from apps.chat.tokens import generate_chat_token


def fill_tokens(apps, schema_editor):
    Conversation = apps.get_model('chat', 'Conversation')
    for conversation in Conversation.objects.filter(token__isnull=True).iterator():
        conversation.token = secrets.token_urlsafe(32)
        conversation.save(update_fields=['token'])


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_conversation_session_key_alter_conversation_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='token',
            field=models.CharField(blank=True, max_length=64, null=True, unique=True),
        ),
        migrations.RunPython(fill_tokens, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='conversation',
            name='token',
            field=models.CharField(
                default=generate_chat_token, editable=False, max_length=64, unique=True
            ),
        ),
    ]
