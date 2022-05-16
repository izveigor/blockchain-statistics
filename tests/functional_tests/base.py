from selenium import webdriver
from channels.testing import ChannelsLiveServerTestCase
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement


firefox_options = Options()
firefox_options.headless = True


class FunctionalTest(ChannelsLiveServerTestCase):  # type: ignore
    serve_static = True

    @classmethod
    def setUpClass(self) -> None:
        super().setUpClass()
        try:
            self.browser = webdriver.Firefox(options=firefox_options)
        except:
            super().tearDownClass()
            raise

    def _get_element_by_id(self, id: str) -> WebElement:
        element = WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.ID, id))
        )
        return element

    def _get_element_by_class(self, class_: str) -> WebElement:
        element = WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_))
        )
        return element

    @classmethod
    def tearDownClass(self) -> None:
        self.browser.quit()
        super().tearDownClass()
