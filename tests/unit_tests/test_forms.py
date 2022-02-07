from .base import UnitTest
from status.forms import TimelineBlockchainForm
from tests.helpers import JsonData, create_node
from status.models import SegmentNode


class FormTest(UnitTest):
    '''Unit test form of timeline blockchain search'''

    def test_form_valid(self):
        segment_tree = JsonData.segment_tree.pop('first_node')
        create_node(1, segment_tree['body']["1"]['the_most_expensive_block'])
        timeline = JsonData.timeline
        form = TimelineBlockchainForm(timeline)
        self.assertTrue(form.is_valid())

    def test_start_less_than_end(self):
        segment_tree = JsonData.segment_tree.pop('first_node')
        create_node(1, segment_tree['body']["1"]['the_most_expensive_block'])
        timeline = JsonData.timeline
        timeline['time_start'], timeline['time_end'] = timeline['time_end'], timeline['time_start']
        form = TimelineBlockchainForm(timeline)
        self.assertEqual(
            form.errors['__all__'][0],
            "Start time greater than end time! Please reload the page!"
        )

    def test_error_period(self):
        segment_tree = JsonData.segment_tree.pop('second_node')

        for i, time in enumerate((5, 7), start=1):
            create_node(time, segment_tree['body'][str(i)]['the_most_expensive_block'])

        timeline = JsonData.timeline
        form = TimelineBlockchainForm(timeline)
        self.assertEqual(
            form.errors['__all__'][0],
            "Server doesn't have data in this period! Please reload the page!"
        )

    def test_empty(self):
        segment_tree = JsonData.segment_tree.pop('first_node')
        create_node(1, segment_tree['body']["1"]['the_most_expensive_block'])
        
        timeline = JsonData.timeline
        for field in list(timeline.keys()):
            new_timeline = timeline.copy()
            new_timeline.pop(field)
            form = TimelineBlockchainForm(new_timeline)
            self.assertEqual(
                form.errors['__all__'][0],
                'Field "{}" is empty! Please reload the page!'.format(field)
            )
    
    def test_start_time_form_greater_than_end_time_segment_node(self):
        segment_tree = JsonData.segment_tree.pop('first_node')
        create_node(1, segment_tree['body']["1"]['the_most_expensive_block'])

        timeline = JsonData.timeline
        timeline['time_start'] = "00:00:02"
        form = TimelineBlockchainForm(timeline)
        self.assertEqual(
            form.errors['__all__'][0],
            "No one element doesn't falls within this period! Please reload the page!"
        )