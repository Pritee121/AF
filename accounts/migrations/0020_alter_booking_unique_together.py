# Generated by Django 5.0.3 on 2025-02-01 06:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0019_service_duration'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='booking',
            unique_together={('artist', 'date', 'time')},
        ),
    ]
