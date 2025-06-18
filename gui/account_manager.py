import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
import logging
from gui.utils import create_section, add_button

class AccountManager:
    """Manages account selection and adding accounts."""
    def __init__(self, root, row, log_console):
        self.root = root
        self.log_console = log_console
        self.logger = logging.getLogger(__name__)
        self.accounts = self.load_accounts()
        self.selected_account = tk.StringVar()
        self.create_widgets(row)

    def load_accounts(self):
        """Load accounts from data/accounts.json."""
        accounts_file = os.path.join(os.path.dirname(__file__), '../data/accounts.json')
        try:
            if os.path.exists(accounts_file):
                with open(accounts_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            self.logger.error(f"Error loading accounts: {str(e)}")
            return []

    def save_accounts(self):
        """Save accounts to data/accounts.json."""
        accounts_file = os.path.join(os.path.dirname(__file__), '../data/accounts.json')
        try:
            with open(accounts_file, 'w') as f:
                json.dump(self.accounts, f, indent=2)
            self.logger.info("Accounts saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving accounts: {str(e)}")

    def create_widgets(self, row):
        """Create account selection widgets."""
        self.account_frame = create_section(self.root, "Accounts", row)
        tk.Label(self.account_frame, text="Select Account:", bg="#2c2c2c", fg="white").pack(side="left", padx=5)
        account_emails = [acc['email'] for acc in self.accounts] or ["No accounts added"]
        self.account_dropdown = ttk.Combobox(self.account_frame, textvariable=self.selected_account, values=account_emails, width=30)
        self.account_dropdown.pack(side="left", padx=5)
        self.account_dropdown.set(account_emails[0])
        add_button(self.account_frame, "Add Account", self.add_account_form)

    def add_account_form(self):
        """Open a form to add accounts."""
        form = tk.Toplevel(self.root)
        form.title("Add Craigslist Account")
        form.geometry("400x300")
        form.configure(bg="#2c2c2c")

        tk.Label(form, text="Email:", bg="#2c2c2c", fg="white").pack(pady=(20, 5))
        email_entry = tk.Entry(form, width=40)
        email_entry.pack(pady=(0, 10))

        tk.Label(form, text="Password:", bg="#2c2c2c", fg="white").pack(pady=(10, 5))
        password_entry = tk.Entry(form, show="*", width=40)
        password_entry.pack(pady=(0, 20))

        def save_account():
            email = email_entry.get().strip()
            password = password_entry.get().strip()
            if not email or not password:
                messagebox.showwarning("Incomplete", "Both fields are required!")
                return
            if any(acc['email'] == email for acc in self.accounts):
                messagebox.showerror("Error", "Email already exists")
                return
            self.accounts.append({"email": email, "password": password})
            self.save_accounts()
            self.account_dropdown['values'] = [acc['email'] for acc in self.accounts]
            self.account_dropdown.set(email)
            self.log_console.insert(f"[✓] Added account: {email}\n")
            form.destroy()

        tk.Button(form, text="Save", command=save_account, bg="#00aa00", fg="white").pack(pady=15)