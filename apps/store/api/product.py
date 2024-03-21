import json
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from rest_framework.pagination import PageNumberPagination
from decimal import Decimal
from apps.store.serializers import ProductListSerializer
from apps.store.models.order import OrderReview
from apps.store.models.product import (
    Product,
    ProductMedia,
    Category,
    ProductVariantAttribute,
)
from apps.store.utils import get_category


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
                .exclude(item_type="002")
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
                products_data = ProductListSerializer(
                    products_res, many=True, context={"request": request}
                )
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

        product_images = self.get_product_images(product)
        product_data_object = {
            "id": product.id,
            "product_name": product.product_name,
            "product_price": product.price,
            "formatted_price": "${:0,.0f}".format(product.price),
            "cover_image": product.cover_image.url,
            "images": product_images,
            "rating": product.rating or 0,
            "category": product.category.name if product.category else None,
            "description": product.description,
            "product_reviews": self.get_product_reviews(product),
        }

        if product.item_type == "003":
            product_varients = self.get_product_variants(product.template)
            # for i in product_varients:
            #     for attr in in
            product_data_object["product_template"] = product.template.id
            product_data_object["product_varients"] = product_varients

        return Response(data=product_data_object)

    def create_product(self, request):
        data: dict = request.data
        item_category = None
        item_type = data.get("item_type")

        mandatory_fields = [
            "product_name",
            "price",
            "net_price",
            "category_id",
            "description",
            "cover_image",
            "stock",
        ]
        for field in mandatory_fields:
            if field not in data.keys():
                return Response(data=f"Missing required field: {field}")

        if data.get("category_id"):
            item_category = get_category(category_id=data.get("category_id"))

        elif data.get("category_name"):
            item_category = get_category(category_name=data.get("category_name"))

        product_object = {
            "product_name": data.get("product_name"),
            "price": Decimal(data.get("price") or 0),
            "net_price": Decimal(data.get("price") or 0),
            "category": item_category,
            "description": data.get("description") or "",
            "stock": data.get("stock"),
        }

        if data.get("cover_image"):
            product_object["cover_image"] = data.get("cover_image")

        if item_type == "003":
            product_object["template"] = self.get_product_object(
                data.get("template_id")
            )

        try:
            product = Product.objects.create(**product_object)
            product.save()

            def filter_product_media_keys(key):
                if str(key).startswith("product_media"):
                    return True
                return False

            product_file_keys = list(filter(filter_product_media_keys, data.keys()))

            for key in product_file_keys:
                product_media_object = ProductMedia.objects.create(
                    product=product, file=data.get(key)
                )
                product_media_object.save()

            return Response(
                data=f"Product created {product.id} : {product.product_name} "
            )
        except Exception as e:
            return Response(data=e)

    def get_product_images(self, product_object):
        query_set = ProductMedia.objects.filter(product=product_object)
        images_list = [
            self.request.build_absolute_uri(row.file.url) for row in query_set
        ]
        images_list.append(
            self.request.build_absolute_uri(product_object.cover_image.url)
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
                    "user_image": obj.customer.user.image.url,
                    "review_content": obj.review_content,
                    "rating": obj.rating or 0,
                    "customer_name": obj.customer.customer_name,
                    "created_on": obj.creation.strftime("%d-%m-%Y"),
                }
            )

        return reviews_data

    def get_product_variants(self, product_object):
        product_varients = Product.objects.filter(template=product_object)
        varients_data = []
        for variant in product_varients:
            varients_data.append(
                {
                    "id": variant.id,
                    "product_name": variant.product_name,
                    "cover_image": self.request.build_absolute_uri(variant.cover_image.url),
                    "price": variant.price,
                    "rating": variant.rating,
                    "attributes": self.get_variant_attributes(variant),
                }
            )
        return varients_data

    def get_variant_attributes(self, varient_object):
        variant_attr_object = ProductVariantAttribute.objects.filter(
            product=varient_object
        ).first()
        return {
            "attribute": variant_attr_object.attribute.attribute_name,
            "attribute_value": variant_attr_object.attribute_value,
        }


class ProductApi(APIView):
    def get(self, request):
        products = Product.objects.all().order_by("rating").exclude(item_type="002")[:36]
        serailized_data = ProductListSerializer(
            products, many=True, context={"request": request}
        )
        return Response(status=200, data=serailized_data.data)
