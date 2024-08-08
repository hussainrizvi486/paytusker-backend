import json
import stripe
import math
from decimal import Decimal
from datetime import datetime
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework import status
from apps.store.utils import get_customer, get_serialized_model_media
from apps.store.models.order import Order, OrderItems, OrderReview
from apps.store.models.customer import CartItem, Cart, Customer
from apps.store.models.product import Product
from apps.store.models import ModelMedia, UserAddress
from apps.store.permissions import IsCustomerUser

# from apps.accounts.models import Address
from apps.store.pagination import ListQuerySetPagination
from apps.store.erpnext import sync_order
from server import settings


stripe.api_key = settings.STRIPE_API_KEY
endpoint_secret = settings.STRIPE_END_SECRECT_KEY


@permission_classes([IsCustomerUser])
class OrderApi(ViewSet):
    @classmethod
    def clear_customer_cart(self, customer_id: str):
        Cart.objects.filter(customer__id=customer_id).delete()

    def create_order(self, request):
        available_payment_methods = [
            "card",
            "klarna",
        ]

        data = request.data
        customer = get_customer(user=request.user)
        payment_method = data.get("payment_method")

        if payment_method not in available_payment_methods:
            return Response(
                data="Please select valid payment method",
                status=status.HTTP_403_FORBIDDEN,
            )

        delivery_address = UserAddress.objects.get(id=data.get("delivery_address"))
        customer_cart = Cart.objects.get(customer=customer)
        cart_items = CartItem.objects.prefetch_related("item").filter(
            cart=customer_cart
        )

        if not self.validate_customer_origin(delivery_address, cart_items):
            return Response(
                data={
                    "message": "Only customers based in the United States can purchase physical products or enter a valid US address."
                },
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )

        ordered_items = []
        line_items = []
        for item in cart_items:
            ordered_items.append(
                {
                    "id": item.item.id,
                    "qty": float(item.qty),
                    "rate": float(item.item.price),
                }
            )

            line_items.append(
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": math.ceil(item.item.price * 100),
                        "product_data": {
                            "name": item.item.product_name,
                            "images": [
                                f"https://crm.paytusker.com{item.item.cover_image.url}"
                            ],
                        },
                    },
                    "quantity": int(item.qty),
                }
            )

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=[payment_method],
            line_items=line_items,
            metadata={
                "items": json.dumps(ordered_items),
                "payment_method": payment_method,
                "delivery_address": delivery_address.id,
                "customer_id": customer.id,
            },
            mode="payment",
            success_url=settings.STRIPE_PAYMENT_SUCCESS_URL,
            cancel_url=settings.STRIPE_PAYMENT_FAILED_URL,
            billing_address_collection="auto",
        )

        self.clear_customer_cart(customer.id)
        return Response(
            {
                "checkout_session": checkout_session.id,
                "checkout_url": checkout_session.url,
            },
            status=status.HTTP_200_OK,
        )

    def validate_customer_origin(self, address_object, cart_items):
        exists = False
        for item in cart_items:
            if not item.item.is_digital:
                exists = True
                break

        if exists and address_object.country != "United States":
            return False
        else:
            return True

    def get_customer_orders(self, request):
        paginator = ListQuerySetPagination(page_size=5)
        customer = get_customer(request.user)
        orders_qs = Order.objects.filter(customer=customer).order_by("-creation")
        if request.GET.get("order_status"):
            orders_qs = orders_qs.filter(order_status=request.GET.get("order_status"))

        data = []
        ORDER_STATUS_OBJECT = {
            "001": {"status": "Pending", "color": "#ffae00"},
            "002": {"status": "Confirmed", "color": "#0066ff"},
            "003": {"status": "In Process", "color": "#ff9900"},
            "004": {"status": "Going For Delivery", "color": "#339966"},
            "005": {"status": "Deliverd", "color": "#0eca05"},
            "006": {"status": "Cancelled", "color": "#ff0000"},
        }

        if orders_qs:
            orders_qs = paginator.paginate_queryset(orders_qs, request)
            for order in orders_qs:
                order_dict = {
                    "order_id": order.order_id,
                    "grand_total": order.grand_total,
                    "total_qty": order.total_qty,
                    "order_date": order.order_date,
                    "delivery_date": (
                        order.delivery_date.strftime("%m-%d-%Y")
                        if hasattr(order, "delivery_date")
                        else None
                    ),
                    "payment_status": order.payment_status,
                    "payment_method": order.payment_method,
                    "delivery_status": order.delivery_status,
                    "order_status": (
                        ORDER_STATUS_OBJECT.get(order.order_status).get("status")
                        if ORDER_STATUS_OBJECT.get(order.order_status) is not None
                        else ""
                    ),
                    "status_color": (
                        ORDER_STATUS_OBJECT.get(order.order_status).get("color")
                        if ORDER_STATUS_OBJECT.get(order.order_status) is not None
                        else ""
                    ),
                }

                order_items_qs = OrderItems.objects.filter(order=order).order_by(
                    "-creation"
                )
                order_items = []

                for oi in order_items_qs:
                    order_items.append(
                        {
                            "product_name": oi.item.product_name,
                            "cover_image": self.request.build_absolute_uri(
                                oi.item.cover_image.url
                            ),
                            "rate": oi.rate,
                            "qty": oi.qty,
                            "amount": oi.amount,
                        }
                    )

                order_dict["items"] = order_items

                data.append(order_dict)

            return paginator.get_paginated_response(data)

        return Response(data={"results": [], "message": "No Orders Found"})


