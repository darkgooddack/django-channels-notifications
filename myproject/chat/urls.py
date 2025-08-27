from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("chat/<str:room_name>/", views.room, name="room"),
    path("api/messages/<str:room_name>/", views.messages_api, name="messages_api"),

    path("feed/", views.feed, name="feed"),
    path('api/user_rooms/', views.user_rooms, name='user_rooms'),

    path("login/", auth_views.LoginView.as_view(template_name="auth/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/login/"), name="logout"),
    path("signup/", views.signup, name="signup"),
]
