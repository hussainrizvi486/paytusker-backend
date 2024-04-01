import json
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework import status
from decimal import Decimal
from apps.store.utils import get_category
from apps.store.models.product import (
    Product,
    ProductMedia,
    ProductVariantAttribute,
)


class ERPNextProductsApi(ViewSet):
    def sync_product(self, request):
        data: dict = request.data
        validated_product_data, message = self.validate_product_data(data)

        if not validated_product_data:
            return Response(data={"message": message}, status=status.HTTP_403_FORBIDDEN)

        product_object: dict = validated_product_data.get("product_object")
        product_media_object: dict = validated_product_data.get("product_media_object")
        variants_object: list = json.loads(
            validated_product_data.get("variants_object")
        )
        product = None
        for i in variants_object:
            print(i)

        if product_object.get("server_id"):
            product = Product.objects.get(id=product_object.get("server_id"))
            ProductMedia.objects.filter(product=product).delete()
        else:
            try:
                product = Product.objects.create(**product_object)
                product.save()
            except Exception as e:
                return Response(data=e)

        if product and product_media_object.get("product_media_keys"):
            for key in product_media_object.get("product_media_keys"):
                if product_media_object.get(key):
                    media_obj = ProductMedia.objects.create(
                        product=product, file=product_media_object.get(key)
                    )
                    media_obj.save()

        if product and product.item_type == "003":
            ProductVariantAttribute.objects.filter(product=product).delete()
            for object in variants_object:
                ProductVariantAttribute.objects.create(
                    product=product,
                    attribute=object.get("attribute"),
                    attribute_value=object.get("attribute_value"),
                )

        return Response(
            data={
                "message": f"Product created {product.id} : {product.product_name}",
                "product_id": product.id,
            }
        )

    def validate_product_data(self, data: dict):
        if data.get("item_type") == "002":
            mandatory_fields = [
                "product_name",
                "category_id",
            ]

            if data.get("item_type") == "003":
                mandatory_fields.append("template_id")
                mandatory_fields.append("variant_attributes")

            for field in mandatory_fields:
                if field not in data.keys():
                    return None, f"Missing required field: {field}"

                if data.get("item_type") == "003" and not data.get("template_id"):
                    return None, f"Item template missing"

            product_object = {
                "product_name": data.get("product_name"),
                "category": get_category(data.get("category_id")),
                "item_type": data.get("item_type"),
            }

            return {
                "product_object": product_object,
                "product_media_object": {},
            }, None

        mandatory_fields = [
            "product_name",
            "price",
            "category_id",
            "cover_image",
            "stock",
        ]

        for field in mandatory_fields:
            if field not in data.keys():
                return None, f"Missing required field: {field}"

            if data.get("item_type") == "003" and not data.get("template_id"):
                return None, f"Item template missing"

        def filter_product_media_keys(key):
            if str(key).startswith("product_media"):
                return True
            return False

        product_object = {
            "product_name": data.get("product_name"),
            "description": data.get("description"),
            "price": Decimal(data.get("price")),
            "cover_image": data.get("cover_image"),
            "stock": data.get("stock"),
            "category": get_category(data.get("category_id")),
            "item_type": data.get("item_type"),
        }

        variants_object = data.get("variant_attributes")

        product_media_object = {
            "product_media_keys": list(filter(filter_product_media_keys, data.keys())),
        }

        for key in product_media_object.get("product_media_keys"):
            if data.get(key):
                product_media_object[key] = data.get(key)

        return {
            "product_object": product_object,
            "product_media_object": product_media_object,
            "variants_object": variants_object,
        }, None
