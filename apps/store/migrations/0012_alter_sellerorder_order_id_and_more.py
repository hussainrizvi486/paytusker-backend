# Generated by Django 5.0.6 on 2024-09-05 21:12

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_alter_sellerorder_order_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sellerorder',
            name='order_id',
            field=models.CharField(max_length=10000, null=True),
        ),
        migrations.AlterField(
            model_name='sellerorder',
            name='order_items',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=999), blank=True, null=True, size=None),
        ),
    ]
