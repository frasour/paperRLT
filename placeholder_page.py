import tkinter as tk
from tkinter import ttk


class PlaceholderPage(ttk.Frame):
    """Simple placeholder page with centered text."""

    def __init__(self, parent: ttk.Frame, message: str) -> None:
        super().__init__(parent, relief=tk.RIDGE, padding=20, style="Content.TFrame")
        self.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        label = ttk.Label(self, text=message, anchor="center", font=("Arial", 16), style="Content.TLabel")
        label.grid(row=0, column=0, sticky="nsew")
