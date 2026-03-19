from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Inventory
from .serializers import InventorySerializer, RestockSerializer

class InventoryListView(generics.ListAPIView):
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['stock_quantity', 'last_updated']

    def get_queryset(self):
        return Inventory.objects.filter(product__user=self.request.user)


class InventoryDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Inventory.objects.filter(product__user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return RestockSerializer
        return InventorySerializer


class LowStockView(generics.ListAPIView):
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Inventory.objects.filter(
            product__user=self.request.user,
            stock_quantity__lte=5
        )