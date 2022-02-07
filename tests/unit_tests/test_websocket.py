from .base import UnitTest
from unittest.mock import patch
from tests.helpers import JsonData
from update.api import BlockData 


class TestWebsocket(UnitTest):
    '''Test to check all classes work!'''

    @patch('update.blockchain.BlockchainUpdate._send_message')
    @patch('update.latest_block.LatestBlock._send_message')
    @patch('update.api.requests.get')
    def test_give_data_to_block_data(self, mock_get, mock_latest_block_send_message, mock_blockchain_send_message):
        mock_get.return_value = type('', (), {'status_code': 200, 'text': JsonData.first_block_json})
        BlockData(1)
        mock_latest_block_send_message.assert_called_once()
        mock_blockchain_send_message.assert_called_once()