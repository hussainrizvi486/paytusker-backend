from django.urls import path
from .api import (
    SearchProductsApi,
    ListSellerProducts,
    UserAddressViewSet,
    get_upload_product_data,
)
from .api.product import ProductsApi, ProductCategory, ProductAPIView
from .api.cart import CartApi
from .api.order import OrderApi, CustomerFunctions, order_payment_confirm_webhook
from .erpnext.apis import ERPNextProductsApi, ERPNextItemGroupsApi
from .webhooks import webhooks_paths, OrderWebhooks, StripeOrderPaymentWebhook
from apps.store.api import CategoryList, ProductTemplateList

erpnext_api_urls = [
    path(
        "api/erpnext/product/sync",
        ERPNextProductsApi.as_view({"post": "sync_product"}),
    ),
    path(
        "api/erpnext/product/delete",
        ERPNextProductsApi.as_view({"post": "remove_product"}),
    ),
    path(
        "api/erpnext/category/sync",
        ERPNextItemGroupsApi.as_view({"post": "sync_category"}),
    ),
    path(
        "api/erpnext/category/delete",
        ERPNextItemGroupsApi.as_view({"post": "remove_category"}),
    ),
]


seller_apis_urls = [
    path("api/seller/product/list", ListSellerProducts.as_view()),
]


urlpatterns = [
    path("api/product/template/list", ProductTemplateList.as_view()),
    path("api/seller/product", ProductAPIView.as_view()),
    path("api/category/list", CategoryList.as_view()),
    path("webhooks/payment/orders", StripeOrderPaymentWebhook.as_view()),
    # path("webhooks/payment/orders", order_payment_confirm_webhook),
    path(
        "api/product/details",
        ProductsApi.as_view({"get": "get_product_detail"}),
    ),
    path(
        "api/product/home",
        ProductsApi.as_view({"get": "get_home_page_products"}),
    ),
    path("api/product/search", SearchProductsApi.as_view()),
    path(
        "api/category/get",
        ProductCategory.as_view({"get": "get_categories"}),
    ),
    # path("product/create", ProductsApi.as_view({"post": "create_product"})),
    # path("product/update", ProductsApi.as_view({"post": "update_product"})),
    # Cart Routes
    path("api/customer/cart/add", CartApi.as_view({"post": "add_to_cart"})),
    path("api/customer/cart/get", CartApi.as_view({"get": "get_cart_detail"})),
    path("api/customer/cart/update", CartApi.as_view({"post": "update_cart_item"})),
    # order routes
    path("api/customer/order/create", OrderApi.as_view({"post": "create_order"})),
    path("api/customer/order/get", OrderApi.as_view({"get": "get_customer_orders"})),
    # reviews
    path(
        "api/customer/reviews/add",
        CustomerFunctions.as_view({"post": "add_order_review"}),
    ),
    path(
        "api/customer/reviews/get",
        CustomerFunctions.as_view({"get": "get_order_review"}),
    ),
    path(
        "api/customer/reviews/pending",
        CustomerFunctions.as_view({"get": "to_review_items"}),
    ),
    path(
        "webhooks/order/update-status",
        OrderWebhooks.as_view({"post": "update_order_status"}),
    ),
    path("api/user/address", UserAddressViewSet.as_view()),
    path("api/product/upload-details", get_upload_product_data),
]


urlpatterns.extend(erpnext_api_urls)
urlpatterns.extend(seller_apis_urls)
