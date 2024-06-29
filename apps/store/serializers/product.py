from rest_framework import serializers
from apps.store.models import Product, Category
from server.utils import format_currency


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField(method_name="get_category_name")
    cover_image = serializers.SerializerMethodField()
    is_discounted = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "cover_image",
            "rating",
            "price",
            "product_name",
            "product_price",
            "discount_percentage",
            "is_discounted",
            "category_name",
        ]

    def get_is_discounted(self, object):
        if object.discount_percentage > 0:
            return True
        return False

    def get_category_name(self, object):
        if object.category:
            return object.category.name
        return None

    def get_cover_image(self, object):
        if object.cover_image:
            if self.context.get("request"):
                request = self.context.get("request")
                return request.build_absolute_uri(object.cover_image.url)
            return object.cover_image.url

    def get_price(self, object):
        return format_currency(object.price or 0)


class AmendProductSerailizer(serializers.ModelSerializer):
    class Meta:
        model = Product


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "image"]

    def get_image(self, obj):
        request = self.context.get("request")
        if request and obj.image:
            return request.build_absolute_uri(obj.image.url)

        return obj.image.url or None


class SellerProductListingSerializer(serializers.ModelSerializer):
    category = CategoryListSerializer()

    class Meta:
        model = Product
        fields = [
            "id",
            "cover_image",
            "product_name",
            "category",
            "net_price",
            "stock",
            "disabled",
            "is_digital",
            "item_type",
        ]

    def get_cover_image(self, obj):
        request = self.context.get("request")
        if request and obj.cover_image:
            return request.build_absolute_uri(obj.cover_image.url)
