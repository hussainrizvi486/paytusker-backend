from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ViewSet
from apps.store.models.order import Order, validated_status
from server.utils import load_request_body


class OrderWebhooks(ViewSet):
    def update_order_status(self, request):
        order_queryset = None
        data = load_request_body(request.data)
        order_id = data.get("order_id")
        order_status = data.get("order_status")
        if order_status not in validated_status:
            return Response(
                data={
                    "message": "Please provide a validated status",
                    "validated_status": validated_status,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            order_queryset = Order.objects.get(id=order_id)
            order_queryset.order_status = order_status
            order_queryset.save()

        except Order.DoesNotExist:
            return Response(data={"message": "No order found"})
