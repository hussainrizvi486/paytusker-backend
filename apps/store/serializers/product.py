from rest_framework import serializers
from apps.store.models import Product


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField(method_name="get_category_name")

    class Meta:
        model = Product
        fields = ["cover_image", "rating", "price", "product_name", "category_name"]

    def get_category_name(self, object):
        if object.category:
            return object.category.name

        return None
