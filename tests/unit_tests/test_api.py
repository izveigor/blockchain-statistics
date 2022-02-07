from .base import UnitTest
from unittest.mock import patch
from tests.helpers import JsonData, TransactionData, empty_function
from update.api import BlockData, GetLatestBlockHeight


class TestAPI(UnitTest):
    '''Unit test of api'''

    @patch('update.api.requests.get', return_value = type('', (), {'status_code': 200, 'text': JsonData.latest_block_json}))
    def test_get_latest_block_hash(self, mock_get):
        self.assertEqual(
            GetLatestBlockHeight(),
            JsonData.latest_block['height']
        )

    @patch('update.api.time.sleep', empty_function)
    @patch('update.api.requests.get', return_value=type('', (), {"status_code": 200, "text": JsonData.first_block_json}))
    @patch('update.api.LatestBlock')
    def test_block_data(self, mock_latest_block, mock_get):
        BlockData(JsonData.latest_block['height']),
        mock_latest_block.assert_called_once_with(JsonData.first_block_result)

    def test_transaction(self): 
        self.assertEqual(
            TransactionData(JsonData.transaction),
            JsonData.transaction_result
        )