@permission_classes([IsCustomerUser])
class CustomerFunctions(ViewSet):
    def check_review_data(self, data: dict, customer):
        product_id = Product.objects.get(id=data.get("product_id"))
        order_item = OrderItems.objects.get(id=data.get("id"))

        if OrderReview.objects.filter(
            product=product_id, customer=customer, order_item=order_item
        ).exists():

            return "Review already exists", False
        return "", True

    def add_order_review(self, request):
        req_data: dict = request.data

        if req_data:
            customer = get_customer(request.user)
            message, validated = self.check_review_data(req_data, customer)

            if not validated:
                return Response(data=message)

            order_item = OrderItems.objects.get(id=req_data.get("id"))

            review = OrderReview.objects.create(
                customer=customer,
                order=order_item.order,
                order_item=order_item,
                product=order_item.item,
                rating=req_data.get("rating"),
                review_content=req_data.get("review_content"),
            )

            def filter_media_keys(key):
                if str(key).startswith("review_media"):
                    return True
                return False

            review.save()
            order_item.has_review = True
            order_item.save()
            review_media_keys = filter(filter_media_keys, req_data.keys())
            if review_media_keys:
                for key in review_media_keys:
                    if req_data.get(key):
                        ModelMedia.objects.create(
                            model_name="OrderReview",
                            file=req_data.get(key),
                            field_id=review.id,
                        )

            return Response(data="Review added", status=status.HTTP_201_CREATED)
        return Response(data="Data is missing", status=status.HTTP_204_NO_CONTENT)

    def get_order_review(
        self,
        request,
    ):
        filters = request.GET.get("filters") or {}
        customer = get_customer(request.user)
        response_data = []
        orders_reviews = OrderReview.objects.filter(customer=customer).order_by(
            "-creation"
        )

        for review in orders_reviews:
            response_data.append(
                {
                    "product_name": review.product.product_name,
                    "product_image": request.build_absolute_uri(
                        review.product.cover_image.url
                    ),
                    "order_id": review.order.order_id,
                    "order_date": review.order.order_date.strftime("%d-%m-%Y"),
                    "review_date": review.creation.strftime("%d-%m-%Y"),
                    "review_content": review.review_content,
                    "rating": review.rating,
                    "review_media": get_serialized_model_media(
                        "OrderReview", review.id, request
                    ),
                }
            )

        if response_data:
            return Response(data={"reviews": response_data, "message": ""})

        return Response(
            data={"reviews": None, "message": "No Reviews Found"},
        )

    def to_review_items(self, request):
        customer = get_customer(request.user)
        order_items = OrderItems.objects.filter(
            order__customer=customer, has_review=False, order__order_status="005"
        )

        data = []

        for row in order_items:
            data.append(
                {
                    "order_id": row.order.order_id,
                    "product_name": row.item.product_name,
                    "product_image": (
                        request.build_absolute_uri(row.item.cover_image.url)
                        if row.item.cover_image
                        else None
                    ),
                    "product_id": row.item.id,
                    "amount": row.amount,
                    "qty": row.qty,
                    "rate": row.rate,
                    "id": row.id,
                }
            )

        if data:
            return Response(data={"reviews": data})
        return Response(data={"reviews": None})


@csrf_exempt
def order_payment_confirm_webhook(request):
    payload = request.body
    event = None
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    if sig_header:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
            if event.type == "checkout.session.completed":
                metadata = event["data"]["object"]["metadata"]
                order_items = metadata["items"]
                order_items = json.loads(order_items)

                payment_method = metadata["payment_method"]
                # delivery_address = Address.objects.get(id=metadata["delivery_address"])
                customer = Customer.objects.get(id=metadata["customer_id"])
                order_queryset = Order.objects.create(
                    # delivery_address=delivery_address,
                    payment_method=payment_method,
                    order_status="001",
                    payment_status=True,
                    customer=customer,
                )

                for item in order_items:
                    product = Product.objects.get(id=item.get("id"))
                    OrderItems.objects.create(
                        order=order_queryset,
                        qty=Decimal(item.get("qty")),
                        item=product,
                    )

                order_queryset.save()
                Cart.objects.filter(customer=order_queryset.customer).delete()
                sync_order(order_queryset)
        except Exception as e:
            from pprint import pprint
            import traceback

            pprint(traceback.format_exc())
            return HttpResponse(status=400)

        return HttpResponse(status=200)

    return HttpResponse(status=400)
