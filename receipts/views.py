from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Receipt, ReceiptItem
from .serializers import ReceiptSerializer, CreateReceiptSerializer
from pos_session.models import POSSession

class ReceiptListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        session_id = request.query_params.get('session')
        receipts = Receipt.objects.filter(user=request.user)
        if session_id:
            receipts = receipts.filter(session__id=session_id)
        serializer = ReceiptSerializer(receipts, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Must have an open session
        session = POSSession.objects.filter(
            user=request.user, status='open'
        ).first()
        if not session:
            return Response(
                {'error': 'No open session. Open a session first.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CreateReceiptSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        items_data = data['items']

        # Validate stock for all items first
        for item in items_data:
            product = item['product']
            if product.user != request.user:
                return Response(
                    {'error': f'Product {product.name} not found.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                inventory = product.inventory
            except Exception:
                return Response(
                    {'error': f'Product {product.name} has no inventory.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if item['quantity'] > inventory.stock_quantity:
                return Response(
                    {'error': f'Insufficient stock for {product.name}. Available: {inventory.stock_quantity}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Calculate subtotal
        subtotal = sum(
            item['product'].price * item['quantity']
            for item in items_data
        )

        # Calculate discount
        discount_type = data.get('discount_type')
        discount_value = data.get('discount_value', 0)
        discount_amount = 0

        if discount_type == 'flat':
            discount_amount = discount_value
        elif discount_type == 'percent':
            discount_amount = (subtotal * discount_value) / 100

        grand_total = subtotal - discount_amount
        if grand_total < 0:
            grand_total = 0

        # Create receipt
        receipt = Receipt.objects.create(
            user=request.user,
            session=session,
            customer_name=data.get('customer_name', ''),
            customer_phone=data.get('customer_phone', ''),
            payment_method=data['payment_method'],
            discount_type=discount_type,
            discount_value=discount_value,
            subtotal=subtotal,
            discount_amount=discount_amount,
            grand_total=grand_total,
        )

        # Create items and deduct stock
        for item in items_data:
            product = item['product']
            quantity = item['quantity']
            unit_price = product.price
            item_subtotal = unit_price * quantity

            ReceiptItem.objects.create(
                receipt=receipt,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=item_subtotal,
            )

            # Deduct stock
            inventory = product.inventory
            inventory.stock_quantity -= quantity
            inventory.save()

        return Response(
            ReceiptSerializer(receipt).data,
            status=status.HTTP_201_CREATED
        )


class ReceiptDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            receipt = Receipt.objects.get(pk=pk, user=request.user)
        except Receipt.DoesNotExist:
            return Response({'error': 'Receipt not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ReceiptSerializer(receipt).data)

    def delete(self, request, pk):
        try:
            receipt = Receipt.objects.get(pk=pk, user=request.user)
        except Receipt.DoesNotExist:
            return Response({'error': 'Receipt not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Restore stock for all items
        for item in receipt.items.all():
            inventory = item.product.inventory
            inventory.stock_quantity += item.quantity
            inventory.save()

        receipt.delete()
        return Response({'message': 'Receipt deleted and stock restored.'}, status=status.HTTP_200_OK)