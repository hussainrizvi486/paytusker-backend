from django.contrib import admin
from apps.store.models.orders import (
    SellerDigitalOrder,
    SellerDigitalOrderItem,
    SellerOrder,
    SellerOrderItem,
)
from apps.store.models.product import (
    Product,
    ProductMedia,
    ProductVariantAttribute,
    ProductCategoryCommission,
    ProductDiscount,
)
from apps.store.models.order import DigitalOrder, DigitalOrderItem, OrderCancellation
from apps.store.models import (
    PaymentEntry,
    Seller,
    Category,
    UserAddress,
    ModelMedia,
    Customer,
    Cart,
    CartItem,
)


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
    list_display = ["product_name", "is_digital", "price", "item_type", "rating"]
    ordering = ["-modified"]
    inlines = [
        ProductImageInline,
        ProductVariantAttributeInline,
    ]
    search_fields = ["product_name", "id"]


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "id"]


class OrderAdmin(BaseModelAdmin):
    class OrderItemInline(admin.TabularInline):
        model = OrderItems

    list_filter = ["payment_status", "order_status"]
    list_display = ["order_id", "grand_total", "order_status", "order_date"]
    inlines = [OrderItemInline]


@admin.register(DigitalOrder)
class DigitalOrderAdmin(BaseModelAdmin):
    class ItemInline(admin.TabularInline):
        model = DigitalOrderItem

    inlines = [ItemInline]


class SellerOrderAdmin(BaseModelAdmin):
    class ItemsInline(admin.TabularInline):
        model = SellerOrderItem

    list_display = [
        "grand_total",
        "status",
        "order_date",
        "customer",
        "seller",
    ]
    inlines = [ItemsInline]


class DigitalOrderAdmin(BaseModelAdmin):
    class ItemsInline(admin.TabularInline):
        model = SellerDigitalOrderItem

    list_display = [
        "grand_total",
        "status",
        "order_date",
        "customer",
        "seller",
    ]
    inlines = [ItemsInline]


admin.site.register(SellerDigitalOrder, DigitalOrderAdmin)

admin.site.register(SellerOrder, SellerOrderAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(PaymentEntry)

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductDiscount)
admin.site.register(OrderCancellation)
admin.site.register(ProductCategoryCommission)
admin.site.register(Category, CategoryAdmin)
admin.site.register(OrderItems)
admin.site.register(Customer, BaseModelAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderReview)
admin.site.register(ModelMedia)
admin.site.register(Seller)
admin.site.register(UserAddress)
