from django.db.models import Q
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view
import stripe
from datetime import datetime


from server.utils import exceute_sql_query
from apps.store.utils import get_customer
from apps.store.models.order import Order, OrderItems, OrderReview
from apps.store.models.customer import CartItem, Cart
from apps.store.models.product import Product
from apps.store.permissions import IsCustomerUser


stripe.api_key = "sk_test_51O2D7TSHIJhZN3ua8TrAYk0UhmTqadkUMggqLR0u9nvofMMVhZdoWMMThEpjPE66cBDDTdNQfA2S0VAv96bzLRgx00oepL2K7G"


@api_view(["GET"])
def test_payment(request):
    test_payment_intent = stripe.PaymentIntent.create(
        amount=1000,
        currency="pln",
        payment_method_types=["card"],
        receipt_email="test@example.com",
    )
    return Response(status=status.HTTP_200_OK, data=test_payment_intent)


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

        customer_cart.delete()
        cart_items.delete()

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


@permission_classes([IsCustomerUser])
class CustomerFunctions(ViewSet):
    def check_review_data(self, data: dict, customer):
        product_id = Product.objects.filter(id=data.get("product_id")).first()
        order_id = Order.objects.filter(order_id=data.get("order_id")).first()

        if OrderReview.objects.filter(
            product=product_id, customer=customer, order=order_id
        ).exists():
            return "Review already exists", False

        return "", True

    def add_order_review(self, request):
        req_data: dict = request.data
        if req_data:
            customer = get_customer(request.user)
            message, validated = self.check_review_data(req_data, customer)
            if not validated:
                return Response(data=message)

            review = OrderReview.objects.create(
                customer=customer,
                order=Order.objects.get(order_id=req_data.get("order_id")),
                product=Product.objects.get(id=req_data.get("product_id")),
                rating=req_data.get("rating"),
                review_content=req_data.get("review_content"),
            )
            review.save()

            return Response(data="Review Added", status=status.HTTP_201_CREATED)
        return Response(data="Data is missing", status=status.HTTP_204_NO_CONTENT)

    def get_order_review(
        self,
        request,
    ):

        filters = request.GET.get("filters") or {}
        customer = get_customer(request.user)
        response_data = []
        orders_reviews = OrderReview.objects.filter(customer=customer)
        for review in orders_reviews:
            response_data.append(
                {
                    "product_name": review.product.product_name,
                    "product_image": review.product.cover_image,
                    "order_id": review.order.order_id,
                    "order_date": review.order.order_date.strftime("%d-%m-%Y"),
                    "review_date": review.creation.strftime("%d-%m-%Y"),
                    "review_content": review.review_content,
                    "rating": review.rating,
                }
            )
        return Response(data=response_data)
