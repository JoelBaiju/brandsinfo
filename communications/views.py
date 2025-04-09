from django.shortcuts import render

# Create your views here.
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from django.utils.timezone import now



def notify_user(user, message):
    notification = Notification.objects.create(user=user, message=message)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {
            "type": "send_notification",
            "message": message,
            "timestamp": now().isoformat(),
        }
    )


    