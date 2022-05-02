from django.core.management.base import BaseCommand
import asyncio
from update.api import client


class Command(BaseCommand):
    help = "Start websocket"

    def handle(self, *args, **options):
        asyncio.run(client())
