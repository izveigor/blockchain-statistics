from .base import FunctionalTest
from selenium.webdriver.common.keys import Keys
from tests.helpers import JsonData, create_node
from update.blockchain import BlockchainUpdate
from unittest.mock import patch
from status.models import SegmentNode


class TimelineTest(FunctionalTest):
    '''Functional test search timeline blockchain (models.SegmentNode)
    '''
    def _get_dict_of_inputs(self):
        date_start = self._get_element_by_id('form_date_start')
        time_start = self._get_element_by_id('form_time_start')
        date_end = self._get_element_by_id('form_date_end')
        time_end = self._get_element_by_id('form_time_end')
        return {
            "date_start": date_start,
            "time_start": time_start,
            "date_end": date_end,
            "time_end": time_end
        }
    
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
        
        attributes = (
            "number_of_satoshi",
            "number_of_blocks",
            "number_of_transactions",
            "time_start",
            "new_block",
            "the_most_expensive_block",
            "the_cheapest_block",
            "the_largest_number_of_transactions",
            "the_least_number_of_transactions",
            "the_largest_transactions_for_inputs",
            "the_largest_transactions_for_outputs",
            "the_most_expensive_transactions"
        )
        
        attributes_string = attributes[:4]
        attributes_objects = attributes[5:]

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
