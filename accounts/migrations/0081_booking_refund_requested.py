# Generated by Django 5.0.3 on 2025-03-30 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0080_service_description_embedding'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='refund_requested',
            field=models.BooleanField(default=False),
        ),
    ]
