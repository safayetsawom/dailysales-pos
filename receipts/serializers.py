from rest_framework import serializers
from .models import Receipt, ReceiptItem
from products.models import Product

class ReceiptItemInputSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)


class ReceiptItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)

    class Meta:
        model = ReceiptItem
        fields = ['id', 'product', 'product_name', 'product_sku', 'quantity', 'unit_price', 'subtotal']


class ReceiptSerializer(serializers.ModelSerializer):
    items = ReceiptItemSerializer(many=True, read_only=True)

    class Meta:
        model = Receipt
        fields = [
            'id', 'session', 'customer_name', 'customer_phone',
            'payment_method', 'discount_type', 'discount_value',
            'subtotal', 'discount_amount', 'grand_total',
            'items', 'created_at'
        ]
        read_only_fields = ['id', 'subtotal', 'discount_amount', 'grand_total', 'created_at']


class CreateReceiptSerializer(serializers.Serializer):
    customer_name = serializers.CharField(required=False, allow_blank=True)
    customer_phone = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.ChoiceField(choices=['cash', 'card', 'mobile_banking'])
    discount_type = serializers.ChoiceField(choices=['flat', 'percent'], required=False, allow_null=True)
    discount_value = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
    items = ReceiptItemInputSerializer(many=True)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("At least one item is required.")
        return items