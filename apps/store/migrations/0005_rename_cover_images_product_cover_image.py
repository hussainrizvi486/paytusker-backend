# Generated by Django 4.2.3 on 2023-12-31 13:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_alter_product_category'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='cover_images',
            new_name='cover_image',
        ),
    ]
