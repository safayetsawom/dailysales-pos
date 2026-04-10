from rest_framework import serializers
from .models import Refund
from receipts.models import Receipt

class RefundSerializer(serializers.ModelSerializer):
    receipt_grand_total = serializers.DecimalField(
        source='receipt.grand_total',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Refund
        fields = [
            'id', 'receipt', 'receipt_grand_total', 'refund_type',
            'refund_amount', 'reason', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CreateRefundSerializer(serializers.Serializer):
    receipt = serializers.PrimaryKeyRelatedField(queryset=Receipt.objects.all())
    refund_type = serializers.ChoiceField(choices=['full', 'partial'])
    refund_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    reason = serializers.CharField()

    def validate(self, data):
        receipt = data['receipt']
        refund_type = data['refund_type']
        refund_amount = data.get('refund_amount', 0)

        # Check already refunded
        if hasattr(receipt, 'refund'):
            raise serializers.ValidationError("This receipt has already been refunded.")

        if refund_type == 'full':
            data['refund_amount'] = receipt.grand_total

        elif refund_type == 'partial':
            if not refund_amount or refund_amount <= 0:
                raise serializers.ValidationError("Partial refund requires a valid refund amount.")
            if refund_amount > receipt.grand_total:
                raise serializers.ValidationError(
                    f"Refund amount cannot exceed receipt total ({receipt.grand_total})."
                )

        return data