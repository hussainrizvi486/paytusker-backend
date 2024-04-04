# Generated by Django 4.2.3 on 2024-04-03 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0050_alter_order_order_status_alter_product_item_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(blank=True, choices=[('003', 'In Process'), ('005', 'Delivered'), ('002', 'Order Confirmed'), ('004', 'Shipping'), ('001', 'Order Pending')], max_length=999, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='item_type',
            field=models.CharField(blank=True, choices=[('002', 'Template'), ('003', 'Varient'), ('001', 'Normal')], default='001', max_length=999, null=True),
        ),
    ]
