from .base import UnitTest
from update.blockchain import BlockchainUpdate
from tests.helpers import JsonData, check_model_fields, get_data_for_blockchain
from status.models import Blockchain
from unittest.mock import patch
from update.blockchain import BlockchainUpdate


class TestBlockchainUpdate(UnitTest):
    '''Unit test of BlockchainUpdate (update.blockchain.BlockchainUpdate)'''

    def test_get_data_from_transactions(self):
        block = JsonData.first_block_result
        blockchain = JsonData.first_blockchain
        transactions = get_data_for_blockchain(block)['transactions']
        data_from_transactions = BlockchainUpdate._get_data_from_transactions(transactions)

        self.assertEqual(blockchain['number_of_satoshi'], data_from_transactions['number_of_satoshi'])
        self.assertEqual(blockchain['new_block']['price'], data_from_transactions['price'])

        for blockchain_attribute, values_data_from_transactions in zip(('the_largest_transactions_for_inputs', 'the_largest_transactions_for_outputs', 
                                                'the_most_expensive_transactions'), list(data_from_transactions.values())[2:]):
            self.assertEqual(blockchain[blockchain_attribute], values_data_from_transactions)
    
    @patch('update.blockchain.SegmentNode.objects.create_node')
    @patch("update.blockchain.BlockchainUpdate._send_message")
    def test_create(self, mock_send_message, mock_create_node):
        first_block = JsonData.first_block_result
        second_block = JsonData.second_block_result

        first_blockchain_data = JsonData.first_blockchain
        second_blockchain_data = JsonData.second_blockchain

        first_block['time'] = first_blockchain_data['time_start']
        second_block['time'] = second_blockchain_data['time_start']
        
        BlockchainUpdate(**get_data_for_blockchain(first_block))
        first_blockchain = Blockchain.objects.first()
        check_model_fields(self, first_blockchain, first_blockchain_data)

        mock_create_node.assert_called_with(first_blockchain)
        mock_send_message.assert_called_with(first_blockchain_data)

        BlockchainUpdate(**get_data_for_blockchain(second_block))
        second_blockchain = Blockchain.objects.first()
        check_model_fields(self, second_blockchain, second_blockchain_data)

        mock_create_node.assert_called_with(second_blockchain)
        mock_send_message.assert_called_with(second_blockchain_data)

        first_blockchain = Blockchain.objects.last()
        self.assertEqual(
            list(Blockchain.objects.all()),
            [second_blockchain, first_blockchain]
        )
