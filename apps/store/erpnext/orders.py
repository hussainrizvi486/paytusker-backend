import requests
import json
from apps.store.models.order import Order, OrderItems
from server.settings import ERPNEXT_API_URL
from apps.store.models import StoreErrorLogs
from django.core.serializers.json import DjangoJSONEncoder


def get_order_items(order_queryset: Order):
    serailized_data = []
    orderitems_queryset = OrderItems.objects.filter(order=order_queryset)

    for row in orderitems_queryset:
        serailized_data.append(
            {
                "product_id": row.item.id,
                "quantity": row.qty,
                "net_rate": row.item.net_price,
                "rate": row.item.price,
                "commission_percent": row.item.commission_rate,
                "commission_rate": row.item.price - row.item.net_price,
            }
        )

    return serailized_data


def sync_order(order_queryset: Order):
    try:
        order_items = get_order_items(order_queryset)
        body = {
            "customer": order_queryset.customer.customer_name,
            "phone_number": order_queryset.customer.user.phone_number,
            "order_date": order_queryset.order_date.strftime("%Y-%m-%d"),
            "customer_address": order_queryset.delivery_address.get_address_html(),
            "items": order_items,
        }

        res = requests.post(
            f"{ERPNEXT_API_URL}api/method/paytusker.django-integration.order.create_website_order",
            data=json.dumps(body, cls=DjangoJSONEncoder),
        )
        StoreErrorLogs.objects.create(log=f"""{res.status_code} \n\n {res.text}""")
    except Exception as e:
        StoreErrorLogs.objects.create(log=f"""{e}""")

    return
