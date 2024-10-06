from django.db import models
from uuid import uuid4
from apps.auth_user.models import User


class CurrencyChoices(models.TextChoices):
    USD = "USD", "United States Dollar"
    EUR = "EUR", "Euro"
    JPY = "JPY", "Japanese Yen"
    GBP = "GBP", "British Pound Sterling"
    AUD = "AUD", "Australian Dollar"
    CAD = "CAD", "Canadian Dollar"
    CHF = "CHF", "Swiss Franc"
    CNY = "CNY", "Chinese Yuan"
    HKD = "HKD", "Hong Kong Dollar"
    NZD = "NZD", "New Zealand Dollar"
    SEK = "SEK", "Swedish Krona"
    KRW = "KRW", "South Korean Won"
    SGD = "SGD", "Singapore Dollar"
    NOK = "NOK", "Norwegian Krone"
    MXN = "MXN", "Mexican Peso"
    INR = "INR", "Indian Rupee"
    RUB = "RUB", "Russian Ruble"
    ZAR = "ZAR", "South African Rand"
    TRY = "TRY", "Turkish Lira"
    BRL = "BRL", "Brazilian Real"
    TWD = "TWD", "New Taiwan Dollar"
    PLN = "PLN", "Polish Zloty"
    THB = "THB", "Thai Baht"
    MYR = "MYR", "Malaysian Ringgit"


class BaseModel(models.Model):
    id = models.CharField(
        default=uuid4, unique=True, editable=False, primary_key=True, max_length=10000
    )
    creation = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-modified"]


class BaseProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class UserAddress(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address_title = models.CharField(max_length=200, null=True)
    address_line = models.CharField(max_length=200, null=True)
    address_type = models.CharField(max_length=200, null=True)
    country = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    default = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.address_title} - {self.address_line}, {self.city}, {self.state}, {self.country} ({'Default' if self.default else 'Secondary'})"
