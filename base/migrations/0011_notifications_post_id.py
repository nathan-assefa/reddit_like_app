# Generated by Django 4.2.6 on 2023-10-24 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_profile_followers'),
    ]

    operations = [
        migrations.AddField(
            model_name='notifications',
            name='post_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
