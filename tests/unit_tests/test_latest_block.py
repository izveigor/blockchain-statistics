from .base import UnitTest
from update.latest_block import LatestBlock
from tests.helpers import JsonData, check_model_fields, empty_function
from status.models import Block, Transaction
from unittest.mock import patch


@patch('update.latest_block.BlockchainUpdate', empty_function)
@patch('update.latest_block.LatestBlock._send_message')
class LatestBlockTest(UnitTest):
    '''Unit test of LatestBlock (update.latest_block.LatestBlock)'''

    def test_work(self, mock_send_message):
        LatestBlock(JsonData.first_block_result)
        
        block_model = Block.objects.all()[0]
        block_data = JsonData.first_block_result
        check_model_fields(self, block_model, block_data)

        for tx_data in block_data["tx"]:
            tx_model = Transaction.objects.get(tx_index=tx_data['tx_index'])
            check_model_fields(self, tx_model, tx_data)
        
        mock_send_message.assert_called_with(block_model)
        