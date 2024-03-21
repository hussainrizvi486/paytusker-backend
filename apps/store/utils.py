from apps.store.models.customer import Customer
from apps.store.models.common import Category


def get_customer(user):
    try:
        return Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        return False


def get_category(category_id=None, category_name=None):
    if category_id:
        return Category.objects.filter(id=category_id).first() or None
    if category_name:
        return Category.objects.filter(name__icontains=category_name).first() or None
    return None
