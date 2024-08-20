from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .api import (
    LoginViewSet,
    UserLoginLogs,
    RegisterUser,
    UserProfileDetail,
    ResetForgotPassword,
    ForgotPasswordAPI,
)

urlpatterns = [
    path("api/user/login", LoginViewSet.as_view({"post": "jwt_login"})),
    path("api/user/update/password", LoginViewSet.as_view({"put": "update_password"})),
    path("api/user/register", RegisterUser.as_view()),
    path("api/user/detail", UserProfileDetail.as_view()),
    path("user/login/history", UserLoginLogs.as_view()),
    path("api/auth-token/refresh", TokenRefreshView.as_view()),
    # path(
    #     "api/user/password/reset",
    #     PaswordResetRequest.as_view({"post": "reset_password_request"}),
    # ),
    path(
        "api/user/password/forgot",
        ForgotPasswordAPI.as_view(),
    ),
    path(
        "api/user/password/reset/validate/<uid>/<token>",
        ResetForgotPassword.as_view(),
    ),
]
