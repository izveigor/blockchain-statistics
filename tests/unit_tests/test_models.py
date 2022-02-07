from .base import UnitTest
from tests.helpers import JsonData
from status.models import Block, Transaction, Blockchain
from tests.helpers import check_model_fields


class ModelsTest(UnitTest):
    '''Unit test of models (Block, Transaction, Blockchain)
    '''
    def test_block(self):
        block_data = JsonData.latest_block
        block_data.pop('txIndexes')
        first_block = Block.objects.create(**block_data)

        block_data['height'] -= 1
        block_data['block_index'] -= 1
        second_block = Block.objects.create(**block_data)

        self.assertEqual(
            list(Block.objects.all()),
            [first_block, second_block]
        )

    def test_transaction(self):
        block_data = JsonData.latest_block
        block_data.pop('txIndexes')
        block = Block.objects.create(**block_data)

        transaction_data = JsonData.transaction_result
        block_index = transaction_data.pop('block_index')

        transaction = Transaction.objects.create(block_index=block, **transaction_data)
        transaction_data.update({'block_index': block_index})
        check_model_fields(self, transaction, transaction_data)

    def test_blockchain(self):
        first_blockchain_data = JsonData.first_blockchain
        first_blockchain = Blockchain.objects.create(**first_blockchain_data)
        check_model_fields(self, first_blockchain, first_blockchain_data)

        second_blockchain_data = JsonData.second_blockchain
        second_blockchain = Blockchain.objects.create(**second_blockchain_data)
        check_model_fields(self, second_blockchain, second_blockchain_data)

        self.assertEqual(
            list(Blockchain.objects.all()),
            [second_blockchain, first_blockchain]
        )
