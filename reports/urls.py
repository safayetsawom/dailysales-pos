from django.urls import path
from .views import (
    OverallSummaryView,
    DailySummaryView,
    SessionReportView,
    ProductReportView,
)

urlpatterns = [
    path('reports/summary/', OverallSummaryView.as_view(), name='overall-summary'),
    path('reports/daily/', DailySummaryView.as_view(), name='daily-summary'),
    path('reports/session/<int:pk>/', SessionReportView.as_view(), name='session-report'),
    path('reports/product/<int:pk>/', ProductReportView.as_view(), name='product-report'),
]