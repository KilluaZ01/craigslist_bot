import tkinter as tk
import logging
import os

from gui.gui_main import CraigslistBotGUI

if __name__ == "__main__":
    # Configure logging
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(
        filename=os.path.join(log_dir, 'bot.log'),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.info("Craigslist Automation Bot started")

    # Start GUI
    root = tk.Tk()
    app = CraigslistBotGUI(root)
    root.mainloop()