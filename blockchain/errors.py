from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync



class _ErrorHandler:
    _channel_layer = get_channel_layer()

    def send_error_to_block_live_update(self, error):
        async_to_sync(self._channel_layer.group_send)(
            "blocks", {
                "type": "send_message",
                "text": {'error': error}
            }
        )


ErrorHandler = _ErrorHandler()        