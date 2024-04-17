from django.db import models
from .base import BaseModel


class Category(BaseModel):
    name = models.CharField(max_length=500)
    image = models.ImageField(null=True, blank=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    digital = models.BooleanField(default=False)

    def __str__(self) -> str:
        if self.parent is None:
            return self.name
        return f"{self.parent} --> {self.name}"


class Discount(BaseModel):
    discount_percentage = models.DecimalField(decimal_places=2, max_digits=5)
    start_date = models.DateField()
    end_date = models.DateField()

    # def save(self, *args, **kwargs):
    #     product_price = self.product.price
    #     discount_price = (product_price / 100) * self.discount_percentage
    #     self.product.price = product_price - discount_price
