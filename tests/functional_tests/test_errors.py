from .base import FunctionalTest
from update.api import BlockData
import json
from unittest.mock import patch
from tests.helpers import JsonData, create_node


class ErrorTest(FunctionalTest):
    '''Functional test of errors (api errors and form errors)
    '''
    @patch('update.api.requests.get')
    def test_api_does_not_have_status_200(self, mock_get):
        mock_get.return_value = type('', (), {"status_code": 404, "text": None})

        self.browser.get(self.live_server_url)
        BlockData(1)
        block_live_update = self._get_element_by_id('body_block_live_update')
        self.assertEqual(
            block_live_update.text,
            "API isn't avalaible."
        )

    @patch('update.api.requests.get')
    def test_block_does_not_have_need_fields(self, mock_get):
        block = JsonData.first_block
        block.pop('time')
        mock_get.return_value = type('', (), {"status_code": 200, "text": json.dumps(block)})

        self.browser.get(self.live_server_url)
        BlockData(1)
        block_live_update = self._get_element_by_id('body_block_live_update')
        self.assertEqual(
            block_live_update.text,
            "New block doesn't have need fields, it won't be saved in database."
        )

    @patch('update.api.requests.get')
    def test_block_does_not_have_json_encoding(self, mock_get):
        block = JsonData.first_block
        mock_get.return_value = type('', (), {"status_code": 200, "text": block})

        self.browser.get(self.live_server_url)
        BlockData(1)
        block_live_update = self._get_element_by_id('body_block_live_update')
        self.assertEqual(
            block_live_update.text,
            "Block is not decrypted."
        )

    def test_form_error_period(self):
        segment_tree = JsonData.segment_tree.pop('second_node')

        for i, time in enumerate((5, 7), start=1):
            create_node(time, segment_tree['body'][str(i)]['the_most_expensive_block'])
        
        self.browser.get(self.live_server_url)

        data = JsonData.timeline

        for key in data.keys():
            web_element = self._get_element_by_id('form_' + key)
            web_element.send_keys(data[key])

        self._get_element_by_id('search_button').click()

        self.assertEqual(
            self._get_element_by_id('error_message').text,
            "Server doesn't have data in this period! Please reload the page!"
        )
    
    def test_form_start_less_than_end(self):
        segment_tree = JsonData.segment_tree.pop('first_node')
        create_node(1, segment_tree['body']["1"]['the_most_expensive_block'])
        
        self.browser.get(self.live_server_url)

        data = JsonData.timeline

        data['time_start'], data['time_end'] = data['time_end'], data['time_start']

        for key in data.keys():
            web_element = self._get_element_by_id('form_' + key)
            web_element.send_keys(data[key])

        self._get_element_by_id('search_button').click()

        self.assertEqual(
            self._get_element_by_id('error_message').text,
            "Start time greater than end time! Please reload the page!"
        )
    
    def test_form_is_empty(self):
        segment_tree = JsonData.segment_tree.pop('first_node')
        create_node(1, segment_tree['body']["1"]['the_most_expensive_block'])
        

        timeline = JsonData.timeline
        for field in list(timeline.keys()):
            new_timeline = timeline.copy()
            new_timeline.pop(field)

            self.browser.get(self.live_server_url)
            for key in new_timeline.keys():
                web_element = self._get_element_by_id('form_' + key)
                web_element.send_keys(new_timeline[key])
            
            self._get_element_by_id('search_button').click()

            self.assertEqual(
                self._get_element_by_id('error_message').text,
                'Field "{}" is empty! Please reload the page!'.format(field)
            )
    
    def test_start_time_form_greater_than_end_time_segment_node(self):
        segment_tree = JsonData.segment_tree.pop('first_node')
        create_node(1, segment_tree['body']["1"]['the_most_expensive_block'])

        self.browser.get(self.live_server_url)
        
        data = JsonData.timeline
        data['time_start'] = "00:00:02"

        for key in data.keys():
            web_element = self._get_element_by_id('form_' + key)
            web_element.send_keys(data[key])

        self._get_element_by_id('search_button').click()

        self.assertEqual(
            self._get_element_by_id('error_message').text,
            "No one element doesn't falls within this period! Please reload the page!"
        )
