from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from utils.timing import TimingUtils
from utils.mail_verifier import get_verification_link
from utils.session import SessionManager
import json
import os
import logging
import time
import re
from config import CHROMEDRIVER_PATH, USER_DATA_DIR, PROFILE_DIR

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
            service=Service(CHROMEDRIVER_PATH or ChromeDriverManager().install()),
            options=options
        )
        self.timing = TimingUtils()
        self.session_manager = SessionManager()
        self.base_url = "https://accounts.craigslist.org"

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
        
            # Wait for the link containing "home of" to be present
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "home of"))
            )
            
            # Find the link element
            link = self.driver.find_element(By.PARTIAL_LINK_TEXT, "home of")
            link_text = link.text.strip()
            
            # Extract the email using regex
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

    def login(self, email, password):
        # Try loading cookies first
        if self.session_manager.load_cookies(self.driver, email):
            self.logger.info(f"[✓] Loaded session cookies for {email}")
            self.driver.refresh()
            if self._get_logged_in_email() == email:
                self.logger.info(f"[✓] Session valid. Logged in as {email}")
                return True
            else:
                self.logger.warning(f"[!] Session cookies invalid or expired for {email}")

        """Login as a specific account. Logs out first if another account is active."""
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

            # Handle email verification if needed
            if "A link has been sent to your email" in driver.page_source or \
            "Make sure the email address above is correct." in driver.page_source:
                self.logger.info("[*] Email verification required...")
                verification_link = get_verification_link(email)
                if verification_link:
                    self.logger.info(f"[*] Visiting verification link: {verification_link}")
                    driver.get(verification_link)
                    time.sleep(5)

                    # Save cookies after verification
                    self.session_manager.save_cookies(driver, email)
                    return True
                else:
                    self.logger.warning("[!] Could not get verification link from email.")
                    return False

            # Final login check
            new_email = self._get_logged_in_email()
            if new_email and new_email.lower() == email.lower():
                self.logger.info(f"[+] Login confirmed as {new_email}")

                # ✅ Save cookies after successful login
                self.session_manager.save_cookies(driver, email)
                return True
            else:
                self.logger.warning(f"[!] Login failed or wrong account active (got: {new_email})")
                return False

        except Exception as e:
            self.logger.error(f"[!] Login failed for {email}: {e}")
            return False


    def post_ad(self, selected_account, title, description, postal_code, price, location, ad_details, category="fso", sub_category="96"):
        self.logger.info("Attempting to post ad")
        self.driver.get(f"{self.base_url}/login/home")

        if not self._is_logged_in():
            self.logger.info("Not logged in. Attempting login.")
            if not self.login(email=selected_account):
                self.logger.error("Login failed. Aborting post.")
                return False
        else:
            self.logger.info("Already logged in. Proceeding to post.")

        try:
            new_post_link = WebDriverWait(self.driver, 30).until(
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

            try:
                self.driver.find_element(By.NAME, "sale_manufacturer").send_keys(ad_details.get("make"))
            except:
                pass
            
            try:
                self.driver.find_element(By.NAME, "sale_model").send_keys(ad_details.get("model"))
            except:
                pass
            
            try:
                self.driver.find_element(By.NAME, "sale_size").send_keys(ad_details.get("dimensions"))
            except:
                pass

            self.driver.find_element(By.XPATH, "//button[contains(text(), 'continue')]").click()
            self.timing.random_delay(1, 3)

            # Image upload
            try:
                images = ad_details.get("images", [])
                if images:
                    self.logger.info(f"Uploading {len(images)} images")
                    image_input = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "plupload"))
                    )
                    for image_path in images:
                        if os.path.exists(image_path):
                            image_input.send_keys(image_path)
                            self.logger.info(f"Uploaded image: {image_path}")
                            self.timing.random_delay(1, 2)  # Wait for upload to process
                        else:
                            self.logger.warning(f"Image not found: {image_path}")
                    # Wait for all uploads to complete
                    WebDriverWait(self.driver, 30).until(
                        EC.element_to_be_clickable((By.ID, "doneWithImages"))
                    )
                else:
                    self.logger.info("No images to upload")
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "doneWithImages"))
                ).click()
            except Exception as e:
                self.logger.warning(f"Image upload failed: {str(e)}")
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "doneWithImages"))
                    ).click()
                except:
                    self.logger.info("Image upload step skipped")

            self.timing.random_delay(1, 3)
            self.driver.find_element(By.NAME, "go").click()
            self.timing.random_delay(1, 3)
            self.logger.info("Successfully Ad Posted!")

            self.driver.get(f"{self.base_url}/login/home")
            return True

        except Exception as e:
            self.logger.error(f"Ad posting error: {str(e)}")
            self.logger.debug(f"Page source: {self.driver.page_source}")
            return False
    
    def logout(self):
        """Logs out of current Craigslist session if logged in."""
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