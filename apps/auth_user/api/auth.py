from django.conf import settings
from django.http import HttpRequest
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.template.loader import render_to_string
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework import viewsets, status, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes


from ..serializers import AuthTokenSerializer
from ..models import User, LoginHistory


def get_client_ip(request: HttpRequest):
    x_forwarded_for: str = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[-1].strip()
    else:
        ip = request.META.get("REMOTE_ADDR", "")
    return ip


def create_login_log(user, device="", ip=""):
    try:
        log_object = LoginHistory.objects.create(
            user=user,
            device=device,
            ip=ip,
        )
        log_object.save()
    except Exception:
        return


class LoginViewSet(viewsets.ViewSet):
    @classmethod
    def validate_auth_data(self, data: dict):
        required_fields = ["email", "password"]
        for key in required_fields:
            if key not in data.keys():
                return False
        return True

    @classmethod
    def get_jwt_tokens(self, user):
        refresh = AuthTokenSerializer.get_token(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def jwt_login(self, request: HttpRequest):
        data: dict = request.data

        if not self.validate_auth_data(data):
            return Response(
                data={"message": "Invalid request data"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = authenticate(email=data.get("email"), password=data.get("password"))
        if user is not None:
            tokens = self.get_jwt_tokens(user)
            create_login_log(
                user,
                request.META.get("HTTP_USER_AGENT", ""),
                get_client_ip(request),
            )
            return Response(
                data={"tokens": tokens, "message": "Login success"},
                status=status.HTTP_200_OK,
            )

        return Response(
            data={"message": "Invaid user credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    @permission_classes([IsAuthenticated])
    def update_password(self, request):
        request_data: dict = request.data
        request_user: User = request.user
        current_password = request_data.get("current_password")
        new_password = request_data.get("new_password")
        if (
            current_password
            and new_password
            and authenticate(email=request_user.email, password=current_password)
        ):
            user = User.objects.get(id=request_user.id)
            user.set_password(new_password)
            user.save()
            return Response(data={"message": "Password updated successfully"})

        else:
            return Response(
                data={"message": "Invalid password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class PasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ["email"]

    def validate(self, attrs: dict):
        try:
            generator = PasswordResetTokenGenerator()
            user = User.objects.get(email=attrs.get("email"))
            token = generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.id))

            # reset_url = (
            #     f"https://paytusker.com/login/password/reset?uid={uid}&token={token}"
            # )
            reset_url = (
                f"http://localhost:5173/login/password/reset?uid={uid}&token={token}"
            )
            message = render_to_string(
                "email/password_reset_email.html",
                {
                    "username": user.username,
                    "reset_url": reset_url,
                },
            )
            send_mail(
                subject="Password Reset",
                message="",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=message,
            )
        except User.DoesNotExist:
            raise ValidationError("User not exists!")
        return super().validate(attrs)


class ResetForgotPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=20)

    def validate(self, attrs: dict):
        try:
            context = self.context
            user_id = smart_str(urlsafe_base64_decode(context.get("uid")))
            user = User.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(
                token=context.get("token"), user=user
            ):
                raise ValidationError("Token is not valid")

            user.set_password(attrs.get("new_password"))
            user.save()

            return super().validate(attrs)

        except Exception:
            PasswordResetTokenGenerator().check_token(user, context.get("token"))
            raise ValidationError("Token is not valid")


#
class ResetForgotPassword(APIView):
    def post(self, request, uid, token):
        serializer = ResetForgotPasswordSerializer(
            data=request.data,
            context={
                "uid": uid,
                "token": token,
            },
        )
        serializer.is_valid(raise_exception=True)
        return Response(data={"message": "Passowrd reset successfully!"})


class ForgotPasswordAPI(APIView):
    def post(self, request):
        serializer = PasswordResetEmailSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return Response(data={"message": "Password reset link sended to email"})


class TokenValidationAPI(viewsets.ViewSet):
    def validate_password_reset_token(self, request: HttpRequest):
        try:
            request_params = request.GET
            user_id = smart_str(urlsafe_base64_decode(request_params.get("uid")))
            user = User.objects.filter(id=user_id).first()

            if not user:
                return Response(
                    data={"message": "Token is not valid"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            token = request_params.get("token")
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response(
                    data={"message": "Token is not valid"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            return Response(
                data={"message": "Token is valid"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                data={"message": "Token is not valid", "exe": e},
                status=status.HTTP_403_FORBIDDEN,
            )
