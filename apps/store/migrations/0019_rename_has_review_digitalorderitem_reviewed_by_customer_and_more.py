# Generated by Django 5.0.6 on 2024-10-03 22:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0018_ordercancellation_alter_digitalorderitem_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='digitalorderitem',
            old_name='has_review',
            new_name='reviewed_by_customer',
        ),
        migrations.AddField(
            model_name='orderreview',
            name='order_type',
            field=models.CharField(blank=True, max_length=999, null=True),
        ),
        migrations.AlterField(
            model_name='orderreview',
            name='order',
            field=models.CharField(max_length=999),
        ),
        migrations.AlterField(
            model_name='orderreview',
            name='order_item',
            field=models.CharField(default=False, max_length=999),
            preserve_default=False,
        ),
    ]
