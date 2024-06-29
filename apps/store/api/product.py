import json
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework import status
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from rest_framework.pagination import PageNumberPagination
from decimal import Decimal
from apps.store.serializers import ProductListSerializer, CategoryListSerializer
from apps.store.models.order import OrderReview
from apps.store.models import (
    Product,
    ProductMedia,
    Category,
    ProductVariantAttribute,
)
from apps.store.utils import get_category, get_serialized_model_media
from server.utils import format_currency, load_request_body


class ProductsListPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"

    def get_paginated_response(self, data, options={}):
        response_dict = {
            "links": {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
            },
            "count": self.page.paginator.count,
            "total_pages": self.page.paginator.num_pages,
            "results": data,
            "page_size": self.page_size,
            "current_page": self.page.number,
        }
        if options:
            response_dict.update(options)
        return Response(response_dict)


class ProductsApi(ViewSet):
    # Product API Methods
    def get_home_page_products(self, request):
        home_sections = ["Just For You", "Explore Digital Products"]
        products_data = {
            "Just For You": Product.objects.list_queryset()[0:24],
            # "Explore Digital Products": Product.objects.list_queryset().filter(
            #     is_digital=True
            # )[0:20],
        }

        for key in products_data.keys():
            products_data[key] = ProductListSerializer(
                products_data.get(key), many=True, context={"request": request}
            ).data

        return Response(
            data={
                "home_products": products_data,
                "digital_products": ProductListSerializer(
                    Product.objects.list_queryset().filter(is_digital=True)[0:20],
                    many=True,
                    context={"request": request},
                ).data,
            }
        )

    def get_product_detail(self, request):
        product_id = request.GET.get("id")
        if not product_id:
            return Response(
                data={"message": "Please give the product"},
                status=status.HTTP_403_FORBIDDEN,
            )

        product = self.get_product_object(product_id)
        if not product:
            return Response(
                data={"message": "Product not found"}, status=status.HTTP_403_FORBIDDEN
            )

        product_images = self.get_product_images(product)
        product_data_object = {
            "id": product.id,
            "product_name": product.product_name,
            "product_price": product.price,
            "formatted_price": format_currency(product.price),
            "cover_image": product.cover_image.url if product.cover_image else None,
            "images": product_images,
            "rating": product.rating or 0,
            "category": product.category.name if product.category else None,
            "description": product.description,
            "product_reviews": self.get_product_reviews(product),
        }

        if product.item_type == "003":
            if product.template:
                product_data_object["product_template"] = product.template.id
                product_data_object["product_varients"] = self.get_product_variants(
                    product.template
                )
            variants_attributes = self.get_variant_attributes(product)
            product_data_object["variants_attributes"] = variants_attributes

        return Response(data=product_data_object)

    def create_product(self, request):
        data: dict = request.data
        validated_product_data, message = self.validate_product_data(data)

        if not validated_product_data:
            return Response(data={"message": message}, status=status.HTTP_403_FORBIDDEN)

        product_object: dict = validated_product_data.get("product_object")
        product_media_object: dict = validated_product_data.get("product_media_object")
        try:
            product = Product.objects.create(**product_object)
            product.save()
            if product:
                for key in product_media_object.get("product_media_keys"):
                    if product_media_object.get(key):
                        media_obj = ProductMedia.objects.create(
                            product=product, file=product_media_object.get(key)
                        )
                        media_obj.save()

                return Response(
                    data={
                        "message": f"Product created {product.id} : {product.product_name}",
                        "product_id": product.id,
                        # "product_media_ids": [
                        #     obj.id
                        #     for obj in ProductMedia.objects.filter(product=product)
                        # ],
                    }
                )
        except Exception as e:
            return Response(data=e)

    def update_product(self, request):
        data: dict = request.data
        validated_product_data, message = self.validate_product_data(data)

        if not validated_product_data:
            return Response(data={"message": message})

        product_object: dict = validated_product_data.get("product_object")
        product_media_object: dict = validated_product_data.get("product_media_object")
        try:
            product = Product.objects.filter(id=data.get("product_id")).update(
                **product_object
            )

            ProductMedia.objects.filter(product=product_object).delete()
            if product:
                for key in product_media_object.get("product_media_keys"):
                    if product_media_object.get(key):
                        media_obj = ProductMedia.objects.create(
                            product=product, file=product_media_object.get(key)
                        )
                        media_obj.save()

                return Response(
                    data={
                        "message": f"Product successfully updated",
                        # "product_id": product.id,
                    }
                )
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_403_FORBIDDEN)

    # Product Utility Methods
    def validate_product_data(self, data: dict):
        mandatory_fields = [
            "product_name",
            "price",
            "category_id",
            # "description",
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
        }

        product_media_object = {
            "product_media_keys": list(filter(filter_product_media_keys, data.keys())),
        }

        for key in product_media_object.get("product_media_keys"):
            if data.get(key):
                product_media_object[key] = data.get(key)

        return {
            "product_object": product_object,
            "product_media_object": product_media_object,
        }, ""

    def get_product_images(self, product_object):
        query_set = ProductMedia.objects.filter(product=product_object)
        images_list = [
            self.request.build_absolute_uri(row.file.url) for row in query_set
        ]
        if product_object.cover_image:
            images_list.insert(
                0, self.request.build_absolute_uri(product_object.cover_image.url)
            )
        return images_list

    def get_product_object(self, id):
        try:
            product = Product.objects.get(id=id)
            return product

        except Product.DoesNotExist:
            return None

    def get_product_reviews(self, product_object):
        product_reviews = OrderReview.objects.filter(product=product_object)
        reviews_data = []

        for obj in product_reviews:
            reviews_data.append(
                {
                    "user_image": (
                        obj.customer.user.image.url if obj.customer.user.image else None
                    ),
                    "review_content": obj.review_content,
                    "rating": obj.rating or 0,
                    "customer_name": obj.customer.customer_name,
                    "created_on": obj.creation.strftime("%B %d, %Y"),
                    "images": get_serialized_model_media(
                        "OrderReview", obj.id, self.request
                    ),
                }
            )

        return reviews_data

    def get_product_variants(self, product_object):
        product_varients = Product.objects.filter(template=product_object)
        varients_data = []
        if product_varients:
            for variant in product_varients:
                varients_data.append(
                    {
                        "id": variant.id,
                        "product_name": variant.product_name,
                        "cover_image": self.request.build_absolute_uri(
                            variant.cover_image.url if variant.cover_image else None
                        ),
                        "price": variant.price,
                        "rating": variant.rating,
                    }
                )
        return varients_data

    def get_variant_attributes(self, varient_object):
        attributes = []
        variant_attr_object = ProductVariantAttribute.objects.filter(
            product=varient_object
        )

        if variant_attr_object:
            for attr in variant_attr_object.iterator():
                attributes.append(
                    {
                        "attribute": attr.attribute,
                        "attribute_value": attr.attribute_value,
                    }
                )

        return attributes


class ProductCategory(ViewSet):
    def get_categories(self, request):
        physical = Category.objects.filter(digital=False)[:12]
        digital = Category.objects.filter(digital=True)[:12]

        category_data = {
            "physical": CategoryListSerializer(
                physical, many=True, context={"request": request}
            ).data,
            "digital": CategoryListSerializer(
                digital, many=True, context={"request": request}
            ).data,
        }
        return Response(data={"categories": category_data})


class ProductAPIViewSet(ViewSet):
    def create_product(self, request):
        req_data = load_request_body(request.data)
        
