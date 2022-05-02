from .base import UnitTest
from tests.helpers import JsonData, check_model_fields
from status.models import Blockchain
from unittest.mock import patch
from update.blockchain import blockchain_update


class TestBlockchainUpdate(UnitTest):
    """Unit test of BlockchainUpdate (update.blockchain.BlockchainUpdate)"""

    @patch("update.blockchain.SegmentNode.objects.create_node")
    @patch("update.blockchain.send_data")
    def test_create(self, mock_send_message, mock_create_node):
        first_block = JsonData.first_block_result
        second_block = JsonData.second_block_result

        first_blockchain_data = JsonData.first_blockchain
        second_blockchain_data = JsonData.second_blockchain

        blockchain_update(first_block, JsonData.first_data_from_transactions)
        first_blockchain = Blockchain.objects.first()
        check_model_fields(self, first_blockchain, first_blockchain_data)

        mock_create_node.assert_called_with(first_blockchain)
        mock_send_message.assert_called_with(first_block, first_blockchain_data)

        blockchain_update(second_block, JsonData.second_data_from_transactions)
        second_blockchain = Blockchain.objects.first()
        check_model_fields(self, second_blockchain, second_blockchain_data)

        mock_create_node.assert_called_with(second_blockchain)
        mock_send_message.assert_called_with(second_block, second_blockchain_data)

        first_blockchain = Blockchain.objects.last()
        self.assertEqual(
            list(Blockchain.objects.all()), [second_blockchain, first_blockchain]
        )
