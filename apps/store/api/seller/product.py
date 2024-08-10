import json
from rest_framework import views
from typing import List, Dict
from datetime import datetime
from django.db.models.query import QuerySet
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ...permissions import IsSellerUser
from ...utils import get_session_seller
from ...pagination import ProductsListPagination
from ...models import Product, Category
from ...serializers import (
    SellerProductListingSerializer,
    CategoryListSerializer,
    TemplateListSerializer,
)


@api_view(["GET"])
def get_upload_product_data(request):
    templates_querysets = Product.objects.filter(disabled=False, item_type="002")
    catergory = Category.objects.all()
    catergory_serializer = CategoryListSerializer(catergory, many=True)
    template_serializer = TemplateListSerializer(templates_querysets, many=True)

    return Response(
        data={
            "templates": template_serializer.data,
            "catergory": catergory_serializer.data,
        }
    )


class ListSellerProducts(views.APIView):
    # serializer = SellerProductListingSerializer()

    def validate_search_filters(self, filters: dict) -> dict:
        q_filters = {}
        if filters.get("item_type"):
            q_filters["item_type"] = filters.get("item_type")

        if filters.get("search_query"):
            q_filters["product_name__icontains"] = filters.get("search_query")

        if filters.get("disabled"):
            q_filters["disabled"] = bool(int(filters.get("disabled")))

        if filters.get("creation"):
            q_filters["creation__date"] = datetime.strptime(
                filters.get("creation"), "%Y-%m-%d"
            )

        return q_filters

    def get_variants_queryset(self, template):
        variants_queryset = Product.objects.select_related("category").filter(
            template__id=template
        )
        serializer = SellerProductListingSerializer(
            variants_queryset, many=True, context={"request": self.request}
        )
        return serializer.data

    def group_by_variances(self, data: List[Dict]) -> List[Dict]:
        for product in data:
            if product.get("item_type") == "002":
                product["variants"] = self.get_variants_queryset(product.get("id"))

        return data

    def get(self, request):
        seller = get_session_seller(request.user.id)
        if request.GET.get("id"):
            product_queryset = Product.objects.select_related("category").get(
                id=request.GET.get("id")
            )
            product_dict = {
                "id": product_queryset.id,
                "product_name": product_queryset.product_name,
                "item_type": product_queryset.item_type,
                "category": (
                    product_queryset.category.id if product_queryset.category else None
                ),
                "category_name": (
                    product_queryset.category.name
                    if product_queryset.category
                    else None
                ),
            }
            if product_queryset.item_type != "002":
                product_media = product_queryset.get_product_images(request) or []
                if product_media:
                    product_media.pop(0)

                product_dict.update(
                    {
                        "cover_image": (
                            request.build_absolute_uri(product_queryset.cover_image.url)
                            if product_queryset.cover_image
                            else None
                        ),
                        "description": product_queryset.description,
                        "net_price": product_queryset.net_price,
                        "disabled": product_queryset.disabled,
                        "is_digital": product_queryset.is_digital,
                        "rating": product_queryset.rating,
                        "stock": product_queryset.stock,
                        "images": product_media,
                    }
                )
            if product_queryset.item_type == "003":
                variants_attributes = []
                for row in product_queryset.productvariantattribute_set.all():
                    variants_attributes.append(
                        {
                            "attribute": row.attribute,
                            "attribute_value": row.attribute_value,
                        }
                    )
                if product_queryset.template:
                    product_dict["template"] = product_queryset.template.id
                    product_dict["template_name"] = (
                        product_queryset.template.product_name
                    )

                product_dict["variants_attributes"] = variants_attributes

            return Response(data=product_dict)

        else:
            pagination = ProductsListPagination()
            search_filter = request.GET.get("filters") or {}
            if search_filter:
                search_filter: dict = json.loads(search_filter)

            queryset_filters = self.validate_search_filters(search_filter)
            queryset = (
                Product.objects.select_related("category")
                .filter(seller=seller)
                .filter(**queryset_filters)
                .exclude(item_type="003")
            )

            paginated_queryset = pagination.paginate_queryset(queryset, request)
            serialized_data = SellerProductListingSerializer(
                paginated_queryset, many=True, context={"request": request}
            )
            products_data = serialized_data.data
            products_data = self.group_by_variances(products_data)
            return pagination.get_paginated_response(products_data)
