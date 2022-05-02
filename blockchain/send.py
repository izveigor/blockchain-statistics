from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


channel_layer = get_channel_layer()


def send_data(block, blockchain_update):
    async_to_sync(channel_layer.group_send)(
        "blockchain",
        {
            "type": "send_message",
            "text": {"block": block, "blockchain": blockchain_update},
        },
    )


def send_error_to_block_live_update(error):
    async_to_sync(channel_layer.group_send)(
        "blockchain", {"type": "send_message", "text": {"error": error}}
    )
