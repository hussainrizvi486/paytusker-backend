from rest_framework.permissions import BasePermission
from apps.store.models.customer import Customer


class IsCustomerUser(BasePermission):
    def has_permission(self, request, view):
        return Customer.objects.filter(user=request.user).exists()
