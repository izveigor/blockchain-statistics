from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from typing import Any


class BlockConsumer(AsyncWebsocketConsumer):  # type: ignore
    async def connect(self) -> None:
        await self.channel_layer.group_add(
            "blockchain",
            self.channel_name,
        )
        await self.accept()

    async def disconnect(self, close_code: str) -> None:
        await self.channel_layer.group_discard(
            "blockchain",
            self.channel_name,
        )

    async def send_message(self, event: Any) -> None:
        await self.send(json.dumps(event["text"]))
