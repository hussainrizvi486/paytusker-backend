# Generated by Django 5.0.6 on 2024-08-12 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_user', '0005_loginhistory_ip'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='modified',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
