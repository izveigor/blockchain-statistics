import asyncio
from typing import Any

from django.core.management.base import BaseCommand

from update.api import client


class Command(BaseCommand):  # type: ignore
    help = "Start websocket"

    def handle(self, *args: Any, **options: Any) -> None:
        asyncio.run(client())
