from django.db import models
from .base import BaseModel
from .common import Category


class ProductManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(disabled=False)


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
    cover_image = models.ImageField(max_length=10000, null=True)
    rating = models.IntegerField(null=True, blank=True, default=0)
    item_type = models.CharField(
        max_length=999,
        choices=(
            ("001", "Normal"),
            ("002", "Template"),
            ("003", "Varient"),
        ),
        default="001",
        null=True,
        blank=True,
    )
    template = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True
    )

    objects = ProductManager()

    def __str__(self) -> str:
        return self.product_name

    def get_product_images(self, request=None):
        query_set = ProductMedia.objects.filter(product=self)
        images_list = []
        if query_set:
            if request:
                images_list = [
                    request.build_absolute_uri(row.file.url) for row in query_set
                ]
                if self.cover_image:
                    images_list.insert(
                        0, request.build_absolute_uri(self.cover_image.url)
                    )
            else:
                images_list = [row.file.url for row in query_set]
                images_list.insert(0, self.cover_image.url)
        return images_list

    def save(self, *args, **kwargs) -> None:
        return super().save(*args, **kwargs)


class ProductMedia(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    file = models.FileField(max_length=10000)

    def __str__(self) -> str:
        return self.product.product_name


# class ProductAttribute(BaseModel):
#     attribute_name = models.CharField(max_length=999)

#     def __str__(self) -> str:
#         return self.attribute_name


class ProductVariantAttribute(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    attribute = models.CharField(max_length=999)
    attribute_value = models.CharField(max_length=999)
