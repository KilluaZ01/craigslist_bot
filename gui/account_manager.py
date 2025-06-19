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
        add_button(self.account_frame, "Edit Account", self.edit_account_form)
        add_button(self.account_frame, "Delete Account", self.delete_account)
        

    def edit_account_form(self):
        """Open a form to edit selected account."""
        selected_email = self.selected_account.get()
        account = next((acc for acc in self.accounts if acc['email'] == selected_email), None)
        if not account:
            messagebox.showerror("Error", "No valid account selected to edit.")
            return

        form = tk.Toplevel(self.root)
        form.title("Edit Craigslist Account")
        form.geometry("400x300")
        form.configure(bg="#2c2c2c")

        tk.Label(form, text="Email:", bg="#2c2c2c", fg="white").pack(pady=(20, 5))
        email_entry = tk.Entry(form, width=40)
        email_entry.insert(0, account['email'])
        email_entry.pack(pady=(0, 10))

        tk.Label(form, text="Password:", bg="#2c2c2c", fg="white").pack(pady=(10, 5))
        password_entry = tk.Entry(form, show="*", width=40)
        password_entry.insert(0, account['password'])
        password_entry.pack(pady=(0, 20))

        def update_account():
            new_email = email_entry.get().strip()
            new_password = password_entry.get().strip()
            if not new_email or not new_password:
                messagebox.showwarning("Incomplete", "Both fields are required!")
                return
            # Check for email conflict if changed
            if new_email != account['email'] and any(acc['email'] == new_email for acc in self.accounts):
                messagebox.showerror("Error", "Another account with this email already exists.")
                return
            account['email'] = new_email
            account['password'] = new_password
            self.save_accounts()
            self.account_dropdown['values'] = [acc['email'] for acc in self.accounts]
            self.account_dropdown.set(new_email)
            self.log_console.insert(f"[✓] Updated account: {new_email}\n")
            form.destroy()

        tk.Button(form, text="Update", command=update_account, bg="#007acc", fg="white").pack(pady=15)

    def delete_account(self):
        """Delete the selected account."""
        selected_email = self.selected_account.get()
        if selected_email == "No accounts added":
            messagebox.showerror("Error", "No account selected to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete: {selected_email}?")
        if not confirm:
            return

        self.accounts = [acc for acc in self.accounts if acc['email'] != selected_email]
        self.save_accounts()

        # Update dropdown
        account_emails = [acc['email'] for acc in self.accounts] or ["No accounts added"]
        self.account_dropdown['values'] = account_emails
        self.account_dropdown.set(account_emails[0])
        self.log_console.insert(f"[✓] Deleted account: {selected_email}\n")


    def add_account_form(self):
        """Open a form to add accounts."""
        form = tk.Toplevel(self.root)
        form.title("Add Craigslist Account")
        form.geometry("400x300")
        form.configure(bg="#2c2c2c")

        tk.Label(form, text="Email (Craigslist Address/ Gmail Address):", bg="#2c2c2c", fg="white").pack(pady=(20, 5))
        email_entry = tk.Entry(form, width=40)
        email_entry.pack(pady=(0, 10))

        tk.Label(form, text="Password (Craigslist Password):", bg="#2c2c2c", fg="white").pack(pady=(10, 5))
        password_entry = tk.Entry(form, show="*", width=40)
        password_entry.pack(pady=(0, 20))

        tk.Label(form, text="App Password (For Gmail Verification): ", bg="#2c2c2c", fg="white").pack(pady=(10, 5))
        app_password_entry = tk.Entry(form, show="*", width=40)
        app_password_entry.pack(pady=(0, 20))

        def save_account():
            email = email_entry.get().strip()
            password = password_entry.get().strip()
            app_password = app_password_entry.get()
            if not email or not password:
                messagebox.showwarning("Incomplete", "Both fields are required!")
                return
            if any(acc['email'] == email for acc in self.accounts):
                messagebox.showerror("Error", "Email already exists")
                return
            self.accounts.append({"email": email, "password": password, "app_password": app_password})
            self.save_accounts()
            self.account_dropdown['values'] = [acc['email'] for acc in self.accounts]
            self.account_dropdown.set(email)
            self.log_console.insert(f"[✓] Added account: {email}\n")
            form.destroy()

        tk.Button(form, text="Save", command=save_account, bg="#00aa00", fg="white").pack(pady=15)