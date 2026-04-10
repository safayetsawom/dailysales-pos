from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import datetime
from products.models import Product
from inventory.models import Inventory
from sales.models import Sale
from receipts.models import Receipt, ReceiptItem
from refunds.models import Refund
from pos_session.models import POSSession


class OverallSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Total revenue from direct sales
        sales_revenue = Sale.objects.filter(user=user).aggregate(
            total=Sum('total_price')
        )['total'] or 0

        # Total revenue from POS receipts
        receipt_revenue = Receipt.objects.filter(user=user).aggregate(
            total=Sum('grand_total')
        )['total'] or 0

        total_revenue = sales_revenue + receipt_revenue

        # Total units sold from direct sales
        sales_units = Sale.objects.filter(user=user).aggregate(
            total=Sum('quantity_sold')
        )['total'] or 0

        # Total units sold from receipts
        receipt_units = ReceiptItem.objects.filter(
            receipt__user=user
        ).aggregate(total=Sum('quantity'))['total'] or 0

        total_units = sales_units + receipt_units

        # Best selling product (by units from receipt items)
        best_seller = ReceiptItem.objects.filter(
            receipt__user=user
        ).values(
            'product__name'
        ).annotate(
            total_sold=Sum('quantity')
        ).order_by('-total_sold').first()

        # Low stock products
        low_stock = Inventory.objects.filter(
            product__user=user,
            stock_quantity__lte=5
        ).values('product__name', 'stock_quantity')

        return Response({
            'total_revenue': total_revenue,
            'total_units_sold': total_units,
            'best_selling_product': best_seller,
            'low_stock_products': list(low_stock),
        })


class DailySummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        date_str = request.query_params.get('date')
        date_from_str = request.query_params.get('date_from')
        date_to_str = request.query_params.get('date_to')

        # Build date filters
        sales_filter = {'user': user}
        receipt_filter = {'user': user}

        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                sales_filter['date'] = date
                receipt_filter['created_at__date'] = date
            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

        if date_from_str:
            try:
                date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
                sales_filter['date__gte'] = date_from
                receipt_filter['created_at__date__gte'] = date_from
            except ValueError:
                return Response({'error': 'Invalid date_from format. Use YYYY-MM-DD.'}, status=400)

        if date_to_str:
            try:
                date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
                sales_filter['date__lte'] = date_to
                receipt_filter['created_at__date__lte'] = date_to
            except ValueError:
                return Response({'error': 'Invalid date_to format. Use YYYY-MM-DD.'}, status=400)

        sales_revenue = Sale.objects.filter(**sales_filter).aggregate(
            total=Sum('total_price')
        )['total'] or 0

        receipt_revenue = Receipt.objects.filter(**receipt_filter).aggregate(
            total=Sum('grand_total')
        )['total'] or 0

        total_sales_count = Sale.objects.filter(**sales_filter).count()
        total_receipt_count = Receipt.objects.filter(**receipt_filter).count()

        return Response({
            'sales_revenue': sales_revenue,
            'receipt_revenue': receipt_revenue,
            'total_revenue': sales_revenue + receipt_revenue,
            'direct_sales_count': total_sales_count,
            'receipt_count': total_receipt_count,
        })


class SessionReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            session = POSSession.objects.get(pk=pk, user=request.user)
        except POSSession.DoesNotExist:
            return Response({'error': 'Session not found.'}, status=404)

        receipts = Receipt.objects.filter(session=session)

        # Total revenue
        total_revenue = receipts.aggregate(
            total=Sum('grand_total')
        )['total'] or 0

        # Total refunds
        total_refunds = Refund.objects.filter(
            receipt__session=session
        ).aggregate(total=Sum('refund_amount'))['total'] or 0

        # Payment method breakdown
        payment_breakdown = receipts.values('payment_method').annotate(
            total=Sum('grand_total'),
            count=Count('id')
        )

        # Units sold per product
        units_per_product = ReceiptItem.objects.filter(
            receipt__session=session
        ).values('product__name').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('subtotal')
        ).order_by('-total_quantity')

        return Response({
            'session_id': session.id,
            'status': session.status,
            'opened_at': session.opened_at,
            'closed_at': session.closed_at,
            'total_receipts': receipts.count(),
            'total_revenue': total_revenue,
            'total_refunds': total_refunds,
            'net_revenue': total_revenue - total_refunds,
            'payment_breakdown': list(payment_breakdown),
            'units_per_product': list(units_per_product),
        })


class ProductReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk, user=request.user)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=404)

        # From direct sales
        sales_data = Sale.objects.filter(
            product=product
        ).aggregate(
            total_units=Sum('quantity_sold'),
            total_revenue=Sum('total_price')
        )

        # From receipts
        receipt_data = ReceiptItem.objects.filter(
            product=product
        ).aggregate(
            total_units=Sum('quantity'),
            total_revenue=Sum('subtotal')
        )

        total_units = (sales_data['total_units'] or 0) + (receipt_data['total_units'] or 0)
        total_revenue = (sales_data['total_revenue'] or 0) + (receipt_data['total_revenue'] or 0)

        return Response({
            'product_id': product.id,
            'product_name': product.name,
            'sku': product.sku,
            'current_stock': product.inventory.stock_quantity,
            'total_units_sold': total_units,
            'total_revenue': total_revenue,
        })