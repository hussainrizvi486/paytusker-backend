from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from apps.store.models.seller import SellerProfileRequest
from apps.store.serializers import SellerProfileRequestSerializer


class SellerProfileRequestViewSet(viewsets.ModelViewSet):
    queryset = SellerProfileRequest.objects.all()
    serializer_class = SellerProfileRequestSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # if self.request.user.is_staff:
        return SellerProfileRequest.objects.all()

    def perform_create(self, serializer):
        serializer.save()
