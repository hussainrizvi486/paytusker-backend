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


def update_products():
    SERVER_URL = "https://crm.paytusker.us"
    file_path = os.path.join(os.path.dirname(__file__), "../products.json")
    json_data = json.load(open(file_path))
    products_data = json_data["data"][:1000]

    for chunk in chunks(products_data, 100):
        bulk_products = []
        bulk_product_images = []

        for product in chunk:
            category = get_category(product.get("item_group"))
            images = product.get("images")
            cover_image = ""
            if images:
                cover_image = f"{SERVER_URL}{images.pop(0)}"

            db_product = Product(
                product_name=product.get("item_name"),
                price=product.get("custom_website_price"),
                description=product.get("item_name"),
                cover_image=cover_image,
                category=category,
                stock=1,
            )
            bulk_products.append(db_product)

            if images:
                for img in images:
                    image_url = f"{SERVER_URL}{img}"
                    bulk_product_images.append(
                        ProductMedia(image_url=image_url, product=db_product)
                    )

        Product.objects.bulk_create(bulk_products)
        ProductMedia.objects.bulk_create(bulk_product_images)


ID_GEN = SnowflakeGenerator(42)


def generate_snf_id():
    id = next(ID_GEN)
    return id
