from django.urls import path
from django.http import JsonResponse
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .api.register import RegisterUser
from .api.user import UserApi


def index(request):
    return JsonResponse("accounts", safe=False)


urlpatterns = [
    path("user/register", RegisterUser.as_view(), name="register_user"),
    path(
        "user/login",
        views.AccountsTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path("user/login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "user/address/get",
        UserApi.as_view({"get": "get_user_address"}),
    ),
    path(
        "user/address/add",
        UserApi.as_view({"post": "add_user_address"}),
    ),
    path(
        "user/address/update",
        UserApi.as_view({"post": "edit_user_address"}),
    ),
    path("register/", RegisterUser.as_view(), name="register_user"),
    # old routes
    path(
        "get-user-details/",
        UserApi.as_view({"get": "get_user_details"}),
    ),
    path(
        "get-user-address/",
        UserApi.as_view({"get": "get_user_address"}),
    ),
    path(
        "add-user-address/",
        UserApi.as_view({"post": "add_user_address"}),
    ),
    path(
        "edit-user-address/",
        UserApi.as_view({"post": "edit_user_address"}),
    ),
    path(
        "auth-token/",
        views.AccountsTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path("auth-token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
