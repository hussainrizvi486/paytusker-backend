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
    path("register/", RegisterUser.as_view(), name="register_user"),
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
        "auth-token/",
        views.AccountsTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path("auth-token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
