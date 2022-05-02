from io import StringIO
from django.core.management import call_command
from .base import UnitTest
from unittest.mock import patch, call
from tests.helpers import JsonData
from django.core.management.base import CommandError
from status.models import Block


class DownloadBlocksTest(UnitTest):
    '''Unit test command "download_blocks"'''
    @patch('update.management.commands.download_blocks.get_block_api')
    def test_with_one_created_block(self, mock_block_data):
        first_block_result = JsonData.first_block_result
        Block.objects.create(**first_block_result)

        out = StringIO()
        call_command('download_blocks', '1', stdout=out)

        mock_block_data.assert_called_with(first_block_result['height'] - 1)
        self.assertEqual(
            out.getvalue(),
            'Waiting time: 10\nComplete download 1 blocks\n'
        )

    @patch('update.management.commands.download_blocks.get_block_api')
    @patch('update.management.commands.download_blocks.get_latest_block_height')
    def test_command_output_without_blocks(self, mock_get_height, mock_block_data):
        height = 100000
        mock_get_height.return_value = height

        out = StringIO()
        call_command('download_blocks', '3', stdout=out)

        mock_block_data.assert_has_calls([
            call(99998), 
            call(99999),
            call(100000)
        ])

        self.assertEqual(
            out.getvalue(),
            'Waiting time: 30\n2 blocks remain\n1 block remains\nComplete download 3 blocks\n'
        )

    def test_errors(self):
        with self.assertRaisesRegex(CommandError, 'Range of number of blocks must be from 1 to 10, not 11'):
            call_command('download_blocks', '11')

        with self.assertRaisesRegex(CommandError, 'Range of number of blocks must be from 1 to 10, not 0'):
            call_command('download_blocks', '0')

        with self.assertRaisesRegex(CommandError, 'Range of number of blocks must be from 1 to 10, not -1'):
            call_command('download_blocks', '-1')
    
    @patch('update.management.commands.download_blocks.get_block_api')
    @patch('update.management.commands.download_blocks.get_latest_block_height')
    def test_height_min(self, mock_get_height, mock_block_data):
        mock_get_height.return_value = 3
        with self.assertRaisesRegex(CommandError, 'Block height must be greater than 0'):
            call_command('download_blocks', '4')
        
        out = StringIO()
        call_command('download_blocks', '3', stdout=out)

        mock_block_data.assert_has_calls([
            call(1), 
            call(2),
            call(3)
        ])
        

