from django.shortcuts import render

# Create your views here.
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from django.utils.timezone import now
from django.http import JsonResponse
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, filters, status
from rest_framework.response import Response
from usershome.models import Extended_User
    

def notify_user(data):
    message     = data['message'] 
    title       = data['title']
    ntype       = data['type']
    buisness    = data['business'] 
    user        = data['user']
    
    channel_layer = get_channel_layer()
    
    print('user:', user ,'from notify_user function')
    notification = Notification.objects.create(
        user=user, 
        message=message,
        title=title,
        ntype=ntype,
        buisness=buisness
        )
    notification.save()
    
    async_to_sync(channel_layer.group_send)(
        "user_" + str(user.id),  
        {
            "type": "send_notification", 
            "message": message,
            "timestamp": now(),
            "title": title,    
            "type": ntype,
            "buisness": buisness,
        }
    )
    
    return {"sent": True}



from rest_framework.decorators import api_view
from .ws_notifications import new_plan_purchased
@api_view(['GET'])
def notify_user_to_all(request):
    user = Extended_User.objects.get(id=request.GET.get('id'))
    buisness= Buisnesses.objects.filter(user=user).first()
    new_plan_purchased(buisness)
    
    return JsonResponse({"sent": True})




class Notifications_View(generics.ListAPIView):
    serializer_class = NotificationsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # This evaluates the queryset to a list of objects
        notifications = list(Notification.objects.filter(user=self.request.user).order_by('-timestamp'))
        return notifications

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()  # list of notifications (evaluated)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            response = Response(serializer.data)

        # Now update notifications as read after response is ready
        Notification.objects.filter(id__in=[n.id for n in queryset], is_read=False).update(is_read=True)

        return response

    
    
    
    

from firebase_admin import messaging

def send_notification_to_device(device_token, title='', body='', data=None):

    message = messaging.Message(
        notification=messaging.Notification(
            title='test notification',
            body='notification pushing success',
        ),
        token=device_token,  
        data=data or {}       
    )
    try:
        response = messaging.send(message)
        print(f"Notification sent successfully: {response}")
    except Exception as e:
        print(f"Error sending notification: {e}")




