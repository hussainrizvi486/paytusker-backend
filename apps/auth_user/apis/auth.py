from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import viewsets, status
from ..serializers import AuthTokenSerializer


class LoginViewSet(viewsets.ViewSet):
    @classmethod
    def validate_auth_data(self, data: dict):
        required_fields = ["email", "password"]
        for key in required_fields:
            if key not in data.keys():
                return {"email"}

        return data

    @classmethod
    def get_jwt_tokens(self, user):
        refresh = AuthTokenSerializer.get_token(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def jwt_login(self, request):
        data: dict = request.data
        self.validate_auth_data(data)
        user = authenticate(email=data.get("email"), password=data.get("password"))

        if user is not None:
            tokens = self.get_jwt_tokens(user)
            return Response(
                data={"tokens": tokens, "message": "Login success"},
                status=status.HTTP_200_OK,
            )

        return Response(
            data={"message": "Invaid user credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )
