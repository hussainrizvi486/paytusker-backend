from typing import Iterable
from django.db import models
from .base import BaseModel, BaseProfile
from apps.auth_user.models import User, UserRoles


class Seller(BaseProfile):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seller_name = models.CharField(max_length=99)
    seller_rating = models.FloatField(default=0)

    def __str__(self) -> str:
        return self.seller_name

    def save(self, *args, **kwargs) -> None:
        if not self.user.has_role(UserRoles.RoleChoices.SELLER):
            UserRoles.objects.create(user=self.user, role=UserRoles.RoleChoices.SELLER)
        return super().save(*args, **kwargs)


class SellerOrder(BaseModel):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    # item = models.ForeignKey(Product, on_delete=models.CASCADE)
    rate = models.DecimalField(decimal_places=2, max_digits=12)
    quantity = models.DecimalField(decimal_places=2, max_digits=12)
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    # status = models.CharField(choices=ORDER_STATUS)
