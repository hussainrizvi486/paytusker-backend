from rest_framework import views
from rest_framework.response import Response
from ...permissions import IsSellerUser
from ...utils import get_session_seller
from ...models import Product
from ...serializers import SellerProductListingSerializer
from django.db import connection


class ListSellerProducts(views.APIView):
    # permission_classes = [IsSellerUser]

    def get(self, request):
        queryset = Product.objects.select_related("category")
        serializer_class = SellerProductListingSerializer(
            queryset, many=True, context={"request": request}
        )
        # .filter(
        #     seller=get_session_seller(user=self.request.user)
        # )

        return Response(data=serializer_class.data)
