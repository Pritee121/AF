# Generated by Django 5.0.3 on 2025-02-01 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0023_alter_user_managers_remove_user_username'),
    ]

    operations = [
        migrations.CreateModel(
            name='AboutUs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='About Us', max_length=255)),
                ('content', models.TextField()),
            ],
        ),
    ]
