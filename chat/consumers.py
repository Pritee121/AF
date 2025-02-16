import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.db import close_old_connections
from asgiref.sync import sync_to_async
from .models import ChatRoom, ChatMessage

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """ ✅ Handles receiving WebSocket messages """
        data = json.loads(text_data)
        message = data["message"]
        sender_id = data["sender_id"]

        chat_room = await self.get_chat_room(self.room_id)
        sender = await self.get_user(sender_id)

        # ✅ Save message to database asynchronously
        new_message = await self.create_message(chat_room, sender, message)

        # ✅ Send message to WebSocket group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "sender": sender.first_name,
                "message": new_message.message,
            },
        )

    async def chat_message(self, event):
        """ ✅ Broadcast message to WebSocket clients """
        await self.send(text_data=json.dumps({
            "sender": event["sender"],
            "message": event["message"]
        }))

    @sync_to_async
    def get_chat_room(self, room_id):
        """ ✅ Get chat room instance """
        return ChatRoom.objects.get(id=room_id)

    @sync_to_async
    def get_user(self, user_id):
        """ ✅ Get user instance """
        return User.objects.get(id=user_id)

    @sync_to_async
    def create_message(self, chat_room, sender, message):
        """ ✅ Save chat message in database """
        close_old_connections()  # ✅ Prevent database connection issues
        return ChatMessage.objects.create(chat_room=chat_room, sender=sender, message=message)
