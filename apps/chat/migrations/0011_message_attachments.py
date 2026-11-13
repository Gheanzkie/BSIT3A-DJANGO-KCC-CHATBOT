from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0010_delete_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='attachments',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
