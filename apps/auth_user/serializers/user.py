from rest_framework import serializers
from ..models import User


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "phone_number",
            "email",
            "username",
            "date_joined",
            "first_name",
            "last_name",
        ]
