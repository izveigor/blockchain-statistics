from status.models import Block, Transaction
from channels.layers import get_channel_layer
from update.blockchain import BlockchainUpdate
from asgiref.sync import async_to_sync


class _NewLatestBlock:
    '''Insert block and transactions data to the database.
       After inserting, send message to template ("block_live_update")
    '''
    _channel_layer = get_channel_layer()

    def _send_message(self, block):
        async_to_sync(self._channel_layer.group_send)(
            "blocks", {
                "type": "send_message",
                "text": {
                    "height": block.height,
                    "hash": block.hash,
                },
            }
        )
    

    def __call__(self, data_about_block):
        transactions = []
        tx_list = data_about_block.copy()['tx']
        data_about_block.pop('tx')
        block = Block.objects.create(**data_about_block)

        for tx in tx_list:
            tx.update({'block_index': block})

        transactions = Transaction.objects.bulk_create([Transaction(**tx) for tx in tx_list])
            
        BlockchainUpdate(block, transactions)

        self._send_message(block)


LatestBlock = _NewLatestBlock()
