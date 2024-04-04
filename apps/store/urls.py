from django.urls import path
from .api.product import ProductApi, ProductsApi, SearchProductsApi
from .api.cart import CartApi
from .api.order import OrderApi, CustomerFunctions, order_payment_confirm_webhook
from .erpnext.apis import ERPNextProductsApi,ERPNextItemGroupsApi

erpnext_api_urls = [
    path(
        "erpnext/product/sync",
        ERPNextProductsApi.as_view({"post": "sync_product"}),
    ),
    path(
        "erpnext/product/delete",
        ERPNextProductsApi.as_view({"post": "remove_product"}),
    ),
    path(
        "erpnext/category/sync",
        ERPNextItemGroupsApi.as_view({"get": "sync_category"}),
    ),
]


urlpatterns = [
    path("webhooks/payment/orders", order_payment_confirm_webhook),
    path(
        "product/details",
        ProductsApi.as_view({"get": "get_product_detail"}),
    ),
    path("product/search", SearchProductsApi.as_view()),
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
    path("get-products", ProductApi.as_view()),
]


urlpatterns.extend(erpnext_api_urls)
