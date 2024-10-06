import json
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework import status
from django.http.request import QueryDict
from django.db import models
from rest_framework.pagination import PageNumberPagination
from decimal import Decimal
from apps.store.serializers import ProductListSerializer, CategoryListSerializer
from apps.store.models.order import OrderReview
from apps.store.models.product import Product, ProductMedia, ProductVariantAttribute
from apps.store.models import Category
from apps.store.utils import (
    get_category,
    get_serialized_model_media,
    get_session_seller,
)
from server.utils import format_currency, load_request_body
from rest_framework import serializers


class ProductMutilMediaSerializerField(serializers.ListField):
    child = serializers.FileField()


class ProductMediaSerializer(serializers.Serializer):
    file = ProductMutilMediaSerializerField()


class VariantAttributeSerializer(serializers.Serializer):
    attribute = serializers.CharField(max_length=50)
    attribute_value = serializers.CharField(max_length=50)


class ProductTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["category", "product_name", "seller", "item_type"]

    def create(self, validated_data: dict) -> Product:
        validated_data["item_type"] = "002"
        product = Product.objects.create(**validated_data)
        return product

    def update(self, instance, validated_data: dict) -> Product:
        to_remove_fields = ["item_type", "seller"]
        for field in to_remove_fields:
            if field in validated_data.keys():
                del validated_data["seller"]

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ProductSerializer(serializers.ModelSerializer):
    product_media = serializers.ListField(
        child=serializers.ImageField(), required=False
    )
    variant_attributes = serializers.ListField(
        child=VariantAttributeSerializer(), required=False
    )

    class Meta:
        model = Product
        fields = [
            "cover_image",
            "product_name",
            "item_type",
            "description",
            "category",
            "template",
            "stock",
            "disabled",
            "is_digital",
            "net_price",
            "discount_percentage",
            "product_media",
            "seller",
            "variant_attributes",
        ]

    def create(self, validated_data: dict):
        product_media = validated_data.pop("product_media", [])
        variant_attributes = validated_data.pop("variant_attributes", [])
        product = Product.objects.create(**validated_data)
        if product_media:
            for file in product_media:
                ProductMedia.objects.create(file=file, product=product)

        if variant_attributes:
            for attr in variant_attributes:
                ProductVariantAttribute.objects.create(
                    product=product,
                    attribute=attr.get("attribute"),
                    attribute_value=attr.get("attribute_value"),
                )
        return product


