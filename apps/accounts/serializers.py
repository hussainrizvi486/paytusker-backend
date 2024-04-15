from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import User, Address


class AccountsTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {"no_active_account": "Invalid credentials"}

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        d_user = User.objects.get(email=user.email)
        token["username"] = d_user.username
        token["full_name"] = d_user.get_full_name()
        token["email"] = user.email

        if d_user.image:
            token["image"] = d_user.image.url
        return token


class UserAddressSerializer(serializers.ModelSerializer):
    address_display = serializers.SerializerMethodField()
    # address_display = address_line_1 + city + state + country

    class Meta:
        model = Address
        fields = [
            "id",
            "address_title",
            "address_type",
            "country",
            "state",
            "city",
            "address_line_1",
            "address_display",
        ]

    def get_address_display(self, obj):
        return f""" <b> {obj.address_title}</b>: {obj.address_line_1 or ""}, {obj.city or ""}, {obj.state or ""}, {obj.country or ""}"""
