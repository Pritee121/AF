# Generated by Django 5.0.3 on 2025-02-18 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0006_chatroom_is_deleted_by_artist_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='audio',
            field=models.FileField(blank=True, null=True, upload_to='voice_messages/'),
        ),
    ]
