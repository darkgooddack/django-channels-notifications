import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = None
        self.room_name = None

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add( # добавляет подключение в группу
            self.room_group_name, # куда, можно маршрутизировать
            self.channel_name # кого
        )
        await self.accept() # подтверждает подключение, чтоб не разрывало соединение

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        from .models import Message

        data = json.loads(text_data)
        print(data)
        message_text = data['message']
        parent_id = data.get('parent')

        parent_msg = None
        if parent_id:
            parent_msg = await sync_to_async(Message.objects.filter(id=parent_id).first)()

        # Django ORM только синхронно работает
        message = await sync_to_async(Message.objects.create)(
            room=self.room_name,
            content=message_text,
            parent=parent_msg
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_text,
                'id': message.id,
                'parent': parent_id
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
