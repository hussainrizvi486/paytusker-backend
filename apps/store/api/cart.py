from rest_framework.viewsets import ViewSet
from apps.store.models.customer import Customer, Cart, CartItem
from apps.store.models.product import Product
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils import tree
from decimal import Decimal
from apps.store.utils import get_customer
from json import loads
from rest_framework import status
from django.shortcuts import get_object_or_404


@permission_classes([IsAuthenticated])
class CartApi(ViewSet):
    def add_to_cart(self, request):
        user = request.user
        data: dict = request.data
        product_id = data.get("product_id")
        qty = data.get("qty") or 1
        product = Product.objects.get(id=product_id)

        customer = get_customer(user)

        cart, created = Cart.objects.get_or_create(customer=customer)

        try:
            cart_item = CartItem.objects.get(item=product, cart=cart)
            cart_item_qty = Decimal(cart_item.qty)
            cart_item.qty += qty
            cart_item.rate = product.price
            cart_item.amount = product.price * cart_item_qty
            cart_item.save()
        except CartItem.DoesNotExist:
            new_cart_item = CartItem.objects.create(
                item=product,
                cart=cart,
                rate=product.price,
                qty=qty,
                amount=(product.price * qty),
            )
            new_cart_item.save()

        return Response("Cart updated/created", status=status.HTTP_200_OK)

    def get_cart_detail(self, request):
        user = request.user
        response_obj = {}
        customer = get_customer(user)
        cart = Cart.objects.filter(customer=customer).first()

        if not cart:
            return Response(data=[])

        from server.utils import exceute_sql_query

        query = f"""SELECT
                        ci.id,
                        ci.qty,
                        ci.rate,
                        p.cover_image,
                        p.product_name,
                        ci.amount
                    FROM
                        store_cartitem ci
                    INNER JOIN store_product p on p.id = ci.item_id 
                    WHERE ci.cart_id = '{cart.id}'
                    """
        cart_items = exceute_sql_query(query)
        response_obj["items"] = cart_items
        response_obj["total_qty"] = cart.total_qty
        response_obj["total_amount"] = cart.total_amount

        return Response(data=response_obj)

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

    # def remove_cart
