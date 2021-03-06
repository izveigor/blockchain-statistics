from __future__ import annotations

from typing import Any, Callable, Optional, Union

from django.db import models
from django.db.models import Max, QuerySet

from blockchain.types_ import (
    TypeBlockAttributes,
    TypeBlockchainAttributes,
    TypeSearchSegment,
    TypeTransactionAttributes,
)


class Transaction(models.Model):  # type: ignore
    """Used tx indexes"""

    tx_index = models.IntegerField(primary_key=True)

    class Meta:
        ordering = ["-tx_index"]


class Block(models.Model):  # type: ignore
    """Model of block"""

    height = models.IntegerField()
    hash = models.CharField(max_length=64)
    time = models.IntegerField()
    block_index = models.IntegerField(primary_key=True)

    class Meta:
        ordering = ["-height"]


class Blockchain(models.Model):  # type: ignore
    """Model of blockchain"""

    # About blockchain
    number_of_satoshi = models.IntegerField()
    number_of_blocks = models.IntegerField()
    number_of_transactions = models.IntegerField()
    time_start = models.IntegerField(primary_key=True)

    # Block
    new_block = models.JSONField()
    new_block_the_largest_transaction_for_inputs = models.JSONField()
    new_block_the_largest_transaction_for_outputs = models.JSONField()
    new_block_the_most_expensive_transaction = models.JSONField()

    the_most_expensive_block = models.JSONField()
    the_cheapest_block = models.JSONField()
    the_largest_number_of_transactions = models.JSONField()
    the_least_number_of_transactions = models.JSONField()

    # Transaction
    the_largest_transaction_for_inputs = models.JSONField()
    the_largest_transaction_for_outputs = models.JSONField()
    the_most_expensive_transaction = models.JSONField()

    class Meta:
        ordering = ["-time_start"]


