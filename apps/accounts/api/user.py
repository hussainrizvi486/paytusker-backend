from rest_framework.viewsets import ViewSet
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.accounts.models import User, Address
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
        print(Address._meta.fields)
        data = {}
        query = f""" SELECT * FROM accounts_address WHERE user_id = '{request.user.id}' ORDER BY creation DESC  """
        data = exceute_sql_query(query)

        return Response(data=data)

    def add_user_address(self, request):
        data = request.data
        address_object = Address.objects.create(
            user=self.request.user,
            address_title=data.get("address_title"),
            address_type=data.get("address_type"),
            country=data.get("country"),
            state=data.get("state"),
            city=data.get("city"),
            address_line_1=data.get("details"),
        )
        address_object.save()

        # print(data)

        return Response(status=status.HTTP_201_CREATED, data="Address Created")
