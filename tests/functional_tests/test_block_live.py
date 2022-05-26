from .base import FunctionalTest
from selenium.webdriver.common.by import By
from status.models import Block
from tests.helpers import (
    create_blocks,
    get_random_block_data,
    JsonData,
)
from selenium.common.exceptions import TimeoutException
from blockchain.constants import NUMBER_OF_BLOCKS_ON_A_PAGE, ATTRIBUTES_OF_BLOCK
from blockchain.send import send_data
from typing import Any
import time


class TestBlockLive(FunctionalTest):
    """Functional test of block live update"""

    def _check_fields_block(self, blocks_model: Any) -> None:
        block_live_update = self._get_element_by_id("body_block_live_update")
        for block_model, row in zip(
            blocks_model, block_live_update.find_elements(By.TAG_NAME, "tr")
        ):
            for model_field, html in zip(
                ATTRIBUTES_OF_BLOCK, row.find_elements(By.TAG_NAME, "td")
            ):
                self.assertEqual(str(getattr(block_model, model_field)), html.text)

    def test_empty(self) -> None:
        self.browser.get(self.live_server_url)
        block_live_update = self._get_element_by_id("block_live_update")
        self.assertEqual(block_live_update.text, "Server has not yet had data")

    def test_live_update(self) -> None:
        create_blocks(NUMBER_OF_BLOCKS_ON_A_PAGE)
        self.browser.get(self.live_server_url)

        self._check_fields_block(Block.objects.all())

    def test_send_latest_block(self) -> None:
        self.browser.get(self.live_server_url)
        block = get_random_block_data()
        Block.objects.create(**block)
        send_data(block, JsonData.first_blockchain)
        self._check_fields_block(Block.objects.all())

        create_blocks(NUMBER_OF_BLOCKS_ON_A_PAGE)
        self.browser.get(self.live_server_url + "?page=2")
        self._check_fields_block(Block.objects.all()[NUMBER_OF_BLOCKS_ON_A_PAGE:])

        next_ = self._get_element_by_id("next")
        self.assertIsNotNone(next_.get_attribute("disabled"))

    def test_messages_overflow(self) -> None:
        self.browser.get(self.live_server_url)

        for i in range(NUMBER_OF_BLOCKS_ON_A_PAGE + 1):
            block = get_random_block_data()
            Block.objects.create(**block)
            time.sleep(1)
            send_data(block, JsonData.first_blockchain)

        self._check_fields_block(Block.objects.all()[:NUMBER_OF_BLOCKS_ON_A_PAGE])

        next_ = self._get_element_by_id("next")
        self.assertIsNone(next_.get_attribute("disabled"))
        next_.click()

        self._check_fields_block(Block.objects.all()[NUMBER_OF_BLOCKS_ON_A_PAGE:])

    def test_check_previous(self) -> None:
        create_blocks(NUMBER_OF_BLOCKS_ON_A_PAGE)
        self.browser.get(self.live_server_url)

        previous = self._get_element_by_id("previous")

        self.assertIsNotNone(previous.get_attribute("disabled"))
        create_blocks(1)
        self.browser.get(self.live_server_url + "?page=2")
        previous = self._get_element_by_id("previous")

        self.assertIsNone(previous.get_attribute("disabled"))

        previous.click()

        self.assertEqual(self.browser.current_url[-7:], "?page=1")

        self._check_fields_block(Block.objects.all()[:NUMBER_OF_BLOCKS_ON_A_PAGE])

    def test_check_next(self) -> None:
        create_blocks(NUMBER_OF_BLOCKS_ON_A_PAGE)
        self.browser.get(self.live_server_url)

        next_ = self._get_element_by_id("next")

        self.assertIsNotNone(next_.get_attribute("disabled"))

        create_blocks(1)
        self.browser.refresh()
        next_ = self._get_element_by_id("next")

        self.assertIsNone(next_.get_attribute("disabled"))

        next_.click()

        self.assertEqual(self.browser.current_url[-7:], "?page=2")
        self._check_fields_block(Block.objects.all()[NUMBER_OF_BLOCKS_ON_A_PAGE:])

    def test_page(self) -> None:
        create_blocks(1)
        self.browser.get(self.live_server_url)

        with self.assertRaises(TimeoutException):
            self._get_element_by_id("previous_page")

        with self.assertRaises(TimeoutException):
            self._get_element_by_id("next_page")

        self._get_element_by_id("actual_page")

        create_blocks(NUMBER_OF_BLOCKS_ON_A_PAGE * 2 - 1)
        self.browser.refresh()
        next_page = self._get_element_by_id("next_page")
        next_page.click()

        self.assertEqual(self.browser.current_url[-7:], "?page=2")

        self._check_fields_block(Block.objects.all()[NUMBER_OF_BLOCKS_ON_A_PAGE:])

        previous_page = self._get_element_by_id("previous_page")
        previous_page.click()

        self._check_fields_block(Block.objects.all()[:NUMBER_OF_BLOCKS_ON_A_PAGE])
