from .base import FunctionalTest
from tests.helpers import JsonData
from blockchain.constants import (
    STRING_ATTRIBUTES_OF_BLOCKCHAIN,
    OBJECT_ATTRIBUTES_OF_BLOCKCHAIN,
)
from status.models import Blockchain
from blockchain.send import send_data
import time


class TestBlockchain(FunctionalTest):
    """Functional test of blockchain"""

    def _check_blockchain(
        self, get_browser_before_blockchain_update: bool = False
    ) -> None:
        blockchain_data = JsonData.third_blockchain
        block_data = JsonData.first_block_result

        if get_browser_before_blockchain_update:
            self.browser.get(self.live_server_url)
            Blockchain.objects.create(**blockchain_data)
            send_data(block_data, blockchain_data)
            time.sleep(3)
        else:
            Blockchain.objects.create(**blockchain_data)
            self.browser.get(self.live_server_url)

        attributes_string = STRING_ATTRIBUTES_OF_BLOCKCHAIN
        attributes_objects = OBJECT_ATTRIBUTES_OF_BLOCKCHAIN

        blockchain = Blockchain.objects.all()[0]

        for field in attributes_string:
            self.assertEqual(
                self._get_element_by_id(field).text, str(getattr(blockchain, field))
            )

        for object_model in attributes_objects:
            json_field = getattr(blockchain, object_model)
            for key in json_field.keys():
                self.assertEqual(
                    str(json_field[key]),
                    self._get_element_by_id(key + "_" + object_model).text,
                )

    def test_empty(self) -> None:
        self.browser.get(self.live_server_url)
        empty = self._get_element_by_id("empty_blockchain")
        self.assertEqual(empty.text, "No data about blockchain!")

        self.assertEqual(
            self._get_element_by_id("blockchain_body").value_of_css_property("display"),
            "none",
        )

    def test_blockchain(self) -> None:
        self._check_blockchain()

    def test_send_blockchain(self) -> None:
        self._check_blockchain(get_browser_before_blockchain_update=True)
