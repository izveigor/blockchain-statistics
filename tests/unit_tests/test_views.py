from .base import UnitTest
from tests.helpers import JsonData, create_blocks, empty_function
from status.models import Block, Blockchain, SegmentNode
from unittest.mock import patch
from update.blockchain import blockchain_update
from status.forms import TimelineBlockchainForm
from tests.helpers import create_node, JsonData
from blockchain.helpers import json_decoder
import json
from django.contrib.messages import get_messages


class ViewsTest(UnitTest):
    '''Unit test of views
    '''
    def test_home_page_returns_correct(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_paginator(self):
        create_blocks(10)

        response = self.client.get('/')
        paginator = response.context['paginator']
        for number in range(1, 3):
            page = paginator.page(number)
            self.assertEqual(
                list(page.object_list),
                list(Block.objects.all()[(number-1)*5:number*5])
            )

    @patch("update.blockchain.send_data", empty_function)
    def test_context(self):
        blockchain_update(JsonData.first_block_result, JsonData.first_data_from_transactions)
        response = self.client.get('/')
        context = response.context

        self.assertEqual(
            context['blockchain'],
            Blockchain.objects.all()[0]
        )

        self.assertIsInstance(
            context['form'],
            TimelineBlockchainForm
        )
    
    def test_segment_tree(self):
        segment_tree = JsonData.segment_tree.pop('second_node')

        for i in range(1, 2):
            data_for_testing = segment_tree['body'][str(i)]
            create_node(i, data_for_testing['the_most_expensive_block'], data_for_testing['the_largest_transaction_for_inputs'])

        response = self.client.post('/search', JsonData.timeline_json, content_type="application/json")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            json_decoder(response.content)['search_result'],
            SegmentNode.objects.search_segment(1, 4)
        )
    
    def test_error_form(self):
        segment_tree = JsonData.segment_tree.pop('second_node')
        data_for_testing = segment_tree['body']["1"]
        create_node(1, data_for_testing['the_most_expensive_block'], data_for_testing['the_largest_transaction_for_inputs'])

        timeline = JsonData.timeline
        timeline['time_start'], timeline['time_end'] = timeline['time_end'], timeline['time_start']

        response = self.client.post('/search', json.dumps(timeline), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            "Start time greater than end time!"
        )
