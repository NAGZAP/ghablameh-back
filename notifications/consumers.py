import json
import logging
from channels.layers import get_channel_layer
from channels.generic.websocket import AsyncWebsocketConsumer
from .auth_jwt import get_user_id

logger = logging.getLogger(__name__)
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        token = self.scope['query_string'].decode('utf-8')  # Extract token from query string
        token = token.split('=')[1]  # Assuming token is in format 'token=<your_token>'
        try:
            self.scope['user_id'] = await get_user_id(token)
            self.room_group_name = f"notify_{self.scope['user_id']}"
            self.channel_layer = get_channel_layer()
            
            
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            logger.info(f"user {self.scope['user_id']} Connected")
        except Exception as e:
            logger.error(e)
            await self.close(code=401, reason="Invalid authentication credentials")
            
            
    async def disconnect(self, close_code):
        # Leave room group
        if self.channel_layer:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"user {self.scope['user_id']} Disconnected")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user_id = self.scope['user_id']
        
        await self.send(text_data=json.dumps({
            'message': message,
            'user_id': user_id
        }))
        
    async def send_notification(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'notification': message
        }))