from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Address


admin.site.register(Address)


@admin.register(User)
class UserAdminView(UserAdmin):
    list_display = ["email", "username", "phone_number"]
    list_filter = ["date_joined"]

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            ("Personal info"),
            {"fields": ("image", "first_name", "last_name", "email", "phone_number")},
        ),
        (
            ("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "username",
                    "email",
                    "phone_number",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_superuser",
                    "is_active",
                )
            },
        ),
        (
            "Password",
            {
                "fields": (
                    "password1",
                    "password2",
                )
            },
        ),
    )
