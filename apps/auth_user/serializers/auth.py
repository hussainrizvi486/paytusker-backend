from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from ..models import User, LoginHistory


class AuthTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: User):
        token = super().get_token(user)
        token["user_id"] = user.id
        token["username"] = user.username
        token["email"] = user.email
        token["full_name"] = user.get_full_name()
        token["roles"] = user.get_user_roles()
        return token


class LoginHistorySerializer(serializers.ModelSerializer):
    log_date = serializers.SerializerMethodField()

    class Meta:
        model = LoginHistory
        fields = ["device", "time", "log_date"]

    def get_log_date(self, obj: LoginHistory):
        return obj.time.strftime("%d-%m-%Y %H:%M:%S")
