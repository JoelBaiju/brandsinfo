from rest_framework import serializers
from .models import * 
from usershome.models import   PhonePeTransaction




class NotificationsSerializer(serializers.ModelSerializer): 
    user = serializers.PrimaryKeyRelatedField(
        queryset=Extended_User.objects.all()
    )

    status = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'user', 'buisness', 'message', 'timestamp', 'is_read', 'ntype', 'status']

    def get_status(self, obj):
        if obj.ntype == "PAYMENT_STATUS":
            try:
                transaction = PhonePeTransaction.objects.get(order_id=obj.order_id)
                return transaction.status
            except PhonePeTransaction.DoesNotExist:
                return None
        return None

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['buisness'] = instance.buisness.name if instance.buisness else None
        return rep
