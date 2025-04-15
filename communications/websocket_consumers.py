from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import Notification  # Replace with your model import
from channels.db import database_sync_to_async


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        print(self.user, "from connect method")
        if self.user.is_authenticated:
            self.group_name = f"user_{self.user}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            print("✅ WebSocket connected usrer:", self.user.username)

            # ✅ Fetch count correctly
            await self.send_notification_count()
        else:
            await self.close()

    @database_sync_to_async
    def get_unread_notification_count(self):
        return Notification.objects.filter(user=self.user, is_read=False).count()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            print("❌ WebSocket disconnected")

    async def receive(self, text_data):
        print("🔌 WebSocket received data:", text_data)
        pass



    async def send_notification(self, event):
        print("📬 Sending notification mesage")
        await self.send(text_data=json.dumps({           
            'event': event,
        }))
        await self.send_notification_count( )
        
        

    async def send_notification_count(self):
        print("📬 Sending notification count")
        count = await self.get_unread_notification_count()
        await self.send(text_data=json.dumps({
            'event':{
                "type": "notification_count",
                "count": count,
                "ntype":'notification_count',    
            }     
        }))

        
        
# class NotificationConsumer(AsyncWebsocketConsumer):
    
#     async def connect(self):
#         print("🔌 WebSocket trying to connect...")
#         self.user = self.scope["user"]
#         # Temporarily skip auth and just accept everyone
#         self.group_name = "test_group"  # Optional group name if you want broadcast
#         await self.channel_layer.group_add(self.group_name, self.channel_name)

#         await self.accept()
#         print("✅ WebSocket connected")
#         print(f"User: {self.user.username}")

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard("test_group", self.channel_name)
#         print("❌ WebSocket disconnected")  
    
#     async def send_notification(self, event):
#         print("📬 Sending notification")
#         await self.send(text_data=json.dumps({
#             "message": event["message"]
#         }))



