from celery import shared_task
from django.contrib.auth import get_user_model
from .models import Notification
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import firebase_admin
from firebase_admin import messaging

User = get_user_model()

@shared_task
def notify_user(user_id, message):
    try:
        user = User.objects.get(id=user_id)

        # 1. Save to DB
        Notification.objects.create(user=user, message=message)

        # 2. Send via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user.id}",
            {
                "type": "send_notification",
                "message": message,
            }
        )

        # 3. Send via FCM (if user has device token)
        if hasattr(user, 'profile') and user.profile.device_token:
            messaging.send(messaging.Message(
                token=user.profile.device_token,
                notification=messaging.Notification(
                    title="New Notification",
                    body=message,
                )
            ))

        return True

    except Exception as e:
        print("Notification Error:", e)
        return False
