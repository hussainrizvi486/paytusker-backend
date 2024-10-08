from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from . import BaseModel
from .product import Product
from apps.auth_user.models import User, UserRoles


class Customer(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=999)

    def __str__(self) -> str:
        return self.user.username

    def save(self, *args, **kwargs) -> None:
        if not self.user.has_role(UserRoles.RoleChoices.CUSTOMER):
            UserRoles.objects.create(
                user=self.user, role=UserRoles.RoleChoices.CUSTOMER
            )
        return super().save(*args, **kwargs)


class Cart(BaseModel):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    total_qty = models.DecimalField(
        decimal_places=2, max_digits=12, null=True, default=0
    )
    total_amount = models.DecimalField(
        decimal_places=2, max_digits=12, null=True, blank=True
    )

    def __str__(self) -> str:
        return self.customer.user.username

    def save(self, *args, **kwargs) -> None:
        self.total_amount = sum([item.amount for item in self.cartitem_set.all()])
        self.total_qty = sum([item.qty for item in self.cartitem_set.all()])

        return super().save(*args, **kwargs)


class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=True, blank=True
    )
    qty = models.DecimalField(
        default=1,
        decimal_places=2,
        max_digits=12,
    )
    rate = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    amount = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)

    def save(self, *args, **kwargs) -> None:
        self.rate = self.product.price
        self.amount = self.qty * self.rate
        return super().save(*args, **kwargs)


@receiver([post_save, post_delete], sender=CartItem)
def update_cart(sender, instance, created=None, *args, **kwargs):
    instance.cart.save()
