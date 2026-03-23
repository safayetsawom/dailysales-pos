from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Sale
from .serializers import SaleSerializer
from .filters import SaleFilter

class SaleListCreateView(generics.ListCreateAPIView):
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = SaleFilter
    ordering_fields = ['date', 'total_price', 'created_at']

    def get_queryset(self):
        return Sale.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SaleDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Sale.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        # Restore stock on delete
        inventory = instance.product.inventory
        inventory.stock_quantity += instance.quantity_sold
        inventory.save()
        instance.delete()