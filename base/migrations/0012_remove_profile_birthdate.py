# Generated by Django 4.2.6 on 2023-10-27 08:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_notifications_post_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='birthdate',
        ),
    ]
