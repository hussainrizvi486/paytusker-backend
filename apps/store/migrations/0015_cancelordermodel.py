# Generated by Django 5.0.6 on 2024-09-17 14:54

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0014_rename_sellerorderitems_sellerdigitalorderitem_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="CancelOrderModel",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=uuid.uuid4,
                        editable=False,
                        max_length=10000,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("creation", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                ("order_id", models.CharField(max_length=300)),
                ("reason", models.CharField(max_length=300)),
                ("notes", models.TextField()),
                ("cancelled_by", models.CharField(max_length=99)),
                ("order_model", models.CharField(max_length=99)),
            ],
            options={
                "ordering": ["-modified"],
                "abstract": False,
            },
        ),
    ]