from .base import FunctionalTest
from selenium.webdriver.common.by import By
from status.models import Block
from tests.helpers import create_blocks, get_random_block_data
from update.latest_block import LatestBlock
from unittest.mock import patch
from selenium.common.exceptions import TimeoutException
from blockchain.constants import NUMBER_OF_BLOCKS_ON_A_PAGE


class TestBlockLive(FunctionalTest):
    '''Functional test of block live update
    '''
    def _check_fields_block(self, blocks_model):
        block_live_update = self._get_element_by_id('body_block_live_update')
        for block_model, row in zip(blocks_model, block_live_update.find_elements(By.TAG_NAME, 'tr')):
            for model_field, html in zip(('height', 'hash'), row.find_elements(By.TAG_NAME, 'td')):
                self.assertEqual(
                    str(getattr(block_model, model_field)),
                    html.text
                )

    def _mock_latest_block_call(self):
        data_about_block = get_random_block_data()
        block = Block.objects.create(**data_about_block)
        self._send_message(block)
    
    def test_empty(self):
        self.browser.get(self.live_server_url)
        block_live_update = self._get_element_by_id('block_live_update')
        self.assertEqual(
            block_live_update.text,
            "Server has not yet had data"
        )

    def test_live_update(self):
        create_blocks(NUMBER_OF_BLOCKS_ON_A_PAGE)
        self.browser.get(self.live_server_url)

        self._check_fields_block(Block.objects.all())
    
    @patch('update.latest_block._NewLatestBlock.__call__', _mock_latest_block_call)
    def test_send_latest_block(self):
        self.browser.get(self.live_server_url)
        LatestBlock()
        self._check_fields_block(Block.objects.all())

        create_blocks(NUMBER_OF_BLOCKS_ON_A_PAGE)
        self.browser.get(self.live_server_url + "?page=2")
        self._check_fields_block(Block.objects.all()[NUMBER_OF_BLOCKS_ON_A_PAGE:])

        next_ = self._get_element_by_id('next')
        self.assertIsNotNone(
            next_.get_attribute('disabled')
        )

    @patch('update.latest_block._NewLatestBlock.__call__', _mock_latest_block_call)
    def test_messages_overflow(self):
        self.browser.get(self.live_server_url)

        for i in range(NUMBER_OF_BLOCKS_ON_A_PAGE+1):
            LatestBlock()
    
        self._check_fields_block(Block.objects.all()[:NUMBER_OF_BLOCKS_ON_A_PAGE])

        next_ = self._get_element_by_id('next')
        self.assertIsNone(
            next_.get_attribute('disabled')
        )
        next_.click()

        self._check_fields_block(Block.objects.all()[NUMBER_OF_BLOCKS_ON_A_PAGE:])

    def test_check_previous(self):
        create_blocks(NUMBER_OF_BLOCKS_ON_A_PAGE)
        self.browser.get(self.live_server_url)

        previous = self._get_element_by_id('previous')

        self.assertIsNotNone(
            previous.get_attribute('disabled')
        )
        create_blocks(1)
        self.browser.get(self.live_server_url + '?page=2')
        previous = self._get_element_by_id('previous')

        self.assertIsNone(
            previous.get_attribute('disabled')
        )

        previous.click()

        self.assertEqual(
            self.browser.current_url[-7:],
            '?page=1'
        )

        self._check_fields_block(Block.objects.all()[:NUMBER_OF_BLOCKS_ON_A_PAGE])
    
    def test_check_next(self):
        create_blocks(NUMBER_OF_BLOCKS_ON_A_PAGE)
        self.browser.get(self.live_server_url)

        next_ = self._get_element_by_id('next')

        self.assertIsNotNone(
            next_.get_attribute('disabled')
        )

        create_blocks(1)
        self.browser.refresh()
        next_ = self._get_element_by_id('next')

        self.assertIsNone(
            next_.get_attribute('disabled')
        )

        next_.click()

        self.assertEqual(
            self.browser.current_url[-7:],
            '?page=2'
        )
        self._check_fields_block(Block.objects.all()[NUMBER_OF_BLOCKS_ON_A_PAGE:])

    def test_page(self):
        create_blocks(1)
        self.browser.get(self.live_server_url)

        with self.assertRaises(TimeoutException):
            self._get_element_by_id('previous_page')
        
        with self.assertRaises(TimeoutException):
            self._get_element_by_id('next_page')
        
        self._get_element_by_id('actual_page')

        create_blocks(NUMBER_OF_BLOCKS_ON_A_PAGE*2-1)
        self.browser.refresh()
        next_page = self._get_element_by_id('next_page')
        next_page.click()

        self.assertEqual(
            self.browser.current_url[-7:],
            '?page=2'
        )

        self._check_fields_block(Block.objects.all()[NUMBER_OF_BLOCKS_ON_A_PAGE:])

        previous_page = self._get_element_by_id('previous_page')
        previous_page.click()

        self._check_fields_block(Block.objects.all()[:NUMBER_OF_BLOCKS_ON_A_PAGE])
