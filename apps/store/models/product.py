from collections.abc import Iterable
from django.db import models
from .base import BaseModel
from .common import Category


PRODUCT_TYPES = {
    ("001", "Normal"),
    ("002", "Template"),
    ("003", "Varient"),
}


class Product(BaseModel):
    product_name = models.CharField(max_length=9999)
    net_price = models.DecimalField(
        decimal_places=2, max_digits=12, null=True, blank=True
    )
    price = models.DecimalField(decimal_places=2, max_digits=12, null=True)
    description = models.TextField(default="", null=True)
    stock = models.IntegerField(default=1)
    disabled = models.BooleanField(default=False, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    cover_image = models.CharField(max_length=10000, null=True)
    rating = models.IntegerField(null=True, blank=True)
    item_type = models.CharField(max_length=999, choices=PRODUCT_TYPES, default="001", null=True, blank=True)
    template = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self) -> str:
        return self.product_name

    def save(self, *args, **kwargs) -> None:
        self.net_price = self.price
        return super().save(*args, **kwargs)


class ProductImages(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    image_url = models.CharField(max_length=10000)

    def __str__(self) -> str:
        return self.product.product_name


class ProductAttribute(BaseModel):
    attribute_name = models.CharField(max_length=999)
    def __str__(self) -> str:
        return self.attribute_name


class ProductVariantAttribute(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE)
    attribute_value = models.CharField(max_length=999)
