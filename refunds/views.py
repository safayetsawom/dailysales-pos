from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, generics
from .models import Refund
from .serializers import RefundSerializer, CreateRefundSerializer

class RefundListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        refunds = Refund.objects.filter(user=request.user).order_by('-created_at')
        serializer = RefundSerializer(refunds, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CreateRefundSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        receipt = data['receipt']

        # Ensure receipt belongs to logged-in user
        if receipt.user != request.user:
            return Response({'error': 'Receipt not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Restore stock only for full refund
        if data['refund_type'] == 'full':
            for item in receipt.items.all():
                inventory = item.product.inventory
                inventory.stock_quantity += item.quantity
                inventory.save()

        refund = Refund.objects.create(
            receipt=receipt,
            user=request.user,
            refund_type=data['refund_type'],
            refund_amount=data['refund_amount'],
            reason=data['reason'],
        )

        return Response(RefundSerializer(refund).data, status=status.HTTP_201_CREATED)


class RefundDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            refund = Refund.objects.get(pk=pk, user=request.user)
        except Refund.DoesNotExist:
            return Response({'error': 'Refund not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(RefundSerializer(refund).data)