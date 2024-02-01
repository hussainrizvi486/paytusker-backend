from django.db import connection
from django.utils import timezone
import uuid
import random
import json
import os
from snowflake import SnowflakeGenerator

from apps.store.models.customer import Customer
from apps.store.models.product import Category, Product, ProductImages

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


def update_products():
    Product.objects.all().delete()
    SERVER_URL = "https://crm.paytusker.us"
    file_path = os.path.join(os.path.dirname(__file__), "../../products.json")
    json_data = json.load(open(file_path))
    products_data = json_data["data"][:100]

    for product in products_data:
        category = get_category(product.get("item_group"))
        images = product.get("images")
        cover_image = f"{SERVER_URL}{images.pop(0)}"
        db_product = Product.objects.create(
            product_name=product.get("item_name"),
            price=product.get("custom_website_price"),
            description=product.get("item_name"),
            cover_image=cover_image,
            category=category,
            stock=1,
        )

        if db_product and images:
            for img in images:
                image_url = f"{SERVER_URL}{img}"
                ProductImages.objects.create(image_url=image_url, product=db_product)


ID_GEN = SnowflakeGenerator(42)


def generate_snf_id():
    id = next(ID_GEN)
    return id
