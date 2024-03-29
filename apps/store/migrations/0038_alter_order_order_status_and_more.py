# Generated by Django 4.2.3 on 2024-03-17 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0037_alter_category_image_alter_order_order_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(blank=True, choices=[('001', 'Order Pending'), ('005', 'Delivered'), ('003', 'In Process'), ('004', 'Shipping'), ('002', 'Order Confirmed')], max_length=999, null=True),
        ),
        migrations.AlterField(
            model_name='productimages',
            name='image_url',
            field=models.ImageField(max_length=10000, upload_to=''),
        ),
    ]
