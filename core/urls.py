from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/', include('products.urls')),
    path('api/', include('inventory.urls')),
    path('api/', include('sales.urls')),
    path('api/', include('pos_session.urls')),
    path('api/', include('receipts.urls')),
    path('api/', include('refunds.urls')),
    path('api/', include('reports.urls')),
]