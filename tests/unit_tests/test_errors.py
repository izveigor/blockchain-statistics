from .base import UnitTest
from blockchain.errors import ErrorHandler
from unittest.mock import patch
from tests.helpers import JsonData
from update.api import BlockData
import json


@patch('update.api.requests.get')
class ErrorTest(UnitTest):
    '''Unit test of errors (if api gets bad data)'''
    @patch('update.api.ErrorHandler.send_error_to_block_live_update')
    def test_api_does_not_have_status_200(self, mock_error_handler, mock_get):
        mock_get.return_value = type('', (), {"status_code": 404, "text": None})
        BlockData(1)
        mock_error_handler.assert_called_with("API isn't avalaible.")
    
    @patch('update.api.ErrorHandler.send_error_to_block_live_update')
    def test_block_does_not_have_need_fields(self, mock_error_handler, mock_get):
        block = JsonData.first_block
        block.pop('time')
        mock_get.return_value = type('', (), {"status_code": 200, "text": json.dumps(block)})
        BlockData(1)
        mock_error_handler.assert_called_with("New block doesn't have need fields, it won't be saved in database.")
    
    @patch('blockchain.helpers.ErrorHandler.send_error_to_block_live_update')
    def test_block_does_not_have_json_encoding(self, mock_error_handler, mock_get):
        block = JsonData.first_block
        mock_get.return_value = type('', (), {"status_code": 200, "text": block})
        BlockData(1)
        mock_error_handler.assert_called_with("Block is not decrypted.")