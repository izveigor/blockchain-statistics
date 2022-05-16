from django.core.management.base import BaseCommand
import asyncio
from update.api import client
from typing import Any


class Command(BaseCommand):  # type: ignore
    help = "Start websocket"

    def handle(self, *args: Any, **options: Any) -> None:
        asyncio.run(client())
