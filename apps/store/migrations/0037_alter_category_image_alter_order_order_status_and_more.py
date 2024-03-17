# Generated by Django 4.2.3 on 2024-03-17 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0036_orderitems_has_review_orderreview_order_item_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='image',
            field=models.CharField(blank=True, max_length=9999, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(blank=True, choices=[('005', 'Delivered'), ('002', 'Order Confirmed'), ('001', 'Order Pending'), ('004', 'Shipping'), ('003', 'In Process')], max_length=999, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='cover_image',
            field=models.ImageField(max_length=10000, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='product',
            name='item_type',
            field=models.CharField(blank=True, choices=[('001', 'Normal'), ('003', 'Varient'), ('002', 'Template')], default='001', max_length=999, null=True),
        ),
    ]