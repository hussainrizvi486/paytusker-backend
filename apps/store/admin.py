from django.contrib import admin
from apps.store.models.product import (
    Product,
    ProductMedia,
    ProductVariantAttribute,
    ProductAttribute,
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


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductAttribute)
admin.site.register(Discount)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItems)
admin.site.register(Customer)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderReview)
