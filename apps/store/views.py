from django.shortcuts import render
from rest_framework.views import APIView, Response
from rest_framework import status
import requests
from apps.store.models.product import Category, Product as ProductM

# https://crm.paytusker.us/api/resource/Item%20Group?fields=[%22name%22,%20%22image%22]&limit=1000


class Product(APIView):
    def get(self, request):
        try:
            req = requests.get(
                """https://crm.paytusker.us/api/resource/Item?fields=[%22name%22,%20%22item_name%22,%20%22item_group%22,%20%22custom_website_price%22,%20%22custom_rating%22,%20%22image%22]&limit=9999"""
            )

            req.raise_for_status()

            data = req.json().get("data", [])
            no_image_url = "https://t4.ftcdn.net/jpg/04/73/25/49/360_F_473254957_bxG9yf4ly7OBO5I0O5KABlN930GwaMQz.jpg"

            # ProductM.objects.all().delete()
            for row in data:
                img = no_image_url
                if row.get("image"):
                    img = f'crm.paytusker.us{row.get("image")}'

                ProductM.objects.create(
                    product_name=row.get("item_name"),
                    cover_images=img,
                    rating=row.get("custom_rating"),
                    price=row.get("custom_website_price"),
                )

            products = ProductM.objects.all()

            return Response(status=200, data={"message": "Data imported successfully"})
        except requests.exceptions.RequestException as e:
            return Response(
                status=500, data={"error": f"Failed to fetch data from API: {e}"}
            )
        except Exception as e:
            return Response(status=500, data={"error": f"An error occurred: {e}"})


class user(APIView):
    def get(self, request):
    
        return Response(self.request.user.username)


class CreateCategory(APIView):
    def get(self, request):
        req = requests.get(
            "https://crm.paytusker.us/api/resource/Item%20Group?fields=[%22name%22,%20%22image%22]&limit=1000"
        )
        data = req.json().get("data", [])
        for row in data:
            Category.objects.create(
                name=row.get("name"),
                image=row.get("image"),
            )

        return Response(status=200, data={"message": "Data imported successfully"})


# class Cart(APIView):
#     def get(self, request):
#         user = self.request.user
#         if user.is_anonymous:
#             return Response({"message": "User is not authenticated", "user": str(self.request.user)})

#         order = Order.objects.filter(user=user.id, ordered=False).first()

#         if not order:
#             return Response({"message": "No active order found"}, status=status.HTTP_404_NOT_FOUND)

#         order_serializer = OrderSerializer(order)
#         order_items = OrderItem.objects.filter(order=order.id)
#         order_items_serailizer = OrderItemSerializers(
#             order_items, many=True)

#         reponse_data = {
#             "order": order_serializer.data,
#             "order_items": order_items_serailizer.data
#         }
#         return Response(reponse_data, status=status.HTTP_200_OK)
