from typing import Any
from decimal import Decimal
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from . import Seller, Category, BaseModel
from server.overrides import ModelTextChoices


class ProductManager(models.Manager):
    def list_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(disabled=False).exclude(item_type="002")


class Product(BaseModel):
    class TypeChoices(ModelTextChoices):
        NORMAL = "001", "Normal"
        TEMPLATE = "002", "Template"
        VARIANT = "003", "Variant"

    class ItemTypeChoices(models.TextChoices):
        TEMPLATE = "002", "Template"
        VARIANT = "003", "Variant"
        NORMAL = "001", "Normal"

    cover_image = models.ImageField(max_length=10000, null=True, blank=True)
    product_name = models.CharField(max_length=9999)
    item_type = models.CharField(
        max_length=999,
        choices=ItemTypeChoices.choices,
        default=ItemTypeChoices.NORMAL,
        null=True,
        blank=True,
    )
    description = models.TextField(null=True, blank=True)
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
    net_price = models.DecimalField(
        default=0, decimal_places=2, max_digits=12, null=True, blank=True
    )
    commission_rate = models.DecimalField(
        default=0, decimal_places=2, max_digits=12, null=True, blank=True
    )
    product_price = models.DecimalField(
        default=0, decimal_places=2, max_digits=12, null=True, blank=True
    )
    discount_percentage = models.DecimalField(
        default=0, decimal_places=2, max_digits=12, null=True, blank=True
    )
    price = models.DecimalField(
        default=0, decimal_places=2, max_digits=12, null=True, blank=True
    )
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, null=True, blank=True)
    objects = ProductManager()

    def __str__(self) -> str:
        return self.product_name

    def delete(self, *args, **kwargs):
        if self.cover_image:
            storage, path = self.cover_image.storage, self.cover_image.path
            super(Product, self).delete(*args, **kwargs)
            storage.delete(path)
        super(Product, self).delete(*args, **kwargs)

    def get_product_images(self, request=None):
        images_list = []
        if hasattr(self, "productmedia_set"):
            if request:
                images_list = [
                    request.build_absolute_uri(row.file.url)
                    for row in self.productmedia_set.all()
                ]
            else:
                images_list = [row.file.url for row in self.productmedia_set.all()]

        if self.cover_image:
            images_list.insert(0, self.cover_image.url)
        return images_list

    def save(self, *args, **kwargs) -> None:
        if hasattr(self.category, "productcategorycommission"):
            commission_rate = Decimal(
                self.category.productcategorycommission.commission_rate or 0
            )
            self.commission_rate = commission_rate
        else:
            self.commission_rate = Decimal(0)

        self.price = self.net_price + ((self.net_price / 100) * self.commission_rate)
        self.product_price = self.price
        self.price = self.price - ((self.price / 100) * self.discount_percentage)
        return super().save(*args, **kwargs)


class ProductMedia(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    file = models.FileField(max_length=10000)

    def __str__(self) -> str:
        return self.product.product_name

    def delete(self, *args, **kwargs):
        if self.file:
            storage, path = self.file.storage, self.file.path
            storage.delete(path)

        super(ProductMedia, self).delete(*args, **kwargs)


class ProductVariantAttribute(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    attribute = models.CharField(max_length=999)
    attribute_value = models.CharField(max_length=999)


class ProductCategoryCommission(BaseModel):
    category = models.OneToOneField(Category, on_delete=models.CASCADE)
    commission_rate = models.DecimalField(
        decimal_places=2, max_digits=12, null=True, blank=True, default=0
    )

    def __str__(self) -> str:
        return f"{self.category} --> {self.commission_rate}"


class ProductDiscount(BaseModel):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    discount_percentage = models.DecimalField(
        default=0, decimal_places=2, max_digits=12, null=True, blank=True
    )

    def __str__(self) -> str:
        return self.product.product_name

    def save(self, *args, **kwargs) -> None:
        self.product.discount_percentage = self.discount_percentage
        self.product.save()
        return super().save(*args, **kwargs)

    def delete(self, using: Any = None, keep_parents: bool = False):
        self.product.discount_percentage = 0
        self.product.save()
        return super().delete(using=using, keep_parents=keep_parents)


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
