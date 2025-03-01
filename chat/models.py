from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatRoom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_chats")
    artist = models.ForeignKey(User, on_delete=models.CASCADE, related_name="artist_chats")
    created_at = models.DateTimeField(auto_now_add=True)
      # Soft delete fields
    is_deleted_by_user = models.BooleanField(default=False)
    is_deleted_by_artist = models.BooleanField(default=False)
    def __str__(self):
        return f"Chat between {self.user.email} and {self.artist.email}"


class ChatMessage(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # ✅ New Field for Read Status

    def __str__(self):
        return f"{self.sender.first_name}: {self.message}"
