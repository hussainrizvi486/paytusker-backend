# Generated by Django 4.2.3 on 2024-04-10 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_alter_order_order_status_alter_product_item_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(blank=True, choices=[('002', 'Order Confirmed'), ('005', 'Delivered'), ('001', 'Order Pending'), ('003', 'In Process'), ('004', 'Shipping')], max_length=999, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='item_type',
            field=models.CharField(blank=True, choices=[('002', 'Template'), ('001', 'Normal'), ('003', 'Varient')], default='001', max_length=999, null=True),
        ),
    ]