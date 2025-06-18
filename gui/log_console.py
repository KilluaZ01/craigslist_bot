import tkinter as tk
from tkinter import scrolledtext
import logging
from gui.utils import create_section

class LogConsole:
    """Manages the log console for GUI output."""
    def __init__(self, root, row):
        self.root = root
        self.log_frame = create_section(self.root, "Log Console", row)
        self.log_console = scrolledtext.ScrolledText(self.log_frame, height=12, bg="black", fg="lime", font=("Courier", 10))
        self.log_console.pack(fill="both", expand=True)
        self.setup_logging()

    def setup_logging(self):
        """Redirect logging to log console."""
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget

            def emit(self, record):
                msg = self.format(record)
                self.text_widget.configure(state='normal')
                self.text_widget.insert(tk.END, msg + '\n')
                self.text_widget.configure(state='disabled')
                self.text_widget.yview(tk.END)

        handler = TextHandler(self.log_console)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(handler)

    def insert(self, message):
        """Insert a message into the log console."""
        self.log_console.configure(state='normal')
        self.log_console.insert(tk.END, message)
        self.log_console.configure(state='disabled')
        self.log_console.yview(tk.END)