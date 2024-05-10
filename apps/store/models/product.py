from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from decimal import Decimal

from .base import BaseModel
from .common import Category


class ProductManager(models.Manager):
    def list_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(disabled=False).exclude(item_type="002")


class Product(BaseModel):
    cover_image = models.ImageField(max_length=10000, null=True)
    product_name = models.CharField(max_length=9999)
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
    description = models.TextField(default=product_name, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    template = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True
    )
    stock = models.IntegerField(default=1)
    rating = models.IntegerField(null=True, blank=True, default=0)
    disabled = models.BooleanField(default=False, null=True)
    is_digital = models.BooleanField(default=False, null=True)
    value = models.DecimalField(
        default=0, decimal_places=2, max_digits=12, null=True, blank=True
    )
    net_price = models.DecimalField(
        default=0, decimal_places=2, max_digits=12, null=True, blank=True
    )

    price = models.DecimalField(
        default=0, decimal_places=2, max_digits=12, null=True, blank=True
    )
    commission_rate = models.DecimalField(
        default=0, decimal_places=2, max_digits=12, null=True, blank=True
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
        if hasattr(self.category, "productcategorycommission"):
            commission_rate = self.category.productcategorycommission.commission_rate
            self.commission_rate = commission_rate

            if self.net_price is not None:
                self.price = self.net_price + (commission_rate / 100 * self.net_price)
        else:
            self.price = self.net_price

        return super().save(*args, **kwargs)


class ProductMedia(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    file = models.FileField(max_length=10000)

    def __str__(self) -> str:
        return self.product.product_name


class ProductVariantAttribute(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    attribute = models.CharField(max_length=999)
    attribute_value = models.CharField(max_length=999)


class ProductCategoryCommission(BaseModel):
    category = models.OneToOneField(Category, on_delete=models.CASCADE)
    commission_rate = models.DecimalField(
        decimal_places=2, max_digits=12, null=True, blank=True
    )

    def __str__(self) -> str:
        return f"{self.category} --> {self.commission_rate}"


@receiver(post_save, sender=ProductCategoryCommission)
def update_product_commission(sender, instance, created=None, *args, **kwargs):
    commission_rate = instance.commission_rate

    if commission_rate > 0:
        products_queryset = Product.objects.filter(category=instance.category)
        if products_queryset:
            for product in products_queryset:
                product.commission_rate = commission_rate
                product.price = product.net_price + (
                    commission_rate / 100 * product.net_price
                )

            Product.objects.bulk_update(products_queryset, ["commission_rate"])
