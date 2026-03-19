from rest_framework import serializers
from .models import Inventory

class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Inventory
        fields = ['id', 'product', 'product_name', 'product_sku', 'stock_quantity', 'is_low_stock', 'last_updated']
        read_only_fields = ['id', 'product', 'product_name', 'product_sku', 'is_low_stock', 'last_updated']

class RestockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ['stock_quantity']