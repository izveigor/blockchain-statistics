from .base import UnitTest
from status.forms import TimelineBlockchainForm
from tests.helpers import JsonData, create_node


class FormTest(UnitTest):
    """Unit test form of timeline blockchain search"""

    def test_form_valid(self):
        segment_tree = JsonData.segment_tree.pop("first_node")
        data_for_testing = segment_tree["body"]["1"]
        create_node(
            1,
            data_for_testing["the_most_expensive_block"],
            data_for_testing["the_largest_transaction_for_inputs"],
        )
        timeline = JsonData.timeline
        form = TimelineBlockchainForm(timeline)
        self.assertTrue(form.is_valid())

    def test_start_less_than_end(self):
        segment_tree = JsonData.segment_tree.pop("first_node")
        data_for_testing = segment_tree["body"]["1"]
        create_node(
            1,
            data_for_testing["the_most_expensive_block"],
            data_for_testing["the_largest_transaction_for_inputs"],
        )
        timeline = JsonData.timeline
        timeline["time_start"], timeline["time_end"] = (
            timeline["time_end"],
            timeline["time_start"],
        )
        form = TimelineBlockchainForm(timeline)
        self.assertEqual(form.errors["__all__"][0], "Start time greater than end time!")

    def test_error_period(self):
        segment_tree = JsonData.segment_tree.pop("second_node")

        for i, time in enumerate((5, 7), start=1):
            data_for_testing = segment_tree["body"][str(i)]
            create_node(
                time,
                data_for_testing["the_most_expensive_block"],
                data_for_testing["the_largest_transaction_for_inputs"],
            )

        timeline = JsonData.timeline
        form = TimelineBlockchainForm(timeline)
        self.assertEqual(
            form.errors["__all__"][0], "Server doesn't have data in this period!"
        )

    def test_empty(self):
        segment_tree = JsonData.segment_tree.pop("first_node")
        data_for_testing = segment_tree["body"]["1"]
        create_node(
            1,
            data_for_testing["the_most_expensive_block"],
            data_for_testing["the_largest_transaction_for_inputs"],
        )

        timeline = JsonData.timeline
        for field in list(timeline.keys()):
            new_timeline = timeline.copy()
            new_timeline.pop(field)
            form = TimelineBlockchainForm(new_timeline)
            self.assertEqual(
                form.errors["__all__"][0], 'Field "{}" is empty!'.format(field)
            )

    def test_start_time_form_greater_than_end_time_segment_node(self):
        segment_tree = JsonData.segment_tree.pop("first_node")
        data_for_testing = segment_tree["body"]["1"]
        create_node(
            1,
            data_for_testing["the_most_expensive_block"],
            data_for_testing["the_largest_transaction_for_inputs"],
        )

        timeline = JsonData.timeline
        timeline["time_start"] = "00:00:02"
        form = TimelineBlockchainForm(timeline)
        self.assertEqual(
            form.errors["__all__"][0],
            "No one element doesn't falls within this period!",
        )
