# Generated by Django 4.2.3 on 2024-04-14 01:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_delete_paymententry_alter_order_order_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_digital',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
