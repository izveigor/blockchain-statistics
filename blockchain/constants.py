from .types_ import (
    TypeBlockchainAttributes,
    TypeClearedBlock,
    TypeInputsAndOut,
    TypeObjectBlockchainAttributes,
    TypeStringBlockchainAttributes,
    TypeUnclearedBlock,
)

URL: dict[str, str] = {
    "WS_LATEST_BLOCK": "wss://ws.blockchain.info/inv",
    "LATEST_BLOCK": "https://blockchain.info/latestblock",
    "RAW_BLOCK": "https://blockchain.info/rawblock/",
}

NEW_BLOCK_WAITING_TIME: float = 10.0
NUMBER_OF_BLOCKS_ON_A_PAGE: int = 5

NEED_FIELDS_OF_TRANSACTION: tuple[str, ...] = (
    "block_index",
    "hash",
    "inputs",
    "out",
    "time",
    "tx_index",
)
ATTRIBUTES_OF_BLOCK: tuple[str, ...] = tuple(TypeClearedBlock.__annotations__.keys())
NEED_FIELDS_OF_INPUTS_AND_OUT: tuple[str, ...] = tuple(
    TypeInputsAndOut.__annotations__.keys()
)
NEED_FIELDS_OF_BLOCK: tuple[str, ...] = tuple(TypeUnclearedBlock.__annotations__.keys())
STRING_ATTRIBUTES_OF_BLOCKCHAIN: tuple[str, ...] = tuple(
    TypeStringBlockchainAttributes.__annotations__.keys()
)
OBJECT_ATTRIBUTES_OF_BLOCKCHAIN: tuple[str, ...] = tuple(
    TypeObjectBlockchainAttributes.__annotations__.keys()
)
ATTRIBUTES_OF_BLOCKCHAIN: tuple[str, ...] = (
    STRING_ATTRIBUTES_OF_BLOCKCHAIN + OBJECT_ATTRIBUTES_OF_BLOCKCHAIN
)
