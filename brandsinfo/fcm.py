from pyfcm import FCMNotification

FCM_SERVER_KEY = "YOUR_FCM_SERVER_KEY"
push_service = FCMNotification(api_key=FCM_SERVER_KEY)

def send_push_notification(user_fcm_token, title, message):
    push_service.notify_single_device(
        registration_id=user_fcm_token,
        message_title=title,
        message_body=message
    )





from celery import shared_task


@shared_task
def send_push_notification_task(user_fcm_token, title, message):
    push_service.notify_single_device(
        registration_id=user_fcm_token,
        message_title=title,
        message_body=message
    )