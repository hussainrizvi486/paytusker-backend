from django.db import models
from uuid import uuid4
from ..accounts.models import User


class BaseModel(models.Model):
    id = models.CharField(default=uuid4, unique=True,
                          editable=False, primary_key=True, max_length=10000)
    creation = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Address(BaseModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    country = models.CharField(max_length=500, null=True, blank=True)
    state = models.CharField(max_length=500, null=True, blank=True)
    city = models.CharField(max_length=500, null=True, blank=True)
    street = models.CharField(max_length=500, null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self) -> str:
        return self.user.username or self.user.email


class Category(BaseModel):
    name = models.CharField(max_length=500)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self) -> str:
        if self.parent is None:
            return self.name
        return f"{self.parent} -->  {self.name}"


class Product(BaseModel):
    product_name = models.CharField(max_length=9999)
    price = models.DecimalField(decimal_places=2, max_digits=12)
    description = models.TextField(default="", null=True)
    stock = models.IntegerField(default=1)
    disabled = models.BooleanField(default=False)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True)
    cover_images = models.CharField(max_length=10000, null=True)


class ProductImages(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    image_url = models.CharField(max_length=10000)

    def __str__(self) -> str:
        return self.product.name
