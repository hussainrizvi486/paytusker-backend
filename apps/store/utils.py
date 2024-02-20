from apps.store.models.customer import Customer
from snowflake import SnowflakeGenerator


def get_customer(user):
    try:
        return Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        return False
