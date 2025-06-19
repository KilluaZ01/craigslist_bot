import tkinter as tk
from tkinter import messagebox
from gui.account_manager import AccountManager
from gui.ad_config import AdConfig
from gui.log_console import LogConsole
from core.bot_engine import CraigslistBot
from core.ad_rewriter import AdRewriter
import logging

class CraigslistBotGUI:
    """Main GUI class to orchestrate components."""
    def __init__(self, root):
        self.root = root
        self.root.title("Craigslist Automation Bot")
        self.root.geometry("1000x700")
        self.root.configure(bg="#1e1e1e")
        self.bot = CraigslistBot(headless=False)
        self.rewriter = AdRewriter()
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.log_console = LogConsole(self.root, row=3)
        self.account_manager = AccountManager(self.root, row=0, log_console=self.log_console)
        self.ad_config = AdConfig(self.root, row=1, log_console=self.log_console, rewriter=self.rewriter)

        # SECTION: Control Buttons
        self.control_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.control_frame.pack(pady=10)
        tk.Button(self.control_frame, text="Rewrite Ad", command=self.rewrite_ad, bg="#444", fg="white", width=15).pack(side="left", padx=10)
        tk.Button(self.control_frame, text="Post Ad", command=self.post_ad, bg="#00aa00", fg="white", width=15).pack(side="left", padx=10)
        tk.Button(self.control_frame, text="Login As", command=self.login, bg="#007acc", fg="white", width=15).pack(side="left", padx=10)

    def get_account_credentials(self, selected_email):
        try:
            import os, json
            accounts_file = os.path.join(os.path.dirname(__file__), '../data/accounts.json')
            with open(accounts_file, 'r') as f:
                accounts = json.load(f)
            for acc in accounts:
                if acc["email"].lower() == selected_email.lower():
                    return acc["password"], acc.get("app_password")
        except Exception as e:
            self.logger.error(f"[ERROR] Could not load account credentials: {str(e)}")
        return None, None

        # Perform login on initialization

    def login(self):
        """Perform login using selected account."""
        selected_account = self.account_manager.selected_account.get()
        if selected_account == "No accounts added":
            self.log_console.insert("[ERROR] No account selected for login\n")
            messagebox.showerror("Error", "Please add an account first")
            return False

        # Get password
        password, _ = self.get_account_credentials(selected_account)
        if not password:
            self.log_console.insert(f"[ERROR] No credentials found for {selected_account}\n")
            messagebox.showerror("Error", f"No password found for {selected_account}")
            return False

        self.log_console.insert(f"[INFO] Logging in as {selected_account}...\n")
        success = self.bot.login(email=selected_account, password=password)
        if success:
            self.log_console.insert(f"[✓] Successfully logged in as {selected_account}\n")
            return True
        else:
            self.log_console.insert(f"[ERROR] Failed to log in as {selected_account}\n")
            messagebox.showerror("Error", f"Failed to log in as {selected_account}")
            return False

    
    def rewrite_ad(self):
        """Rewrite ad using Gemini API."""
        title = self.ad_config.title_entry.get()
        description = self.ad_config.description_text.get("1.0", tk.END).strip()
        
        # Check if we have content to rewrite
        if not title.strip() and not description.strip():
            self.log_console.insert("[ERROR] No title or description to rewrite\n")
            return
        
        # Show original content in console
        self.log_console.insert(f"[INFO] Original Title: {title}\n")
        self.log_console.insert(f"[INFO] Original Description: {description}\n")
        self.log_console.insert("[INFO] Rewriting ad content...\n")
        
        # Check if API key is configured
        if not self.rewriter.api_key:
            self.log_console.insert("[ERROR] No Gemini API key configured\n")
            return
        
        try:
            # Call the rewrite_ad method on the AdRewriter instance
            new_title, new_description = self.rewriter.rewrite_ad(title, description)
            
            # Check if content was actually rewritten
            if new_title == title and new_description == description:
                self.log_console.insert("[WARNING] Content was not rewritten - API may have failed\n")
                self.log_console.insert("[INFO] Check your API key and internet connection\n")
            else:
                self.log_console.insert("[SUCCESS] Content successfully rewritten!\n")
            
            # Show rewritten content in console
            self.log_console.insert(f"[SUCCESS] New Title: {new_title}\n")
            self.log_console.insert(f"[SUCCESS] New Description: {new_description}\n")
            
            # Update the GUI fields
            self.ad_config.title_entry.delete(0, tk.END)
            self.ad_config.title_entry.insert(0, new_title)
            self.ad_config.description_text.delete("1.0", tk.END)
            self.ad_config.description_text.insert(tk.END, new_description)
            
            self.log_console.insert("[INFO] Ad content updated in GUI\n")
        
        except Exception as e:
            self.log_console.insert(f"[ERROR] Exception during rewrite: {str(e)}\n")
            
        self.log_console.insert("=" * 50 + "\n")  # Add separator line for clarity

    def post_ad(self):
        selected_account = self.account_manager.selected_account.get()

        if selected_account == "No accounts added":
            self.log_console.insert("[ERROR] No account selected for posting\n")
            messagebox.showerror("Error", "Please add an account first")
            return

        # Make sure we're logged into the right account
        if not self.login():
            return

        # Include images in ad_details
        ad_details = {
            "make": self.ad_config.ad_details["make"].get(),
            "model": self.ad_config.ad_details["model"].get(),
            "size": self.ad_config.ad_details["size"].get(),
            "dimensions": self.ad_config.ad_details["dimensions"].get(),
            "condition": self.ad_config.ad_details["condition"].get(),
            "language": self.ad_config.ad_details["language"].get(),
            "checkboxes": [k for k, v in self.ad_config.ad_details["checkboxes"].items() if v.get()],
            "images": self.ad_config.image_paths  # Add image paths
        }

        self.log_console.insert(f"[INFO] Attempting to post ad: {self.ad_config.title_entry.get()}\n")
        success = self.bot.post_ad(
            selected_account,
            title=self.ad_config.title_entry.get(),
            description=self.ad_config.description_text.get("1.0", tk.END).strip(),
            category="fso",
            sub_category="96",
            postal_code=self.ad_config.postal_entry.get(),
            price=self.ad_config.price_entry.get(),
            location=self.ad_config.location_entry.get(),
            ad_details=ad_details
        )

        if success:
            self.log_console.insert(f"[✓] Ad posted successfully with account: {selected_account}\n")
        else:
            self.log_console.insert("[ERROR] Failed to post ad\n")
            messagebox.showerror("Error", "Failed to post ad")

    def __del__(self):
        self.bot.quit()