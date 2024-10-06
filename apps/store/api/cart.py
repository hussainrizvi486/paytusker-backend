from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from decimal import Decimal
from json import loads
from apps.store.utils import get_customer
from server.utils import exceute_sql_query
from apps.store.models.customer import Cart, CartItem
from apps.store.models.product import Product


@permission_classes([IsAuthenticated])
class CartApi(ViewSet):
    def add_to_cart(self, request):
        user = request.user
        data: dict = request.data
        product_id = data.get("product_id")
        qty = data.get("qty") or 1
        product = Product.objects.get(id=product_id)
        customer = get_customer(user)
        if not customer:
            return Response(
                data={"message": "only customer can add products to cart"},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )
        cart, created = Cart.objects.get_or_create(customer=customer)
        try:
            cart_item = CartItem.objects.get(product=product, cart=cart)
            cart_item_qty = Decimal(cart_item.qty)
            cart_item.qty += qty
            cart_item.rate = product.price
            cart_item.amount = product.price * cart_item_qty
            cart_item.save()

        except CartItem.DoesNotExist:
            new_cart_item = CartItem.objects.create(
                product=product,
                cart=cart,
                rate=product.price,
                qty=qty,
                amount=(product.price * qty),
            )
            new_cart_item.save()

        return Response("Cart updated/created", status=status.HTTP_200_OK)

    def get_cart_detail(self, request):
        user = request.user
        user_cart_data = {"items": None, "total_qty": 0, "total_amount": 0}
        customer = get_customer(user)
        cart_object = Cart.objects.filter(customer=customer).first()

        if not cart_object:
            return Response(data=user_cart_data)

        cart_items_queryset = CartItem.objects.prefetch_related("product").filter(
            cart=cart_object
        )
        if cart_items_queryset:
            user_cart_data["items"] = []
            for item in cart_items_queryset:
                user_cart_data["items"].append(
                    {
                        "id": item.id,
                        "qty": item.qty,
                        "product_id": item.product.id,
                        "rate": item.rate,
                        "amount": item.amount,
                        "formatted_amount": item.amount,
                        "formatted_rate": item.rate,
                        "product_name": item.product.product_name,
                        "cover_image": self.request.build_absolute_uri(
                            item.product.cover_image.url
                        ),
                    }
                )

        user_cart_data["total_qty"] = cart_object.total_qty
        user_cart_data["total_amount"] = cart_object.total_amount

        return Response(data=user_cart_data)

    def update_cart_item(self, request):
        data = loads(self.request.body)
        cart_item_id = data.get("cart_item_id")
        qty = Decimal(data.get("qty") or 1)
        cart_item = get_object_or_404(CartItem, id=cart_item_id)

        if data.get("action") == "increase":
            cart_item.qty += qty
            cart_item.save()

        elif data.get("action") == "decrease":
            if cart_item.qty == 1:
                cart_item.delete()
            else:
                cart_item.qty -= qty
                cart_item.save()

        elif data.get("action") == "remove":
            cart_item.delete()
            cart = Cart.objects.get(id=cart_item.cart.id)
            cart.total_amount = 0
            cart.total_qty = 0
            cart.save()

        return Response(data={"message": "Cart Updated"}, status=status.HTTP_200_OK)
