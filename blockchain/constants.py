URL = {
    "WS_LATEST_BLOCK": "wss://ws.blockchain.info/inv",
    "LATEST_BLOCK": "https://blockchain.info/latestblock",
    "RAW_BLOCK": "https://blockchain.info/rawblock/",
}

NEW_BLOCK_WAITING_TIME = 10.0
NUMBER_OF_BLOCKS_ON_A_PAGE = 5

NEED_FIELDS_OF_TRANSACTION = (
    "block_index",
    "hash",
    "inputs",
    "out",
    "time",
    "tx_index",
)

NEED_FIELDS_OF_INPUTS_AND_OUT = (
    "addr",
    "tx_index",
    "value",
)

NEED_FIELDS_OF_BLOCK = (
    "block_index",
    "hash",
    "height",
    "time",
    "tx",
)
