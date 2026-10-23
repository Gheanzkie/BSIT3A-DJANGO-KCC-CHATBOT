from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0006_conversation_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='closing_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
    ]
