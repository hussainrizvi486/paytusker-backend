from rest_framework.serializers import ModelSerializer
from ..models.order import Order, OrderItems


class OrderDetailSerailizer(ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "delivery_address",
            "grand_total",
            "total_qty",
            "delivery_status",
            "payment_status",
            "payment_method",
            "customer",
            "order_date",
            "delivery_date",
            "order_status",
        ]
