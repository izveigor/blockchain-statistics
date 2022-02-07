from status.models import Blockchain, Transaction, SegmentNode
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class _BlockchainUpdate:
    '''Class creates blockchain instance.
       After creating, send message to template ("blockchain_body")
    '''
    _channel_layer = get_channel_layer()

    def _send_message(self, blockchain_update):
        async_to_sync(self._channel_layer.group_send)(
            "blockchain", {
                "type": "send_message",
                "text": blockchain_update,
            }
        )

    def _get_data_from_transactions(self, transactions):
        data_from_transactions = {
            "price": 0, 
            "number_of_satoshi": 0, 
            "number_of_inputs": {"number_of_inputs": 0}, 
            "number_of_outputs": {"number_of_outputs": 0},
            "price_of_transaction": {"price": 0},
        }

        addresses = dict()

        for transaction in transactions:
            tx_ins = transaction.inputs
            price_of_transaction, number_of_inputs, number_of_outputs = 0, 0, 0

            for tx_in in tx_ins:
                number_of_inputs += 1
                addr = tx_in['addr']

                if not Transaction.objects.filter(tx_index=tx_in['tx_index_prev']).exists():
                    data_from_transactions['number_of_satoshi'] += tx_in['value']
        
                if addresses.get(addr) is not None:
                    addresses[addr] += tx_in['value']
                addresses[addr] = tx_in['value']

            tx_outs = transaction.out
            for tx_out in tx_outs:
                number_of_outputs += 1
                price_of_transaction += tx_out['value']
                addr = tx_out['addr']
                if addresses.get(addr) is not None:
                    price_of_transaction -= addresses.pop(addr)
            
            transaction_dict = transaction.__dict__
            transaction_dict.pop('_state')
            transaction_dict.pop('inputs')
            transaction_dict.pop('out')

            if data_from_transactions['price_of_transaction']['price'] < price_of_transaction:
                data_from_transactions['price_of_transaction'].update({**transaction_dict, "price": price_of_transaction})
    
            data_from_transactions['price'] += price_of_transaction
    
            if data_from_transactions['number_of_inputs']['number_of_inputs'] < number_of_inputs:
                data_from_transactions['number_of_inputs'].update({**transaction_dict, "number_of_inputs": number_of_inputs})

            if data_from_transactions['number_of_outputs']['number_of_outputs'] < number_of_outputs:
                data_from_transactions['number_of_outputs'].update({**transaction_dict, "number_of_outputs": number_of_outputs})
    
        return data_from_transactions

    def __call__(self, block, transactions):
        if Blockchain.objects.exists():
            blockchain = Blockchain.objects.first()
        else:
            blockchain = False

        blockchain_update = dict()

        transactions_number = len(transactions)
        data_from_transactions = self._get_data_from_transactions(transactions)

        blockchain_update['number_of_satoshi'] = data_from_transactions['number_of_satoshi']
        blockchain_update['number_of_blocks'] = 1
        blockchain_update['number_of_transactions'] = transactions_number 
        
        if blockchain:
            for field in ('number_of_satoshi', 'number_of_blocks', 'number_of_transactions'):
                blockchain_update[field] += getattr(blockchain, field)

        block_dict = block.__dict__
        block_dict.pop('_state')

        for field, attribute, variable in zip(('the_most_expensive_block', 'the_largest_number_of_transactions'), 
                                              ('price', 'tx_number'), 
                                              (data_from_transactions['price'], transactions_number)):
            if blockchain and getattr(blockchain, field)[attribute] >= variable:
                blockchain_update[field] = getattr(blockchain, field)
            else:
                result = {'price': data_from_transactions['price'], 'tx_number': transactions_number}
                result.update(block_dict)
                blockchain_update[field] = result

        for field, attribute, variable in zip(('the_largest_transactions_for_inputs', 'the_largest_transactions_for_outputs',
                                               'the_most_expensive_transactions'),
                                              ('number_of_inputs', 'number_of_outputs', 'price'),
                                              list(data_from_transactions.values())[2:]):
    
            if blockchain and getattr(blockchain, field)[attribute] >= variable[attribute]:
                blockchain_update[field] = getattr(blockchain, field)
            else:
                blockchain_update[field] = variable
        
        for field, attribute, variable in zip(('the_cheapest_block', 'the_least_number_of_transactions'), 
                                              ('price', 'tx_number'), (data_from_transactions['price'], transactions_number)):
            if blockchain and getattr(blockchain, field)[attribute] <= variable:
                blockchain_update[field] = getattr(blockchain, field)
            else:
                result = {'price': data_from_transactions['price'], 'tx_number': transactions_number}
                result.update(block_dict)
                blockchain_update[field] = result
        
        new_block = {'price': data_from_transactions['price'], "tx_number": transactions_number}
        new_block.update(block_dict)

        blockchain_update['new_block'] = new_block
        blockchain_update['time_start'] = block_dict['time']

        blockchain_model = Blockchain.objects.create(**blockchain_update)
        
        SegmentNode.objects.create_node(
            blockchain_model
        )

        self._send_message(blockchain_update)


BlockchainUpdate = _BlockchainUpdate()
