# Generated by Django 5.0.6 on 2024-09-05 21:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_alter_sellerorder_order_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sellerorder',
            name='order_items',
            field=models.CharField(blank=True, max_length=999, null=True),
        ),
    ]