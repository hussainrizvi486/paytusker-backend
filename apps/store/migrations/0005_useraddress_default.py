# Generated by Django 5.0.6 on 2024-07-05 23:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_useraddress'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraddress',
            name='default',
            field=models.BooleanField(default=False),
        ),
    ]