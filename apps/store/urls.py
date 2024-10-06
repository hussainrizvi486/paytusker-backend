from django.urls import path
from .webhooks import webhooks_urls

from .api import (
    SearchProductsApi,
    ListSellerProducts,
    UserAddressViewSet,
    get_upload_product_data,
)
from .api.product import ProductsApi, ProductCategory, ProductAPIView
from .api.cart import CartApi
from .api.order import OrderApi, CustomerFunctions
from .api.customer.order import CustomerCheckout, CustomerOrderViewSet
from .api.customer.reviews import CustomerOrderReviewView

from apps.store.api import (
    CategoryList,
    ProductTemplateList,
    SellerDigitalOrderViewSet,
    ProcessOrderView,
)


customer_urls = [
    path(
        "api/customer/reviews/add",
        CustomerOrderReviewView.as_view({"post": "add_review"}),
    ),
    path(
        "api/customer/reviews/get",
        CustomerOrderReviewView.as_view({"get": "get_reviews"}),
    ),
    path(
        "api/customer/reviews/pending",
        CustomerOrderReviewView.as_view({"get": "pending_reviews"}),
    ),
]

seller_api = [
    path("api/seller/product/list", ListSellerProducts.as_view()),
    path(
        "api/seller/order/digital",
        SellerDigitalOrderViewSet.as_view({"get": "order_detail"}),
    ),
    path(
        "api/seller/order/digital/list",
        SellerDigitalOrderViewSet.as_view({"get": "orders_list"}),
    ),
    path(
        "api/seller/order/digital/update-status",
        ProcessOrderView.as_view({"post": "update_status"}),
    ),
]


urlpatterns = [
    path("api/product/template/list", ProductTemplateList.as_view()),
    path("api/category/list", CategoryList.as_view()),
    path("api/seller/product", ProductAPIView.as_view()),
    # path("webhooks/payment/orders", order_payment_confirm_webhook),
    # path("test/orders", make_seller_orders),
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
    # path("api/customer/order/create", OrderApi.as_view({"post": "create_order"})),
    path("api/customer/order/create", CustomerCheckout.as_view()),
    # path("api/customer/order/get", OrderApi.as_view({"get": "get_customer_orders"})),
    path("api/customer/order/get", CustomerOrderViewSet.as_view({"get": "list"})),
    # reviews
    # path(
    #     "api/customer/reviews/add",
    #     CustomerFunctions.as_view({"post": "add_order_review"}),
    # ),
    # path(
    #     "api/customer/reviews/get",
    #     CustomerFunctions.as_view({"get": "get_order_review"}),
    # ),
    # path(
    #     "api/customer/reviews/pending",
    #     CustomerFunctions.as_view({"get": "to_review_items"}),
    # ),
    path("api/user/address", UserAddressViewSet.as_view()),
    path("api/product/upload-details", get_upload_product_data),
    # path(
    #     "api/seller/order/detail",
    #     SellerOrderViewSet.as_view({"get": "get_order_detail"}),
    # ),
]


urlpatterns.extend(webhooks_urls)
urlpatterns.extend(seller_api)
urlpatterns.extend(customer_urls)
