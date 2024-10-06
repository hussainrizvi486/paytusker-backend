from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.db.models import Avg

from .product import Product
from server.utils import generate_snf_id
from . import UserAddress, BaseModel, Customer
from .choices import DigitalOrderStatusChoices


class OrderStatusChoices(models.TextChoices):
    ORDER_PENDING = "001", "Order Pending"
    ORDER_CONFIRMED = "002", "Order Confirmed"
    IN_PROCESS = "003", "In Process"
    SHIPPING = "004", "Shipping"
    DELIVERED = "005", "Delivered"
    CANCELLED = "006", "Cancelled"
    Refunded = "007", "Refunded"


class Order(BaseModel):
    order_id = models.CharField(
        default=generate_snf_id, unique=True, max_length=999, editable=True
    )
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    order_date = models.DateField(auto_now_add=True)
    delivery_date = models.DateField(null=True, blank=True)
    order_status = models.CharField(
        choices=OrderStatusChoices.choices,
        null=True,
        blank=True,
        max_length=50,
    )
    delivery_status = models.BooleanField(default=False)
    payment_status = models.BooleanField(default=False)
    payment_method = models.CharField(
        null=True,
        blank=True,
        max_length=99,
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
        choices=OrderStatusChoices.choices,
        null=True,
        blank=True,
        max_length=999,
    )

    def __str__(self) -> str:
        return f"{self.order.order_id} {self.item.product_name} {self.rate}"

    def save(self, *args, **kwargs):
        if self.rate:
            self.rate = self.item.price
        self.amount = self.rate * self.qty
        super().save(*args, **kwargs)


class OrderReview(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_type = models.CharField(max_length=999, null=True, blank=True)
    order = models.CharField(max_length=999)
    order_id = models.CharField(max_length=999)
    order_item = models.CharField(max_length=999)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.FloatField()
    review_content = models.TextField()

    def __str__(self) -> str:
        return f"{self.customer.customer_name}-{self.order}"

    # def save(self, *args, **kwargs):
    #     total_rating = OrderReview.objects.filter(product=self.product).aggregate(
    #         Avg("rating", default=0)
    #     )
    #     self.product.rating = total_rating.get("rating__avg") or 0
    #     self.product.save()
    #     return super().save(*args, **kwargs)


class DigitalOrder(BaseModel):
    order_id = models.CharField(
        default=generate_snf_id, unique=True, max_length=999, editable=True
    )
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    order_date = models.DateField(auto_now_add=True)
    order_status = models.CharField(
        choices=DigitalOrderStatusChoices.choices,
        default=DigitalOrderStatusChoices.PLACED,
        null=True,
        blank=True,
        max_length=50,
    )
    payment_status = models.BooleanField(default=False)
    payment_method = models.CharField(
        null=True,
        blank=True,
        max_length=99,
    )
    total_qty = models.DecimalField(
        default=1, decimal_places=2, max_digits=12, blank=True
    )
    grand_total = models.DecimalField(
        decimal_places=2, max_digits=12, null=True, blank=True
    )

    def __str__(self) -> str:
        return f"{self.customer} {self.order_id}"

    def calulate_total(self):
        # if hasattr(self, "items"):
        self.total_qty = sum(item.qty for item in self.items.all())
        self.grand_total = sum(item.amount for item in self.items.all())

    def save(self, *args, **kwargs):
        self.calulate_total()
        super().save(*args, **kwargs)


class DigitalOrderItem(BaseModel):
    order = models.ForeignKey(
        DigitalOrder, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.DecimalField(
        default=1,
        decimal_places=2,
        max_digits=12,
    )
    rate = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    amount = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    reviewed_by_customer = models.BooleanField(default=False)
    status = models.CharField(
        choices=DigitalOrderStatusChoices.choices,
        default=DigitalOrderStatusChoices.PLACED,
        null=True,
        blank=True,
        max_length=999,
    )

    def __str__(self) -> str:
        return f"{self.order}"

    def save(self, *args, **kwargs):
        self.amount = self.rate * self.qty
        super().save(*args, **kwargs)


class OrderCancellation(models.Model):
    order_id = models.CharField(max_length=299)
    cancelled_by = models.CharField(max_length=200, null=True, blank=True)
    cancellation_reason = models.CharField(max_length=1000)
    notes = models.TextField()
    cancelled_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.order} cancelled by {self.cancelled_by}"

    class Meta:
        ordering = ["-cancelled_at"]
