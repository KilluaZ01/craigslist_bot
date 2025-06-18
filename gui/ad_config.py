import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
from gui.utils import create_section, add_button

class AdConfig:
    """Manages ad configuration and template loading."""
    def __init__(self, root, row, log_console, rewriter):
        self.root = root
        self.log_console = log_console
        self.rewriter = rewriter
        self.ad_details = {}
        self.create_widgets(row)

    def create_widgets(self, row):
        """Create ad configuration widgets."""
        self.ad_frame = create_section(self.root, "Ad Configuration", row)
        add_button(self.ad_frame, "Load Ad Template", self.load_template)

        # Ad details
        tk.Label(self.ad_frame, text="Title:", bg="#2c2c2c", fg="white").pack(anchor="w", padx=5)
        self.title_entry = ttk.Entry(self.ad_frame, width=50)
        self.title_entry.pack(fill="x", padx=5, pady=2)
        self.title_entry.insert(0, "(NEW AD)Samsung Galaxy Tab S6 Lite - Excellent Condition")

        tk.Label(self.ad_frame, text="Description:", bg="#2c2c2c", fg="white").pack(anchor="w", padx=5)
        self.description_text = scrolledtext.ScrolledText(self.ad_frame, width=50, height=5, bg="#333", fg="white")
        self.description_text.pack(fill="x", padx=5, pady=2)
        self.description_text.insert(tk.END, "This is a gently used Samsung Galaxy Tab S6 Lite tablet with stylus and case.\n\nPerfect for students or professionals.\nBattery is still great, no scratches, and fully functional.")

        # Additional fields in a grid
        fields_frame = tk.Frame(self.ad_frame, bg="#2c2c2c")
        fields_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(fields_frame, text="Postal Code:", bg="#2c2c2c", fg="white").grid(row=0, column=0, sticky="w", padx=5)
        self.postal_entry = ttk.Entry(fields_frame, width=10)
        self.postal_entry.grid(row=0, column=1, sticky="w", padx=5)
        self.postal_entry.insert(0, "94103")

        tk.Label(fields_frame, text="Price:", bg="#2c2c2c", fg="white").grid(row=0, column=2, sticky="w", padx=5)
        self.price_entry = ttk.Entry(fields_frame, width=10)
        self.price_entry.grid(row=0, column=3, sticky="w", padx=5)
        self.price_entry.insert(0, "180")

        tk.Label(fields_frame, text="Location:", bg="#2c2c2c", fg="white").grid(row=1, column=0, sticky="w", padx=5)
        self.location_entry = ttk.Entry(fields_frame, width=20)
        self.location_entry.grid(row=1, column=1, sticky="w", padx=5)
        self.location_entry.insert(0, "Kathmandu")

        self.ad_details = {
            "make": ttk.Entry(fields_frame, width=20),
            "model": ttk.Entry(fields_frame, width=20),
            "size": ttk.Entry(fields_frame, width=20),
            "dimensions": ttk.Entry(fields_frame, width=20),
            "condition": ttk.Combobox(fields_frame, values=["", "10", "20", "30", "40", "50", "60"], width=10),
            "language": ttk.Entry(fields_frame, width=20),
            "checkboxes": {
                "crypto_ok": tk.BooleanVar(),
                "delivery": tk.BooleanVar(),
                "show_ads": tk.BooleanVar()
            }
        }

        tk.Label(fields_frame, text="Make:", bg="#2c2c2c", fg="white").grid(row=2, column=0, sticky="w", padx=5)
        self.ad_details["make"].grid(row=2, column=1, sticky="w", padx=5)
        self.ad_details["make"].insert(0, "Samsung")

        tk.Label(fields_frame, text="Model:", bg="#2c2c2c", fg="white").grid(row=2, column=2, sticky="w", padx=5)
        self.ad_details["model"].grid(row=2, column=3, sticky="w", padx=5)
        self.ad_details["model"].insert(0, "Galaxy Tab S6 Lite")

        tk.Label(fields_frame, text="Size:", bg="#2c2c2c", fg="white").grid(row=3, column=0, sticky="w", padx=5)
        self.ad_details["size"].grid(row=3, column=1, sticky="w", padx=5)
        self.ad_details["size"].insert(0, "10.4 inch")

        tk.Label(fields_frame, text="Dimensions:", bg="#2c2c2c", fg="white").grid(row=3, column=2, sticky="w", padx=5)
        self.ad_details["dimensions"].grid(row=3, column=3, sticky="w", padx=5)
        self.ad_details["dimensions"].insert(0, "24 x 15 x 0.7 cm")

        tk.Label(fields_frame, text="Condition:", bg="#2c2c2c", fg="white").grid(row=4, column=0, sticky="w", padx=5)
        self.ad_details["condition"].grid(row=4, column=1, sticky="w", padx=5)
        self.ad_details["condition"].set("10")

        tk.Label(fields_frame, text="Language:", bg="#2c2c2c", fg="white").grid(row=4, column=2, sticky="w", padx=5)
        self.ad_details["language"].grid(row=4, column=3, sticky="w", padx=5)
        self.ad_details["language"].insert(0, "English")

        tk.Checkbutton(fields_frame, text="Crypto OK", variable=self.ad_details["checkboxes"]["crypto_ok"], bg="#2c2c2c", fg="white", selectcolor="#333").grid(row=5, column=0, sticky="w", padx=5)
        tk.Checkbutton(fields_frame, text="Delivery", variable=self.ad_details["checkboxes"]["delivery"], bg="#2c2c2c", fg="white", selectcolor="#333").grid(row=5, column=1, sticky="w", padx=5)
        tk.Checkbutton(fields_frame, text="Show Ads", variable=self.ad_details["checkboxes"]["show_ads"], bg="#2c2c2c", fg="white", selectcolor="#333").grid(row=5, column=2, sticky="w", padx=5)

    def load_template(self):
        """Load ad template from file and populate all fields."""
        path = filedialog.askopenfilename(title="Select Ad Template", filetypes=[("Text files", "*.txt")])
        if path:
            try:
                with open(path, 'r') as f:
                    content = f.read()
                # Parse template (format: Key: Value\n)
                fields = {
                    "Title": "",
                    "Description": "",
                    "Postal Code": "",
                    "Location": "",
                    "Make": "",
                    "Size": "",
                    "Condition": "",
                    "Price": "",
                    "Model": "",
                    "Dimensions": "",
                    "Language": ""
                }
                lines = content.split('\n')
                current_key = None
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    if ': ' in line:
                        key, value = line.split(': ', 1)
                        if key in fields:
                            current_key = key
                            fields[key] = value.strip()
                    elif current_key == "Description":
                        # Append to Description for multi-line content
                        fields["Description"] += '\n' + line.strip()
                fields["Description"] = fields["Description"].strip()

                # Validate required fields
                missing = [key for key, value in fields.items() if not value]
                if missing:
                    self.log_console.insert(f"[ERROR] Missing fields in template: {', '.join(missing)}\n")
                    return

                # Populate GUI fields
                self.title_entry.delete(0, tk.END)
                self.title_entry.insert(0, fields["Title"])
                self.description_text.delete("1.0", tk.END)
                self.description_text.insert(tk.END, fields["Description"])
                self.postal_entry.delete(0, tk.END)
                self.postal_entry.insert(0, fields["Postal Code"])
                self.location_entry.delete(0, tk.END)
                self.location_entry.insert(0, fields["Location"])
                self.price_entry.delete(0, tk.END)
                self.price_entry.insert(0, fields["Price"])
                self.ad_details["make"].delete(0, tk.END)
                self.ad_details["make"].insert(0, fields["Make"])
                self.ad_details["size"].delete(0, tk.END)
                self.ad_details["size"].insert(0, fields["Size"])
                self.ad_details["condition"].set(fields["Condition"])
                self.ad_details["model"].delete(0, tk.END)
                self.ad_details["model"].insert(0, fields["Model"])
                self.ad_details["dimensions"].delete(0, tk.END)
                self.ad_details["dimensions"].insert(0, fields["Dimensions"])
                self.ad_details["language"].delete(0, tk.END)
                self.ad_details["language"].insert(0, fields["Language"])

                self.log_console.insert(f"[INFO] Loaded template: {path}\n")
            except Exception as e:
                self.log_console.insert(f"[ERROR] Failed to load template: {str(e)}\n")