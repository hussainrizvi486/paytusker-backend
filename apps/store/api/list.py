from rest_framework import generics, serializers
from apps.store.models import Category, Product
from apps.store.serializers import CategoryListSerializer


class CategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryListSerializer


class TemplateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "product_name"]


class ProductTemplateList(generics.ListAPIView):
    serializer_class = TemplateListSerializer

    def get_queryset(self, *args, **kwargs):
        queryset_list = Product.objects.filter(item_type="002")
        return queryset_list
