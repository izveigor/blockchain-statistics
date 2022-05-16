import requests
from blockchain.helpers import json_decoder
from status.models import Block, Transaction
import time
from blockchain.constants import (
    URL,
    NEW_BLOCK_WAITING_TIME,
    NEED_FIELDS_OF_INPUTS_AND_OUT,
    NEED_FIELDS_OF_TRANSACTION,
    NEED_FIELDS_OF_BLOCK,
)
import json
import asyncio
import websockets
from .blockchain import blockchain_update
from blockchain.send import send_error_to_block_live_update
from blockchain.types_ import (
    TypeUnclearedBlock,
    TypeInputsAndOut,
    TypeTransactionAttributes,
    TypeDataFromTransaction,
    TypeBlockAttributes,
)
from typing import Any, Union


def _clear_data(data: Any, need_fields_tuple: tuple[str, ...]) -> Any:
    """Check and clear data"""
    need_fields: list[str] = list(need_fields_tuple)
    result: Any = data.copy()
    for fields in data:
        try:
            need_fields.remove(fields)
        except ValueError:
            result.pop(fields)
    if len(need_fields) != 0:
        raise ValueError
    return result


def _get_data_from_transactions(transactions: Any) -> TypeDataFromTransaction:
    """Function of clearing and checking data of transactions
    from api"""

    data_from_transactions: TypeDataFromTransaction = {
        "price": 0,
        "number_of_satoshi": 0,
        "number_of_transactions": 0,
        "number_of_inputs": {"number_of_inputs": 0},
        "number_of_outputs": {"number_of_outputs": 0},
        "max_price_of_transaction": {"price": 0},
    }

    tx_indexes: list[int] = []
    transaction: Any
    for transaction in transactions:
        try:
            tx_result: Any = _clear_data(transaction, NEED_FIELDS_OF_TRANSACTION)
        except ValueError:
            continue
        else:
            tx_result.update(
                {"number_of_inputs": 0, "number_of_outputs": 0, "price": 0}
            )

        addresses: dict[str, int] = {}
        tx_indexes.append(tx_result["tx_index"])
        data_from_transactions["number_of_transactions"] += 1

        for input_ in tx_result.pop("inputs"):
            try:
                new_input: TypeInputsAndOut = _clear_data(
                    input_["prev_out"], NEED_FIELDS_OF_INPUTS_AND_OUT
                )
            except ValueError:
                continue

            tx_result["number_of_inputs"] += 1
            prev_tx_index: int = new_input["tx_index"]
            is_previous_tx_index_in_tx_indexes: bool

            try:
                tx_indexes.index(prev_tx_index)
            except ValueError:
                is_previous_tx_index_in_tx_indexes = False
            else:
                is_previous_tx_index_in_tx_indexes = True
            if not (
                Transaction.objects.filter(tx_index=prev_tx_index).exists()
                or is_previous_tx_index_in_tx_indexes
            ):
                data_from_transactions["number_of_satoshi"] += new_input["value"]

            address: str
            value: int
            address, value = new_input["addr"], new_input["value"]
            if addresses.get(address):
                addresses[address] += value
            else:
                addresses[address] = value

        for out in tx_result.pop("out"):
            try:
                new_out: TypeInputsAndOut = _clear_data(
                    out, NEED_FIELDS_OF_INPUTS_AND_OUT
                )
            except ValueError:
                continue

            tx_result["number_of_outputs"] += 1

            if addresses.get(new_out["addr"]) is None:
                tx_result["price"] += new_out["value"]

        data_from_transactions["price"] += tx_result["price"]

        if (
            data_from_transactions["max_price_of_transaction"]["price"]
            < tx_result["price"]
        ):
            data_from_transactions["max_price_of_transaction"].update({**tx_result})  # type: ignore

        if (
            data_from_transactions["number_of_inputs"]["number_of_inputs"]
            < tx_result["number_of_inputs"]
        ):
            data_from_transactions["number_of_inputs"].update({**tx_result})  # type: ignore

        if (
            data_from_transactions["number_of_outputs"]["number_of_outputs"]
            < tx_result["number_of_outputs"]
        ):
            data_from_transactions["number_of_outputs"].update({**tx_result})  # type: ignore

    Transaction.objects.bulk_create(
        [Transaction(tx_index=tx_index) for tx_index in tx_indexes]
    )

    return data_from_transactions


def get_block_api(height: int) -> None:
    """Function of clearing and checking data of blocks
    from api"""

    time.sleep(NEW_BLOCK_WAITING_TIME)
    request = requests.get(URL["RAW_BLOCK"] + str(height))
    if request.status_code == 200:
        data: Any = json_decoder(request.text, error_message="Block is not decrypted.")
        if data is None:
            return

        try:
            block: Any = _clear_data(data, NEED_FIELDS_OF_BLOCK)
        except ValueError:
            send_error_to_block_live_update(
                "New block doesn't have need fields, it won't be saved in database."
            )
        else:
            data_from_transactions: TypeDataFromTransaction = (
                _get_data_from_transactions(block.pop("tx"))
            )
            Block.objects.create(**block)
            blockchain_update(block, data_from_transactions)
    else:
        send_error_to_block_live_update("API isn't avalaible.")


def get_latest_block_height() -> int:
    """Gets latest block height (only for download_blocks)"""
    request: requests.Response = requests.get(URL["LATEST_BLOCK"])
    if request.status_code == 200:
        data: Any = json_decoder(request.text)
        height: int = data["height"]
        return height
    raise requests.exceptions.ConnectionError()


async def client() -> None:
    async for websocket in websockets.connect(URL["WS_LATEST_BLOCK"]):
        print("WebSocket server runs!", flush=True)
        await websocket.send(json.dumps({"op": "blocks_sub"}))
        try:
            async for message in websocket:
                loop = asyncio.get_running_loop()
                result = json_decoder(message)["x"]["hash"]
                await loop.run_in_executor(None, get_block_api, result)
        except websockets.ConnectionClosed:
            print("WebSocket server disconnects!", flush=True)
            continue
