import re

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.db import models
from . import BaseProfile
from apps.auth_user.models import User, UserRoles, generate_password
from apps.store.models.base import BaseModel


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


class SellerProfileRequest(BaseModel):
    seller_user = models.CharField(
        max_length=255, null=True, blank=True, editable=False
    )
    full_name = models.CharField(max_length=255)
    store_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    email = models.CharField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    website_url = models.CharField(max_length=100, null=True, blank=True)
    business_license = models.FileField(
        upload_to="business_licenses/", null=True, blank=True
    )
    description = models.TextField(null=True, blank=True)
    request_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="pending",
    )
    request_date = models.DateTimeField(auto_now_add=True)
    user_password = models.CharField(
        max_length=299, null=True, editable=False, blank=True
    )

    def __str__(self):
        return f"Seller Application from {self.store_name} ({self.full_name})"

    def save(self, *args, **kwargs):
        if not self.seller_user and self.request_status == "approved":
            user_password = generate_password()
            self.user_password = user_password
            user_instance = User.objects.create(
                **{
                    "email": self.email,
                    "username": re.sub(
                        r"\s+", "_", str(self.full_name).strip().lower()
                    ),
                    "first_name": self.full_name,
                    "phone_number": self.contact_number,
                    "password": user_password,
                }
            )
            user_instance.set_password(user_password)
            user_instance.save()
            self.seller_user = user_instance.id
            seller = Seller.objects.create(
                seller_name=user_instance.get_full_name(), user=user_instance
            )
            seller.save()
            seller_account_approval_email(self)

        return super().save(*args, **kwargs)


def seller_account_approval_email(object):
    message = render_to_string(
        "email/seller_registraion.html",
        {
            "user_password": object.user_password,
            "user_email": object.email,
            "full_name": object.full_name,
        },
    )

    send_mail(
        subject="Account Request",
        message="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[object.email],
        html_message=message,
    )
