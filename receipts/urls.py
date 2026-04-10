from django.urls import path
from .views import ReceiptListCreateView, ReceiptDetailView

urlpatterns = [
    path('receipts/', ReceiptListCreateView.as_view(), name='receipt-list-create'),
    path('receipts/<int:pk>/', ReceiptDetailView.as_view(), name='receipt-detail'),
]