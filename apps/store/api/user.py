from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, views

from server.utils import load_request_body
from apps.auth_user.models import User
from ..models import UserAddress
from ..serializers import UserAddressSerializer


def set_default_address(user, address):
    UserAddress.objects.filter(user__id=user).exclude(id=address).update(default=False)


class UserAddressViewSet(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        address_data = []
        if request.GET.get("id"):
            queryset = UserAddress.objects.get(id=request.GET.get("id"))
            if queryset:
                serializer = UserAddressSerializer(queryset)
                address_data = serializer.data
        else:
            queryset = UserAddress.objects.filter(user__id=request.user.id)
            if queryset:
                serializer = UserAddressSerializer(queryset, many=True)
                address_data = serializer.data
        return Response(data=address_data)

    def post(self, request):
        clean_data = load_request_body(request.data)
        user_queryset = User.objects.get(id=request.user.id)
        clean_data["user"] = user_queryset
        address_object = UserAddress.objects.create(**clean_data)
        address_object.save()
        if address_object.default:
            set_default_address(request.user.id, address_object.id)

        return Response(data={"message": "Address created successfully"})

    def put(self, request):
        clean_data = load_request_body(request.data)
        id = clean_data.get("id")
        del clean_data["id"]
        UserAddress.objects.filter(id=id).update(**clean_data)
        if clean_data.get("default"):
            set_default_address(request.user.id, id)
        return Response(data={"message": "Address updated successfully"})

    def delete(self, request):
        body = load_request_body(request.data)
        address_id = body.get("id")
        if address_id:
            UserAddress.objects.filter(id=address_id).delete()
            return Response(data={"message": "Address deleted successfully"})

        return Response(
            data={"message": "Please provide address id"},
            status=status.HTTP_403_FORBIDDEN,
        )
