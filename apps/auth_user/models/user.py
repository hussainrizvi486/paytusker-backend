import string
import random
from uuid import uuid4
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.hashers import make_password


def generate_password(length=9):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


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
    modified = models.DateTimeField(auto_now=True, null=True)
    verified = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        return str(self.email)

    def get_user_roles(self):
        roles = [obj.role for obj in self.roles.all()]
        return roles

    def has_role(self, role):
        roles = self.get_user_roles()
        return role in roles


class UserRoles(models.Model):
    class RoleChoices(models.TextChoices):
        SELLER = "seller", "Seller"
        CUSTOMER = "customer", "Customer"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="roles")
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        null=False,
        blank=False,
    )

    def __str__(self) -> str:
        return f"""{self.user.get_full_name()} | {self.role}"""
