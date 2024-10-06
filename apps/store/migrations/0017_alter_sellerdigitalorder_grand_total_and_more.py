# Generated by Django 5.0.6 on 2024-09-22 18:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0016_digitalorder_digitalorderitem_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sellerdigitalorder',
            name='grand_total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11),
        ),
        migrations.AlterField(
            model_name='sellerdigitalorder',
            name='total_qty',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11),
        ),
        migrations.AlterField(
            model_name='sellerdigitalorderitem',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11),
        ),
        migrations.AlterField(
            model_name='sellerdigitalorderitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='store.sellerdigitalorder'),
        ),
        migrations.AlterField(
            model_name='sellerdigitalorderitem',
            name='qty',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11),
        ),
        migrations.AlterField(
            model_name='sellerdigitalorderitem',
            name='rate',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11),
        ),
    ]