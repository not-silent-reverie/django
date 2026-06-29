import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Product, Review
from django.contrib.auth.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.product_id = self.scope['url_route']['kwargs']['product_id']
        self.room_group_name = f'chat_{self.product_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'comment')

        if message_type == 'comment':
            await self.save_comment(data)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': data['message'],
                    'username': data['username'],
                    'rating': data.get('rating', 0),
                    'created_at': data.get('created_at', '')
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'comment',
            'message': event['message'],
            'username': event['username'],
            'rating': event['rating'],
            'created_at': event['created_at']
        }))

    @database_sync_to_async
    def save_comment(self, data):
        try:
            product = Product.objects.get(id=self.product_id)
            user = User.objects.get(username=data['username'])
            rating = data.get('rating', 0)

            review = Review.objects.create(
                product=product,
                user=user,
                rating=rating,
                comment=data['message']
            )
            return review
        except Exception as e:
            print(f"Error saving comment: {e}")
            return None