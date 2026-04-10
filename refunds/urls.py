from django.urls import path
from .views import RefundListCreateView, RefundDetailView

urlpatterns = [
    path('refunds/', RefundListCreateView.as_view(), name='refund-list-create'),
    path('refunds/<int:pk>/', RefundDetailView.as_view(), name='refund-detail'),
]