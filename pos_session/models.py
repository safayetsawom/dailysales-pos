from django.db import models
from django.contrib.auth.models import User

class POSSession(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pos_sessions')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Session #{self.id} — {self.user.username} — {self.status}"