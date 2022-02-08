import requests
from blockchain.helpers import json_decoder
from status.models import Block
import time 
from blockchain.constants import URL
import json
from .latest_block import LatestBlock
from blockchain.constants import NEW_BLOCK_WAITING_TIME
from blockchain.errors import ErrorHandler
import asyncio
import websockets


def _clear_data(data, need_fields_tuple):
    '''Check and clear data 
    '''
    need_fields = list(need_fields_tuple)
    result = data.copy()
    for fields in data:
        try:
            need_fields.index(fields)
            need_fields.remove(fields)
        except ValueError:
            result.pop(fields)
    if len(need_fields) != 0:
        return False
    return result


class _TransactionAPI:
    '''Class for clearing and checking data of transactions
       from api'''
    _need_fields_transaction = (
        'hash',
        'tx_index',
        'time',
        "block_index",
        'inputs',
        'out',
    )
    _need_fields_ins_and_out = (
        'tx_index',
        'value',
        'addr',
    )
    
    def _get_result(self, transaction):
        tx_result = _clear_data(transaction, self._need_fields_transaction)
        tx_result['inputs'] = []
        tx_result['out'] = []
        for input_ in transaction['inputs']:
            prev_out = input_['prev_out']
            tx_index=prev_out['spending_outpoints'][0]['tx_index']
            new_input = _clear_data(prev_out, self._need_fields_ins_and_out)
            if not new_input:
                continue
            new_input['tx_index_prev'] = new_input['tx_index']
            new_input['tx_index'] = tx_index
            tx_result['inputs'].append(new_input)
        for output in transaction['out']:
            new_out = _clear_data(output, self._need_fields_ins_and_out)
            if not new_out:
                continue
            tx_result['out'].append(new_out)
        return tx_result

    def __call__(self, tx):
        result = self._get_result(tx)
        if result:
            return result
        else:
            print("Wrong data")


class _BlockAPI:
    '''Class for clearing and checking data of blocks
       from api'''
    _TransactionData = _TransactionAPI()
    _need_fields = (
        'height',
        'hash',
        'time',
        'block_index',
        'tx',
    )

    def __call__(self, height):
        time.sleep(NEW_BLOCK_WAITING_TIME)
        request = requests.get(URL['RAW_BLOCK'] + str(height))
        if request.status_code == 200:
            data = json_decoder(request.text, error_message="Block is not decrypted.")
            if data is None:
                return

            block = _clear_data(data, self._need_fields)
            if block:
                result_block = block.copy()
                result_block['tx'] = []
                for tx in block['tx']:
                    clear_transaction = self._TransactionData(tx)
                    result_block['tx'].append(clear_transaction)
                LatestBlock(result_block)
            else:
                ErrorHandler.send_error_to_block_live_update(
                    "New block doesn't have need fields, it won't be saved in database."
                )
        else:
            ErrorHandler.send_error_to_block_live_update(
                "API isn't avalaible."
            )


class _GetLatestBlockHeight:
    '''Gets latest block height (only for download_blocks)
    '''
    def __call__(self):
        request = requests.get(URL['LATEST_BLOCK'])
        if request.status_code == 200:
            data = json_decoder(request.text)
            height = data['height']
            return height


BlockData = _BlockAPI()
GetLatestBlockHeight = _GetLatestBlockHeight()


async def client():
    async for websocket in websockets.connect(URL['WS_LATEST_BLOCK']):
        await websocket.send(json.dumps({'op': 'blocks_sub'}))
        try:
            async for message in websocket:
                loop = asyncio.get_event_loop()
                result = json_decoder(message)['x']['hash']
                await loop.run_in_executor(None, BlockData, result)
        except websockets.ConnectionClosed:
            continue
