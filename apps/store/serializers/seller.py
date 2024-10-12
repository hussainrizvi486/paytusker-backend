from rest_framework import serializers
from apps.store.models.seller import SellerProfileRequest


class SellerProfileRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerProfileRequest
        fields = [
            "id",
            "full_name",
            "store_name",
            "contact_number",
            "email",
            "address",
            "city",
            "country",
            "website_url",
            "business_license",
            "description",
            "request_status",
            "request_date",
        ]

        read_only_fields = ["request_status", "request_date"]

    def create(self, validated_data):
        validated_data["request_status"] = "pending"
        return super().create(validated_data)
