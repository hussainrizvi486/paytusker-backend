from rest_framework.permissions import BasePermission
from apps.store.models.customer import Customer
from apps.store.models import Seller


class IsCustomerUser(BasePermission):
    def has_permission(self, request, view):
        return Customer.objects.filter(user=request.user).exists()


class IsSellerUser(BasePermission):
    def has_permission(self, request, view):
        return Seller.objects.filter(user=request.user).exists()
