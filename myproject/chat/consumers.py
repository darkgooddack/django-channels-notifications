import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        message_text = data['message']
        parent_id = data.get('parent')

        user = self.scope.get("user")
        username = user.username if user and user.is_authenticated else "Anonymous"

        from .models import Message
        parent_msg = None
        if parent_id:
            parent_msg = await sync_to_async(Message.objects.filter(id=parent_id).first)()

        message = await sync_to_async(Message.objects.create)(
            room=self.room_name,
            content=message_text,
            parent=parent_msg,
            author=user if user and user.is_authenticated else None
        )

        event = {
            "type": "chat_message",
            "id": message.id,
            "message": message_text,
            "parent": parent_id,
            "room": self.room_name,
            "author": username,
        }

        # Отправляем сообщение только в комнату
        await self.channel_layer.group_send(self.room_group_name, event)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))


class FeedConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        from .models import Message
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close()
            return

        # Получаем все комнаты, где есть сообщения пользователя
        rooms = await sync_to_async(list)(
            Message.objects.filter(author=user).values_list("room", flat=True).distinct()
        )

        # Подписываем канал на каждую комнату пользователя
        for room in rooms:
            await self.channel_layer.group_add(f"chat_{room}", self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        from .models import Message
        user = self.scope.get("user")
        if user and user.is_authenticated:
            rooms = await sync_to_async(list)(
                Message.objects.filter(author=user).values_list("room", flat=True).distinct()
            )
            for room in rooms:
                await self.channel_layer.group_discard(f"chat_{room}", self.channel_name)

    async def chat_message(self, event):
        # Отправляем только те события, которые пришли из подписанных комнат
        await self.send(text_data=json.dumps(event))
