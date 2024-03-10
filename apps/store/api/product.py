from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from django.db.models import Q
from apps.store.models.product import Product, ProductImages, Category
from rest_framework import serializers
from apps.store.serializers import ProductListSerializer
from apps.store.models.order import OrderItems
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from rest_framework.pagination import PageNumberPagination
import json
from decimal import Decimal


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

    def get_product_object(self, id):
        try:
            product = Product.objects.get(id=id)
            return product
        except Product.DoesNotExist:
            return None


class ProductDetail(APIView):
    def get(self, request, product_id):
        data = {}
        product = get_object_or_404(Product, id=product_id)
        if product:
            data = dict(Product.objects.values().filter(id=product_id)[0])
            pi = list(
                ProductImages.objects.values("image_url").filter(product=product_id)
            )

            images = []
            if pi:
                for image in pi:
                    images.append(image.get("image_url"))

            images.insert(0, data.get("cover_image"))
            data["images"] = images

            product_category = Category.objects.filter(
                id=data.get("category_id")
            ).first()

            if product_category:
                data["category"] = product_category
            from server.utils import exceute_sql_query

            reviews_query = f""" SELECT r.* , c.customer_name, c.user_id FROM store_orderreview r
              INNER JOIN store_customer c on r.customer_id = c.id"""
            reviews = exceute_sql_query(reviews_query)
            from apps.accounts.models import User

            for r in reviews:
                r_user = User.objects.get(id=r.get("user_id"))
                r["customer_image"] = r_user.image.url

            data["reviews"] = reviews
        return Response(status=200, data=data)


class ProductApi(APIView):
    def get(self, request):
        products = Product.objects.values(
            "id", "product_name", "price", "cover_image", "category"
        )[:36]

        return Response(status=200, data=products)

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
