from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User


class AccountsTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # token['id'] = user.id
        d_user = User.objects.get(email=user.email)
        token["username"] = d_user.username
        token["email"] = user.email
        return token
