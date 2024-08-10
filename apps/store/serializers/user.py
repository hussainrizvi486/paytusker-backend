from rest_framework import serializers
from ..models import UserAddress


class UserAddressSerializer(serializers.ModelSerializer):
    address_display = serializers.SerializerMethodField()

    class Meta:
        model = UserAddress
        fields = [
            "id",
            "address_title",
            "address_type",
            "country",
            "state",
            "city",
            "default",
            "address_line",
            "address_display",
        ]

    def get_address_display(self, obj: UserAddress):
        return f""" <b> {obj.address_title}</b>: {obj.address_line or ""}, {obj.city or ""}, {obj.state or ""}, {obj.country or ""}"""
