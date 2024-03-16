from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from django.db.models import Q
from apps.store.models.product import Product, ProductImages, Category
from rest_framework import serializers
from apps.store.serializers import ProductListSerializer
from apps.store.models.order import OrderReview
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from rest_framework.pagination import PageNumberPagination
import json
from decimal import Decimal
from django.core import serializers


class ProductMethods: ...


class ProductsListPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"

    def get_paginated_response(self, data):
        return Response(
            {
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
        )


def get_top_rated_items():
    products_queryset = Product.objects.order_by("rating")[:12]

    if products_queryset:
        return ProductListSerializer(products_queryset).data
    return []


class ProductsApi(ViewSet):
    def search_products(self, request):
        query = request.GET.get("query")
        pagniator = ProductsListPagination()
        filters = {}
        if request.GET.get("filters"):
            try:
                filters = json.loads(request.GET.get("filters"))
            except Exception:
                filters = {}

        if query:
            query = str(query).strip()
            vector = SearchVector("product_name", "description")
            search_query = SearchQuery(query)
            products_queryset = (
                Product.objects.annotate(
                    rank=SearchRank(vector=vector, query=search_query)
                )
                .filter(rank__gte=0.001)
                .order_by("-rank")
            )

            if products_queryset:
                if filters.get("category_id"):
                    category = Category.objects.get(id=filters.get("category_id"))

                    products_queryset = products_queryset.filter(category=category)

                if filters.get("min_price"):
                    products_queryset = products_queryset.filter(
                        price__gte=Decimal(filters.get("min_price"))
                    )

                if filters.get("max_price"):
                    products_queryset = products_queryset.filter(
                        price__lte=Decimal(filters.get("max_price"))
                    )

                products_res = pagniator.paginate_queryset(products_queryset, request)
                products_data = ProductListSerializer(products_res, many=True)
                return pagniator.get_paginated_response(products_data.data)

            return Response(data={"results": [], "message": "No items Found"})
        return Response(data="Please enter a query")

    def get_product_detail(self, request):
        product_id = request.GET.get("id")

        if not product_id:
            return Response(data={"message": "Please give the product"})

        product = self.get_product_object(product_id)
        if not product:
            return Response(data={"message": "Product not found"})

        product_data_object = {
            "product_name": product.product_name,
            "product_price": product.price,
            "formatted_price": "${:0,.0f}".format(product.price),
            "cover_image": product.cover_image,
            "images": self.get_product_images(product),
            "rating": product.rating or 0,
            "category": product.category.name if product.category else None,
            "description": product.description,
            "product_reviews": self.get_product_reviews(product),
        }

        return Response(data=product_data_object)

    def get_product_images(self, product_object):
        query_set = ProductImages.objects.filter(product=product_object)
        images_list = []
        for row in query_set:
            images_list.append(row.image_url)
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
                    "user_image": obj.customer.user.image.url,
                    "review_content": obj.review_content,
                    "rating": obj.rating or 0,
                    "customer_name": obj.customer.customer_name,
                    "created_on": obj.creation.strftime("%d-%m-%Y"),
                }
            )

        return reviews_data


class ProductApi(APIView):
    def get(self, request):
        products = Product.objects.all().order_by("rating")[:36]
        serailized_data = ProductListSerializer(products, many=True)
        return Response(status=200, data=serailized_data.data)

    def create_product(self, request):
        product_object = {
            "product_name": "",
            "price": 0,
            "description": "",
            "stock": 0,
            "disabled": "",
            "category": "",
            "cover_images": "",
        }

        product = Product.objects.create(
            product_name=product_object.get("product_name"),
            net_price=product_object.get("net_price"),
            price=product_object.get("price"),
            description=product_object.get("description"),
            stock=product_object.get("stock"),
            disabled=product_object.get("disabled"),
            category=product_object.get("category"),
            cover_images=product_object.get("cover_images"),
        )
        product.save()
