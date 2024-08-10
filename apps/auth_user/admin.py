from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserRoles, LoginHistory


@admin.register(UserRoles)
class UserRoleAdmin(admin.ModelAdmin):
    def __init__(self, model: type, admin_site: admin.AdminSite | None) -> None:
        super().__init__(model, admin_site)
        self.opts.verbose_name_plural = "User Roles"


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    def __init__(self, model: type, admin_site: admin.AdminSite | None) -> None:
        super().__init__(model, admin_site)
        self.opts.verbose_name_plural = "User Login History"


@admin.register(User)
class UserAdminView(UserAdmin):
    def __init__(self, model: type, admin_site: admin.AdminSite | None) -> None:
        super().__init__(model, admin_site)
        self.opts.verbose_name_plural = "User"

    list_display = ["email", "username", "phone_number", "id"]
    list_filter = ["date_joined", "username", "phone_number", "email"]
    ordering = ["-date_joined"]

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
