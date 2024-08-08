# Generated by Django 5.0.6 on 2024-08-08 06:32

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_useraddress_default'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentEntry',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=10000, primary_key=True, serialize=False, unique=True)),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('party_type', models.CharField(choices=[('customer', 'Customer'), ('seller', 'Seller')], max_length=99)),
                ('party_id', models.CharField(max_length=99)),
                ('mode_of_payment', models.CharField(max_length=99)),
                ('reference_type', models.CharField(max_length=99)),
                ('reference_id', models.CharField(max_length=99)),
                ('currency', models.CharField(choices=[('USD', 'United States Dollar'), ('EUR', 'Euro'), ('JPY', 'Japanese Yen'), ('GBP', 'British Pound Sterling'), ('AUD', 'Australian Dollar'), ('CAD', 'Canadian Dollar'), ('CHF', 'Swiss Franc'), ('CNY', 'Chinese Yuan'), ('HKD', 'Hong Kong Dollar'), ('NZD', 'New Zealand Dollar'), ('SEK', 'Swedish Krona'), ('KRW', 'South Korean Won'), ('SGD', 'Singapore Dollar'), ('NOK', 'Norwegian Krone'), ('MXN', 'Mexican Peso'), ('INR', 'Indian Rupee'), ('RUB', 'Russian Ruble'), ('ZAR', 'South African Rand'), ('TRY', 'Turkish Lira'), ('BRL', 'Brazilian Real'), ('TWD', 'New Taiwan Dollar'), ('PLN', 'Polish Zloty'), ('THB', 'Thai Baht'), ('MYR', 'Malaysian Ringgit')], default='USD', max_length=99)),
            ],
            options={
                'ordering': ['-modified'],
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='product',
            name='cover_image',
            field=models.ImageField(blank=True, max_length=10000, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='item_type',
            field=models.CharField(blank=True, choices=[('002', 'Template'), ('003', 'Variant'), ('001', 'Normal')], default='001', max_length=999, null=True),
        ),
        migrations.AlterField(
            model_name='productmedia',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='store.product'),
        ),
    ]