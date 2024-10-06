from django.urls import path
from .seller.order import ProcessOrderView

seller_url = [
    path(
        "api/seller/order/digital/update",
        ProcessOrderView.as_view({"post": "update_status"}),
    ),
    # path("seller/order/digital/list"),
    #     path("seller/order/list"),
    #     path("seller/order/details"),
    #     path("seller/product/list"),
    #     path("seller/product/create"),
    #     path("seller/product/update"),
    #     path("seller/product/detail"),
]
