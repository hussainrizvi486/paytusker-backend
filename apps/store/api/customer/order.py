import json
import stripe
import math
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from rest_framework import status, viewsets, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from server import settings
from server.utils import get_media_url

from apps.store.models import UserAddress, Customer, CartItem, Cart
from apps.store.pagination import ListQuerySetPagination
from apps.store.permissions import CustomerPermission
from apps.store.models.order import (
    DigitalOrder,
    DigitalOrderItem,
    DigitalOrderStatusChoices as StatusChoices,
)


class CustomerOrderListSerializer(serializers.ModelSerializer):
    class ItemsList(serializers.ModelSerializer):
        product_name = serializers.SerializerMethodField()
        cover_image = serializers.SerializerMethodField()

        class Meta:
            model = DigitalOrderItem
            fields = [
                "product_name",
                "amount",
                "rate",
                "qty",
                "reviewed_by_customer",
                "status",
                "cover_image",
            ]

        def get_product_name(self, obj):
            return obj.product.product_name if obj else None

        def get_cover_image(self, obj):
            file = obj.product.cover_image
            if file:
                return get_media_url(file.url)

    items = ItemsList(many=True, read_only=True)
    order_date = serializers.SerializerMethodField()

    class Meta:
        model = DigitalOrder
        fields = [
            "order_id",
            "order_date",
            "order_status",
            "grand_total",
            "total_qty",
            "payment_status",
            "payment_method",
            "items",
        ]

    def get_order_date(self, obj):
        return obj.order_date.strftime("%d-%m-%Y")


class CustomerOrderViewSet(viewsets.ViewSet):
    def list(self, *args, **kwargs):
        paginator = ListQuerySetPagination(page_size=20)
        customer_queryset = get_object_or_404(Customer, user=self.request.user.id)
        orders_queryset = (
            DigitalOrder.objects.filter(customer=customer_queryset)
            .select_related("customer")
            .prefetch_related(
                Prefetch(
                    "items", queryset=DigitalOrderItem.objects.select_related("product")
                )
            )
        )
        paginated_queryset = paginator.paginate_queryset(orders_queryset, self.request)
        serializer = CustomerOrderListSerializer(paginated_queryset, many=True)
        customer_orders = serializer.data
        response_dict = {}
        response_dict.update(paginator.get_pagination_details())
        response_dict.update({"results": customer_orders})
        return Response(data=response_dict)


#   def get_customer_orders(self, request):
#         customer = get_customer(request.user)
#         orders_qs = Order.objects.filter(customer=customer).order_by("-creation")
#         if request.GET.get("order_status"):
#             orders_qs = orders_qs.filter(order_status=request.GET.get("order_status"))

#         data = []
#         ORDER_STATUS_OBJECT = {
#             "001": {"status": "Pending", "color": "#ffae00"},
#             "002": {"status": "Confirmed", "color": "#0066ff"},
#             "003": {"status": "In Process", "color": "#ff9900"},
#             "004": {"status": "Going For Delivery", "color": "#339966"},
#             "005": {"status": "Deliverd", "color": "#0eca05"},
#             "006": {"status": "Cancelled", "color": "#ff0000"},
#         }

#         if orders_qs:
#             orders_qs = paginator.paginate_queryset(orders_qs, request)
#             for order in orders_qs:
#                 order_dict = {
#                     "order_id": order.order_id,
#                     "grand_total": order.grand_total,
#                     "total_qty": order.total_qty,
#                     "order_date": order.order_date,
#                     "delivery_date": (
#                         order.delivery_date.strftime("%m-%d-%Y")
#                         if hasattr(order, "delivery_date")
#                         else None
#                     ),
#                     "payment_status": order.payment_status,
#                     "payment_method": order.payment_method,
#                     "delivery_status": order.delivery_status,
#                     "order_status": (
#                         ORDER_STATUS_OBJECT.get(order.order_status).get("status")
#                         if ORDER_STATUS_OBJECT.get(order.order_status) is not None
#                         else ""
#                     ),
#                     "status_color": (
#                         ORDER_STATUS_OBJECT.get(order.order_status).get("color")
#                         if ORDER_STATUS_OBJECT.get(order.order_status) is not None
#                         else ""
#                     ),
#                 }

#                 order_items_qs = OrderItems.objects.filter(order=order).order_by(
#                     "-creation"
#                 )
#                 order_items = []

#                 for oi in order_items_qs:
#                     order_items.append(
#                         {
#                             "product_name": oi.item.product_name,
#                             "cover_image": self.request.build_absolute_uri(
#                                 oi.item.cover_image.url
#                             ),
#                             "rate": oi.rate,
#                             "qty": oi.qty,
#                             "amount": oi.amount,
#                         }
#                     )

#                 order_dict["items"] = order_items

#                 data.append(order_dict)

#             return paginator.get_paginated_response(data)

#         return Response(data={"results": [], "message": "No Orders Found"})


# path "order/checkout/"
class CustomerCheckout(APIView):
    permission_classes = [CustomerPermission]

    def post(self, *args, **kwargs):
        stripe.api_key = settings.STRIPE_API_KEY
        if not stripe.api_key:
            return Response(
                {"message": "Order service down."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        customer_queryset = get_object_or_404(Customer, user=self.request.user.id)
        requested_data: dict = self.request.data
        payment_method = requested_data.get("payment_method")
        # address_queryset = UserAddress.objects.filter(
        #     id=requested_data.get("delivery_address")
        # ).first()
        delivery_address = None
        # if address_queryset:
        #     delivery_address = address_queryset.id

        cart_queryset = Cart.objects.get(customer=customer_queryset)
        cartitems_queryset = CartItem.objects.select_related("product").filter(
            cart=cart_queryset
        )

        checkout_items = []
        items_ordered = []

        for item in cartitems_queryset:
            product = item.product
            items_ordered.append(
                {
                    "product_id": product.id,
                    "qty": int(item.qty),
                    "rate": float(item.rate),
                    "seller_rate": float(product.net_price),
                }
            )
            cover_image = None
            if product.cover_image:
                cover_image = get_media_url(product.cover_image.url)

            checkout_items.append(
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": math.ceil(item.product.price * 100),
                        "product_data": {
                            "name": item.product.product_name,
                            "images": [cover_image],
                        },
                    },
                    "quantity": int(item.qty),
                }
            )

        stripe_metadata = {
            "shipping_address": delivery_address,
            "payment_method": payment_method,
            "customer": customer_queryset.id,
            "items_ordered": json.dumps(items_ordered),
        }

        session = stripe.checkout.Session.create(
            payment_method_types=[payment_method],
            line_items=checkout_items,
            metadata=stripe_metadata,
            mode="payment",
            success_url=settings.STRIPE_PAYMENT_SUCCESS_URL,
            cancel_url=settings.STRIPE_PAYMENT_FAILED_URL,
            billing_address_collection="auto",
        )

        return Response(
            {
                "checkout_session": session.id,
                "redirect_url": session.url,
            },
            status=status.HTTP_200_OK,
        )
