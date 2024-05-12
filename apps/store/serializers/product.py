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


class CategoryListSerializer(serializers.ModelSerializer):
    # image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "image"]

    def get_image(self, object):
        if self.context.get("request") and object.image:
            return self.context.get("request").build_absolute_uri(object.image.url)

        return object.image.url or None
