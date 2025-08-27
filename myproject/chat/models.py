from django.db import models
from django.conf import settings


class Message(models.Model):
    room = models.CharField(max_length=100, default="room")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="messages"
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies"
    )

    def __str__(self):
        return f"[{self.room}] {self.author}: {self.content[:20]}"
