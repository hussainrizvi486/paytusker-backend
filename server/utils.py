from django.db import connection
from django.utils import timezone
import uuid
import random
import json
import os
from snowflake import SnowflakeGenerator

from apps.store.models.customer import Customer
from apps.store.models.product import Category, Product, ProductMedia


def exceute_sql_query(query: str, serialized=True):
    with connection.cursor() as cursor:
        cursor.execute(query)
        res = cursor.fetchall()
        columns = cursor.description
        columns = [col[0] for col in columns]
        rows = [dict(zip(columns, row)) for row in res]
        return rows


def generate_order_id():
    current_time = timezone.now()
    timestamp_str = current_time.strftime("%Y%m%d%H%M%S")
    timestamp_str = list(timestamp_str)
    random.shuffle(timestamp_str)
    unique_id = str(uuid.uuid4().hex)[:6]
    order_id = f"{''.join(timestamp_str)}-{unique_id}"
    return order_id


def get_category(q):
    try:
        category = Category.objects.get(name=q)
        return category
    except Category.DoesNotExist:
        return None


def chunks(lst, chunk_size):
    """Yield successive chunk_size-sized chunks from lst."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]


ID_GEN = SnowflakeGenerator(42)


def generate_snf_id():
    id = next(ID_GEN)
    return id


def format_currency(value):
    formatted_value = "0.00"
    try:
        formatted_value = "{:,.2f}".format(value)
    except Exception:
        formatted_value = "0.00"

    currency_symbol = "$"
    formatted_value = f"{currency_symbol}{formatted_value}"

    return formatted_value


from django.http import QueryDict


def load_request_body(data):
    if type(data) == QueryDict:
        return data.dict()

    body = data
    try:
        return json.loads(body)
    except Exception:
        return body
