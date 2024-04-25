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
    Category,
)


class ERPNextProductsApi(ViewSet):
    def sync_product(self, request):
        data: dict = request.data
        validated_product_data, message = self.validate_product_data(data)

        if not validated_product_data:
            return Response(data={"message": message}, status=status.HTTP_403_FORBIDDEN)

        product_object: dict = validated_product_data.get("product_object")
        product_media_object: dict = validated_product_data.get("product_media_object")
        product_id = validated_product_data.get("product_id")
        variants_object = None
        if validated_product_data.get("variants_object"):
            variants_object: list = json.loads(
                validated_product_data.get("variants_object")
            )

        product = None
        if product_id:
            Product.objects.filter(id=product_id).update(**product_object)
            product = Product.objects.get(id=product_id)
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

        if product:
            if product.item_type == "003":
                ProductVariantAttribute.objects.filter(product=product).delete()
                if variants_object:
                    for object in variants_object:
                        ProductVariantAttribute.objects.create(
                            product=product,
                            attribute=object.get("attribute"),
                            attribute_value=object.get("attribute_value"),
                        )

        return Response(
            data={
                "message": f"Product sync successfully!",
                "product_id": product.id,
                "product_name": product.product_name,
            }
        )

    def validate_product_data(self, data: dict):
        product_object = {}

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
                "product_id": data.get("product_id"),
            }, None

        mandatory_fields = [
            "product_name",
            "price",
            "category_id",
            "cover_image",
            "is_digital",
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
            "description": data.get("description") or data.get("product_name"),
            "price": Decimal(data.get("price")),
            "cover_image": data.get("cover_image"),
            "stock": data.get("stock"),
            "category": get_category(data.get("category_id")),
            "item_type": data.get("item_type"),
            "is_digital": data.get("is_digital"),
        }

        if data.get("product_id") and data.get("item_type") == "003":
            product_object["template"] = Product.objects.get(id=data.get("template_id"))

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
            "product_id": data.get("product_id"),
        }, None

    def remove_product(self, request):
        product_id = request.data.get("product_id")
        if not product_id:
            return Response(
                data={"message": "Please provide product id"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            product = Product.objects.get(id=product_id)
            if product.item_type == "002":
                products_variant = Product.objects.filter(template=product)
                if products_variant:
                    products_variant.delete()

            product.delete()

            return Response(
                data={
                    "message": "Product deleted",
                },
                status=status.HTTP_200_OK,
            )
        except Product.DoesNotExist:
            return Response(
                data={
                    "message": "Product not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )


class ERPNextItemGroupsApi(ViewSet):
    def sync_category(self, request):
        validated_data = self.validate_category_object(request.data)
        if not validated_data.get("category_object"):
            return Response(
                data={"message": validated_data.get("message")},
                status=status.HTTP_403_FORBIDDEN,
            )

        category_object = validated_data.get("category_object")
        category_id = validated_data.get("category_id")

        try:
            if category_id:
                if category_object.get("image") is None:
                    category = Category.objects.get(id=category_id)
                    category.image.delete()

                category, created = Category.objects.update_or_create(
                    id=category_id, defaults=category_object
                )
            else:
                category = Category.objects.create(**category_object)

            if category:
                return Response(
                    data={
                        "message": "Category synced successfully!",
                        "category_id": category.id,
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            return Response(data={"message": e}, status=status.HTTP_403_FORBIDDEN)

    def validate_category_object(self, data: dict):
        if not data.get("name"):
            return {"message": "Please provide category name"}

        category_object = {
            "name": data.get("name"),
            "digital": bool(data.get("digital")),
        }
        category_object["image"] = data.get("image")
        if data.get("parent"):
            category_object["parent"] = Category.objects.get(id=data.get("parent"))
        else:
            category_object["parent"] = None

        return {
            "message": "Validated",
            "category_object": category_object,
            "category_id": data.get("category_id"),
        }

    def remove_category(self, request):
        category_id = request.data.get("category_id")
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                category.delete()
                return Response(
                    data={"message": "Category removed successfully"},
                    status=status.HTTP_200_OK,
                )
            except Category.DoesNotExist:
                return Response(
                    data={"message": "No category found with this id"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                data={"message": "Please provide category id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
