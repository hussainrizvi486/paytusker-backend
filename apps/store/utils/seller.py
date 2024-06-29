from ..models import Seller


def get_session_seller(user):
    try:
        seller = Seller.objects.get(user=user)
        return seller
    except Seller.DoesNotExist:
        return None


