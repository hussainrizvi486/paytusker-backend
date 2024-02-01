from .serializers import AccountsTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
import json
from django.http import JsonResponse
from django.core.validators import EmailValidator
from django.shortcuts import render
from rest_framework.views import APIView, Response
from rest_framework.decorators import api_view
from .models import User


class Register(APIView):
    def post(self, request):
        # request_data: dict = request.data
        # first_name = request_data.get("first_name")
        # last_name = request_data.get("last_name")
        # email = request_data.get("email")
        # phone = request_data.get("phone")
        # username = request_data.get("username")
        # password = request_data.get("password")

        # if not first_name:
        #     return JsonResponse({"message": "first name required"})

        # if not last_name:
        #     return JsonResponse({"message": "last name required"})

        # if not email:
        #     return JsonResponse({"message": "email required"})

        # if not phone:
        #     return JsonResponse({"message": "phone required"})

        # if not password:
        #     return JsonResponse({"message": "password required"})

        # user = User.objects.create(
        #     first_name=first_name,
        #     last_name=last_name,
        #     username=username,
        #     email=email,
        #     phone_number=phone,
        #     password=password,
        # )
        # user.save()

        # if user:
        return JsonResponse({"message": "user created successfully", "success": True})

        return JsonResponse({"message": "error while creating user", })


class AccountsTokenObtainPairView(TokenObtainPairView):
    serializer_class = AccountsTokenObtainPairSerializer
