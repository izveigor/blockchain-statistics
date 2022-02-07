from django.db import models
from django.db.models import Max


class Transaction(models.Model):
    '''Model of transaction'''

    hash = models.CharField(max_length=32)
    tx_index = models.IntegerField(primary_key=True)
    time = models.IntegerField()
    block_index = models.ForeignKey('Block', on_delete=models.CASCADE)
    inputs = models.JSONField()
    out = models.JSONField()


class Block(models.Model):
    '''Model of block'''
    height = models.IntegerField()
    hash = models.CharField(max_length=64)
    time = models.IntegerField()
    block_index = models.IntegerField(primary_key=True)

    class Meta:
        ordering = ['-height']


class Blockchain(models.Model):
    '''Model of blockchain'''

    # About blockchain
    number_of_satoshi = models.IntegerField()
    number_of_blocks = models.IntegerField()
    number_of_transactions = models.IntegerField()
    time_start = models.IntegerField(primary_key=True)

    # Block
    new_block = models.JSONField()
    the_most_expensive_block = models.JSONField()
    the_cheapest_block = models.JSONField()
    the_largest_number_of_transactions = models.JSONField()
    the_least_number_of_transactions = models.JSONField()

    # Transaction
    the_largest_transactions_for_inputs = models.JSONField()
    the_largest_transactions_for_outputs = models.JSONField()
    the_most_expensive_transactions = models.JSONField()

    class Meta:
        ordering = ["-time_start"]


