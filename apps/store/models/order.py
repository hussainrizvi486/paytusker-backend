from django.db import models
from django.db.models import Avg
from datetime import timedelta

from . import UserAddress, Product, BaseModel
from .customer import Customer
from server.utils import generate_snf_id


validated_status = ["001", "002", "003", "004", "005", "006"]


class Order(BaseModel):
    class StatusChoices(models.TextChoices):
        ORDER_PENDING = "001", "Order Pending"
        ORDER_CONFIRMED = "002", "Order Confirmed"
        IN_PROCESS = "003", "In Process"
        SHIPPING = "004", "Shipping"
        DELIVERED = "005", "Delivered"
        CANCELLED = "006", "Cancelled"

    order_id = models.CharField(
        default=generate_snf_id, unique=True, max_length=999, editable=True
    )
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    order_date = models.DateField(auto_now_add=True)
    delivery_date = models.DateField(null=True, blank=True)
    order_status = models.CharField(
        choices=StatusChoices,
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
        UserAddress, null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self) -> str:
        return f"{self.customer} {self.order_id}"

    def calulate_validate_total(self):
        if hasattr(self, "order_items"):
            self.total_qty = sum(item.qty for item in self.order_items.all())
            self.grand_total = sum(item.amount for item in self.order_items.all())

    def save(self, *args, **kwargs):
        self.calulate_validate_total()
        if not self.delivery_date and self.order_date:
            self.delivery_date = self.order_date + timedelta(days=10)
        super().save(*args, **kwargs)

    def get_order_items(self):
        serailized_data = []
        orderitems_queryset = OrderItems.objects.filter(order=self)
        for order_item in orderitems_queryset:
            serailized_data.append(
                {
                    "product_name": order_item.item.product_name,
                    "product_id": order_item.item.id,
                    "rate": order_item.rate,
                    "amount": order_item.amount,
                    "qty": order_item.qty,
                }
            )
        return serailized_data


class OrderItems(BaseModel):
    class StatusChoices(models.TextChoices):
        ORDER_PENDING = "001", "Order Pending"
        ORDER_CONFIRMED = "002", "Order Confirmed"
        IN_PROCESS = "003", "In Process"
        SHIPPING = "004", "Shipping"
        DELIVERED = "005", "Delivered"
        CANCELLED = "006", "Cancelled"

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
    status = models.CharField(
        choices=StatusChoices,
        null=True,
        blank=True,
        max_length=999,
    )

    def __str__(self) -> str:
        return self.order.order_id

    def save(self, *args, **kwargs):
        if self.rate:
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
