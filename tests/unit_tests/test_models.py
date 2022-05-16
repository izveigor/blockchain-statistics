from .base import UnitTest
from tests.helpers import JsonData
from status.models import Block, Blockchain, Transaction
from tests.helpers import check_model_fields


class ModelsTest(UnitTest):
    """Unit test of models (Block, Transaction, Blockchain)"""

    def test_block(self) -> None:
        block_data = JsonData.latest_block
        block_data.pop("txIndexes")
        first_block = Block.objects.create(**block_data)

        block_data["height"] -= 1
        block_data["block_index"] -= 1
        second_block = Block.objects.create(**block_data)

        self.assertEqual(list(Block.objects.all()), [first_block, second_block])

    def test_blockchain(self) -> None:
        first_blockchain_data = JsonData.first_blockchain
        first_blockchain = Blockchain.objects.create(**first_blockchain_data)
        check_model_fields(self, first_blockchain, first_blockchain_data)

        second_blockchain_data = JsonData.second_blockchain
        second_blockchain = Blockchain.objects.create(**second_blockchain_data)
        check_model_fields(self, second_blockchain, second_blockchain_data)

        self.assertEqual(
            list(Blockchain.objects.all()), [second_blockchain, first_blockchain]
        )

    def test_transaction(self) -> None:
        second_block = JsonData.second_block
        first_tx_index = second_block["tx"][0]["tx_index"]
        second_tx_index = second_block["tx"][1]["tx_index"]

        first_transaction = Transaction.objects.create(tx_index=first_tx_index)
        second_transaction = Transaction.objects.create(tx_index=second_tx_index)

        self.assertEqual(
            list(Transaction.objects.all()), [second_transaction, first_transaction]
        )
