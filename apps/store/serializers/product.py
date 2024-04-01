from rest_framework import serializers
from apps.store.models import Product
from server.utils import format_currency


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField(method_name="get_category_name")
    cover_image = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "cover_image",
            "rating",
            "price",
            "product_name",
            "category_name",
        ]

    def get_category_name(self, object):
        if object.category:
            return object.category.name
        return None

    def get_cover_image(self, object):
        request = self.context.get("request")
        if object.cover_image:
            return request.build_absolute_uri(object.cover_image.url)

    def get_price(self, object):
        return format_currency(object.price or 0)
