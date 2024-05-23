from django.urls import path
from .order import OrderWebhooks

webhooks_paths = [
    path(
        "webhooks/order/update-status",
        OrderWebhooks.as_view({"post", "update_order_status"}),
    ),
]
