# 🛠 Craigslist Automation Bot

Craigslist Automation Bot is a desktop automation tool built with Python and Selenium that streamlines Craigslist ad posting. It features a GUI interface for managing multiple accounts, posting ads (with image support), rewriting content using Gemini API, and persistent session support using saved cookies.

---

## 🚀 Features

### ✅ Core Features
- GUI-based Craigslist account management
- Automated ad posting via Selenium
- Image uploading (classic uploader supported)
- Ad rewriting using Google Gemini API
- Persistent login sessions using cookies
- Live logging panel in the GUI

### 🧠 Advanced
- Multi-account rotation support
- Human-like timing behavior using randomized delays
- Gmail-based email verification handling

---

## 🛠 Installation & Setup

### 📦 Prerequisites
- Windows 10 or higher
- Chrome browser (latest)

### 📁 Setup Steps
1. **Download the release ZIP** from the Releases tab.
2. **Extract** the contents to a folder (e.g., `Desktop/CraigslistBot`).
3. **Run `bot.exe`** — no setup or terminal needed.
4. On first launch, the bot will create:
   - `data/` (for account and ad JSON)
   - `cookies/` (for saved sessions)
   - `logs/` (for log files in `%APPDATA%\CraigslistBot`)

---

## 🧭 How to Use

### ✨ Add Account
- Click **"Add Account"** in the GUI.
- Enter your Craigslist email, password, and Gmail app password.
- The app supports multiple accounts from `accounts.json`.

### ✏️ Create and Rewrite Ads
- Fill in ad details: title, price, postal code, images, etc.
- Use **"Rewrite Ad"** to enhance your content via Gemini.

### 📤 Post Ad
- Select your account and click **"Post Ad"**.
- The bot will:
  - Login (or reuse session)
  - Switch to the classic image uploader
  - Upload images
  - Submit the ad

---

## 📁 Project Structure

| File / Module      | Purpose |
|--------------------|---------|
| `bot.exe`          | Final executable for production use |
| `main.py`          | Entry point for development/testing |
| `config.py`        | Global settings and paths |
| `ad_config.py`     | GUI form for ad data |
| `bot_engine.py`    | Craigslist automation logic |
| `account_manager.py` | GUI for managing accounts |
| `ad_rewriter.py`   | Gemini-powered rewriting tool |
| `session.py`       | Cookie-based session reuse |
| `mail_verifier.py` | Handles Craigslist email verification |
| `timing.py`        | Adds human-like timing |
| `log_console.py`   | Real-time logs inside the GUI |
| `data/`            | Stores `accounts.json` and `ads.json` |
| `cookies/`         | Per-account cookie storage |
| `logs/`            | Log files saved inside `%APPDATA%/CraigslistBot/logs` |

---

## 🔐 Security Notice

⚠️ **Craigslist prohibits automated posting**. This tool includes human-like delays and session reuse to reduce detection risk, but **use it responsibly and at your own risk.**

---

## 📌 Notes

- The bot uses the **classic image uploader** to avoid issues with the modern UI.
- Gmail **App Password** is required if 2FA is enabled on your Gmail account.
- All sessions are stored in `cookies/` and reused automatically when possible.

---

## 📬 Support & Contact

For bugs or feature requests, please open an [issue](https://github.com/KilluaZ01/craigslist_bot/issues).  
If you’re a freelancer delivering this, remove this section before handoff.

---

## 🧪 Dev Notes (Optional Section)

> If sharing source code:
- Run using `python main.py`
- Dependencies in `requirements.txt`
- Install with `pip install -r requirements.txt`

---

## 📄 License

This project is privately developed for freelance use.  
Do not redistribute or publish without written permission.

---

"_The obstacle is the way._" — Marcus Aurelius
