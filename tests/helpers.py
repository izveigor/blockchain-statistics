from blockchain.helpers import json_decoder
from status.models import Block, Blockchain, SegmentNode
from django.db.models import Max
import json
import string
import random


ATTRIBUTES_OF_BLOCK = (
    "height",
    "block_index",
    "hash",
    "time",
)


ATTRIBUTES_OF_BLOCKCHAIN = (
    "number_of_satoshi",
    "number_of_blocks",
    "number_of_transactions",
    "time_start",
    "new_block",
    "new_block_the_largest_transaction_for_inputs",
    "new_block_the_largest_transaction_for_outputs",
    "new_block_the_most_expensive_transaction",
    "the_most_expensive_block",
    "the_cheapest_block",
    "the_largest_number_of_transactions",
    "the_least_number_of_transactions",
    "the_largest_transaction_for_inputs",
    "the_largest_transaction_for_outputs",
    "the_most_expensive_transaction",
)


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


def create_node(time, block, transaction):
    '''Creates nodes for testing'''
    blockchain_data = JsonData.first_blockchain
    blockchain_data['time_start'] = time
    blockchain_data['new_block'] = block

    blockchain_data['new_block_the_largest_transaction_for_inputs'] = transaction
    blockchain_data['new_block_the_largest_transaction_for_outputs'] = transaction
    blockchain_data['new_block_the_most_expensive_transaction'] = transaction

    blockchain = Blockchain.objects.create(**blockchain_data)
    return  {
            "node": SegmentNode.objects.create_node(blockchain=blockchain),
            "blockchain": blockchain
            }

def empty_function(*args, **kwargs):
    pass
