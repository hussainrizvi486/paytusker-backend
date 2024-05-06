from django.db import models
from django.db.models import Avg
from typing import List
from .base import BaseModel
from .product import Product
from .customer import Customer
from server.utils import generate_snf_id
from apps.accounts.models import Address


class Order(BaseModel):
    order_id = models.CharField(
        default=generate_snf_id, unique=True, max_length=999, editable=True
    )
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    order_date = models.DateField(auto_now_add=True)
    delivery_date = models.DateField(auto_now_add=True)
    order_status = models.CharField(
        choices=(
            ("001", "Order Pending"),
            ("002", "Order Confirmed"),
            ("003", "In Process"),
            ("004", "Shipping"),
            ("005", "Delivered"),
            ("006", "Cancelled"),
        ),
        null=True,
        blank=True,
        max_length=999,
    )
    delivery_status = models.BooleanField(default=False)
    payment_status = models.BooleanField(default=False)
    payment_method = models.CharField(
        null=True,
        blank=True,
        max_length=999,
    )
    total_qty = models.DecimalField(
        default=1, decimal_places=2, max_digits=12, blank=True
    )
    grand_total = models.DecimalField(
        decimal_places=2, max_digits=12, null=True, blank=True
    )

    delivery_address = models.ForeignKey(
        Address, null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self) -> str:
        return f"{self.customer} {self.order_id}"

    def save(self, *args, **kwargs):
        self.total_qty = sum(item.qty for item in self.order_items.all())
        self.grand_total = sum(item.amount for item in self.order_items.all())
        super().save(*args, **kwargs)

    # def get_order_items(self):
    #     serailized_data = []
    #     orderitems_queryset: List[OrderItems] = self.order_items_set.all()
    #     for row in orderitems_queryset:
    #         serailized_data.append({"product_id": row.item.id, "qty": row.qty, })


class OrderItems(BaseModel):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_items"
    )
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.DecimalField(
        default=1,
        decimal_places=2,
        max_digits=12,
    )
    rate = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    amount = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    has_review = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.order.order_id

    def save(self, *args, **kwargs):
        self.rate = self.item.price
        self.amount = self.rate * self.qty
        super().save(*args, **kwargs)


class OrderReview(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_item = models.ForeignKey(OrderItems, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.FloatField()
    review_content = models.TextField()

    def __str__(self) -> str:
        return f"{self.customer.customer_name}-{self.order.order_id}"

    def save(self, *args, **kwargs):
        total_rating = OrderReview.objects.filter(product=self.product).aggregate(
            Avg("rating", default=0)
        )
        self.product.rating = total_rating.get("rating__avg") or 0
        self.product.save()
        return super().save(*args, **kwargs)


class CustomersOrdersHistory(models.Model):
    customer = models.CharField(max_length=999)
    order_id = models.CharField(max_length=999)
    total_amount = models.CharField(max_length=999)
    total_qty = models.CharField(max_length=999)
    payment_method = models.CharField(max_length=999)
    delivery_status = models.CharField(max_length=999)
    delivery_address = models.CharField(max_length=999)
