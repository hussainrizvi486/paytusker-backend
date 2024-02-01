from rest_framework.viewsets import ViewSet
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.accounts.models import User
from django.core import serializers
from rest_framework import status
from server.utils import exceute_sql_query


@permission_classes([IsAuthenticated])
class UserApi(ViewSet):
    def get_user_details(self, request):
        user_object = User.objects.get(id=request.user.id)

        data = {
            "first_name": user_object.first_name,
            "last_name": user_object.last_name,
            "email": user_object.email,
            "phone_number": user_object.phone_number,
            "username": user_object.username,
        }

        return Response(data=data, status=status.HTTP_200_OK)

    def get_user_address(self, request):
        user = request.user
        data = {}
        query = (
            f""" SELECT * FROM accounts_address WHERE user_id = '{request.user.id}' """
        )
        data = exceute_sql_query(query)

        return Response(data=data)
