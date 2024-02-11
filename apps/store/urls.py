from django.urls import path
from . import views
from .api.product import ProductApi, ProductDetail, ProductsApi
from .api.cart import CartApi
from .api.order import OrderApi


urlpatterns = [
    path("product/details/<str:product_id>", ProductDetail.as_view()),
    path("product/search", ProductsApi.as_view({"get": "search_products"})),
    path("get-products", ProductApi.as_view()),
    path("add-to-cart", CartApi.as_view({"post": "add_to_cart"})),
    path("get-cart", CartApi.as_view({"get": "get_cart_detail"})),
    # path("user-orders", views.Cart.as_view())
    path("product", views.Product.as_view()),
    path("get-user", views.user.as_view()),
    path("categories", views.CreateCategory.as_view()),
    path("order/create-order", OrderApi.as_view({"post": "create_order"})),
    path("order/get-orders", OrderApi.as_view({"get": "get_customer_orders"})),
    path("cart/update-cart", CartApi.as_view({"post": "update_cart_item"})),
]