class NodeManager(models.Manager):
    '''Manager for segment tree'''
    '''
                     1-3           1-4
                    /   \        /     \ 
           1-2     1-2   3      1-2    3-4
    1 ->   / \ ->  / \     ->   / \    /  \ 
          1   2   1   2        1   2  3    4

    '''
    def _get_root(self):
        try:
            return self.get(node_left=None, node_right=None)
        except SegmentNode.DoesNotExist:
            return None
    
    def _get_reverse_relationship(self, node, attribute):
        if hasattr(node, attribute):
            return getattr(node, attribute)
        else:
            return None

    def _create_single_node(self, blockchain):
        block_index=blockchain.new_block['block_index']
        node = self.create(
            time_start=blockchain.time_start,
            price = blockchain.new_block['price'],
            the_most_expensive_block = blockchain.new_block,
            the_cheapest_block = blockchain.new_block,
            the_largest_number_of_transactions = blockchain.new_block,
            the_least_number_of_transactions = blockchain.new_block,
        )
        node.blockchains.add(blockchain)
        return node
    
    def _get_previous_element_by_id(self, id):
        queryset = self.filter(id__gte=id, id__lte=id)
        previous_id = id
        while len(queryset) == 1:
            if previous_id == 1:
                previous_id = None
                break

            previous_id -= 1
            queryset = self.filter(id__gte=previous_id, id__lte=id)

        return previous_id

    def _set_time_end(self, time, id):
        previous_id = self._get_previous_element_by_id(id)
        if previous_id == self.first().id:
            node = self.get(id=previous_id)
        else:
            node = self.get(id=self._get_previous_element_by_id(previous_id))
        node.time_end = time
        node.save()
        while self._get_reverse_relationship(node, 'node_right') is not None:
            node = self._get_reverse_relationship(node, 'node_right')
            node.time_end = time
            node.save()
    
    def _update_data_blockchain(self, blockchain, node):
            node.price += blockchain.new_block['price']
            node.the_most_expensive_block = max(
                node.the_most_expensive_block, 
                blockchain.new_block,
                key=lambda x:x['price']
            )
            node.the_cheapest_block = min(
                node.the_cheapest_block, 
                blockchain.new_block,
                key=lambda x:x['price']
            )
            node.the_largest_number_of_transactions = max(
                node.the_largest_number_of_transactions, 
                blockchain.new_block,
                key=lambda x:x['tx_number']
            )
            node.the_least_number_of_transactions = min(
                node.the_least_number_of_transactions, 
                blockchain.new_block,
                key=lambda x:x['tx_number']
            )
            node.save()
            node.blockchains.add(blockchain)

    def _update_blockchain(self, blockchain, node):
        if self._get_reverse_relationship(node, 'node_right') is None:
            self._update_data_blockchain(blockchain, node)
            return
        else:
            self._update_data_blockchain(blockchain, node)
            return self._update_blockchain(blockchain, node.node_right)

    def _add_node(self, blockchain, root):
        node = self._create_single_node(blockchain)

        parent = self._get_reverse_relationship(root, 'node_right')
        if parent:
            parent.right = None
            parent.save()

        new_root = self.create(
            time_start=root.time_start,
            left=root,
            right=node,
            price=root.price + node.price,
            the_most_expensive_block=max(
                root.the_most_expensive_block, 
                node.the_most_expensive_block, 
                key=lambda x:x['price']
            ),
            the_cheapest_block=min(
                root.the_cheapest_block, 
                node.the_cheapest_block, 
                key=lambda x:x['price']
            ),
            the_largest_number_of_transactions=max(
                root.the_largest_number_of_transactions, 
                node.the_largest_number_of_transactions, 
                key=lambda x:x['tx_number']
            ),
            the_least_number_of_transactions=min(
                root.the_least_number_of_transactions, 
                node.the_least_number_of_transactions, 
                key=lambda x:x['tx_number']
            )
        )

        new_root.blockchains.set(root.blockchains.all())
        new_root.blockchains.add(blockchain)

        if parent:
            parent.right = new_root
            parent.save()
            self._update_blockchain(blockchain, parent)
        
        self._set_time_end(blockchain.time_start, node.id)
        return node

    def _update_tree(self, blockchain, root):
        if root.left is None and root.right is None or root.left.blockchains.count() == root.right.blockchains.count():
            return self._add_node(blockchain, root)
        else:
            return self._update_tree(blockchain, root.right)
    
    def create_node(self, blockchain):
        root = self._get_root()
        if root is None:
            node = self._create_single_node(blockchain)
        else:
            node = self._update_tree(blockchain, root)
        return node
    
    def search_segment(self, time_start, time_end):
        price = 0
        the_most_expensive_block, the_cheapest_block = {'price': 0}, {'price': 210000000000000}
        the_largest_number_of_transactions, the_least_number_of_transactions = {'tx_number': 0}, {'tx_number': 100000}

        visited = set()
        node = self._get_root()
        visited.add(node)
        while not (time_start == node.time_start and node.time_end is not None and node.time_end <= time_end ): 
            left = node.left
            right = node.right
            if left is None and right is None:
                break
        
            if (right.time_start <= time_start and right.time_end is None) or right.time_start <= time_start <= right.time_end:
                visited.add(right)
                node = right
            else:
                if right.time_end is not None and right.time_end <= time_end:
                    price+=right.price
                    the_most_expensive_block=max(
                        the_most_expensive_block, 
                        right.the_most_expensive_block, 
                        key=lambda x:x['price']
                    )
                    the_cheapest_block=min(
                        the_cheapest_block, 
                        right.the_cheapest_block, 
                        key=lambda x:x['price']
                    )
                    the_largest_number_of_transactions=max(
                        the_largest_number_of_transactions, 
                        right.the_largest_number_of_transactions, 
                        key=lambda x:x['tx_number']
                    )
                    the_least_number_of_transactions=min(
                        the_least_number_of_transactions, 
                        right.the_least_number_of_transactions, 
                        key=lambda x:x['tx_number']
                    )
                visited.add(left)
                node = left
        price += node.price
    
        start_blockchain_model = node.blockchains.get(time_start=node.time_start)
        start_blockchain_dict = start_blockchain_model.__dict__
        start_blockchain_dict.pop('_state')
        start_blockchain = start_blockchain_dict

        the_most_expensive_block=max(
            the_most_expensive_block, 
            node.the_most_expensive_block, 
            key=lambda x:x['price']
        )
        the_cheapest_block=min(
            the_cheapest_block, 
            node.the_cheapest_block, 
            key=lambda x:x['price']
        )
        the_largest_number_of_transactions=max(
            the_largest_number_of_transactions, 
            node.the_largest_number_of_transactions, 
            key=lambda x:x['tx_number']
        )
        the_least_number_of_transactions=min(
            the_least_number_of_transactions, 
            node.the_least_number_of_transactions, 
            key=lambda x:x['tx_number']
        )

        node = self._get_root()
        while time_end != node.time_end:
            left = node.left
            right = node.right
            if right is None:
                break
            if time_end > left.time_end or (time_end == left.time_end and time_start == time_end):
                if left not in visited and left.time_start >= time_start:
                    price += left.price
                    the_most_expensive_block=max(
                        the_most_expensive_block, 
                        left.the_most_expensive_block, 
                        key=lambda x:x['price']
                    )
                    the_cheapest_block=min(
                        the_cheapest_block, 
                        left.the_cheapest_block, 
                        key=lambda x:x['price']
                    )
                    the_largest_number_of_transactions=max(
                        the_largest_number_of_transactions, 
                        left.the_largest_number_of_transactions, 
                        key=lambda x:x['tx_number']
                    )
                    the_least_number_of_transactions=min(
                        the_least_number_of_transactions, 
                        left.the_most_expensive_block, 
                        key=lambda x:x['tx_number']
                    )
                node = right
            else:
                node = left
    
        end_blockchain_model = node.blockchains.get(time_start=node.blockchains.aggregate(Max('time_start'))['time_start__max'])
        end_blockchain_dict = end_blockchain_model.__dict__
        end_blockchain_dict.pop('_state')
        end_blockchain = end_blockchain_dict

        if node not in visited:
            price += node.price
            the_most_expensive_block=max(
                the_most_expensive_block, 
                node.the_most_expensive_block, 
                key=lambda x:x['price']
            )
            the_cheapest_block=min(
                the_cheapest_block, 
                node.the_cheapest_block, 
                key=lambda x:x['price']
            )
            the_largest_number_of_transactions=max(
                the_largest_number_of_transactions, 
                node.the_largest_number_of_transactions, 
                key=lambda x:x['tx_number']
            )
            the_least_number_of_transactions=min(
                the_least_number_of_transactions, 
                node.the_most_expensive_block, 
                key=lambda x:x['tx_number']
            )
        return {
                    "start_blockchain": start_blockchain,
                    "price": price,
                    "the_most_expensive_block": the_most_expensive_block,
                    "the_cheapest_block": the_cheapest_block,
                    "the_largest_number_of_transactions": the_largest_number_of_transactions,
                    "the_least_number_of_transactions": the_least_number_of_transactions,
                    "end_blockchain": end_blockchain
                }


class SegmentNode(models.Model):
    '''Model of segment node'''

    objects = NodeManager()
    time_start = models.IntegerField()
    time_end = models.IntegerField(null=True)

    price = models.IntegerField()
    the_most_expensive_block = models.JSONField()
    the_cheapest_block = models.JSONField()
    the_largest_number_of_transactions = models.JSONField() 
    the_least_number_of_transactions = models.JSONField()

    blockchains = models.ManyToManyField('Blockchain')

    left = models.OneToOneField('self', null=True, related_name="node_left", on_delete=models.SET_NULL)
    right = models.OneToOneField('self', null=True, related_name="node_right", on_delete=models.SET_NULL)