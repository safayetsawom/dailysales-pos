import django_filters
from .models import Sale

class SaleFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(field_name='date')
    date_from = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    product = django_filters.NumberFilter(field_name='product__id')

    class Meta:
        model = Sale
        fields = ['date', 'date_from', 'date_to', 'product']