from django.urls import path
from .api.product import ProductApi, ProductsApi
from .api.cart import CartApi
from .api.order import OrderApi, CustomerFunctions


urlpatterns = [
    path(
        "product/details",
        ProductsApi.as_view({"get": "get_product_detail"}),
    ),
    path("product/search", ProductsApi.as_view({"get": "search_products"})),
    path("product/create", ProductsApi.as_view({"post":"create_product"})),
    path("get-products", ProductApi.as_view()),
    # protect routes
    path("add-to-cart", CartApi.as_view({"post": "add_to_cart"})),
    path("get-cart", CartApi.as_view({"get": "get_cart_detail"})),
    path("order/create-order", OrderApi.as_view({"post": "create_order"})),
    path("order/get-orders", OrderApi.as_view({"get": "get_customer_orders"})),
    path("cart/update-cart", CartApi.as_view({"post": "update_cart_item"})),
    path(
        "customer/add-order-review",
        CustomerFunctions.as_view({"post": "add_order_review"}),
    ),
    path(
        "customer/get-reviews",
        CustomerFunctions.as_view({"get": "get_order_review"}),
    ),
    path(
        "customer/to-review-items",
        CustomerFunctions.as_view({"get": "to_review_items"}),
    ),
]
