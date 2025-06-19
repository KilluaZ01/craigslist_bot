from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from utils.timing import TimingUtils
from utils.mail_verifier import get_verification_link
from utils.session import SessionManager
import json
import os
import logging
import time
import re
from datetime import datetime, timedelta

class CraigslistBot:
    def __init__(self, headless=False):
        self.logger = logging.getLogger(__name__)
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.timing = TimingUtils()
        self.session_manager = SessionManager()
        self.base_url = "https://accounts.craigslist.org"
        self.ads_file = os.path.join(os.path.dirname(__file__), '../data/ads.json')
        os.makedirs(os.path.dirname(self.ads_file), exist_ok=True)

    def _is_logged_in(self):
        try:
            self.driver.get(f"{self.base_url}/login/home")
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.LINK_TEXT, "make new post"))
            )
            self.logger.info("[✓] Detected 'make new post' link — user is logged in.")
            return True
        except:
            self.logger.info("[!] 'make new post' link not found — user is not logged in.")
            return False
    
    def _get_logged_in_email(self):
        try:
            self.driver.get(f"{self.base_url}/login/home")
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "home of"))
            )
            link = self.driver.find_element(By.PARTIAL_LINK_TEXT, "home of")
            link_text = link.text.strip()
            email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
            email_match = re.search(email_pattern, link_text)
            if email_match:
                email = email_match.group(0)
                self.logger.info(f"Extracted email: {email}")
                return email
            else:
                self.logger.warning("[!] No email found in the link text.")
                return None
        except Exception as e:
            self.logger.warning(f"[!] Could not detect logged-in email: {e}")
            return None

    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), '../config/settings.json')
        with open(config_path, 'r') as f:
            return json.load(f)

    def _save_ad(self, email, title, description, postal_code, price, location, ad_details, category, sub_category):
        self.logger.info("[*] Attempting to save ad to ads.json")
        ad_data = {
            "email": email,
            "title": title,
            "description": description,
            "postal_code": postal_code,
            "price": price,
            "location": location,
            "ad_details": ad_details,
            "category": category,
            "sub_category": sub_category,
            "posted_at": datetime.now().isoformat(),
            "last_renewed_at": None
        }
        try:
            os.makedirs(os.path.dirname(self.ads_file), exist_ok=True)
            ads = []
            if os.path.exists(self.ads_file):
                with open(self.ads_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        try:
                            ads = json.loads(content)
                            if not isinstance(ads, list):
                                self.logger.warning("[!] ads.json is not a list, resetting to empty list")
                                ads = []
                        except json.JSONDecodeError as e:
                            self.logger.error(f"[!] Invalid JSON in ads.json: {e}. Content: '{content}'")
                            ads = []
                    else:
                        self.logger.info("[*] ads.json is empty, initializing empty list")
            else:
                self.logger.info("[*] ads.json does not exist, creating new file")
            ads.append(ad_data)
            with open(self.ads_file, 'w') as f:
                json.dump(ads, f, indent=2)
            self.logger.info(f"[✓] Saved ad details for '{title}' to {self.ads_file}")
        except Exception as e:
            self.logger.error(f"[!] Failed to save ad details: {e}")
            self.logger.debug(f"[DEBUG] Ad data attempted: {ad_data}")
            raise

    def login(self, email, password):
        if self.session_manager.load_cookies(self.driver, email):
            self.logger.info(f"[✓] Loaded session cookies for {email}")
            self.driver.refresh()
            if self._get_logged_in_email() == email:
                self.logger.info(f"[✓] Session valid. Logged in as {email}")
                return True
            else:
                self.logger.warning(f"[!] Session cookies invalid or expired for {email}")

        current_email = self._get_logged_in_email()
        self.logger.info(f"current email = {current_email}")

        if current_email:
            if current_email.lower() == email.lower():
                self.logger.info(f"[✓] Already logged in as {email}")
                return True
            else:
                self.logger.info(f"[!] Logged in as {current_email}, logging out to switch to {email}")
                self.logout()

        driver = self.driver
        wait = WebDriverWait(driver, 20)
        driver.get("https://accounts.craigslist.org/login")

        try:
            email_input = wait.until(EC.presence_of_element_located((By.ID, "inputEmailHandle")))
            email_input.clear()
            email_input.send_keys(email)
            driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
            time.sleep(3)

            password_inputs = driver.find_elements(By.ID, "inputPassword")
            if password_inputs:
                password_input = password_inputs[0]
                password_input.clear()
                password_input.send_keys(password)
                driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
                time.sleep(3)

            if "A link has been sent to your email" in driver.page_source or \
               "Make sure the email address above is correct." in driver.page_source:
                self.logger.info("[*] Email verification required...")
                verification_link = get_verification_link(email)
                if verification_link:
                    self.logger.info(f"[*] Visiting verification link: {verification_link}")
                    driver.get(verification_link)
                    time.sleep(5)
                    self.session_manager.save_cookies(driver, email)
                    return True
                else:
                    self.logger.warning("[!] Could not get verification link from email.")
                    return False

            new_email = self._get_logged_in_email()
            if new_email and new_email.lower() == email.lower():
                self.logger.info(f"[+] Login confirmed as {new_email}")
                self.session_manager.save_cookies(driver, email)
                return True
            else:
                self.logger.warning(f"[!] Login failed or wrong account active (got: {new_email})")
                return False
        except Exception as e:
            self.logger.error(f"[!] Login failed for {email}: {e}")
            return False

    def post_ad(self, selected_account, title, description, postal_code, price, location, ad_details, category="fso", sub_category="96"):
        self.logger.info(f"Attempting to post ad: {title}")
        self.driver.get(f"{self.base_url}/login/home")

        if not self._is_logged_in():
            self.logger.info("Not logged in. Attempting login.")
            if not self.login(email=selected_account, password=None):  # Password handled by caller
                self.logger.error("Login failed. Aborting post.")
                return False

        try:
            # Navigate to post page
            WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.LINK_TEXT, "make new post"))).click()
            self.timing.random_delay(1, 2)

            # Category selections
            try:
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.NAME, "continue"))).click()
            except: pass

            try:
                self.driver.find_element(By.XPATH, f"//input[@type='radio' and @value='{category}']").click()
                self.timing.random_delay(1, 1.5)
            except: pass

            try:
                self.driver.find_element(By.XPATH, f"//input[@type='radio' and @value='{sub_category}']").click()
                self.driver.find_element(By.XPATH, "//button[@value='continue']").click()
                self.timing.random_delay(1, 1.5)
            except: pass

            # Fill ad form
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
            except: self.logger.warning("Geographic area field not found")

            # Optional fields
            optional_fields = {
                "sale_manufacturer": ad_details.get("make"),
                "sale_model": ad_details.get("model"),
                "sale_size": ad_details.get("dimensions")
            }
            for field, value in optional_fields.items():
                try:
                    self.driver.find_element(By.NAME, field).send_keys(value)
                except: pass

            self.driver.find_element(By.XPATH, "//button[contains(text(), 'continue')]").click()
            self.timing.random_delay(1, 2)

            # ========== IMAGE UPLOAD SECTION ==========
            images = ad_details.get("images", [])
            if images:
                try:
                    # Switch to classic uploader
                    WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "classic"))).click()
                    self.logger.info("[✓] Switched to classic image uploader")
                    self.timing.random_delay(1, 2)

                    image_input = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "classic-file-input"))
                    )

                    for image_path in images:
                        absolute_path = os.path.abspath(image_path)
                        if os.path.exists(absolute_path):
                            try:
                                image_input.send_keys(absolute_path)
                                self.logger.info(f"[✓] Uploaded image: {absolute_path}")
                                WebDriverWait(self.driver, 30).until(
                                    EC.presence_of_element_located((By.CLASS_NAME, "thumb"))
                                )
                            except Exception as e:
                                self.logger.error(f"[!] Upload failed for {absolute_path}: {e}")
                        else:
                            self.logger.warning(f"[!] Image not found: {absolute_path}")

                except Exception as e:
                    self.logger.error(f"[!] Image upload error: {e}")
                    self.logger.debug(f"[DEBUG] Page source: {self.driver.page_source[:1000]}")

            else:
                self.logger.info("No images provided for upload")

            # Click "Done with Images"
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.ID, "doneWithImages"))
                ).click()
            except Exception as e:
                self.logger.warning(f"[!] Could not click 'Done With Images': {e}")

            self.timing.random_delay(1, 2)

            # Final post publish
            try:
                self.driver.find_element(By.NAME, "go").click()
                self.timing.random_delay(1, 2)
                self.logger.info("[✓] Ad successfully posted.")
            except Exception as e:
                self.logger.error(f"[!] Failed to finalize posting: {e}")
                return False

            # Save ad metadata
            try:
                self._save_ad(selected_account, title, description, postal_code, price, location, ad_details, category, sub_category)
            except Exception as e:
                self.logger.error(f"[!] Error saving ad: {e}")

            return True

        except Exception as e:
            self.logger.error(f"Ad posting error: {e}")
            self.logger.debug(f"Page source: {self.driver.page_source}")
            return False

    
    def renew_ads(self, email, password):
        self.logger.info(f"[*] Checking for ads to renew for {email}")
        if not self._is_logged_in():
            self.logger.info("Not logged in. Attempting login.")
            if not self.login(email=email, password=password):
                self.logger.error("Login failed. Aborting renewal.")
                return False

        try:
            if not os.path.exists(self.ads_file):
                self.logger.info(f"[!] No ads file found at {self.ads_file}, creating empty file")
                with open(self.ads_file, 'w') as f:
                    json.dump([], f)
                return True

            with open(self.ads_file, 'r') as f:
                content = f.read().strip()
                if content:
                    try:
                        ads = json.loads(content)
                        if not isinstance(ads, list):
                            self.logger.error("[!] ads.json is not a list, resetting to empty list")
                            ads = []
                    except json.JSONDecodeError as e:
                        self.logger.error(f"[!] Invalid JSON in ads.json: {e}. Content: '{content}'")
                        ads = []
                else:
                    self.logger.info("[*] ads.json is empty, initializing empty list")
                    ads = []

            ads_to_renew = []
            current_time = datetime.now()
            for ad in ads:
                if ad['email'].lower() != email.lower():
                    continue
                try:
                    posted_at = datetime.fromisoformat(ad['posted_at'])
                    last_renewed_at = datetime.fromisoformat(ad['last_renewed_at']) if ad['last_renewed_at'] else posted_at
                    if (current_time - last_renewed_at) >= timedelta(hours=48):
                        ads_to_renew.append(ad)
                except ValueError as e:
                    self.logger.warning(f"[!] Invalid timestamp in ad '{ad['title']}': {e}")
                    continue

            if not ads_to_renew:
                self.logger.info("[*] No ads eligible for renewal.")
                return True

            self.logger.info(f"[*] Found {len(ads_to_renew)} ads to renew")
            self.driver.get(f"{self.base_url}/login/home")
            for ad in ads_to_renew:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.LINK_TEXT, "active"))
                    ).click()

                    ad_elements = self.driver.find_elements(By.XPATH, f"//a[contains(text(), '{ad['title']}')]")
                    if not ad_elements:
                        self.logger.warning(f"[!] Ad '{ad['title']}' not found in active posts")
                        continue

                    ad_elements[0].click()
                    self.timing.random_delay(1, 3)

                    renew_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'renew')]"))
                    )
                    renew_button.click()
                    self.timing.random_delay(1, 3)

                    ad['last_renewed_at'] = datetime.now().isoformat()
                    self.logger.info(f"[✓] Renewed ad: {ad['title']}")

                    with open(self.ads_file, 'w') as f:
                        json.dump(ads, f, indent=2)

                    self.driver.get(f"{self.base_url}/login/home")
                except Exception as e:
                    self.logger.error(f"[!] Failed to renew ad '{ad['title']}': {e}")
                    continue

            self.logger.info("[✓] Ad renewal process completed")
            return True
        except Exception as e:
            self.logger.error(f"[!] Error during ad renewal: {e}")
            return False

    def logout(self):
        self.logger.info("[INFO] Attempting logout...")
        try:
            logout_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "log out"))
            )
            logout_link.click()
            self.logger.info("[✓] Successfully logged out.")
        except Exception as e:
            self.logger.warning(f"[!] Logout link not found or already logged out. ({e})")

    def quit(self):
        self.driver.quit()
        self.logger.info("Browser closed")