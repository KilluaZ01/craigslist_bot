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
        self.image_paths = []  # Store selected image paths
        self.create_widgets(row)

    def create_widgets(self, row):
        """Create ad configuration widgets."""
        self.ad_frame = create_section(self.root, "Ad Configuration", row)
        add_button(self.ad_frame, "Load Ad Template", self.load_template)
        add_button(self.ad_frame, "Select Images", self.select_images)  # New button for image selection

        # Ad details
        tk.Label(self.ad_frame, text="Title:", bg="#2c2c2c", fg="white").pack(anchor="w", padx=5)
        self.title_entry = ttk.Entry(self.ad_frame, width=50)
        self.title_entry.pack(fill="x", padx=5, pady=2)
        self.title_entry.insert(0, "None")

        tk.Label(self.ad_frame, text="Description:", bg="#2c2c2c", fg="white").pack(anchor="w", padx=5)
        self.description_text = scrolledtext.ScrolledText(self.ad_frame, width=50, height=5, bg="#333", fg="white")
        self.description_text.pack(fill="x", padx=5, pady=2)
        self.description_text.insert(tk.END, "None")

        # Image display
        tk.Label(self.ad_frame, text="Images:", bg="#2c2c2c", fg="white").pack(anchor="w", padx=5)
        self.image_label = tk.Label(self.ad_frame, text="No images selected", bg="#2c2c2c", fg="white")
        self.image_label.pack(anchor="w", padx=5, pady=2)

        # Additional fields in a grid
        fields_frame = tk.Frame(self.ad_frame, bg="#2c2c2c")
        fields_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(fields_frame, text="Postal Code:", bg="#2c2c2c", fg="white").grid(row=0, column=0, sticky="w", padx=5)
        self.postal_entry = ttk.Entry(fields_frame, width=10)
        self.postal_entry.grid(row=0, column=1, sticky="w", padx=5)
        self.postal_entry.insert(0, "-")

        tk.Label(fields_frame, text="Price:", bg="#2c2c2c", fg="white").grid(row=0, column=2, sticky="w", padx=5)
        self.price_entry = ttk.Entry(fields_frame, width=10)
        self.price_entry.grid(row=0, column=3, sticky="w", padx=5)
        self.price_entry.insert(0, "0")

        tk.Label(fields_frame, text="Location:", bg="#2c2c2c", fg="white").grid(row=1, column=0, sticky="w", padx=5)
        self.location_entry = ttk.Entry(fields_frame, width=20)
        self.location_entry.grid(row=1, column=1, sticky="w", padx=5)
        self.location_entry.insert(0, "None")

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
        self.ad_details["make"].insert(0, "None")

        tk.Label(fields_frame, text="Model:", bg="#2c2c2c", fg="white").grid(row=2, column=2, sticky="w", padx=5)
        self.ad_details["model"].grid(row=2, column=3, sticky="w", padx=5)
        self.ad_details["model"].insert(0, "None")

        tk.Label(fields_frame, text="Size:", bg="#2c2c2c", fg="white").grid(row=3, column=0, sticky="w", padx=5)
        self.ad_details["size"].grid(row=3, column=1, sticky="w", padx=5)
        self.ad_details["size"].insert(0, "0 inch")

        tk.Label(fields_frame, text="Dimensions:", bg="#2c2c2c", fg="white").grid(row=3, column=2, sticky="w", padx=5)
        self.ad_details["dimensions"].grid(row=3, column=3, sticky="w", padx=5)
        self.ad_details["dimensions"].insert(0, "0")

        tk.Label(fields_frame, text="Condition:", bg="#2c2c2c", fg="white").grid(row=4, column=0, sticky="w", padx=5)
        self.ad_details["condition"].grid(row=4, column=1, sticky="w", padx=5)
        self.ad_details["condition"].set("0")

        tk.Label(fields_frame, text="Language:", bg="#2c2c2c", fg="white").grid(row=4, column=2, sticky="w", padx=5)
        self.ad_details["language"].grid(row=4, column=3, sticky="w", padx=5)
        self.ad_details["language"].insert(0, "English")

        tk.Checkbutton(fields_frame, text="Crypto OK", variable=self.ad_details["checkboxes"]["crypto_ok"], bg="#2c2c2c", fg="white", selectcolor="#333").grid(row=5, column=0, sticky="w", padx=5)
        tk.Checkbutton(fields_frame, text="Delivery", variable=self.ad_details["checkboxes"]["delivery"], bg="#2c2c2c", fg="white", selectcolor="#333").grid(row=5, column=1, sticky="w", padx=5)
        tk.Checkbutton(fields_frame, text="Show Ads", variable=self.ad_details["checkboxes"]["show_ads"], bg="#2c2c2c", fg="white", selectcolor="#333").grid(row=5, column=2, sticky="w", padx=5)

    def select_images(self):
        """Open file dialog to select image files."""
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")]
        )
        if files:
            self.image_paths = list(files)
            self.image_label.config(text=f"{len(self.image_paths)} images selected")
            self.log_console.insert(f"[INFO] Selected {len(self.image_paths)} images: {', '.join(self.image_paths)}\n")

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
                    "Language": "",
                    "Images": ""  # New field for image paths
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

                # Handle image paths
                if fields["Images"]:
                    self.image_paths = [p.strip() for p in fields["Images"].split(',') if p.strip()]
                    self.image_label.config(text=f"{len(self.image_paths)} images selected")
                else:
                    self.image_paths = []
                    self.image_label.config(text="No images selected")

                # Validate required fields
                missing = [key for key, value in fields.items() if not value and key != "Images"]
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
                if self.image_paths:
                    self.log_console.insert(f"[INFO] Loaded {len(self.image_paths)} images: {', '.join(self.image_paths)}\n")
            except Exception as e:
                self.log_console.insert(f"[ERROR] Failed to load template: {str(e)}\n")

    def get_ad_details(self):
        """Return ad details including images."""
        return {
            "title": self.title_entry.get(),
            "description": self.description_text.get("1.0", tk.END).strip(),
            "postal_code": self.postal_entry.get(),
            "price": self.price_entry.get(),
            "location": self.location_entry.get(),
            "make": self.ad_details["make"].get(),
            "model": self.ad_details["model"].get(),
            "size": self.ad_details["size"].get(),
            "dimensions": self.ad_details["dimensions"].get(),
            "condition": self.ad_details["condition"].get(),
            "language": self.ad_details["language"].get(),
            "checkboxes": {
                "crypto_ok": self.ad_details["checkboxes"]["crypto_ok"].get(),
                "delivery": self.ad_details["checkboxes"]["delivery"].get(),
                "show_ads": self.ad_details["checkboxes"]["show_ads"].get()
            },
            "images": self.image_paths  # Include image paths
        }