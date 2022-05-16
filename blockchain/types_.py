from typing import TypedDict, Any


class TypeClearedBlock(TypedDict, total=False):
    height: int
    block_index: int
    hash: str
    time: int


class TypeUnclearedBlock(TypeClearedBlock, total=False):
    tx: Any


class TypeLatestBlock(TypeClearedBlock, total=False):
    txIndexes: list[int]


class TypeBlockAttributes(TypedDict, total=False):
    price: int
    tx_number: int
    height: int
    hash: str
    time: int
    block_index: int


class TypeInputsAndOut(TypedDict, total=False):
    addr: str
    tx_index: int
    value: int


class TypeTransactionAttributes(TypedDict, total=False):
    price: int
    block_index: int
    hash: int
    number_of_inputs: int
    number_of_outputs: int
    time: int
    tx_index: int


class TypeDataFromTransaction(TypedDict, total=False):
    price: int
    number_of_satoshi: int
    number_of_transactions: int
    number_of_inputs: TypeTransactionAttributes
    number_of_outputs: TypeTransactionAttributes
    max_price_of_transaction: TypeTransactionAttributes


class TypeStringBlockchainAttributes(TypedDict, total=False):
    number_of_satoshi: int
    number_of_blocks: int
    number_of_transactions: int
    time_start: int


class TypeObjectBlockchainAttributes(TypedDict, total=False):
    new_block: TypeBlockAttributes
    new_block_the_largest_transaction_for_inputs: TypeTransactionAttributes
    new_block_the_largest_transaction_for_outputs: TypeTransactionAttributes
    new_block_the_most_expensive_transaction: TypeTransactionAttributes
    the_most_expensive_block: TypeBlockAttributes
    the_cheapest_block: TypeBlockAttributes
    the_largest_number_of_transactions: TypeBlockAttributes
    the_least_number_of_transactions: TypeBlockAttributes
    the_largest_transaction_for_inputs: TypeTransactionAttributes
    the_largest_transaction_for_outputs: TypeTransactionAttributes
    the_most_expensive_transaction: TypeTransactionAttributes


class TypeBlockchainAttributes(
    TypeStringBlockchainAttributes, TypeObjectBlockchainAttributes
):
    pass


class TypeSearchSegment(TypeBlockchainAttributes):
    start_blockchain: TypeBlockchainAttributes
    end_blockchain: TypeBlockchainAttributes
