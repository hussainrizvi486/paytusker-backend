from rest_framework import viewsets
from rest_framework.response import Response

from apps.store.models import Category
from apps.store.serializers import CategoryListSerializer


class CategoryAPIView(viewsets.ViewSet):
    def list(self, *args, **kwargs):
        category_queryset = Category.objects.all()
        serializer = CategoryListSerializer(category_queryset, many=True)
        return Response(data=serializer.data)

    def detail(self, *args, **kwargs): ...
    def create(self, *args, **kwargs): ...
