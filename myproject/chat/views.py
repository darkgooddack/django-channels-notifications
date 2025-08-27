from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.shortcuts import render, redirect
from .models import Message
from django.contrib.auth.decorators import login_required


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "auth/signup.html", {"form": form})


@login_required
def room(request, room_name):
    return render(
        request,
        "chat/room.html",
        {"room_name": room_name}
    )


@login_required
def feed(request):
    return render(request, "chat/feed.html")


@require_GET
def messages_api(request, room_name):
    qs = (Message.objects
          .filter(room=room_name)
          .order_by('created_at')
          .values('id', 'content', 'parent_id', 'created_at'))
    return JsonResponse({"messages": list(qs)})


def user_rooms(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"rooms": []})

    rooms = Message.objects.filter(author=user).values_list("room", flat=True).distinct()
    return JsonResponse({"rooms": list(rooms)})
