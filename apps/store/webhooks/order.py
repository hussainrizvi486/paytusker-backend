from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ViewSet
from apps.store.models.order import Order, validated_status
from server.utils import load_request_body
from django.shortcuts import get_object_or_404


class OrderWebhooks(ViewSet):
    def update_order_status(self, request):
        data = load_request_body(request.data)
        order_id = data.get("order_id")
        order_status = data.get("order_status")

        if order_status not in validated_status:
            return Response(
                data={
                    "message": "Please provide a validated status",
                    "validated_status": validated_status,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        order = get_object_or_404(Order, id=order_id)
        order.order_status = order_status
        order.save()

        return Response(
            data={"message": "Order status updated successfully"},
            status=status.HTTP_200_OK,
        )
