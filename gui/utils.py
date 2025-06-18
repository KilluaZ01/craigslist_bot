import tkinter as tk

def create_section(root, title, row):
    """Create a labeled section frame."""
    frame = tk.LabelFrame(root, text=title, bg="#2c2c2c", fg="white", padx=10, pady=10)
    frame.pack(padx=20, pady=10, fill="x")
    return frame

def add_button(frame, label, command):
    """Add a styled button to a frame."""
    btn = tk.Button(frame, text=label, command=command, bg="#444", fg="white")
    btn.pack(side="left", padx=5, pady=5)