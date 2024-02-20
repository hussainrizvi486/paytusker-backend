from django.db import models
from .base import BaseModel
from .product import Product
from .customer import Customer
from uuid import uuid4
from server.utils import generate_snf_id
from apps.accounts.models import User

ORDER_STATUS = {
    ("001", "Order Pending"),
    ("002", "Order Confirmed"),
    ("003", "In Process"),
    ("004", "Shipping"),
    ("005", "Delivered"),
}

PAYMENT_METHOD = [
    ("001", "Cash On Delivery"),
    ("002", "Stripe"),
    ("003", "PayPal"),
    ("004", "Crypto"),
]


class Order(BaseModel):
    order_id = models.CharField(
        default=generate_snf_id, unique=True, max_length=999, editable=True
    )
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    order_date = models.DateField(auto_now_add=True)
    delivery_date = models.DateField(auto_now_add=True)
    order_status = models.CharField(
        choices=ORDER_STATUS, null=True, blank=True, max_length=999
    )
    delivery_status = models.BooleanField(default=False)
    payment_status = models.BooleanField(default=False)
    payment_method = models.CharField(
        choices=PAYMENT_METHOD, null=True, blank=True, max_length=999
    )
    total_qty = models.DecimalField(
        default=1, decimal_places=2, max_digits=12, blank=True
    )
    grand_total = models.DecimalField(
        decimal_places=2, max_digits=12, null=True, blank=True
    )

    def __str__(self) -> str:
        return f"{self.customer} {self.order_id}"

    def save(self, *args, **kwargs):
        self.total_qty = sum(item.qty for item in self.order_items.all())
        self.grand_total = sum(item.amount for item in self.order_items.all())
        super().save(*args, **kwargs)


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

    def __str__(self) -> str:
        return self.order.order_id

    def save(self, *args, **kwargs):
        self.rate = self.item.price
        self.amount = self.rate * self.qty
        super().save(*args, **kwargs)


class OrderReview(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.FloatField()
    review_content = models.TextField()

    def __str__(self) -> str:
        return f"{self.customer.customer_name}-{self.order.order_id}"
