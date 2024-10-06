from typing import Any, Iterable
from django.db import models
from django.contrib.postgres.fields import ArrayField

from .. import BaseModel, Customer, Seller, UserAddress
from ..choices import DigitalOrderStatusChoices
from ..product import Product
from ..order import DigitalOrderItem


class SellerDigitalOrder(BaseModel):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    order_id = models.CharField(
        max_length=10000,
        null=True,
    )
    order_items = ArrayField(models.CharField(max_length=299), size=1000, null=True)
    order_date = models.DateField(auto_now_add=True)
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    status = models.CharField(
        choices=DigitalOrderStatusChoices.choices,
        default=DigitalOrderStatusChoices.PLACED,
        max_length=50,
    )
    grand_total = models.DecimalField(decimal_places=2, max_digits=11, default=0)
    total_qty = models.DecimalField(decimal_places=2, max_digits=11, default=0)

    def __str__(self) -> str:
        return f"{self.order_id} {self.seller} {self.order_date}"

    def calculate_total(self):
        self.grand_total = sum([item.amount for item in self.items.all() or []])
        self.total_qty = sum([item.qty for item in self.items.all() or []])

    def generate_order_id(self):
        if self.seller:
            max_count = SellerDigitalOrder.objects.filter(seller=self.seller).count()
            return f"#{str(max_count + 1).zfill(5)}"

    def save(self, *args, **kwargs):
        self.calculate_total()

        if not self.order_id:
            self.order_id = self.generate_order_id()

        super().save(*args, **kwargs)

    def update_status(self, status):
        self.status = status
        DigitalOrderItem.objects.filter(id__in=self.order_items).update(status=status)
        self.save()


class SellerDigitalOrderItem(BaseModel):
    order = models.ForeignKey(
        SellerDigitalOrder, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rate = models.DecimalField(decimal_places=2, max_digits=11, default=0)
    qty = models.DecimalField(decimal_places=2, max_digits=11, default=0)
    amount = models.DecimalField(decimal_places=2, max_digits=11, default=0)

    def calculate_total(self):
        self.amount = self.rate * self.qty

    def save(self, *args, **kwargs):
        self.calculate_total()
        return super().save(*args, **kwargs)


class SellerOrder(BaseModel):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    order_date = models.DateField(auto_now_add=True)
    status = models.CharField(
        null=True,
        blank=True,
        max_length=50,
    )
    delivery_date = models.DateField(null=True, blank=True)
    delivery_address = models.ForeignKey(
        UserAddress, null=True, blank=True, on_delete=models.SET_NULL
    )
    order_id = models.CharField(max_length=10000, null=True)
    order_items = models.CharField(max_length=999, blank=True, null=True)
    shipping_id = models.CharField(max_length=10000)
    grand_total = models.DecimalField(decimal_places=2, max_digits=11)
    total_qty = models.DecimalField(decimal_places=2, max_digits=11)

    def __str__(self) -> str:
        return f"{self.order_id} {self.seller} {self.order_date}"


class SellerOrderItem(BaseModel):
    order = models.ForeignKey(SellerOrder, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rate = models.DecimalField(decimal_places=2, max_digits=11)
    qty = models.DecimalField(decimal_places=2, max_digits=11)
    amount = models.DecimalField(decimal_places=2, max_digits=11)
