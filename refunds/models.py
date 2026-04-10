from django.db import models
from django.contrib.auth.models import User
from receipts.models import Receipt

class Refund(models.Model):
    REFUND_TYPE_CHOICES = [
        ('full', 'Full'),
        ('partial', 'Partial'),
    ]

    receipt = models.OneToOneField(Receipt, on_delete=models.CASCADE, related_name='refund')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refunds')
    refund_type = models.CharField(max_length=10, choices=REFUND_TYPE_CHOICES)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Refund for Receipt #{self.receipt.id} — {self.refund_type}"