from django.urls import path
from .views import chat_list, chat_room
from .views import start_chat
from .views import delete_chat_room 

urlpatterns = [
    path("chats/", chat_list, name="chat_list"),
    path("chats/<int:room_id>/", chat_room, name="chat_room"),
    path("start/<int:artist_id>/", start_chat, name="start_chat"),
    path("delete-chat-room/<int:room_id>/", delete_chat_room, name="delete_chat_room"),
]
