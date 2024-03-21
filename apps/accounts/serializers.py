from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import User, Address


class AccountsTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        d_user = User.objects.get(email=user.email)
        token["username"] = d_user.username
        token["email"] = user.email
        return token


class UserAddressSerializer(serializers.ModelSerializer):
    # date = serializers.DateTimeField(source="modified", format="%Y-%m-%d")

    class Meta:
        model = Address
        fields = [
            "id",
            # "date",
            "address_title",
            "address_type",
            "country",
            "state",
            "city",
            "address_line_1",
        ]
