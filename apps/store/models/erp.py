from . import BaseModel
from django.db import models


class PaymentEntry(BaseModel):
    party = models.CharField(max_length=999)
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    reference = models.CharField(max_length=200)
    reference_id = models.CharField(max_length=200)
    currency = models.CharField(max_length=200)
    is_paid = models.BooleanField(default=False)
