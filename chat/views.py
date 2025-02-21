from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, ChatMessage
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Subquery, OuterRef
from django.shortcuts import render
from .models import ChatRoom, ChatMessage

@login_required
def chat_list(request):
    """ ✅ List all chat rooms for the logged-in user, ordered by most recent message """
    chats = ChatRoom.objects.filter(Q(user=request.user) | Q(artist=request.user))

    # ✅ Get the latest message for each chat
    latest_message_subquery = ChatMessage.objects.filter(
        chat_room=OuterRef('pk')
    ).order_by('-timestamp').values('message')[:1]  # Only get the latest message

    chats = chats.annotate(last_message=Subquery(latest_message_subquery))

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



from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, ChatMessage

@csrf_exempt
@login_required
def delete_chat_room(request, room_id):
    """Soft delete the chat for the user, but keep it visible for the other participant."""
    if request.method == "POST":
        chat_room = get_object_or_404(ChatRoom, id=room_id)

        if request.user == chat_room.user:
            chat_room.is_deleted_by_user = True
        elif request.user == chat_room.artist:
            chat_room.is_deleted_by_artist = True
        chat_room.save()

        # ✅ If both users delete, delete the chat permanently
        if chat_room.is_deleted_by_user and chat_room.is_deleted_by_artist:
            chat_room.delete()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)




from django.utils.timezone import localtime

def chat_view(request, room_id):
    messages = ChatMessage.objects.filter(chat_room_id=room_id).order_by("timestamp")
    
    # Convert timestamps to Nepal Time before sending to template
    for message in messages:
        message.timestamp = localtime(message.timestamp, timezone='Asia/Kathmandu')

    return render(request, 'chat/chat_room.html', {'messages': messages})
