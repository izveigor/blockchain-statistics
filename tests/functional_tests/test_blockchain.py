from .base import FunctionalTest
from tests.helpers import JsonData, check_model_fields, get_data_for_blockchain, empty_function, ATTRIBUTES_OF_BLOCKCHAIN
from status.models import Blockchain
from unittest.mock import patch
from update.blockchain import BlockchainUpdate
from unittest.mock import patch


class TestBlockchain(FunctionalTest):
    '''Functional test of blockchain
    '''
    def _check_blockchain(self, get_browser_before_blockchain_update=False):
        blockchain_data = JsonData.first_blockchain
        first_block_result = JsonData.first_block_result
        first_block_result['time'] = blockchain_data['time_start']

        data_for_blockchain_model = get_data_for_blockchain(first_block_result)

        if get_browser_before_blockchain_update:
            self.browser.get(self.live_server_url)
            BlockchainUpdate(**data_for_blockchain_model)
        else:
            BlockchainUpdate(**data_for_blockchain_model)
            self.browser.get(self.live_server_url)
        
        attributes_string = ATTRIBUTES_OF_BLOCKCHAIN[:4]
        attributes_objects = ATTRIBUTES_OF_BLOCKCHAIN[5:]

        blockchain = Blockchain.objects.all()[0]

        for field in attributes_string:
            self.assertEqual(
                self._get_element_by_id(field).text,
                str(getattr(blockchain, field))
            )

        for object_model in attributes_objects:
            json_field = getattr(blockchain, object_model)
            for key in json_field.keys():
                self.assertEqual(
                    str(json_field[key]),
                    self._get_element_by_id(key + '_' + object_model).text
                )
    
    def test_empty(self):
        self.browser.get(self.live_server_url)
        empty = self._get_element_by_id("empty_blockchain")
        self.assertEqual(empty.text, "No data about blockchain!")

        self.assertEqual(
            self._get_element_by_id("blockchain_body").value_of_css_property("display"),
            "none"
        )
    
    @patch("update.blockchain.BlockchainUpdate._send_message", empty_function)
    def test_blockchain(self):
        self._check_blockchain()
    
    def test_send_blockchain(self):
        self._check_blockchain(get_browser_before_blockchain_update=True)
