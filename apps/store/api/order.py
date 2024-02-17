from apps.store.models.order import Order, OrderItems
from apps.store.models.customer import CartItem, Cart
from apps.store.models.product import Product
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from apps.store.utils import get_customer
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core import serializers
from rest_framework import status
from server.utils import exceute_sql_query


@permission_classes([IsAuthenticated])
class OrderApi(ViewSet):
    def create_order(self, request):
        data = request.data
        customer = get_customer(user=request.user)
        if not customer:
            return Response(data="User is not a customer")

        customer_cart = Cart.objects.get(customer=customer)
        cart_items = CartItem.objects.all().filter(cart=customer_cart)

        order = Order.objects.create()
        order.customer = customer
        order.order_status = "001"
        order.payment_method = str(data.get("payment_method") or "")
        order.payment_status = False
        for item in cart_items:
            OrderItems.objects.create(
                order=order,
                item=item.item,
                qty=item.qty,
            )

        order.save()

        return Response(status=200, data=order.id)

    def get_customer_orders(self, request):
        customer = get_customer(request.user)
        orders_qs = Order.objects.filter(customer=customer)
        data = []
        if orders_qs:
            for order in orders_qs:
                order_dict = {
                    "order_id": order.order_id,
                    "grand_total": order.grand_total,
                    "total_qty": order.total_qty,
                    "order_date": order.order_date,
                    "delivery_date": order.delivery_date,
                    "payment_status": order.payment_status,
                    "payment_method": order.payment_method,
                    "delivery_status": order.delivery_status,
                    "order_status": order.order_status,
                }
                order_items = exceute_sql_query(
                    f"""SELECT
                        p.product_name,
                        p.cover_image,
                        oi.rate,
                        oi.qty,
                        oi.amount
                    FROM
                        store_orderitems oi
                        INNER JOIN store_product p ON oi.item_id = p.id
                    WHERE
                        oi.order_id = '{order.id}' """
                )

                order_dict["items"] = order_items

                data.append(order_dict)

            return Response(data=data, status=status.HTTP_200_OK)
