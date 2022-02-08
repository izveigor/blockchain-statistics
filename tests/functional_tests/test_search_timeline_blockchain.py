from .base import FunctionalTest
from selenium.webdriver.common.keys import Keys
from tests.helpers import JsonData, create_node, ATTRIBUTES_OF_BLOCKCHAIN
from update.blockchain import BlockchainUpdate
from unittest.mock import patch
from status.models import SegmentNode


class TimelineTest(FunctionalTest):
    '''Functional test search timeline blockchain (models.SegmentNode)
    '''
    
    def test_empty(self):
        self.browser.get(self.live_server_url)

        for id in ("form_time", "timeline_blockchain_body"):
            self.assertEqual(
                self._get_element_by_id(id).value_of_css_property("display"),
                "none"
            )
        
        self.assertEqual(
            self._get_element_by_id("empty_search_blockchain").text,
            "No data for search blockchain!"
        )

        segment_tree = JsonData.segment_tree.pop("first_node")
        create_node(1, segment_tree['body']['1']['the_most_expensive_block'])

        self.browser.get(self.live_server_url)
        self.assertEqual(
            self._get_element_by_id("form_time").value_of_css_property("display"),
            "flex"
        )

        self.assertEqual(
            self._get_element_by_id("timeline_blockchain_body").value_of_css_property("display"),
            "none"
        )
    
    def _mock_blockchain(self, time, segment_tree_data):
        first_blockchain = JsonData.first_blockchain
        create_node(time, segment_tree_data)
        self._send_message(first_blockchain)

    @patch('update.blockchain._BlockchainUpdate.__call__', _mock_blockchain)
    def test_form_after_send_blockchain(self):
        segment_tree = JsonData.segment_tree.pop('second_node')
        self.browser.get(self.live_server_url)

        for time in range(1, 2):
            BlockchainUpdate(time, segment_tree['body'][str(time)]['the_most_expensive_block'])

        self._test_form()


    def test_form_after_add_nodes(self):
        segment_tree = JsonData.segment_tree.pop('second_node')
        for time in range(1, 2):
            create_node(time, segment_tree['body'][str(time)]['the_most_expensive_block'])

        self.browser.get(self.live_server_url)
        self._test_form()

    def _test_form(self):
        data = JsonData.timeline

        for key in data.keys():
            web_element = self._get_element_by_id('form_' + key)
            web_element.send_keys(data[key])

        self._get_element_by_id('search_button').click()

        self.assertEqual(
            self._get_element_by_id("timeline_blockchain_body").value_of_css_property('display'),
            "block"
        )

        search_blockchain_objects = (
            'the_most_expensive_block',
            'the_cheapest_block',
            'the_largest_number_of_transactions',
            'the_least_number_of_transactions'
        )

        search_result = SegmentNode.objects.search_segment(1, 4)
        start_blockchain = search_result.pop('start_blockchain')
        end_blockchain = search_result.pop('end_blockchain')

        self.assertEqual(
            self._get_element_by_id('timeline_price').text,
            str(search_result['price'])
        )

        for object_model in search_blockchain_objects:
            field = search_result[object_model]
            for key in field.keys():
                self.assertEqual(
                    str(field[key]),
                    self._get_element_by_id('timeline_' + key + '_' + object_model).text
                )
        
        attributes_string = ATTRIBUTES_OF_BLOCKCHAIN[:4]
        attributes_objects = ATTRIBUTES_OF_BLOCKCHAIN[5:]

        for field in attributes_string:
            self.assertEqual(
                self._get_element_by_id('timeline_blockchain_' + field).text,
                str(start_blockchain[field]) + ' -> ' + str(end_blockchain[field])
            )

        for object_model in search_blockchain_objects:
            field = start_blockchain[object_model]
            for key in field.keys():
                self.assertEqual(
                    str(start_blockchain[object_model][key]) + ' -> ' + str(end_blockchain[object_model][key]),
                    self._get_element_by_id('timeline_blockchain_' + key + '_' + object_model).text
                )
