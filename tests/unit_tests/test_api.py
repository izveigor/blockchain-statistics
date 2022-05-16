from .base import UnitTest
from unittest.mock import patch, Mock
from tests.helpers import JsonData, check_model_fields, get_random_hash
from update.api import (
    _get_data_from_transactions,
    get_block_api,
    get_latest_block_height,
)
from status.models import Transaction, Block


class TestAPI(UnitTest):
    """Unit test of api"""

    @patch(
        "update.api.requests.get",
        return_value=type(
            "", (), {"status_code": 200, "text": JsonData.latest_block_json}
        ),
    )
    def test_get_latest_block_hash(self, mock_get: Mock) -> None:
        self.assertEqual(get_latest_block_height(), JsonData.latest_block["height"])

    @patch("update.api.time.sleep")
    @patch(
        "update.api.requests.get",
        return_value=type(
            "", (), {"status_code": 200, "text": JsonData.first_block_json}
        ),
    )
    @patch("update.api.blockchain_update")
    def test_block_data(
        self, mock_blockchain_update: Mock, mock_get: Mock, mock_time_sleep: Mock
    ) -> None:
        latest_block = JsonData.latest_block
        first_block_result = JsonData.first_block_result

        get_block_api(latest_block["height"])
        mock_blockchain_update.assert_called_once_with(
            first_block_result, JsonData.first_data_from_transactions
        )

        check_model_fields(self, Block.objects.all()[0], first_block_result)


class TestGetDataFromTransactions(UnitTest):
    """Unit test of _get_data_from_transactions"""

    def test_get(self) -> None:
        transactions = JsonData.first_block["tx"]
        self.assertEqual(
            _get_data_from_transactions(transactions),
            JsonData.first_data_from_transactions,
        )

        for transaction_model, transaction in zip(
            Transaction.objects.all(),
            sorted(transactions, key=lambda x: x["tx_index"], reverse=True),  # type: ignore
        ):
            self.assertEqual(transaction_model.tx_index, transaction["tx_index"])

    def test_get_if_a_previous_transaction_in_the_database(self) -> None:
        transactions = JsonData.first_block["tx"]
        Transaction.objects.create(
            tx_index=transactions[0]["inputs"][0]["prev_out"]["tx_index"]
        )

        data_from_transactions = _get_data_from_transactions(transactions)
        test_data_from_transactions = JsonData.first_data_from_transactions
        test_data_from_transactions["number_of_satoshi"] -= transactions[0]["inputs"][
            0
        ]["prev_out"]["value"]

        self.assertEqual(data_from_transactions, test_data_from_transactions)

    def test_get_if_a_previous_transaction_in_tx_indexes(self) -> None:
        transactions = JsonData.first_block["tx"]
        delta = transactions[1]["inputs"][0]["prev_out"]["value"]
        transactions[1]["inputs"][0]["prev_out"]["tx_index"] = transactions[0][
            "tx_index"
        ]

        data_from_transactions = _get_data_from_transactions(transactions)
        test_data_from_transactions = JsonData.first_data_from_transactions
        test_data_from_transactions["number_of_satoshi"] -= delta

        self.assertEqual(data_from_transactions, test_data_from_transactions)

    def test_if_inputs_addr_equals_outputs_addr(self) -> None:
        transactions = JsonData.first_block["tx"]
        delta = transactions[0]["out"][1]["value"]
        transactions[0]["out"][1]["addr"] = transactions[0]["inputs"][0]["prev_out"][
            "addr"
        ]

        data_from_transactions = _get_data_from_transactions(transactions)
        test_data_from_transactions = JsonData.first_data_from_transactions
        test_data_from_transactions["price"] -= delta

        for field in ("number_of_inputs", "number_of_outputs"):
            test_data_from_transactions[field]["price"] -= delta

        test_data_from_transactions["max_price_of_transaction"] = {
            "hash": "505b42ec5e8499843ae3ad6f56f66ce52025d37205df19fb5777179d407b2978",
            "tx_index": 4227825818378990,
            "time": 1322131230,
            "block_index": 154595,
            "number_of_inputs": 1,
            "number_of_outputs": 2,
            "price": 8174436009,
        }

        self.assertEqual(data_from_transactions, test_data_from_transactions)
