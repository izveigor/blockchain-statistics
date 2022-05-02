from status.models import Blockchain, SegmentNode
from blockchain.send import send_data


def blockchain_update(block, data_from_transactions):
    '''Function creates blockchain instance.
       After creating, send message to template ("blockchain_body")
    '''
    if Blockchain.objects.exists():
        blockchain = Blockchain.objects.first()
    else:
        blockchain = False

    blockchain_update = dict()
    transactions_number = data_from_transactions['number_of_transactions']

    blockchain_update['number_of_satoshi'] = data_from_transactions['number_of_satoshi']
    blockchain_update['number_of_blocks'] = 1
    blockchain_update['number_of_transactions'] = transactions_number

    block_attributes = result = {'price': data_from_transactions['price'], 'tx_number': transactions_number}
    block_attributes.update(block)

    blockchain_update['new_block_the_largest_transaction_for_inputs'] = data_from_transactions['number_of_inputs']
    blockchain_update['new_block_the_largest_transaction_for_outputs'] = data_from_transactions['number_of_outputs']
    blockchain_update['new_block_the_most_expensive_transaction'] = data_from_transactions['max_price_of_transaction']
    blockchain_update['new_block'] = block_attributes
    blockchain_update['time_start'] = block['time']

    if blockchain:
        for field in ('number_of_satoshi', 'number_of_blocks', 'number_of_transactions'):
            blockchain_update[field] += getattr(blockchain, field)

    for field, attribute, variable in zip(('the_most_expensive_block', 'the_largest_number_of_transactions'), 
                                          ('price', 'tx_number'), 
                                          (data_from_transactions['price'], transactions_number)):
        if blockchain and getattr(blockchain, field)[attribute] >= variable:
            blockchain_update[field] = getattr(blockchain, field)
        else:
            blockchain_update[field] = block_attributes

    for field, attribute, variable in zip(('the_largest_transaction_for_inputs', 'the_largest_transaction_for_outputs',
                                           'the_most_expensive_transaction'),
                                          ('number_of_inputs', 'number_of_outputs', 'price'),
                                          list(data_from_transactions.values())[3:]):
    
        if blockchain and getattr(blockchain, field)[attribute] >= variable[attribute]:
            blockchain_update[field] = getattr(blockchain, field)
        else:
            blockchain_update[field] = variable
        
    for field, attribute, variable in zip(('the_cheapest_block', 'the_least_number_of_transactions'), 
                                          ('price', 'tx_number'), (data_from_transactions['price'], transactions_number)):
        if blockchain and getattr(blockchain, field)[attribute] <= variable:
            blockchain_update[field] = getattr(blockchain, field)
        else:
            blockchain_update[field] = block_attributes

    blockchain_model = Blockchain.objects.create(**blockchain_update)
    SegmentNode.objects.create_node(
        blockchain_model
    )

    send_data(block, blockchain_update)
