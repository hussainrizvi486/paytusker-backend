from django.http import HttpRequest
from django.contrib.auth import authenticate
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

from ..serializers import AuthTokenSerializer
from ..models import User, LoginHistory


def get_client_ip(request: HttpRequest):
    x_forwarded_for: str = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[-1].strip()
    else:
        ip = request.META.get("REMOTE_ADDR", "")
    return ip


def create_login_log(user, device="", ip=""):
    try:
        log_object = LoginHistory.objects.create(
            user=user,
            device=device,
            ip=ip,
        )
        log_object.save()
    except Exception:
        return


class LoginViewSet(viewsets.ViewSet):
    @classmethod
    def validate_auth_data(self, data: dict):
        required_fields = ["email", "password"]
        for key in required_fields:
            if key not in data.keys():
                return False
        return True

    @classmethod
    def get_jwt_tokens(self, user):
        refresh = AuthTokenSerializer.get_token(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def jwt_login(self, request: HttpRequest):
        data: dict = request.data

        if not self.validate_auth_data(data):
            return Response(
                data={"message": "Invalid request data"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = authenticate(email=data.get("email"), password=data.get("password"))
        if user is not None:
            tokens = self.get_jwt_tokens(user)
            create_login_log(
                user,
                request.META.get("HTTP_USER_AGENT", ""),
                get_client_ip(request),
            )
            return Response(
                data={"tokens": tokens, "message": "Login success"},
                status=status.HTTP_200_OK,
            )

        return Response(
            data={"message": "Invaid user credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    @permission_classes([IsAuthenticated])
    def update_password(self, request):
        request_data: dict = request.data
        request_user: User = request.user
        current_password = request_data.get("current_password")
        new_password = request_data.get("new_password")
        if (
            current_password
            and new_password
            and authenticate(email=request_user.email, password=current_password)
        ):
            user = User.objects.get(id=request_user.id)
            user.set_password(new_password)
            user.save()
            return Response(data={"message": "Password updated successfully"})

        else:
            return Response(
                data={"message": "Invalid password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
