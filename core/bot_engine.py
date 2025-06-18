from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.timing import TimingUtils
# from utils.gmail_utils import get_verification_link
import json
import os
import logging
import time
from config import CHROMEDRIVER_PATH, USER_DATA_DIR, PROFILE_DIR, EMAIL, PASSWORD

class CraigslistBot:
    def __init__(self, headless=False):
        self.logger = logging.getLogger(__name__)
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
        options.add_argument(f"--profile-directory={PROFILE_DIR}")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(
            service=Service(CHROMEDRIVER_PATH or ChromeDriverManager().install()),
            options=options
        )
        self.timing = TimingUtils()
        self.base_url = "https://accounts.craigslist.org"

    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), '../config/settings.json')
        with open(config_path, 'r') as f:
            return json.load(f)

    def login(self, email=EMAIL, password=PASSWORD):
        """Login to Craigslist."""
        self.logger.info("Attempting to log in")
        self.driver.get(f"{self.base_url}/login/home")
        self.timing.random_delay(1, 3)

        if "Log in" in self.driver.title:
            self.logger.info("Logging in...")
            try:
                self.driver.find_element(By.ID, "inputEmailHandle").send_keys(email)
                self.driver.find_element(By.ID, "inputPassword").send_keys(password)
                self.driver.find_element(By.ID, "login").click()
                self.timing.random_delay(3, 5)

                if "verify" in self.driver.page_source.lower():
                    self.logger.info("Verification required...")
                    try:
                        WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(text(), 'CLICKHERE', 'clickhere'), 'click here')]"))
                        ).click()
                        self.timing.random_delay(3, 5)
                    except Exception as e:
                        self.logger.warning(f"Verification button not found: {str(e)}")

                    login_link = None
                    for _ in range(6):
                        login_link = get_verification_link()
                        if login_link:
                            break
                        self.timing.random_delay(8, 12)

                    if login_link:
                        self.driver.execute_script("window.open('');")
                        self.driver.switch_to.window(self.driver.window_handles[1])
                        self.driver.get(login_link)
                        self.timing.random_delay(3, 5)
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                    else:
                        self.logger.error("Manual verification required")
                        input("Press Enter after verifying manually...")
                else:
                    self.logger.info("Login successful")
            except Exception as e:
                self.logger.error(f"Login error: {str(e)}")
                return False
        else:
            self.logger.info("Already logged in")
        return True

    def post_ad(self, title, description, postal_code, price, location, category="fso", sub_category="96", ad_details=None):
        """Post an ad on Craigslist using provided data."""
        self.logger.info("Attempting to post ad")
        try:
            self.logger.info("Navigating to new post form")
            self.driver.get(f"{self.base_url}/login/home")
            new_post_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "make new post"))
            )
            new_post_link.click()
            self.timing.random_delay(1, 3)

            try:
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.NAME, "continue"))).click()
            except:
                pass

            try:
                self.driver.find_element(By.XPATH, f"//input[@type='radio' and @value='{category}']").click()
                self.timing.random_delay(1, 3)
            except:
                pass

            try:
                self.driver.find_element(By.XPATH, f"//input[@type='radio' and @value='{sub_category}']").click()
                self.driver.find_element(By.XPATH, "//button[@value='continue']").click()
                self.timing.random_delay(1, 3)
            except:
                pass

            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "PostingTitle")))
            self.driver.find_element(By.ID, "PostingTitle").send_keys(title)

            self.driver.find_element(By.ID, "postal_code").clear()
            self.driver.find_element(By.ID, "postal_code").send_keys(postal_code)

            self.driver.find_element(By.ID, "PostingBody").send_keys(description)
            
            self.driver.find_element(By.NAME, "price").clear()
            self.driver.find_element(By.NAME, "price").send_keys(price)

            try:
                self.driver.find_element(By.ID, "geographic_area").clear()
                self.driver.find_element(By.ID, "geographic_area").send_keys(location)
            except:
                self.logger.warning("Geographic area field not found, skipping")

            if ad_details:
                for field, value in ad_details.items():
                    if field != "checkboxes" and field != "condition":
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
            self.timing.random_delay(1, 3)

            try:
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "doneWithImages"))).click()
            except:
                self.logger.info("Image upload step skipped")
            self.timing.random_delay(1, 3)

            self.driver.find_element(By.NAME, "go").click()
            self.timing.random_delay(1, 3)

            self.logger.info("Sucessfully Ad Posted!")

            self.driver.get(f"{self.base_url}/login/home")
            return True

        except Exception as e:
            self.logger.error(f"Ad posting error: {str(e)}")
            self.logger.debug(f"Page source: {self.driver.page_source}")
            return False

    def quit(self):
        self.driver.quit()
        self.logger.info("Browser closed")