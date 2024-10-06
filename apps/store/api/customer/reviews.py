from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.store.models import ModelMedia
from apps.store.models.order import (
    DigitalOrder,
    DigitalOrderStatusChoices,
    DigitalOrderItem,
    Product,
    OrderReview,
    Customer,
)
from django.db import transaction
from server.utils import get_media_url


class CustomerReviewsSerializers(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    review_media = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()
    review_date = serializers.SerializerMethodField()

    class Meta:
        model = OrderReview
        fields = [
            "product_name",
            "product_image",
            "review_date",
            "order_id",
            "order_item",
            "product",
            "review_content",
            "rating",
            # "order_date",
            # "customer",
            "review_media",
        ]

    def get_product_name(self, obj):
        return obj.product.product_name

    def get_product_image(self, obj):
        image = obj.product.cover_image
        if image:
            return get_media_url(image.url)

    def get_review_date(self, obj):
        return obj.creation.strftime("%d-%m-%Y")

    def get_review_media(self, obj):
        media_queryset = ModelMedia.objects.filter(
            model_name="OrderReview", field_id=obj.id
        )
        media = []
        for i in media_queryset:
            if i.file:
                media.append(get_media_url(i.file.url))
        return media


class CustomerOrderToReviewSerializer(serializers.ModelSerializer):
    order_id = serializers.SerializerMethodField()
    product_id = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = DigitalOrderItem
        fields = [
            "order_id",
            "product_id",
            "product_name",
            "product_image",
            "id",
            "rate",
            "qty",
            "amount",
        ]

    def get_order_id(self, obj: DigitalOrderItem):
        return obj.order.order_id

    def get_product_name(self, obj: DigitalOrderItem):
        return obj.product.product_name

    def get_product_id(self, obj: DigitalOrderItem):
        return obj.product.id

    def get_product_image(self, obj: DigitalOrderItem):
        image = obj.product.cover_image
        if image:
            return get_media_url(image.url)


class CustomerOrderReviewView(viewsets.ViewSet):
    def pending_reviews(self, *args, **kwargs):
        customer_queryset = get_object_or_404(Customer, user=self.request.user)
        order_items_queryset = DigitalOrderItem.objects.filter(
            reviewed_by_customer=False,
            status=DigitalOrderStatusChoices.COMPLETED,
            order__customer=customer_queryset,
        ).select_related("product")
        serializer = CustomerOrderToReviewSerializer(order_items_queryset, many=True)
        return Response(data={"reviews": serializer.data})

    def get_reviews(self, *args, **kwargs):
        customer_queryset = get_object_or_404(Customer, user=self.request.user)
        reviews_queryset = OrderReview.objects.filter(
            customer=customer_queryset
        ).select_related("product")
        serializer = CustomerReviewsSerializers(reviews_queryset, many=True)
        return Response(data={"reviews": serializer.data})

    def filter_media_keys(self, key):
        if str(key).startswith("review_media"):
            return True
        return False

    def add_review(self, *args, **kwargs):
        request_data: dict = self.request.data
        customer_queryset = get_object_or_404(Customer, user=self.request.user)
        order_item_queryset = get_object_or_404(
            DigitalOrderItem.objects.select_related("order"),
            id=request_data.get("id"),
        )
        if OrderReview.objects.filter(
            customer=customer_queryset, order_item=order_item_queryset.id
        ).exists():
            return Response(
                {"message": "This order has already been reviewed by the customer."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            with transaction.atomic():
                review_object = OrderReview.objects.create(
                    customer=customer_queryset,
                    order=order_item_queryset.order,
                    order_item=order_item_queryset.id,
                    product=order_item_queryset.product,
                    rating=request_data.get("rating"),
                    review_content=request_data.get("review_content"),
                )

                order_item_queryset.reviewed_by_customer = True
                order_item_queryset.save()

                review_media_keys = filter(self.filter_media_keys, request_data.keys())
                media_objects = []

                for key in review_media_keys:
                    if request_data.get(key):
                        media_objects.append(
                            ModelMedia(
                                model_name="OrderReview",
                                file=request_data.get(key),
                                field_id=review_object.id,
                            )
                        )

                if media_objects:
                    ModelMedia.objects.bulk_create(media_objects)

                return Response(
                    {"message": "Your review has been added successfully!"},
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            return Response(
                {"message": "Internal server error", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# def get_order_review(
#         self,
#         request,
#     ):
#         filters = request.GET.get("filters") or {}
#         customer = get_customer(request.user)
#         response_data = []
#         orders_reviews = OrderReview.objects.filter(customer=customer).order_by(
#             "-creation"
#         )

#         for review in orders_reviews:
#             response_data.append(
#                 {
#                     "product_name": review.product.product_name,
#                     "product_image": request.build_absolute_uri(
#                         review.product.cover_image.url
#                     ),
#                     "order_id": review.order.order_id,
#                     "order_date": review.order.order_date.strftime("%d-%m-%Y"),
#                     "review_date": review.creation.strftime("%d-%m-%Y"),
#                     "review_content": review.review_content,
#                     "rating": review.rating,
#                     "review_media": get_serialized_model_media(
#                         "OrderReview", review.id, request
#                     ),
#                 }
#             )

#         if response_data:
#             return Response(data={"reviews": response_data, "message": ""})

#         return Response(
#             data={"reviews": None, "message": "No Reviews Found"},
#         )
