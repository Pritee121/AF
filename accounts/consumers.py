# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from .models import ChatMessage, User
# from django.utils.timezone import now

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         """ Connects WebSocket to a chat room """
#         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
#         self.room_group_name = f"chat_{self.room_name}"

#         # ✅ Add the WebSocket to the room group
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#         await self.accept()

#     async def disconnect(self, close_code):
#         """ Disconnect WebSocket from chat room """
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#     async def receive(self, text_data):
#         """ Receive message from WebSocket """
#         data = json.loads(text_data)
#         message = data["message"]
#         sender_id = data["sender"]
#         receiver_id = data["receiver"]

#         sender = await User.objects.aget(id=sender_id)
#         receiver = await User.objects.aget(id=receiver_id)

#         # ✅ Save message to database
#         chat_message = ChatMessage.objects.create(
#             sender=sender, receiver=receiver, message=message, timestamp=now()
#         )

#         # ✅ Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 "type": "chat_message",
#                 "message": message,
#                 "sender": sender.first_name,
#                 "receiver": receiver.first_name,
#                 "timestamp": chat_message.timestamp.strftime("%Y-%m-%d %H:%M"),
#             },
#         )

#     async def chat_message(self, event):
#         """ Send message to WebSocket """
#         await self.send(text_data=json.dumps(event))
