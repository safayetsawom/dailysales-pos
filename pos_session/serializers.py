from rest_framework import serializers
from .models import POSSession

class POSSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = POSSession
        fields = ['id', 'status', 'opened_at', 'closed_at', 'note']
        read_only_fields = ['id', 'status', 'opened_at', 'closed_at']


class OpenSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = POSSession
        fields = ['note']


class CloseSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = POSSession
        fields = ['note']