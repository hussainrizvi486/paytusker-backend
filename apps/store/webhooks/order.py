import json
import stripe
from decimal import Decimal
from server.utils import load_request_body
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from apps.store.models import PaymentEntry, Product
from apps.store.models.order import Order, validated_status, OrderItems
from apps.store.models.customer import Customer, Cart
from server import settings


class OrderWebhooks(ViewSet):
    def update_order_status(self, request):
        data = load_request_body(request.data)
        order_id = data.get("order_id")
        order_status = data.get("order_status")

        if order_status not in validated_status:
            return Response(
                data={
                    "message": "Please provide a validated status",
                    "validated_status": validated_status,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        order = get_object_or_404(Order, id=order_id)
        order.order_status = order_status
        order.save()

        return Response(
            data={"message": "Order status updated successfully"},
            status=status.HTTP_200_OK,
        )


class StripeOrderPaymentWebhook(APIView):
    @classmethod
    def make_payment_entry(self, data: Order):
        try:
            pe_object = PaymentEntry.objects.create(
                party_type=PaymentEntry.PartTypeChoices.CUSTOMER,
                reference_type=data._meta.db_table,
                reference_id=data.id,
                mode_of_payment=data.payment_method,
                party_id=data.customer.id,
                amount=data.grand_total,
            )
            pe_object.save()
            return pe_object

        except Exception:
            return None

    @classmethod
    def make_customer_order(self, data: dict):
        try:
            customer = Customer.objects.get(id=data.get("customer_id"))
            order_object = Order.objects.create(
                customer=customer,
                order_status=Order.StatusChoices.ORDER_PENDING,
                payment_status=True,
                payment_method=data.get("payment_method"),
            )

            order_object.save()
            for item in data.get("items", []):
                orderitem_object = OrderItems.objects.create(
                    order=order_object,
                    rate=Decimal(item.get("rate")),
                    qty=Decimal(item.get("qty")),
                    item=Product.objects.get(id=item.get("id")),
                )
                orderitem_object.save()
            order_object.save()

            Cart.objects.filter(customer=customer).delete()
            return order_object
        except Exception:
            return None

    @csrf_exempt
    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        try:
            if sig_header:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, settings.STRIPE_END_SECRECT_KEY
                )
                if event.type == "checkout.session.completed":
                    metadata: dict = event["data"]["object"]["metadata"]
                    order_object = {
                        "items": json.loads(metadata.get("items")),
                        "payment_method": metadata.get("payment_method"),
                        "customer_id": metadata.get("customer_id"),
                        "delivery_address": metadata.get("delivery_address"),
                    }
                    order_queryset = self.make_customer_order(order_object)

                    if order_queryset:
                        self.make_payment_entry(order_queryset)

                    return Response(
                        data={
                            "message": "payment confirmed",
                            "order_status": "Processing",
                        },
                        status=status.HTTP_202_ACCEPTED,
                    )

                return Response(status=status.HTTP_200_OK)
            else:
                return Response(
                    data={
                        "message": "HTTP_STRIPE_SIGNATURE not found",
                        "order_status": "Failed",
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            return Response(
                data={"error": str(e), "message": "stripe order webhook failed"}
            )
