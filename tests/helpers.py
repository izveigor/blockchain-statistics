from blockchain.helpers import json_decoder
from update.api import _TransactionAPI
from status.models import Block, Transaction, Blockchain, SegmentNode
from django.db.models import Max
import json
import string
import random

class _JsonData:
    '''Testing class of getting data from "data.json"
       To get test data from file, get attribute from instance of class (JsonData) with name of field.
       For example: JsonData.first_block_result (return clearing first block like a python dictionary)
       To get test data with json encoding, get attribute from instance of class (JsonData) with name of field + "_json".
       For example: JsonData.first_block_json (return first block like a json data).
    '''
    _file_name = 'tests/data.json'
    
    def __getattr__(self, name):
        with open(self._file_name) as json_file:
            file_data = json_file.read()
            data = json_decoder(file_data)
            try:
                if name.rfind('_json', -5) != -1:
                    return json.dumps(data[name[:-5]])
                else:
                    return data[name]
            except KeyError as e:
                raise e


JsonData = _JsonData()
TransactionData = _TransactionAPI()


def check_model_fields(self, model, data, *args):
    '''Compare fields of model and testing data from JsonData'''
    fields = vars(model)
    fields.pop('_state')

    for delete_field in args:
        fields.pop(delete_field)

    for key in fields.keys():
        self.assertEqual(
            fields[key],
            data[key if key.rfind('_id', -3) == -1 else key[:-3]]
        )


def get_random_hash():
    '''Get random hash for creating a testing block'''
    alphabet = string.hexdigits[:-5]
    random_hash = ''
    for i in range(64):
        random_hash += alphabet[random.randint(0, 15)]
    
    return random_hash


def get_random_block_data():
    '''Get random block data for testing (without repeating unique fields)'''
    block_data = JsonData.latest_block
    block_data.pop('txIndexes')

    block_data['hash'] = get_random_hash()
    block_index_max = Block.objects.aggregate(Max('block_index'))['block_index__max']
    height_max = Block.objects.aggregate(Max('height'))['height__max']

    for field in ('block_index', 'height'):
        field_max = Block.objects.aggregate(Max(field))[field + '__max']
        if field_max is None:
            block_data[field] += 1
        else:
            block_data[field] = field_max + 1
    
    return block_data


def create_blocks(number):
    '''Creates random blocks for testing'''
    for i in range(number):
        block_data = get_random_block_data()
        Block.objects.create(**block_data)


def create_node(time, block):
    '''Creates nodes for testing'''
    blockchain_data = JsonData.first_blockchain
    blockchain_data['time_start'] = time
    blockchain_data['new_block'] = block
    blockchain = Blockchain.objects.create(**blockchain_data)
    return  {
            "node": SegmentNode.objects.create_node(blockchain=blockchain),
            "blockchain": blockchain
            }


def get_data_for_blockchain(block_data):
    '''Get data for testing blockchain'''
    tx_list = block_data.pop('tx')
    block = Block.objects.create(**block_data)

    for tx in tx_list:
        tx.update({'block_index': block})
    
    Transaction.objects.bulk_create([Transaction(**tx) for tx in tx_list])

    return {"block": block, "transactions": Transaction.objects.filter(block_index=block)}


def empty_function(*args, **kwargs):
    pass