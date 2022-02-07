from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
import json
from blockchain.errors import ErrorHandler
from threading import Thread
from django.core.management import call_command
from channels.generic.websocket import AsyncWebsocketConsumer


class BlockConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            'blocks',
            self.channel_name,
        )
        await self.channel_layer.group_add(
            'blockchain',
            self.channel_name,
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            'blocks',
            self.channel_name,
        )
        await self.channel_layer.group_discard(
            'blockchain',
            self.channel_name,
        )

    async def send_message(self, event):
        await self.send(json.dumps(event["text"]))
