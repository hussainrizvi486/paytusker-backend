from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import json
from server.utils import exceute_sql_query
from apps.store.utils import get_customer, get_serialized_model_media
from apps.store.models.order import Order, OrderItems, OrderReview
from apps.store.models.customer import CartItem, Cart
from apps.store.models.product import Product
from apps.store.models.base import ModelMedia
from apps.store.permissions import IsCustomerUser
from apps.accounts.models import Address


@permission_classes([IsAuthenticated])
class OrderApi(ViewSet):
    def create_order(self, request):
        data = request.data
        customer = get_customer(user=request.user)
        if not customer:
            return Response(data="User is not a customer")

        delivery_address = Address.objects.get(id=data.get("delivery_address"))
        customer_cart = Cart.objects.get(customer=customer)
        cart_items = CartItem.objects.all().filter(cart=customer_cart)

        order = Order.objects.create(
            customer=customer,
            order_status="001",
            payment_method=str(data.get("payment_method")),
            payment_status=False,
            delivery_address=delivery_address,
        )

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
        filters = {}

        if request.GET.get("filters"):
            try:
                filters = json.loads(filters)
            except Exception:
                filters = {}

        orders_qs = Order.objects.filter(customer=customer).order_by("-creation")

        if filters.get("order_status"):
            orders_qs.filter(order_status=filters.get("order_status"))

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

                order_items_qs = OrderItems.objects.filter(order=order).order_by(
                    "-creation"
                )
                order_items = []
                for oi in order_items_qs:
                    order_items.append(
                        {
                            "product_name": oi.item.product_name,
                            "cover_image": self.request.build_absolute_uri(
                                oi.item.cover_image.url
                            ),
                            "rate": oi.rate,
                            "qty": oi.qty,
                            "amount": oi.amount,
                        }
                    )

                # order_items = exceute_sql_query(
                #     f"""SELECT
                #         p.product_name,
                #         p.cover_image,
                #         oi.rate,
                #         oi.creation,
                #         oi.qty,
                #         oi.amount
                #     FROM
                #         store_orderitems oi
                #         INNER JOIN store_product p ON oi.item_id = p.id
                #     WHERE
                #         oi.order_id = '{order.id}'
                #     ORDER BY DATE(oi.creation) DESC
                #     """
                # )

                order_dict["items"] = order_items
                data.append(order_dict)

        return Response(data=data, status=status.HTTP_200_OK)


@permission_classes([IsCustomerUser])
class CustomerFunctions(ViewSet):
    def check_review_data(self, data: dict, customer):
        product_id = Product.objects.get(id=data.get("product_id"))
        order_item = OrderItems.objects.get(id=data.get("id"))

        if OrderReview.objects.filter(
            product=product_id, customer=customer, order_item=order_item
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

            order_item = OrderItems.objects.get(id=req_data.get("id"))

            review = OrderReview.objects.create(
                customer=customer,
                order=order_item.order,
                order_item=order_item,
                product=order_item.item,
                rating=req_data.get("rating"),
                review_content=req_data.get("review_content"),
            )

            def filter_media_keys(key):
                if str(key).startswith("review_media"):
                    return True
                return False

            review.save()
            order_item.has_review = True
            order_item.save()
            review_media_keys = filter(filter_media_keys, req_data.keys())
            if review_media_keys:
                for key in review_media_keys:
                    if req_data.get(key):
                        ModelMedia.objects.create(
                            model_name="OrderReview",
                            file=req_data.get(key),
                            field_id=review.id,
                        )

            return Response(data="Review Added", status=status.HTTP_201_CREATED)
        return Response(data="Data is missing", status=status.HTTP_204_NO_CONTENT)

    def get_order_review(
        self,
        request,
    ):
        filters = request.GET.get("filters") or {}
        customer = get_customer(request.user)
        response_data = []
        orders_reviews = OrderReview.objects.filter(customer=customer).order_by(
            "-creation"
        )

        for review in orders_reviews:
            response_data.append(
                {
                    "product_name": review.product.product_name,
                    "product_image": request.build_absolute_uri(
                        review.product.cover_image.url
                    ),
                    "order_id": review.order.order_id,
                    "order_date": review.order.order_date.strftime("%d-%m-%Y"),
                    "review_date": review.creation.strftime("%d-%m-%Y"),
                    "review_content": review.review_content,
                    "rating": review.rating,
                    "review_media": get_serialized_model_media(
                        "OrderReview", review.id, request
                    ),
                }
            )

        if response_data:
            return Response(data={"reviews": response_data, "message": ""})

        return Response(
            data={"reviews": None, "message": "No Reviews Found"},
        )

    def to_review_items(self, request):
        customer = get_customer(request.user)
        order_items = OrderItems.objects.filter(
            order__customer=customer, has_review=False
        )
        data = []

        for row in order_items:
            data.append(
                {
                    "order_id": row.order.order_id,
                    "product_name": row.item.product_name,
                    "product_image": request.build_absolute_uri(
                        row.item.cover_image.url
                    ),
                    "product_id": row.item.id,
                    "amount": row.amount,
                    "qty": row.qty,
                    "rate": row.rate,
                    "id": row.id,
                }
            )

        if data:
            return Response(data={"reviews": data})

        return Response(data={"reviews": None})
