from django.urls import path
from .order import StripeOrderPaymentWebhook

webhooks_urls = [
    path(
        "webhooks/payment/orders",
        StripeOrderPaymentWebhook.as_view(),
    ),
]
