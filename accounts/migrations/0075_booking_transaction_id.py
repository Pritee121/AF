# Generated by Django 5.0.3 on 2025-03-12 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0074_alter_booking_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
