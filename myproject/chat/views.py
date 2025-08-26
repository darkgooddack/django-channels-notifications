from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.shortcuts import render
from .models import Message

def room(request, room_name):
    return render(
        request,
        "chat/room.html",
        {"room_name": room_name}
    )

@require_GET
def messages_api(request, room_name):
    qs = (Message.objects
          .filter(room=room_name)
          .order_by('created_at')
          .values('id', 'content', 'parent_id', 'created_at'))
    return JsonResponse({"messages": list(qs)})
