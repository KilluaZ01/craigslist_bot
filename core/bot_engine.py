from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.timing import TimingUtils
import json
import os
import logging

class CraigslistBot:
    def __init__(self, headless=False):
        self.logger = logging.getLogger(__name__)
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.timing = TimingUtils()
        self.base_url = "https://accounts.craigslist.org"

    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), '../config/settings.json')
        with open(config_path, 'r') as f:
            return json.load(f)

    def post_ad(self, title, description, category="fso", sub_category="96", postal_code="94103", price="180", location="Kathmandu", ad_details=None):
        self.logger.info("Attempting to post ad")
        try:
            self.logger.info("Navigating to new post form")
            self.driver.get(f"{self.base_url}/login/home")
            new_post_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "make new post"))
            )
            new_post_link.click()
            self.timing.random_delay()

            self.driver.find_element(By.XPATH, f"//input[@type='radio' and @value='{category}']").click()
            self.timing.random_delay()

            self.driver.find_element(By.XPATH, f"//input[@type='radio' and @value='{sub_category}']").click()
            self.driver.find_element(By.XPATH, "//button[@value='continue']").click()
            self.timing.random_delay()

            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "PostingTitle")))
            self.driver.find_element(By.ID, "PostingTitle").send_keys(title)
            self.driver.find_element(By.ID, "postal_code").send_keys(postal_code)
            self.driver.find_element(By.ID, "PostingBody").send_keys(description)
            self.driver.find_element(By.NAME, "price").clear()
            self.driver.find_element(By.NAME, "price").send_keys(price)

            try:
                self.driver.find_element(By.ID, "geographic_area").send_keys(location)
            except:
                self.logger.warning("Geographic area field not found, skipping")

            if ad_details:
                for field, value in ad_details.items():
                    try:
                        self.driver.find_element(By.NAME, field).send_keys(value)
                    except:
                        self.logger.warning(f"Field {field} not found, skipping")

                if ad_details.get("condition"):
                    try:
                        condition_dropdown = self.driver.find_element(By.NAME, "condition")
                        condition_dropdown.find_element(By.XPATH, f"./option[@value='{ad_details['condition']}']").click()
                    except:
                        self.logger.warning("Condition dropdown not found, skipping")

                for checkbox_name in ad_details.get("checkboxes", []):
                    try:
                        checkbox = self.driver.find_element(By.NAME, checkbox_name)
                        if not checkbox.is_selected():
                            checkbox.click()
                    except:
                        self.logger.warning(f"Checkbox {checkbox_name} not found, skipping")

            self.driver.find_element(By.XPATH, "//button[contains(text(), 'continue')]").click()
            self.timing.random_delay()

            try:
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "doneWithImages"))).click()
            except:
                self.logger.info("Image upload step skipped")
            self.timing.random_delay()

            self.driver.find_element(By.NAME, "go").click()
            self.timing.random_delay()

            self.logger.info("Reached the publish page")
            return True
        except Exception as e:
            self.logger.error(f"Ad posting error: {str(e)}")
            self.logger.debug(f"Page source: {self.driver.page_source}")
            return False

    def quit(self):
        self.driver.quit()
        self.logger.info("Browser closed")