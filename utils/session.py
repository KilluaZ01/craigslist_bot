import os
import json

class SessionManager:
    COOKIE_DIR = os.path.join(os.path.dirname(__file__), '../cookies')

    def __init__(self):
        os.makedirs(self.COOKIE_DIR, exist_ok=True)

    def get_cookie_file(self, email):
        filename = email.replace("@", "_at_").replace(".", "_dot_")
        return os.path.join(self.COOKIE_DIR, f"{filename}.json")

    def save_cookies(self, driver, email):
        cookies = driver.get_cookies()
        with open(self.get_cookie_file(email), "w") as f:
            json.dump(cookies, f)

    def load_cookies(self, driver, email):
        path = self.get_cookie_file(email)
        if not os.path.exists(path):
            return False
        with open(path, "r") as f:
            cookies = json.load(f)
        driver.get("https://accounts.craigslist.org")  # required before adding cookies
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except Exception:
                continue  # Ignore invalid cookies
        return True
