# # from django.db import models
# # from accounts.models import User  # Import User model from accounts app

# # class ChatRoom(models.Model):
# #     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_chats")
# #     artist = models.ForeignKey(User, on_delete=models.CASCADE, related_name="artist_chats")
# #     created_at = models.DateTimeField(auto_now_add=True)

# #     def __str__(self):
# #         return f"Chat between {self.user.first_name} and {self.artist.first_name}"
# from django.db import models
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class ChatRoom(models.Model):
#     """Defines a chat room between a user and an artist"""
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats_as_user")
#     artist = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats_as_artist")
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Chat between {self.user.first_name} and {self.artist.first_name}"

# # class ChatMessage(models.Model):
# #     room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
# #     sender = models.ForeignKey(User, on_delete=models.CASCADE)
# #     message = models.TextField()
# #     timestamp = models.DateTimeField(auto_now_add=True)

# #     def __str__(self):
# #         return f"Message from {self.sender.first_name} at {self.timestamp}"
# class ChatMessage(models.Model):
#     """Stores chat messages between user and artist"""
#     chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
#     sender = models.ForeignKey(User, on_delete=models.CASCADE)
#     message = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Message from {self.sender.first_name} at {self.timestamp}"
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatRoom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_chats")
    artist = models.ForeignKey(User, on_delete=models.CASCADE, related_name="artist_chats")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat between {self.user.email} and {self.artist.email}"

class ChatMessage(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.first_name}: {self.message}"
