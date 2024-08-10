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
from apps.store.models import ModelMedia
from apps.store.permissions import IsCustomerUser
# from apps.accounts.models import Address
from apps.store.pagination import ListQuerySetPagination
from apps.store.erpnext import sync_order
from server import settings


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
                order_items = json.loads(metadata["items"])
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
            return HttpResponse(status=400)
        return HttpResponse(status=200)
    return HttpResponse(status=400)


def create_seller_orders():
    order_items = OrderItems.objects.select_related("item__seller")
    seller_wise_orders = {}
    for order in order_items:
        seller_id = order.item.seller.id
        if seller_id in seller_wise_orders.keys():
            seller_wise_orders[seller_id].append(order)
        else:
            seller_wise_orders[seller_id] = [order]

    print(seller_wise_orders)
