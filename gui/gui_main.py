import tkinter as tk
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

    def rewrite_ad(self):
        """Rewrite ad using Gemini API."""
        title = self.ad_config.title_entry.get()
        description = self.ad_config.description_text.get("1.0", tk.END).strip()
        new_title, new_description = self.rewriter.rewrite_ad(title, description)
        self.ad_config.title_entry.delete(0, tk.END)
        self.ad_config.title_entry.insert(0, new_title)
        self.ad_config.description_text.delete("1.0", tk.END)
        self.ad_config.description_text.insert(tk.END, new_description)
        self.log_console.insert(f"[INFO] Ad content updated with rewritten text\n")

    def post_ad(self):
        """Post ad using selected account."""
        if self.account_manager.selected_account.get() == "No accounts added":
            self.log_console.insert("[ERROR] No account selected for posting\n")
            tk.messagebox.showerror("Error", "Please add an account first")
            return
        ad_details = {
            "make": self.ad_config.ad_details["make"].get(),
            "model": self.ad_config.ad_details["model"].get(),
            "size": self.ad_config.ad_details["size"].get(),
            "dimensions": self.ad_config.ad_details["dimensions"].get(),
            "condition": self.ad_config.ad_details["condition"].get(),
            "language": self.ad_config.ad_details["language"].get(),
            "checkboxes": [k for k, v in self.ad_config.ad_details["checkboxes"].items() if v.get()]
        }
        success = self.bot.post_ad(
            title=self.ad_config.title_entry.get(),
            description=self.ad_config.description_text.get("1.0", tk.END).strip(),
            account_email=self.account_manager.selected_account.get(),
            category="fso",
            sub_category="96",
            postal_code=self.ad_config.postal_entry.get(),
            price=self.ad_config.price_entry.get(),
            location=self.ad_config.location_entry.get(),
            ad_details=ad_details
        )
        if success:
            self.log_console.insert(f"[✓] Ad posted successfully with account: {self.account_manager.selected_account.get()}\n")
        else:
            self.log_console.insert("[ERROR] Failed to post ad\n")

    def __del__(self):
        self.bot.quit()