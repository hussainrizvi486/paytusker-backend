from django.db import models
from . import BaseProfile
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
