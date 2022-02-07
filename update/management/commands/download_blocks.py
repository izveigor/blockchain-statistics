from django.core.management.base import BaseCommand, CommandError
from update.api import BlockData, GetLatestBlockHeight
from status.models import Block


class Command(BaseCommand):
    help = 'Download blocks, range of number from 1 to 10.'

    def add_arguments(self, parser):
        parser.add_argument('number_of_blocks', type=int)

    def handle(self, *args, **options):
        number_of_blocks = options['number_of_blocks']
        if number_of_blocks > 10 or number_of_blocks < 1:
            raise CommandError('Range of number of blocks must be from 1 to 10, not %d' % number_of_blocks)
        else:
            if Block.objects.exists():
                latest_block_height = Block.objects.last().height
                latest_block_height -= 1
            else:
                latest_block_height = GetLatestBlockHeight()

            latest_block_height = latest_block_height + 1 - number_of_blocks

            if latest_block_height < 1:
                raise CommandError('Block height must be greater than 0')

            self.stdout.write("Waiting time: %d" % (number_of_blocks * 10))

            while number_of_blocks > 0:
                BlockData(latest_block_height)
                latest_block_height += 1
                number_of_blocks -= 1
                if number_of_blocks > 0:
                    self.stdout.write("%d blocks remain" % number_of_blocks if number_of_blocks != 1 else "1 block remains")
            
            self.stdout.write("Complete download %d blocks" % options['number_of_blocks'])
