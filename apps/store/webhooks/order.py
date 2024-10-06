import json
import stripe
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from apps.store.services import ProcessCheckoutOrder
from django.views.decorators.csrf import csrf_exempt


class StripeOrderPaymentWebhook(APIView):
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
                    order_data = metadata
                    order_data.update(
                        {"items_ordered": json.loads(metadata.get("items_ordered"))}
                    )
                    process = ProcessCheckoutOrder(order_data)
                    process.process_orders()

                    return Response(
                        data={
                            "message": "payment confirmed",
                            "order_status": "Processing",
                        },
                        status=status.HTTP_202_ACCEPTED,
                    )

                return Response(status=status.HTTP_100_CONTINUE)

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
