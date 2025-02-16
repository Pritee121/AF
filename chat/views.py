from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ChatRoom

@login_required
def chat_list(request):
    """ ✅ List all chat rooms for the logged-in user """
    chats = ChatRoom.objects.filter(user=request.user) | ChatRoom.objects.filter(artist=request.user)
    return render(request, "chat/chat_list.html", {"chats": chats})

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import ChatRoom, ChatMessage

@login_required
def chat_room(request, room_id):
    """ ✅ Renders chat messages and handles new messages """
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    messages = ChatMessage.objects.filter(chat_room=chat_room).order_by("timestamp")

    if request.method == "POST":
        message_text = request.POST.get("message")
        if message_text:
            new_message = ChatMessage.objects.create(
                chat_room=chat_room,
                sender=request.user,
                message=message_text
            )
            return JsonResponse({"success": True, "message": new_message.message})

    return render(request, "chat/chat_room.html", {"chat_room": chat_room, "messages": messages})



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, ChatMessage
from accounts.models import User  # ✅ Import the correct User model

@login_required
def start_chat(request, artist_id):
    """ ✅ Start a chat between the logged-in user and an artist """
    artist = get_object_or_404(User, id=artist_id, is_artist=True)
    chat_room, created = ChatRoom.objects.get_or_create(user=request.user, artist=artist)
    return redirect("chat_room", room_id=chat_room.id)



