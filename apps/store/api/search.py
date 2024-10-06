from decimal import Decimal
from django.http import HttpRequest
from django.db import models
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from apps.store.serializers import ProductListSerializer
from apps.store.models.product import (
    Product,
    ProductVariantAttribute,
)
from apps.store.pagination import ProductsListPagination
from server.utils import parse_json


class SearchProductsApi(APIView):
    def get(self, request: HttpRequest):
        query = request.GET.get("query")
        category_id = request.GET.get("category")
        filters = parse_json(request.GET.get("filters", {}))
        products_queryset: models.QuerySet[Product] = None
        pagniator = ProductsListPagination()

        if not query and not category_id:
            return Response(data="Please enter a query or category id")
        if query:
            query = str(query).strip()
            vector = SearchVector("product_name")
            search_query = SearchQuery(query)
            products_queryset = (
                Product.objects.list_queryset()
                .prefetch_related("category")
                .annotate(rank=SearchRank(vector=vector, query=search_query))
                .filter(rank__gte=0.001)
                .order_by("-rank")
            )

        elif category_id:
            products_queryset = (
                Product.objects.list_queryset()
                .prefetch_related("category")
                .filter(category__id=category_id)
            )

        if products_queryset:
            products_queryset = products_queryset.order_by("-rating")
            filters_attributes = self.get_search_product_attributes(products_queryset)
            attributes_filter: dict = filters.get("attributes")
            if attributes_filter:
                for key, values in attributes_filter.items():
                    if key and values:
                        products_queryset = products_queryset.filter(
                            productvariantattribute__attribute=key,
                            productvariantattribute__attribute_value__in=values,
                        )

            if filters.get("category_id"):
                products_queryset = products_queryset.filter(
                    category__id=filters.get("category_id")
                )

            if filters.get("min_price"):
                products_queryset = products_queryset.filter(
                    price__gte=Decimal(filters.get("min_price"))
                )

            if filters.get("max_price"):
                products_queryset = products_queryset.filter(
                    price__lte=Decimal(filters.get("max_price"))
                )
            if filters.get("rating"):
                products_queryset = products_queryset.filter(
                    price__gte=Decimal(filters.get("rating"))
                )

            if products_queryset:
                products_res = pagniator.paginate_queryset(products_queryset, request)
                products_data = ProductListSerializer(
                    products_res, many=True, context={"request": request}
                )

                return pagniator.get_paginated_response(
                    products_data.data, {"filters_attributes": filters_attributes}
                )

        return Response(data={"results": [], "message": "No items Found"})

    def get_search_product_attributes(self, products_queryset):
        variant_queryset = ProductVariantAttribute.objects.filter(
            product__in=products_queryset
        )
        attribute_object = {}
        serialized_variant_queryset = []

        for attr in variant_queryset:
            serialized_variant_queryset.append(
                {
                    "attribute": attr.attribute,
                    "attribute_value": attr.attribute_value,
                }
            )

        for dict in serialized_variant_queryset:
            if dict.get("attribute") in attribute_object:
                attribute_object[dict.get("attribute")].add(dict.get("attribute_value"))
            else:
                attribute_object[dict.get("attribute")] = {dict.get("attribute_value")}
        return attribute_object
