from .models import RequestLog
from rest_framework import serializers

# serializers.py
class IPLogSerializer(serializers.Serializer):
    ip_address = serializers.CharField()
    visited_paths = serializers.ListField(child=serializers.CharField())
    visit_count = serializers.IntegerField(required=False)
    timestamp = serializers.DateTimeField(required=False)