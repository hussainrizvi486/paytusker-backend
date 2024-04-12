from apps.store.models.customer import Customer
from apps.store.models.common import Category
from apps.store.models import ModelMedia
from django.conf import settings
from apps.store.models.customer import Cart


def get_customer(user):
    try:
        return Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        return False


def get_customer_cart(customer):
    if not customer:
        raise ValueError("please p")
    try:
        return Cart.objects.get(customer=customer)
    except Cart.DoesNotExist:
        return Cart.objects.create(customer=customer)


def get_category(category_id=None, category_name=None):
    if category_id:
        return Category.objects.filter(id=category_id).first() or None
    if category_name:
        return Category.objects.filter(name__icontains=category_name).first() or None
    return None


def get_serialized_model_media(model_name, id, request=None):
    media_query_set = ModelMedia.objects.filter(model_name=model_name, field_id=id)
    media_data = []
    if media_query_set:
        media_data = [
            get_full_file_url(obj.file.url, request) for obj in media_query_set
        ]
    return media_data


def get_full_file_url(file_url, request=None):
    if request:
        return request.build_absolute_uri(file_url)
    else:
        return file_url
