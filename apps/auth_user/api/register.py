from rest_framework.response import Response
from rest_framework import status, views

from ..models import User, UserRoles


class RegisterUser(views.APIView):
    def post(self, request):
        user_object: dict = request.data
        if not user_object:
            return Response("Please send user object", status=status.HTTP_403_FORBIDDEN)

        required_fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "phone",
            "password",
        ]

        for field in required_fields:
            if field not in user_object.keys():
                return Response(
                    f"{field} is missing.", status=status.HTTP_403_FORBIDDEN
                )
        email_exists = User.objects.filter(email=user_object.get("email")).exists()
        if email_exists:
            return Response(
                "The email is already in use.", status=status.HTTP_403_FORBIDDEN
            )

        phone_exists = User.objects.filter(
            phone_number=user_object.get("phone")
        ).exists()

        if phone_exists:
            return Response(
                "The phone number is already in use.", status=status.HTTP_403_FORBIDDEN
            )

        user = User.objects.create_user(
            first_name=user_object.get("first_name"),
            last_name=user_object.get("last_name"),
            username=user_object.get("username"),
            email=user_object.get("email"),
            phone_number=user_object.get("phone"),
            password=user_object.get("password"),
        )

        user.save()
        UserRoles.objects.create(user=user, role="customer")
        from apps.store.models.customer import Customer
        if user:
            Customer.objects.create(
                user=user, customer_name=f"{user.first_name} {user.last_name}"
            )
        return Response({"message": "user registered"}, status=200)

    def validate_user_object(self, user_object: dict):
        if not self.validate_email(user_object.get("email")):
            raise Exception("email is not vaild")

        if len(user_object.get("phone")) < 8:
            raise Exception("Password is to short")

        return user_object

    def validate_email(self, email):
        "first we have validate email with RE"

        user = User.objects.filter(email=email)

        if user:
            raise Exception("email already taken")

        return True
