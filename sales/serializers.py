from rest_framework import serializers
from .models import Sale
from products.models import Product

class SaleSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)

    class Meta:
        model = Sale
        fields = [
            'id', 'product', 'product_name', 'product_sku',
            'quantity_sold', 'unit_price', 'total_price',
            'note', 'date', 'created_at'
        ]
        read_only_fields = ['id', 'unit_price', 'total_price', 'date', 'created_at']

    def validate(self, data):
        request = self.context.get('request')
        product = data.get('product')

        # Ensure product belongs to the logged-in user
        if product.user != request.user:
            raise serializers.ValidationError("Product not found.")

        # Check stock availability
        inventory = product.inventory
        if data['quantity_sold'] > inventory.stock_quantity:
            raise serializers.ValidationError(
                f"Insufficient stock. Available: {inventory.stock_quantity}"
            )
        return data

    def create(self, validated_data):
        product = validated_data['product']

        # Auto-calculate prices
        validated_data['unit_price'] = product.price
        validated_data['total_price'] = product.price * validated_data['quantity_sold']

        # Deduct stock
        inventory = product.inventory
        inventory.stock_quantity -= validated_data['quantity_sold']
        inventory.save()

        return super().create(validated_data)