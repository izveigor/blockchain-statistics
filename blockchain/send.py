from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .types_ import TypeClearedBlock, TypeBlockchainAttributes


channel_layer = get_channel_layer()


def send_data(
    block: TypeClearedBlock, blockchain_update: TypeBlockchainAttributes
) -> None:
    async_to_sync(channel_layer.group_send)(
        "blockchain",
        {
            "type": "send_message",
            "text": {"block": block, "blockchain": blockchain_update},
        },
    )


def send_error_to_block_live_update(error: str) -> None:
    async_to_sync(channel_layer.group_send)(
        "blockchain", {"type": "send_message", "text": {"error": error}}
    )
