from typing import List, Dict
from datetime import datetime
from rest_framework import views, viewsets
from rest_framework import status, serializers
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Prefetch


from apps.store.pagination import ListQuerySetPagination
from ...models.orders import (
    SellerOrder,
    SellerDigitalOrder,
    SellerDigitalOrderItem,
)
from ...models.order import DigitalOrderStatusChoices, OrderCancellation
from ...serializers import UserAddressSerializer
from server.utils import get_media_url


class SellerOrderListingSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()

    class Meta:
        model = SellerDigitalOrder
        fields = [
            "id",
            "creation",
            "modified",
            "status",
            "order_id",
            "order_date",
            "customer",
            "grand_total",
        ]

    def get_customer(self, obj):
        return {
            "customer": obj.customer.id,
            "customer_name": obj.customer.customer_name,
        }


class DigitalOrderSerializer(serializers.ModelSerializer):
    class ItemSerializer(serializers.ModelSerializer):
        product_name = serializers.SerializerMethodField()
        product_id = serializers.SerializerMethodField()
        cover_image = serializers.SerializerMethodField()

        class Meta:
            model = SellerDigitalOrderItem
            fields = [
                "product_name",
                "product_id",
                "cover_image",
                "rate",
                "amount",
                "qty",
            ]

        def get_product_name(self, obj):
            return obj.product.product_name

        def get_product_id(self, obj):
            return obj.product.id

        def get_cover_image(self, obj):
            return (
                get_media_url(obj.product.cover_image.url)
                if obj.product.cover_image
                else None
            )

    customer = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    items = ItemSerializer(many=True, read_only=True)

    class Meta:
        model = SellerDigitalOrder
        fields = [
            "id",
            "status",
            "seller",
            "total",
            "grand_total",
            "customer",
            "order_date",
            "creation",
            "items",
            "modified",
        ]

    def get_customer(self, obj):
        return {"id": obj.customer.id, "customer_name": obj.customer.customer_name}

    def get_total(self, obj):
        return {"grand_total": obj.grand_total, "qty": obj.total_qty}


class SellerOrderViewSet(viewsets.ViewSet):
    def get_order_detail(self, *args):
        order_id = self.request.GET.get("id")
        if order_id:
            order_object = {}
            order_queryset = get_object_or_404(
                SellerOrder.objects.select_related(
                    "delivery_address", "customer", "seller"
                ),
                id=order_id,
            )
            if order_queryset.delivery_address:
                address_serializer = UserAddressSerializer(
                    order_queryset.delivery_address
                )
                order_object.update({"delivery_address": address_serializer.data})

        return Response(status=status.HTTP_200_OK, data=order_object)


class SellerDigitalOrderViewSet(viewsets.ViewSet):
    def get_order_status_timeline(self, queryset: SellerDigitalOrder, statues):
        timeline = []
        order_status = queryset.status
        max_count = 4
        for idx, row in enumerate(statues):
            object = {"id": row[0], "status": row[1]}
            if int(object.get("id")) < max_count:
                if order_status == object.get("id"):
                    if idx < (len(statues) + 1) - max_count:
                        object["next"] = True
                    object["current"] = True
                timeline.append(object)

        for row in timeline:
            if int(row.get("id")) < int(order_status):
                row["completed"] = True
        return timeline

    def order_detail(self, request):
        order_id = self.request.GET.get("id")
        if order_id:
            order_object = {"curreny_symbol": "$"}
            order_queryset = get_object_or_404(
                SellerDigitalOrder.objects.select_related(
                    "customer", "seller"
                ).prefetch_related(
                    Prefetch(
                        "items",
                        queryset=SellerDigitalOrderItem.objects.select_related(
                            "product"
                        ),
                    )
                ),
                id=order_id,
            )

            serialized_order = DigitalOrderSerializer(order_queryset)
            order_object.update(serialized_order.data)
            status_timeline = self.get_order_status_timeline(
                order_queryset, DigitalOrderStatusChoices.choices
            )

            if order_object.get("status") == "004":
                details = dict(
                    OrderCancellation.objects.filter(order_id=order_id)
                    .values("cancellation_reason", "notes", "cancelled_at")
                    .first()
                )
                details.update(
                    {"cancelled_at": details.get("cancelled_at").strftime("%d-%m-%Y")}
                )
                order_object.update({"cancellation_details": details})
            order_object.update({"status_timeline": status_timeline})
            return Response(status=status.HTTP_200_OK, data=order_object)
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
        )

    def orders_list(self, request):
        query_params = self.request.GET
        query_filters = {}
        ignore_filters_params = ["sort_by"]
        date_filter_keys = ["order_date"]
        for key in query_params.keys():
            if key not in ignore_filters_params:
                if query_params.get(key):
                    if key in date_filter_keys:
                        query_filters.update(
                            {
                                key: datetime.strptime(
                                    query_params.get(key), "%Y-%m-%d"
                                ).date()
                            }
                        )
                    else:
                        query_filters.update({key: query_params.get(key)})

        status_choices = DigitalOrderStatusChoices
        orders_stats: List[Dict] = list(
            SellerDigitalOrder.objects.values("status").annotate(count=Count("status"))
        )

        orders_counts = {
            key: {"count": 0, "label": status_choices.to_dict().get(key)}
            for key in status_choices.to_dict().keys()
        }
        for i in orders_stats:
            orders_counts[i.get("status")].update({"count": i.get("count")})

        response_data = {
            "order_status": status_choices.to_dict(),
            "orders_stats": orders_counts,
        }

        pagniator = ListQuerySetPagination(page_size=20)

        # status
        # order_date
        # sort_by

        orders_queryset = SellerDigitalOrder.objects.filter(**query_filters)

        if query_params.get("sort_by"):
            orders_queryset = orders_queryset.order_by(query_params.get("sort_by"))

        paginated_orders = pagniator.paginate_queryset(orders_queryset, request)
        serializer = SellerOrderListingSerializer(paginated_orders, many=True)
        response_data["orders"] = serializer.data
        response_data.update(pagniator.get_pagination_details())
        return Response(data=response_data)


class ProcessOrderView(viewsets.ViewSet):
    def update_status(self, *args, **kwarg):
        request_data: dict = self.request.data
        order_status = request_data.get("status")
        seller_order = get_object_or_404(SellerDigitalOrder, id=request_data.get("id"))

        if order_status == "004":
            cancellation = OrderCancellation.objects.create(
                order_id=seller_order.id,
                cancelled_by="seller",
                cancellation_reason=request_data.get("reason"),
                notes=request_data.get("notes"),
            )
            cancellation.save()
        seller_order.update_status(status=order_status)
        return Response(
            data={
                "message": "Order status updated successfully!",
                "status": status.HTTP_200_OK,
            }
        )


class SellerOrderView(viewsets.ViewSet): ...
