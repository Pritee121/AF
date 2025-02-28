from django.urls import path
from .views import chat_list, chat_room
from .views import start_chat
from .views import delete_chat_room 
# from .views import get_chat_notifications, mark_chat_notifications_read
from .views import (
    get_user_chat_notifications, 
    get_artist_chat_notifications, 
    mark_user_chat_notifications_read, 
    mark_artist_chat_notifications_read
)


urlpatterns = [
    path("chats/", chat_list, name="chat_list"),
    path("chats/<int:room_id>/", chat_room, name="chat_room"),
    path("start/<int:artist_id>/", start_chat, name="start_chat"),
    path("delete-chat-room/<int:room_id>/", delete_chat_room, name="delete_chat_room"),
    # path("get-chat-notifications/", get_chat_notifications, name="get_chat_notifications"),
    # path("mark-chat-notifications-read/", mark_chat_notifications_read, name="mark_chat_notifications_read"),
        path("notifications/user/", get_user_chat_notifications, name="get_user_chat_notifications"),
    path("notifications/artist/", get_artist_chat_notifications, name="get_artist_chat_notifications"),
    
    # Separate mark-as-read routes
    path("notifications/user/read/", mark_user_chat_notifications_read, name="mark_user_chat_notifications_read"),
    path("notifications/artist/read/", mark_artist_chat_notifications_read, name="mark_artist_chat_notifications_read"),

]
