from rest_framework import serializers
from .models import * 



class NotificationsSerializer(serializers.ModelSerializer): 
    user = serializers.PrimaryKeyRelatedField(
        queryset=Extended_User.objects.all()
    )
    
    class Meta:
        model = Notification
        fields = ['id', 'user', 'buisness', 'message', 'timestamp','is_read']

    def to_representation(self, instance):
        buisness = instance.buisness.name if instance.buisness else None
        return super().to_representation(instance)