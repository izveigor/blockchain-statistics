import json
import random
import string
from typing import Any, Optional, TypedDict
from unittest import TestCase

from django.db.models import Max, Model

from blockchain.helpers import json_decoder
from blockchain.types_ import (
    TypeBlockchainAttributes,
    TypeClearedBlock,
    TypeLatestBlock,
    TypeTransactionAttributes,
    TypeUnclearedBlock,
)
from status.models import Block, Blockchain, SegmentNode


class _JsonData:
    """Testing class of getting data from "data.json"
    To get test data from file, get attribute from instance of class (JsonData) with name of field.
    For example: JsonData.first_block_result (return clearing first block like a python dictionary)
    To get test data with json encoding, get attribute from instance of class (JsonData) with name of field + "_json".
    For example: JsonData.first_block_json (return first block like a json data).
    """

    _file_name = "tests/data.json"

    def __getattr__(self, name: str) -> Any:
        with open(self._file_name) as json_file:
            file_data = json_file.read()
            data: Any = json_decoder(file_data)
            try:
                if name.rfind("_json", -5) != -1:
                    return json.dumps(data[name[:-5]])
                else:
                    return data[name]
            except KeyError as e:
                raise e


JsonData = _JsonData()


def check_model_fields(
    self: TestCase, model: Model, data: dict[Any, Any], *args: str
) -> None:
    """Compare fields of model and testing data from JsonData"""
    fields: dict[str, Any] = vars(model)
    fields.pop("_state")

    for delete_field in args:
        fields.pop(delete_field)

    for key in fields.keys():
        self.assertEqual(
            fields[key], data[key if key.rfind("_id", -3) == -1 else key[:-3]]
        )


def get_random_hash() -> str:
    """Get random hash for creating a testing block"""
    alphabet = string.hexdigits[:-5]
    random_hash = ""
    for i in range(64):
        random_hash += alphabet[random.randint(0, 15)]

    return random_hash


def get_random_block_data() -> TypeClearedBlock:
    """Get random block data for testing (without repeating unique fields)"""
    block_data: TypeLatestBlock = JsonData.latest_block
    block_data.pop("txIndexes")

    block_data["hash"] = get_random_hash()
    block_index_max = Block.objects.aggregate(Max("block_index"))["block_index__max"]
    height_max = Block.objects.aggregate(Max("height"))["height__max"]

    field: str
    for field in ("block_index", "height"):
        field_max: Optional[int] = Block.objects.aggregate(Max(field))[field + "__max"]
        if field_max is None:
            block_data[field] += 1  # type: ignore
        else:
            block_data[field] = field_max + 1  # type: ignore

    return block_data


def create_blocks(number: int) -> None:
    """Creates random blocks for testing"""
    i: int
    for i in range(number):
        block_data = get_random_block_data()
        Block.objects.create(**block_data)


TypeCreateNode = TypedDict(
    "TypeCreateNode",
    {"node": SegmentNode, "blockchain": TypeBlockchainAttributes},
    total=False,
)


def create_node(
    time: int, block: TypeClearedBlock, transaction: TypeTransactionAttributes
) -> TypeCreateNode:
    """Creates nodes for testing"""
    blockchain_data: TypeBlockchainAttributes = {
        **JsonData.first_blockchain,  # type: ignore
        "time_start": time,
        "new_block": block,
        "new_block_the_largest_transaction_for_inputs": transaction,
        "new_block_the_largest_transaction_for_outputs": transaction,
        "new_block_the_most_expensive_transaction": transaction,
    }

    blockchain: Blockchain = Blockchain.objects.create(**blockchain_data)
    return {
        "node": SegmentNode.objects.create_node(blockchain=blockchain),
        "blockchain": blockchain_data,
    }
