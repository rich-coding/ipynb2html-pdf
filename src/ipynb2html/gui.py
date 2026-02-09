import logging
import tkinter as tk
from pathlib import Path
from threading import Thread
from tkinter import filedialog, messagebox

from .converter import NotebookConverter

logger = logging.getLogger(__name__)


class NotebookConverterGUI:
    """Refactored GUI for ipynb2html."""

    def __init__(self, master=None):
        self.window = master or tk.Tk()
        self.window.title("ipynb2html-pdf Converter")
        self.window.geometry("520x340")
        self.window.resizable(False, False)
        self.file_path = None
        self.converter = NotebookConverter()
        self.setup_ui()

    def setup_ui(self):
        main_frame = tk.Frame(self.window, padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")

        # Header
        tk.Label(main_frame, text="Jupyter Notebook Converter", font=("Arial", 14, "bold")).pack(
            pady=(0, 15)
        )

        # File selection
        file_frame = tk.Frame(main_frame)
        file_frame.pack(fill="x", pady=5)

        self.file_label = tk.Label(
            file_frame, text="No file selected", wraplength=350, fg="gray", justify="left"
        )
        self.file_label.pack(side="left", expand=True, fill="x")

        tk.Button(file_frame, text="Browse...", command=self.select_file).pack(side="right")

        # Options
        opt_frame = tk.LabelFrame(main_frame, text="Options", padx=10, pady=10)
        opt_frame.pack(fill="x", pady=10)

        self.install_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            opt_frame, text="Auto-install missing dependencies", variable=self.install_var
        ).pack(anchor="w")

        fmt_frame = tk.Frame(opt_frame)
        fmt_frame.pack(fill="x", pady=(5, 0))
        tk.Label(fmt_frame, text="Output Format:").pack(side="left")

        self.format_var = tk.StringVar(value="html")
        tk.Radiobutton(fmt_frame, text="HTML", variable=self.format_var, value="html").pack(
            side="left", padx=10
        )
        tk.Radiobutton(fmt_frame, text="PDF", variable=self.format_var, value="pdf").pack(
            side="left"
        )

        # Action
        self.convert_button = tk.Button(
            main_frame,
            text="Convert Now",
            command=self.start_conversion,
            state="disabled",
            bg="#007bff",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
        )
        self.convert_button.pack(pady=10)

        # Status
        self.status_label = tk.Label(main_frame, text="", fg="blue", wraplength=480, height=2)
        self.status_label.pack(fill="x", pady=(5, 0))

    def log_status(self, message):
        self.status_label.config(text=message)
        self.window.update_idletasks()

    def select_file(self):
        path = filedialog.askopenfilename(
            title="Select Jupyter Notebook",
            initialdir=Path.home(),
            filetypes=[("Jupyter Notebook", "*.ipynb")],
        )
        if path:
            self.file_path = path
            # Show only the basename to prevent window expansion issues
            self.file_label.config(text=Path(path).name, fg="black")
            self.convert_button.config(state="normal")

    def start_conversion(self):
        self.convert_button.config(state="disabled")
        self.log_status("Starting conversion...")
        self.converter.install_missing = self.install_var.get()

        def run():
            try:
                final = self.converter.convert(self.file_path, output_format=self.format_var.get())
                self.log_status(f"Success! Output: {Path(final).name}")
                messagebox.showinfo("Success", f"File saved at:\n{final}")
            except Exception as e:
                logger.exception("Conversion failed")
                self.log_status(f"Error: {e}")
                messagebox.showerror("Error", str(e))
            finally:
                self.convert_button.config(state="normal")

        Thread(target=run, daemon=True).start()


def main():
    logging.basicConfig(level=logging.INFO)
    root = tk.Tk()
    NotebookConverterGUI(master=root)
    root.mainloop()


if __name__ == "__main__":
    main()
