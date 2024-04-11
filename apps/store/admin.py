from django.contrib import admin
from apps.store.models.base import ModelMedia
from apps.store.models.product import (
    Product,
    ProductMedia,
    ProductVariantAttribute,
)
from apps.store.models.common import Discount, Category
from apps.store.models.customer import Customer, Cart, CartItem
from apps.store.models.order import Order, OrderItems, OrderReview


class ProductImageInline(admin.TabularInline):
    model = ProductMedia


class ProductVariantAttributeInline(admin.TabularInline):
    model = ProductVariantAttribute


class ProductAdmin(admin.ModelAdmin):
    list_filter = ["disabled", "creation"]
    list_display = ["product_name", "price", "item_type", "rating"]
    ordering = ["-modified"]
    inlines = [
        ProductImageInline,
        ProductVariantAttributeInline,
    ]
    search_fields = ["product_name", "id"]


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "id"]


class OrderAdmin(admin.ModelAdmin):
    list_filter = ["payment_status", "order_status"]


admin.site.register(Product, ProductAdmin)
admin.site.register(Discount)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItems)
admin.site.register(Customer)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderReview)
admin.site.register(ModelMedia)
