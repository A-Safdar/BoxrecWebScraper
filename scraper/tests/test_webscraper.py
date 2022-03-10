import unittest
from time import sleep
import json
import sys
import os
from selenium.webdriver.common.by import By
import selenium.common.exceptions as driver_exceptions

# Get current and parent directories to allow for imports
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from webscraper import WebDriver


class WebScraperTestCase(unittest.TestCase):
    def setUp(self):
        with open(f"{parent}/credentials.json", "r") as f:
            self.scraper_config = json.load(f)

        self.instance = WebDriver(
            url="https://boxrec.com", username=self.scraper_config["username"], password=self.scraper_config["password"]
        )

    def test_login(self):
        sleep(2)
        self.instance.load_login_page(By.LINK_TEXT, "login")
        self.instance.submit_login_credentials(
            username_field_by=By.ID,
            username_field_locator="username",
            password_field_by=By.ID,
            password_field_locator="password",
            submit_button_by=By.CLASS_NAME,
            submit_button_locator="submitButton",
        )
        expected_result = "https://boxrec.com/"
        actual_result = self.instance.driver.current_url
        self.assertEqual(expected_result, actual_result)

    def test_accept_cookies(self):
        sleep(2)
        self.instance.load_login_page(By.LINK_TEXT, "login")
        self.instance.submit_login_credentials(
            username_field_by=By.ID,
            username_field_locator="username",
            password_field_by=By.ID,
            password_field_locator="password",
            submit_button_by=By.CLASS_NAME,
            submit_button_locator="submitButton",
        )
        self.instance.accept_cookies(
            container_by=By.XPATH,
            container_locator_string='//div[@id="qc-cmp2-ui"]',
            button_by=By.XPATH,
            button_locator_string='//button[contains(@class, "css-1my9mvs")]',
        )

        self.assertRaises(
            driver_exceptions.NoSuchElementException,
            self.instance.driver.find_element,
            By.XPATH,
            '//div[@id="qc-cmp2-ui"]',
        )


unittest.main()
