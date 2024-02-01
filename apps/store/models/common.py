from django.db import models
from .base import BaseModel


class Category(BaseModel):
    name = models.CharField(max_length=500)
    image = models.CharField(max_length=9999, null=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self) -> str:
        if self.parent is None:
            return self.name
        return f"{self.parent} --> {self.name}"


class Discount(BaseModel):
    # product = models.ForeignKey(Product, on_delete=models.CASCADE)
    discount_percentage = models.DecimalField(decimal_places=2, max_digits=5)
    start_date = models.DateField()
    end_date = models.DateField()

    # def save(self, *args, **kwargs):
    #     product_price = self.product.price
    #     discount_price = (product_price / 100) * self.discount_percentage
    #     self.product.price = product_price - discount_price
