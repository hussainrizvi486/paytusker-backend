from rest_framework.viewsets import ViewSet
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.accounts.models import User, Address
from django.core import serializers
from rest_framework import status
from server.utils import exceute_sql_query
from ..serializers import UserAddressSerializer


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
        address_id = request.GET.get("id")

        if address_id:
            address_query_set = Address.objects.filter(id=address_id).order_by(
                "-modified"
            )
            if address_query_set:
                serailized_data = UserAddressSerializer(address_query_set)
                return Response(data=serailized_data.data)
            return Response(data=[])
        else:
            address_query_set = Address.objects.filter(user=request.user)
            serailized_data = UserAddressSerializer(address_query_set, many=True)
            if serailized_data.data:
                return Response(data=serailized_data.data)

            return Response(data=[])

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
        return Response(status=status.HTTP_201_CREATED, data="Address Created")

    def edit_user_address(self, request):
        address_id = request.GET.get("id")
        address_object = request.GET.get("address_object")
        address_record = Address.objects.filter(id=address_id)
        address_record.update(**address_object)

        return Response(data="Address updated")
