# Generated by Django 4.2.3 on 2024-06-21 23:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import server.utils
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=10000, primary_key=True, serialize=False, unique=True)),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('total_qty', models.DecimalField(decimal_places=2, default=0, max_digits=12, null=True)),
                ('total_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=10000, primary_key=True, serialize=False, unique=True)),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=500)),
                ('image', models.ImageField(blank=True, null=True, upload_to='')),
                ('digital', models.BooleanField(default=False)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.category')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=10000, primary_key=True, serialize=False, unique=True)),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('customer_name', models.CharField(max_length=999)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CustomersOrdersHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer', models.CharField(max_length=999)),
                ('order_id', models.CharField(max_length=999)),
                ('total_amount', models.CharField(max_length=999)),
                ('total_qty', models.CharField(max_length=999)),
                ('payment_method', models.CharField(max_length=999)),
                ('delivery_status', models.CharField(max_length=999)),
                ('delivery_address', models.CharField(max_length=999)),
            ],
        ),
        migrations.CreateModel(
            name='ModelMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_name', models.CharField(max_length=999)),
                ('field_id', models.CharField(max_length=999)),
                ('file', models.FileField(upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=10000, primary_key=True, serialize=False, unique=True)),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('order_id', models.CharField(default=server.utils.generate_snf_id, max_length=999, unique=True)),
                ('order_date', models.DateField(auto_now_add=True)),
                ('delivery_date', models.DateField(blank=True, null=True)),
                ('order_status', models.CharField(blank=True, choices=[('001', 'Order Pending'), ('002', 'Order Confirmed'), ('003', 'In Process'), ('004', 'Shipping'), ('005', 'Delivered'), ('006', 'Cancelled')], max_length=999, null=True)),
                ('delivery_status', models.BooleanField(default=False)),
                ('payment_status', models.BooleanField(default=False)),
                ('payment_method', models.CharField(blank=True, max_length=999, null=True)),
                ('total_qty', models.DecimalField(blank=True, decimal_places=2, default=1, max_digits=12)),
                ('grand_total', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.customer')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrderItems',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=10000, primary_key=True, serialize=False, unique=True)),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('qty', models.DecimalField(decimal_places=2, default=1, max_digits=12)),
                ('rate', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('has_review', models.BooleanField(default=False)),
                ('status', models.CharField(blank=True, choices=[('001', 'Order Pending'), ('002', 'Order Confirmed'), ('003', 'In Process'), ('004', 'Shipping'), ('005', 'Delivered'), ('006', 'Cancelled')], max_length=999, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=10000, primary_key=True, serialize=False, unique=True)),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('cover_image', models.ImageField(max_length=10000, null=True, upload_to='')),
                ('product_name', models.CharField(max_length=9999)),
                ('item_type', models.CharField(blank=True, choices=[('001', 'Normal'), ('002', 'Template'), ('003', 'Varient')], default='001', max_length=999, null=True)),
                ('description', models.TextField(default=models.CharField(max_length=9999), null=True)),
                ('stock', models.IntegerField(default=1)),
                ('rating', models.IntegerField(blank=True, default=0, null=True)),
                ('disabled', models.BooleanField(default=False, null=True)),
                ('is_digital', models.BooleanField(default=False, null=True)),
                ('value', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, null=True)),
                ('net_price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, null=True)),
                ('product_price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, null=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, null=True)),
                ('commission_rate', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, null=True)),
                ('discount_percentage', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, null=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.category')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Seller',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=10000, primary_key=True, serialize=False, unique=True)),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('seller_name', models.CharField(max_length=99)),
                ('seller_rating', models.FloatField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StoreErrorLogs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='SellerOrder',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=10000, primary_key=True, serialize=False, unique=True)),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('rate', models.DecimalField(decimal_places=2, max_digits=12)),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=12)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.seller')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductVariantAttribute',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=10000, primary_key=True, serialize=False, unique=True)),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('attribute', models.CharField(max_length=999)),
                ('attribute_value', models.CharField(max_length=999)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductMedia',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=10000, primary_key=True, serialize=False, unique=True)),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('file', models.FileField(max_length=10000, upload_to='')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.product')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductDiscount',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=10000, primary_key=True, serialize=False, unique=True)),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('discount_percentage', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, null=True)),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='store.product')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductCategoryCommission',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=10000, primary_key=True, serialize=False, unique=True)),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('commission_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('category', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='store.category')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='product',
            name='seller',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.seller'),
        ),
        migrations.AddField(
            model_name='product',
            name='template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.product'),
        ),
        migrations.CreateModel(
            name='OrderReview',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=10000, primary_key=True, serialize=False, unique=True)),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('rating', models.FloatField()),
                ('review_content', models.TextField()),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.customer')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.order')),
                ('order_item', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='store.orderitems')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='orderitems',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product'),
        ),
        migrations.AddField(
            model_name='orderitems',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='store.order'),
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=10000, primary_key=True, serialize=False, unique=True)),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('qty', models.DecimalField(decimal_places=2, default=1, max_digits=12)),
                ('rate', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.cart')),
                ('item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.product')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='cart',
            name='customer',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='store.customer'),
        ),
    ]
