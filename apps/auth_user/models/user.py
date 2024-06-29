from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from uuid import uuid4


class UserManager(BaseUserManager):
    def create_user(self, email, phone_number=None, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        password = make_password(password)
        user.password = password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, phone_number, password, **extra_fields)


class User(AbstractUser):
    id = models.CharField(
        default=uuid4, primary_key=True, editable=False, unique=True, max_length=999
    )
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=False, null=False)
    phone_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    verified = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        return self.username or self.email or self.id

    def get_user_roles(self):
        roles = []
        if hasattr(self, "userroles_set"):
            roles = [obj.role for obj in self.userroles_set.all()]
        return roles


class UserRoles(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(
        choices=(
            ("seller", "seller"),
            ("customer", "customer"),
        ),
        null=False,
        blank=False,
    )

    def __str__(self) -> str:
        return f"""{self.user.get_full_name()} | {self.role}"""