class ProductAPIView(APIView):
    def post(self, request):
        body = load_request_body(request.data)
        validated_data = body
        category_object = Category.objects.get(id=validated_data.get("category"))

        seller_queryset = get_session_seller(request.user.id)
        validated_data["category"] = category_object.id
        validated_data["seller"] = seller_queryset.id

        if validated_data.get("item_type") == "003":
            validated_data["variant_attributes"] = json.loads(
                body.get("variant_attributes")
            )

        if validated_data.get("item_type") == "002":
            serialized_data = ProductTemplateSerializer(data=validated_data)
        else:
            serialized_data = ProductSerializer(data=validated_data)

        if serialized_data.is_valid():
            serialized_data.save()
            return Response(
                data="Product created successfully!", status=status.HTTP_201_CREATED
            )

        return Response(data=serialized_data.errors, status=status.HTTP_403_FORBIDDEN)

    def put(self, request):
        try:
            # product_data = load_request_body(request.data)
            product_data: QueryDict = request.data
            product_queryset = Product.objects.get(id=product_data.get("id"))
            updated_dict = {
                "product_name": product_data.get("product_name"),
                "category": Category.objects.get(id=product_data.get("category")),
                "item_type": product_data.get("item_type"),
            }

            if product_queryset.item_type == "002":
                serialized_data = ProductTemplateSerializer(
                    product_queryset, data=updated_dict, partial=True
                )
                if serialized_data.is_valid():
                    serialized_data.save()
            else:
                if product_data.get("cover_image"):
                    updated_dict["cover_image"] = product_data.get("cover_image")

                if product_queryset.item_type != "002":
                    updated_dict.update(
                        {
                            "description": product_data.get("description"),
                            "stock": product_data.get("stock"),
                            "disabled": json.loads(
                                product_data.get("disabled") or "false"
                            ),
                            "is_digital": json.loads(
                                product_data.get("is_digital") or "false"
                            ),
                            "net_price": Decimal(product_data.get("net_price") or 0),
                        }
                    )

                if product_data.get("item_type") == "003":
                    updated_dict["template_id"] = product_data.get("template")
                    variant_attributes = json.loads(
                        product_data.get("variant_attributes")
                    )
                    ProductVariantAttribute.objects.filter(
                        product=product_queryset
                    ).delete()
                    for attr in variant_attributes:
                        ProductVariantAttribute.objects.create(
                            product=product_queryset, **attr
                        )

                for key in updated_dict.keys():
                    setattr(product_queryset, key, updated_dict[key])

                product_queryset.save()

                if product_data.get("item_type") != "002":
                    ntd_files = []
                    request_files = request.FILES
                    media_files = request_files.getlist("product_media")
                    if media_files:
                        for file in media_files:
                            media_object = ProductMedia.objects.create(
                                product=product_queryset, file=file
                            )
                            ntd_files.append(media_object.file.url)

                    current_media_file = product_data.getlist("product_media")

                    for url in current_media_file:
                        if isinstance(url, str):
                            ntd_files.append("/media/" + url.split("/media/")[-1])

                    current_media_querysets = ProductMedia.objects.filter(
                        product=product_queryset
                    )
                    for fq in current_media_querysets:
                        if fq.file.url not in ntd_files:
                            fq.delete()

            return Response(
                data="Product updated successfully!",
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                data=str(e),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


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
    def get_home_page_products(self, request):
        products_queryset = (
            Product.objects.list_queryset()
            .select_related("category")
            .filter(is_digital=True)
            .order_by("-rating", "?")[:24]
        )

        serialized_data = ProductListSerializer(
            products_queryset, many=True, context={"request": request}
        )

        products2 = ProductListSerializer(
            Product.objects.list_queryset()
            .select_related("category")
            .filter(is_digital=True)
            .order_by("-rating", "?")[:24],
            many=True,
            context={"request": request},
        )

        return Response(
            data={
                "digital_products": serialized_data.data,
                "home_products": products2.data,
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
            "is_digital": product.is_digital,
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
            product = Product.objects.prefetch_related("category").get(id=id)
            return product

        except Product.DoesNotExist:
            return None

    def get_product_reviews(self, product_object):
        product_reviews = OrderReview.objects.prefetch_related("customer").filter(
            product=product_object
        )
        reviews_data = []

        for obj in product_reviews:
            reviews_data.append(
                {
                    # "user_image": (
                    #     obj.customer.user.image.url if obj.customer.user.image else None
                    # ),
                    "user_image": None,
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
        physical_order = [
            "Cosmetics",
            "Jewelry",
            "Dogs & Pets",
            "Cameras",
            "Household Items",
            "Gadgets",
            "Computers",
            "Watches",
            "Women's shoes",
            "Men's Clothes",
            "Headphones",
        ]

        digital_order = [
            "Apps",
            "HTML Template",
            "Course",
            "Word Press Plugin",
            "Software Programs",
            "Photography",
            "Recipes",
            "Music",
            "eBooks",
            "Graphics",
            "Coaching",
            "Arts & Crafts",
        ]

        # physical = Category.objects.filter(digital=False).order_by(
        #     models.Case(
        #         *[
        #             models.When(name=name, then=pos)
        #             for pos, name in enumerate(physical_order)
        #         ]
        #     )
        # )[:12]
        physical = Category.objects.filter(digital=True).exclude(
            name__in=digital_order
        )[:12]

        # physical = Category.objects.filter(digital=False)[:12]
        digital = Category.objects.filter(digital=True).order_by(
            models.Case(
                *[
                    models.When(name=name, then=pos)
                    for pos, name in enumerate(digital_order)
                ]
            )
        )[:12]

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
