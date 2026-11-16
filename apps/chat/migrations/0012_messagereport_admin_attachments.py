from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0011_message_attachments'),
    ]

    operations = [
        migrations.AddField(
            model_name='messagereport',
            name='admin_attachments',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
