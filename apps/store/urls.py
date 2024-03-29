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
    path("product/create", ProductsApi.as_view({"post": "create_product"})),
    path("product/update", ProductsApi.as_view({"post": "update_product"})),
    # Cart Routes
    path("customer/cart/add", CartApi.as_view({"post": "add_to_cart"})),
    path("customer/cart/get", CartApi.as_view({"get": "get_cart_detail"})),
    path("customer/cart/update", CartApi.as_view({"post": "update_cart_item"})),
    # order routes
    path("customer/order/create", OrderApi.as_view({"post": "create_order"})),
    path("customer/order/get", OrderApi.as_view({"get": "get_customer_orders"})),
    # reviews
    path(
        "customer/reviews/add",
        CustomerFunctions.as_view({"post": "add_order_review"}),
    ),
    path(
        "customer/reviews/get",
        CustomerFunctions.as_view({"get": "get_order_review"}),
    ),
    path(
        "customer/reviews/pending",
        CustomerFunctions.as_view({"get": "to_review_items"}),
    ),
    # old routes
    path("add-to-cart", CartApi.as_view({"post": "add_to_cart"})),
    path("get-cart", CartApi.as_view({"get": "get_cart_detail"})),
    path("cart/update-cart", CartApi.as_view({"post": "update_cart_item"})),
    path("order/create-order", OrderApi.as_view({"post": "create_order"})),
    path("order/get-orders", OrderApi.as_view({"get": "get_customer_orders"})),
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
    path("get-products", ProductApi.as_view()),
]
