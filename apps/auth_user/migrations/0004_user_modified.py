# Generated by Django 5.0.6 on 2024-07-04 23:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_user', '0003_alter_loginhistory_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
