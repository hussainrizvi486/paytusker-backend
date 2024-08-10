from ..models import Seller


def get_session_seller(user_id):
    try:
        seller = Seller.objects.get(user__id=user_id)
        return seller
    except Seller.DoesNotExist:
        return None
