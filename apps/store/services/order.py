from typing import List, Dict
from decimal import Decimal
from apps.store.models import Cart
from apps.store.models.product import Product
from apps.store.models.orders import SellerDigitalOrderItem, SellerDigitalOrder
from apps.store.models.order import (
    Customer,
    Order,
    OrderItems,
    DigitalOrder,
    DigitalOrderItem,
    DigitalOrderStatusChoices,
    OrderStatusChoices,
)


class ProcessCheckoutOrder:
    def __init__(self, checkout_data: dict) -> None:
        self.shipping_address: str = checkout_data.get("shipping_address")
        self.payment_method: str = checkout_data.get("payment_method")
        self.customer: str = checkout_data.get("customer")
        self.items_ordered: List[Dict] = checkout_data.get("items_ordered")
        self.customer_queryset = Customer.objects.get(id=self.customer)
        self.digital_order_status = DigitalOrderStatusChoices
        self.physical_order_status = OrderStatusChoices

    def process_orders(self):
        self.clear_customer_cart()
        self.create_customer_orders()

    def clear_customer_cart(self):
        Cart.objects.filter(customer=self.customer_queryset).delete()

    def create_customer_orders(self):
        items: List[Dict] = self.items_ordered
        product_id = [i.get("product_id") for i in items]
        items_lookup = {
            i.get("product_id"): {"rate": i.get("rate"), "qty": i.get("qty")}
            for i in items
        }
        products_data = list(
            Product.objects.filter(id__in=product_id).values(
                "id", "net_price", "is_digital"
            )
        )
        digital_products: List[Dict] = []
        physical_products: List[Dict] = []

        for product in products_data:
            item_data = items_lookup.get(product.get("id"))
            if item_data:
                product.update(item_data)

            if product.get("is_digital"):
                digital_products.append(product)
            else:
                physical_products.append(product)

        if physical_products:
            order_queryset = Order.objects.create(
                customer=self.customer_queryset,
                delivery_address_id=self.shipping_address,
                order_status=self.physical_order_status.ORDER_PENDING,
                payment_status=True,
                payment_method=self.payment_method,
            )
            order_queryset.save()

            for row in physical_products:
                item_queryset = OrderItems.objects.create(
                    item_id=row.get("id"),
                    order=order_queryset,
                    rate=Decimal(row.get("rate")),
                    qty=Decimal(row.get("qty")),
                )
                item_queryset.save()

            order_queryset.save()

        if digital_products:
            order_queryset = DigitalOrder.objects.create(
                customer=self.customer_queryset,
                payment_status=True,
                payment_method=self.payment_method,
                order_status=self.digital_order_status.PLACED,
            )
            order_queryset.save()
            for row in digital_products:
                item_queryset = DigitalOrderItem.objects.create(
                    product_id=row.get("id"),
                    order=order_queryset,
                    rate=Decimal(row.get("rate")),
                    qty=Decimal(row.get("qty")),
                )
                item_queryset.save()
            order_queryset.save()
            self.create_seller_digital_orders(order_queryset)

    def create_seller_digital_orders(self, order_queryset: DigitalOrder):
        seller_wise_orders = {}
        items_queryset = DigitalOrderItem.objects.filter(
            order=order_queryset
        ).select_related("product")

        for item in items_queryset:
            seller = str(item.product.seller.id)
            if seller not in seller_wise_orders.keys():
                seller_wise_orders[seller] = []

            seller_wise_orders[seller].append(item.id)

        for seller, item_ids in seller_wise_orders.items():
            seller_order = SellerDigitalOrder.objects.create(
                seller_id=seller,
                order_items=item_ids,
                customer=order_queryset.customer,
            )
            seller_order.save()
            seller_orderitems = []
            for id in item_ids:
                item_object = items_queryset.filter(id=id).first()
                rate = item_object.product.net_price
                seller_orderitems.append(
                    SellerDigitalOrderItem(
                        product=item_object.product,
                        order=seller_order,
                        qty=item_object.qty,
                        rate=rate,
                        amount=rate * item_object.qty,
                    )
                )

            SellerDigitalOrderItem.objects.bulk_create(seller_orderitems)
            seller_order.save()