class NodeManager(models.Manager):  # type: ignore
    """Manager for segment tree"""

    """
                     1-3           1-4
                    /   \        /     \ 
           1-2     1-2   3      1-2    3-4
    1 ->   / \ ->  / \     ->   / \    /  \ 
          1   2   1   2        1   2  3    4

    """

    def _get_root(self) -> Any:
        try:
            return self.get(node_left=None, node_right=None)
        except SegmentNode.DoesNotExist:
            return None

    def _get_reverse_relationship(self, node: SegmentNode, attribute: Any) -> Any:
        if hasattr(node, attribute):
            return getattr(node, attribute)
        else:
            return None

    def _create_single_node(self, blockchain: Blockchain) -> SegmentNode:
        block_index: int = blockchain.new_block["block_index"]
        node: SegmentNode = self.create(
            time_start=blockchain.time_start,
            price=blockchain.new_block["price"],
            the_most_expensive_block=blockchain.new_block,
            the_cheapest_block=blockchain.new_block,
            the_largest_number_of_transactions=blockchain.new_block,
            the_least_number_of_transactions=blockchain.new_block,
            the_largest_transaction_for_inputs=blockchain.new_block_the_largest_transaction_for_inputs,
            the_largest_transaction_for_outputs=blockchain.new_block_the_largest_transaction_for_outputs,
            the_most_expensive_transaction=blockchain.new_block_the_most_expensive_transaction,
        )
        node.blockchains.add(blockchain)
        return node

    def _get_previous_element_by_id(self, id: int) -> Optional[int]:
        queryset: QuerySet = self.filter(id__gte=id, id__lte=id)
        if queryset is None:
            return None

        previous_id: int = id
        while len(queryset) == 1:
            if previous_id == 1:
                return None

            previous_id -= 1
            queryset = self.filter(id__gte=previous_id, id__lte=id)

        return previous_id

    def _set_time_end(self, time: int, id: int) -> None:
        previous_id: Optional[int] = self._get_previous_element_by_id(id)
        if previous_id is None:
            return

        node: SegmentNode
        if previous_id == self.first().id:
            node = self.get(id=previous_id)
        else:
            node = self.get(id=self._get_previous_element_by_id(previous_id))
        node.time_end = time
        node.save()
        while self._get_reverse_relationship(node, "node_right") is not None:
            node = self._get_reverse_relationship(node, "node_right")
            node.time_end = time
            node.save()

    def _update_data_blockchain(
        self, blockchain: Blockchain, node: SegmentNode
    ) -> None:
        node.price += blockchain.new_block["price"]
        node.the_most_expensive_block = max(
            node.the_most_expensive_block,
            blockchain.new_block,
            key=lambda x: x["price"],  # type: ignore
        )
        node.the_cheapest_block = min(
            node.the_cheapest_block, blockchain.new_block, key=lambda x: x["price"]  # type: ignore
        )
        node.the_largest_number_of_transactions = max(
            node.the_largest_number_of_transactions,
            blockchain.new_block,
            key=lambda x: x["tx_number"],  # type: ignore
        )
        node.the_least_number_of_transactions = min(
            node.the_least_number_of_transactions,
            blockchain.new_block,
            key=lambda x: x["tx_number"],  # type: ignore
        )
        node.the_largest_transaction_for_inputs = max(
            node.the_largest_transaction_for_inputs,
            blockchain.new_block_the_largest_transaction_for_inputs,
            key=lambda x: x["number_of_inputs"],  # type: ignore
        )
        node.the_largest_transaction_for_outputs = max(
            node.the_largest_transaction_for_outputs,
            blockchain.new_block_the_largest_transaction_for_outputs,
            key=lambda x: x["number_of_outputs"],  # type: ignore
        )
        node.the_most_expensive_transaction = max(
            node.the_most_expensive_transaction,
            blockchain.new_block_the_most_expensive_transaction,
            key=lambda x: x["price"],  # type: ignore
        )
        node.save()
        node.blockchains.add(blockchain)

    def _update_blockchain(self, blockchain: Blockchain, node: SegmentNode) -> None:
        if self._get_reverse_relationship(node, "node_right") is None:
            self._update_data_blockchain(blockchain, node)
        else:
            self._update_data_blockchain(blockchain, node)
            self._update_blockchain(blockchain, node.node_right)

    def _add_node(self, blockchain: Blockchain, root: SegmentNode) -> SegmentNode:
        node: SegmentNode = self._create_single_node(blockchain)

        parent: SegmentNode = self._get_reverse_relationship(root, "node_right")
        if parent:
            parent.right = None
            parent.save()

        new_root = self.create(
            time_start=root.time_start,
            left=root,
            right=node,
            price=root.price + node.price,
            the_most_expensive_block=max(
                root.the_most_expensive_block,
                node.the_most_expensive_block,
                key=lambda x: x["price"],  # type: ignore
            ),
            the_cheapest_block=min(
                root.the_cheapest_block,
                node.the_cheapest_block,
                key=lambda x: x["price"],  # type: ignore
            ),
            the_largest_number_of_transactions=max(
                root.the_largest_number_of_transactions,
                node.the_largest_number_of_transactions,
                key=lambda x: x["tx_number"],  # type: ignore
            ),
            the_least_number_of_transactions=min(
                root.the_least_number_of_transactions,
                node.the_least_number_of_transactions,
                key=lambda x: x["tx_number"],  # type: ignore
            ),
            the_largest_transaction_for_inputs=max(
                root.the_largest_transaction_for_inputs,
                node.the_largest_transaction_for_inputs,
                key=lambda x: x["number_of_inputs"],  # type: ignore
            ),
            the_largest_transaction_for_outputs=max(
                root.the_largest_transaction_for_outputs,
                node.the_largest_transaction_for_outputs,
                key=lambda x: x["number_of_outputs"],  # type: ignore
            ),
            the_most_expensive_transaction=max(
                root.the_most_expensive_transaction,
                node.the_most_expensive_transaction,
                key=lambda x: x["price"],  # type: ignore
            ),
        )

        new_root.blockchains.set(root.blockchains.all())
        new_root.blockchains.add(blockchain)

        if parent:
            parent.right = new_root
            parent.save()
            self._update_blockchain(blockchain, parent)

        self._set_time_end(blockchain.time_start, node.id)
        return node

    def _update_tree(self, blockchain: Blockchain, root: SegmentNode) -> SegmentNode:
        if (
            (root.left is None)
            and (root.right is None)
            or (root.left.blockchains.count() == root.right.blockchains.count())
        ):
            return self._add_node(blockchain, root)
        else:
            return self._update_tree(blockchain, root.right)

    def create_node(self, blockchain: Blockchain) -> SegmentNode:
        node: SegmentNode
        root: SegmentNode
        root = self._get_root()
        if root is None:
            node = self._create_single_node(blockchain)
        else:
            node = self._update_tree(blockchain, root)
        return node

    @staticmethod
    def _update_nodes_attributes(attributes: Any, node: SegmentNode) -> None:
        attributes["price"] += node.price
        attributes["the_most_expensive_block"] = max(
            attributes["the_most_expensive_block"],
            node.the_most_expensive_block,
            key=lambda x: x["price"],  # type: ignore
        )
        attributes["the_cheapest_block"] = min(
            attributes["the_cheapest_block"],
            node.the_cheapest_block,
            key=lambda x: x["price"],  # type: ignore
        )
        attributes["the_largest_number_of_transactions"] = max(
            attributes["the_largest_number_of_transactions"],
            node.the_largest_number_of_transactions,
            key=lambda x: x["tx_number"],  # type: ignore
        )
        attributes["the_least_number_of_transactions"] = min(
            attributes["the_least_number_of_transactions"],
            node.the_least_number_of_transactions,
            key=lambda x: x["tx_number"],  # type: ignore
        )
        attributes["the_largest_transaction_for_inputs"] = max(
            attributes["the_largest_transaction_for_inputs"],
            node.the_largest_transaction_for_inputs,
            key=lambda x: x["number_of_inputs"],  # type: ignore
        )
        attributes["the_largest_transaction_for_outputs"] = max(
            attributes["the_largest_transaction_for_outputs"],
            node.the_largest_transaction_for_outputs,
            key=lambda x: x["number_of_outputs"],  # type: ignore
        )
        attributes["the_most_expensive_transaction"] = max(
            attributes["the_most_expensive_transaction"],
            node.the_most_expensive_transaction,
            key=lambda x: x["price"],  # type: ignore
        )

    def search_segment(self, time_start: int, time_end: int) -> TypeSearchSegment:
        attributes: dict[Any, Any] = {
            "price": 0,
            "the_most_expensive_block": {"price": 0},
            "the_cheapest_block": {"price": 210000000000000},
            "the_largest_number_of_transactions": {"tx_number": 0},
            "the_least_number_of_transactions": {"tx_number": 100000},
            "the_largest_transaction_for_inputs": {"number_of_inputs": 0},
            "the_largest_transaction_for_outputs": {"number_of_outputs": 0},
            "the_most_expensive_transaction": {"price": 0},
        }

        visited: set[SegmentNode] = set()
        node: SegmentNode = self._get_root()
        visited.add(node)
        while not (
            (time_start == node.time_start)
            and (node.time_end is not None)
            and (node.time_end <= time_end)
        ):
            left: SegmentNode = node.left
            right: SegmentNode = node.right
            if left is None and right is None:
                break

            if ((right.time_start <= time_start) and (right.time_end is None)) or (
                right.time_start <= time_start <= right.time_end
            ):
                visited.add(right)
                node = right
            else:
                if (right.time_end is not None) and (right.time_end <= time_end):
                    self._update_nodes_attributes(attributes, right)
                visited.add(left)
                node = left

        start_blockchain_model: Blockchain = node.blockchains.get(
            time_start=node.time_start
        )
        start_blockchain: dict[str, Any] = start_blockchain_model.__dict__
        start_blockchain.pop("_state")

        self._update_nodes_attributes(attributes, node)

        node = self._get_root()
        while time_end != node.time_end:
            left = node.left
            right = node.right
            if right is None:
                break
            if (time_end > left.time_end) or (
                (time_end == left.time_end) and (time_start == time_end)
            ):
                if (left not in visited) and (left.time_start >= time_start):
                    self._update_nodes_attributes(attributes, left)
                node = right
            else:
                node = left

        end_blockchain_model = node.blockchains.get(
            time_start=node.blockchains.aggregate(Max("time_start"))["time_start__max"]
        )
        end_blockchain = end_blockchain_model.__dict__
        end_blockchain.pop("_state")

        if node not in visited:
            self._update_nodes_attributes(attributes, node)
        return {
            "start_blockchain": start_blockchain,
            **attributes,  # type: ignore
            "end_blockchain": end_blockchain,
        }


class SegmentNode(models.Model):  # type: ignore
    """Model of segment node"""

    objects = NodeManager()
    time_start = models.IntegerField()
    time_end = models.IntegerField(null=True)

    price = models.IntegerField()
    the_most_expensive_block = models.JSONField()
    the_cheapest_block = models.JSONField()
    the_largest_number_of_transactions = models.JSONField()
    the_least_number_of_transactions = models.JSONField()
    the_largest_transaction_for_inputs = models.JSONField()
    the_largest_transaction_for_outputs = models.JSONField()
    the_most_expensive_transaction = models.JSONField()

    blockchains = models.ManyToManyField("Blockchain")

    left = models.OneToOneField(
        "self", null=True, related_name="node_left", on_delete=models.SET_NULL
    )
    right = models.OneToOneField(
        "self", null=True, related_name="node_right", on_delete=models.SET_NULL
    )
