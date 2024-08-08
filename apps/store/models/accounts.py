from django.db import models
from .base import BaseModel, CurrencyChoices


class PaymentEntry(BaseModel):
    class PartTypeChoices(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        SELLER = "seller", "Seller"

    amount = models.DecimalField(
        decimal_places=2,
        default=0,
        max_digits=11,
    )
    party_type = models.CharField(choices=PartTypeChoices, max_length=99)
    party_id = models.CharField(max_length=99)
    mode_of_payment = models.CharField(max_length=99)
    reference_type = models.CharField(max_length=99)
    reference_id = models.CharField(max_length=99)
    currency = models.CharField(
        choices=CurrencyChoices, default=CurrencyChoices.USD, max_length=99
    )

    def __str__(self) -> str:
        return f"""{self.party_type} {self.party_id} {self.amount}"""
