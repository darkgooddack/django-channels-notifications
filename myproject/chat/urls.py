from django.urls import path
from . import views
from .views import messages_api

urlpatterns = [
    path('<str:room_name>/', views.room, name='room'),
    path("api/messages/<str:room_name>/", messages_api, name="messages_api"),
]
