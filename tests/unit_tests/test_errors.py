from .base import UnitTest
from blockchain.send import send_error_to_block_live_update
from unittest.mock import patch, Mock
from tests.helpers import JsonData
from update.api import get_block_api
import json


@patch("update.api.time.sleep")
@patch("update.api.requests.get")
class ErrorTest(UnitTest):
    """Unit test of errors (if api gets bad data)"""

    @patch("update.api.send_error_to_block_live_update")
    def test_api_does_not_have_status_200(
        self, mock_error_handler: Mock, mock_get: Mock, mock_time_sleep: Mock
    ) -> None:
        mock_get.return_value = type("", (), {"status_code": 404, "text": None})
        get_block_api(1)
        mock_error_handler.assert_called_with("API isn't avalaible.")

    @patch("update.api.send_error_to_block_live_update")
    def test_block_does_not_have_need_fields(
        self, mock_error_handler: Mock, mock_get: Mock, mock_time_sleep: Mock
    ) -> None:
        block = JsonData.first_block
        block.pop("time")
        mock_get.return_value = type(
            "", (), {"status_code": 200, "text": json.dumps(block)}
        )
        get_block_api(1)
        mock_error_handler.assert_called_with(
            "New block doesn't have need fields, it won't be saved in database."
        )

    @patch("blockchain.helpers.send_error_to_block_live_update")
    def test_block_does_not_have_json_encoding(
        self, mock_error_handler: Mock, mock_get: Mock, mock_time_sleep: Mock
    ) -> None:
        block = JsonData.first_block
        mock_get.return_value = type("", (), {"status_code": 200, "text": block})
        get_block_api(1)
        mock_error_handler.assert_called_with("Block is not decrypted.")
