from django.urls import path
from .views import InventoryListView, InventoryDetailView, LowStockView

urlpatterns = [
    path('inventory/', InventoryListView.as_view(), name='inventory-list'),
    path('inventory/<int:pk>/', InventoryDetailView.as_view(), name='inventory-detail'),
    path('inventory/low-stock/', LowStockView.as_view(), name='inventory-low-stock'),
]