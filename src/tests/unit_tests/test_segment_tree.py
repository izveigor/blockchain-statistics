from typing import Any

from status.models import Blockchain, SegmentNode
from tests.helpers import JsonData, check_model_fields, create_node

from .base import UnitTest


class SegmentTreeTest(UnitTest):
    """Unit test of segment tree (models.SegmentNode)"""

    _attributes = (
        "price",
        "the_most_expensive_block",
        "the_cheapest_block",
        "the_largest_number_of_transactions",
        "the_least_number_of_transactions",
        "the_largest_transaction_for_inputs",
        "the_largest_transaction_for_outputs",
        "the_most_expensive_transaction",
    )
    _node_ids = [1] + [i for i in range(2, 16, 2)]

    def _create_test_array(self, number: int) -> Any:
        start_array: dict[Any, Any] = {}
        array: dict[Any, Any] = {}
        for attr in self._attributes:
            start_array[attr] = []
            array[attr] = []

        segment_tree = JsonData.segment_tree
        node_ids = [1] + [i for i in range(2, number * 2, 2)]
        for node_id in node_ids:
            body = segment_tree[list(segment_tree.keys())[number - 1]]["body"]
            node_data = body[str(node_id)]
            for attr in self._attributes:
                start_array[attr].append(node_data[attr])

        for attr, function, field in zip(
            self._attributes,
            (sum, max, min, max, min, max, max, max),
            (
                None,
                "price",
                "price",
                "tx_number",
                "tx_number",
                "number_of_inputs",
                "number_of_outputs",
                "price",
            ),
        ):
            for i in range(number):
                p = []
                for j in range(i, number + 1):
                    if i == j:
                        p.append(start_array[attr][i])
                    else:
                        if function is sum:
                            p.append(function(start_array[attr][i:j]))  # type: ignore
                        else:
                            p.append(
                                function(start_array[attr][i:j], key=lambda x: x[field])  # type: ignore
                            )
                array[attr].append(p)

        def delete_state(blockchain_dict: Any) -> Any:
            blockchain_dict.pop("_state")
            return blockchain_dict

        return {
            "start_blockchain": [
                [
                    delete_state(Blockchain.objects.get(time_start=i).__dict__)
                    for j in range(number + 2 - i)
                ]
                for i in range(1, number + 1)
            ],
            **array,
            "end_blockchain": [
                [delete_state(Blockchain.objects.get(time_start=i).__dict__)]
                + [
                    delete_state(Blockchain.objects.get(time_start=j).__dict__)
                    for j in range(i, number + 1)
                ]
                for i in range(1, number + 1)
            ],
        }

    def test_create_nodes(self) -> None:
        segment_tree = JsonData.segment_tree
        for time, (nodes, node_id) in enumerate(
            zip(segment_tree.values(), self._node_ids), start=1
        ):
            data_for_testing = nodes["body"][str(node_id)]
            create_node(
                time,
                data_for_testing["the_most_expensive_block"],
                data_for_testing["the_largest_transaction_for_inputs"],
            )
            self.assertEqual(nodes["root"], SegmentNode.objects._get_root().id)

            for node_id, blockchain_time_starts in nodes["blockchains"].items():
                blockchains = []
                for blockchain_time_start in blockchain_time_starts:
                    blockchains.extend(
                        list(
                            Blockchain.objects.filter(time_start=blockchain_time_start)
                        )
                    )

                self.assertEqual(
                    list(SegmentNode.objects.get(id=node_id).blockchains.all()),
                    blockchains,
                )

            for node_id, node_data in nodes["body"].items():
                check_model_fields(
                    self, SegmentNode.objects.get(id=node_id), node_data, "id"
                )

    def test_search(self) -> None:
        segment_tree = JsonData.segment_tree
        attributes = ["start_blockchain"] + list(self._attributes) + ["end_blockchain"]
        for time, (nodes, node_id) in enumerate(
            zip(segment_tree.values(), self._node_ids), start=1
        ):
            data_for_testing = nodes["body"][str(node_id)]
            create_node(
                time,
                data_for_testing["the_most_expensive_block"],
                data_for_testing["the_largest_transaction_for_inputs"],
            )
            test_array = self._create_test_array(time)
            for i in range(1, time + 1):
                for j in range(i, time + 1):
                    array = {}
                    for attr in attributes:
                        array[attr] = test_array[attr][i - 1][j - i]
                    self.assertEqual(SegmentNode.objects.search_segment(i, j), array)
