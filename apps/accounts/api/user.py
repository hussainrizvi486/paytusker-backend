from rest_framework.viewsets import ViewSet
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.accounts.models import User, Address
from django.core import serializers
from rest_framework import status
from server.utils import exceute_sql_query
from ..serializers import UserAddressSerializer
from django.contrib.auth import authenticate


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

    # api/user/password/update
    def update_user_password(self, request):
        data = request.data
        if not data.get("current_password") or not data.get("new_password"):
            return Response(
                data={
                    "message": "Please provide the current password and new password!"
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        user = authenticate(
            email=request.user.email, password=data.get("current_password")
        )

        if user is None:
            return Response(
                data={"message": "Invalid credentials!"},
                status=status.HTTP_403_FORBIDDEN,
            )

        user_object = User.objects.get(id=request.user.id)
        user_object.set_password(data.get("new_password"))
        user_object.save()

        return Response(data={"message": "Password updated successfully!"})

    def get_user_address(self, request):
        address_id = request.GET.get("id")
        if address_id:
            address_query_set = Address.objects.get(id=address_id)
            if address_query_set:
                serailized_data = UserAddressSerializer(address_query_set)
                return Response(data=serailized_data.data)
            return Response(data=None)
        else:
            address_query_set = Address.objects.filter(user=request.user)
            serailized_data = UserAddressSerializer(address_query_set, many=True)
            if serailized_data.data:
                return Response(data=serailized_data.data)
            return Response(data=[])

    def add_user_address(self, request):
        data: dict = request.data
        data["user"] = request.user

        if data.get("default"):
            old_df_addr = Address.objects.filter(default=True).first()
            if old_df_addr:
                old_df_addr.default = False
                old_df_addr.save()

        address_object = Address.objects.create(**data)
        address_object.save()
        return Response(status=status.HTTP_201_CREATED, data="Address Created")

    def edit_user_address(self, request):
        request_data = request.data
        address_id = request_data.get("id")

        if request_data.get("action") == "remove":
            try:
                Address.objects.filter(id=address_id).delete()
                return Response(data="Address deleted")

            except Address.DoesNotExist:
                return Response(data="Address not found")

        if request_data.get("action") == "edit":
            address_object = request_data.get("address_object")
            if address_object.get("default"):
                old_df_addr = Address.objects.filter(default=True).first()
                if old_df_addr:
                    old_df_addr.default = False
                    old_df_addr.save()

            address_record = Address.objects.filter(id=address_id)
            address_record.update(**address_object)

        return Response(data="Address updated")
