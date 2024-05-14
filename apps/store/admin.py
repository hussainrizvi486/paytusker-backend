from django.contrib import admin
from apps.store.models.base import ModelMedia, StoreErrorLogs
from apps.store.models.product import (
    Product,
    ProductMedia,
    ProductVariantAttribute,
    ProductCategoryCommission,
    ProductDiscount,
)
from apps.store.models.common import Category
from apps.store.models.customer import Customer, Cart, CartItem
from apps.store.models.order import Order, OrderItems, OrderReview


admin.site.site_header = "Paytukser Core Administration"


class BaseModelAdmin(admin.ModelAdmin):
    ordering = ["-modified"]


class ProductImageInline(admin.TabularInline):
    model = ProductMedia


class ProductVariantAttributeInline(admin.TabularInline):
    model = ProductVariantAttribute


class ProductAdmin(admin.ModelAdmin):
    list_filter = ["disabled", "creation", "category"]
    list_display = ["product_name", "price", "item_type", "rating"]
    ordering = ["-modified"]
    inlines = [
        ProductImageInline,
        ProductVariantAttributeInline,
    ]
    search_fields = ["product_name", "id"]


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "id"]


class OrderItemInline(admin.TabularInline):
    model = OrderItems


class OrderAdmin(BaseModelAdmin):
    list_filter = ["payment_status", "order_status"]
    list_display = ["order_id", "grand_total", "order_status", "order_date"]
    inlines = [OrderItemInline]


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductDiscount)
admin.site.register(ProductCategoryCommission)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItems)
admin.site.register(Customer, BaseModelAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderReview)
admin.site.register(ModelMedia)
admin.site.register(StoreErrorLogs)
