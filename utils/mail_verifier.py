import imaplib
import email
import re
import time
import os
import json

def get_verification_link(email_address, wait_seconds=10, retries=12):
    print(f"[*] Checking Gmail for Craigslist verification email for {email_address}...")

    # Load accounts.json
    try:
        accounts_path = os.path.join(os.path.dirname(__file__), '../data/accounts.json')
        with open(accounts_path, 'r') as f:
            accounts = json.load(f)
    except Exception as e:
        print(f"[!] Failed to load accounts.json: {e}")
        return None

    # Find matching account
    account = next((acc for acc in accounts if acc["email"].lower() == email_address.lower()), None)
    if not account:
        print(f"[!] No matching account found for {email_address}")
        return None

    GMAIL_EMAIL = account["email"]
    GMAIL_PASSWORD = account["app_password"]

    for attempt in range(1, retries + 1):
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(GMAIL_EMAIL, GMAIL_PASSWORD)
            mail.select("inbox")

            result, data = mail.search(None, '(FROM "craigslist.org")')
            email_ids = data[0].split()
            if not email_ids:
                print(f"[*] Attempt {attempt}: No email found. Retrying in {wait_seconds} seconds...")
                mail.logout()
                time.sleep(wait_seconds)
                continue

            latest_email_id = email_ids[-1]
            result, msg_data = mail.fetch(latest_email_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")

            subject = msg.get("Subject", "(No Subject)")
            print(f"[*] Attempt {attempt}: Email subject: {subject}")
            print(f"[*] Email body snippet: {body[:200].replace(chr(10), ' ')}")

            # ✅ FIXED REGEX (no double escape)
            match = re.search(r'https://accounts\.craigslist\.org/login/onetime\?[^ \n\r]+', body)
            if match:
                mail.logout()
                print("[+] Verification link found!")
                return match.group(0)

            mail.logout()

        except Exception as e:
            print(f"[!] Error on attempt {attempt}: {e}")

        time.sleep(wait_seconds)

    print("[!] No verification link found after all retries.")
    return None
