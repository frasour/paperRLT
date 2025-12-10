import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk


class LibraryPage(ttk.Frame):
    """Document library view with add/delete and notes editing."""

    def __init__(self, parent: ttk.Frame, data_file: Path, palette_provider) -> None:
        super().__init__(parent, padding=12, style="Content.TFrame")
        self.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)

        self._data_file = data_file
        self._palette_provider = palette_provider

        self._library_data: list[dict[str, str]] = []
        self._selected_title = tk.StringVar(value="")
        self._library_title_var = tk.StringVar(value="")
        self._controls: dict[str, tk.Widget | ttk.Widget] = {}

        self._build_layout()
        self._load_library_data()
        self.refresh_list()
        self.apply_theme()

    # Layout
    def _build_layout(self) -> None:
        left = ttk.Frame(self, padding=(0, 0, 8, 0), style="Content.TFrame")
        left.grid(row=0, column=0, sticky="nsew")
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)

        controls = ttk.Frame(left, padding=(0, 0, 0, 6), style="Content.TFrame")
        controls.grid(row=0, column=0, sticky="ew")
        controls.columnconfigure(1, weight=1)

        add_btn = ttk.Button(controls, text="添加", command=self.add_document, style="Nav.TButton")
        add_btn.grid(row=0, column=0, padx=(0, 6))

        title_entry = ttk.Entry(controls, textvariable=self._library_title_var)
        title_entry.grid(row=0, column=1, sticky="ew")

        del_btn = ttk.Button(controls, text="删除", command=self.delete_document, style="Nav.TButton")
        del_btn.grid(row=0, column=2, padx=(6, 0))

        list_container = ttk.Frame(left, style="Content.TFrame")
        list_container.grid(row=1, column=0, sticky="nsew")
        list_container.columnconfigure(0, weight=1)
        list_container.rowconfigure(0, weight=1)

        listbox = tk.Listbox(
            list_container,
            exportselection=False,
            activestyle="dotbox",
            highlightthickness=1,
            selectmode=tk.SINGLE,
        )
        listbox.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        listbox.configure(yscrollcommand=scrollbar.set)
        listbox.bind("<<ListboxSelect>>", self._on_document_select)

        right = ttk.Frame(self, padding=(8, 0, 0, 0), style="Content.TFrame")
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        title_label = ttk.Label(
            right,
            textvariable=self._selected_title,
            font=("Arial", 14, "bold"),
            style="Content.TLabel",
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 6))

        notes_text = tk.Text(
            right,
            wrap="word",
            height=10,
            highlightthickness=1,
        )
        notes_text.grid(row=1, column=0, sticky="nsew")

        actions = ttk.Frame(right, padding=(0, 8, 0, 0), style="Content.TFrame")
        actions.grid(row=2, column=0, sticky="e")

        clear_btn = ttk.Button(actions, text="清空", command=lambda: self.clear_notes(notes_text), style="Nav.TButton")
        clear_btn.grid(row=0, column=0, padx=(0, 6))

        save_btn = ttk.Button(actions, text="保存", command=lambda: self.save_notes(notes_text), style="Nav.TButton")
        save_btn.grid(row=0, column=1)

        self._controls = {
            "listbox": listbox,
            "notes_text": notes_text,
            "title_entry": title_entry,
        }

    # Data handling
    def _load_library_data(self) -> None:
        if self._data_file.exists():
            try:
                self._library_data = json.loads(self._data_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self._library_data = []

    def _persist_library_data(self) -> None:
        self._data_file.write_text(
            json.dumps(self._library_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def refresh_list(self) -> None:
        listbox = self._controls.get("listbox")
        if not isinstance(listbox, tk.Listbox):
            return
        listbox.delete(0, tk.END)
        for doc in self._library_data:
            listbox.insert(tk.END, doc.get("title", ""))

    # Actions
    def add_document(self) -> None:
        title = self._library_title_var.get().strip()
        if not title:
            return

        for doc in self._library_data:
            if doc.get("title") == title:
                self._select_document_by_title(title)
                return

        self._library_data.append({"title": title, "notes": ""})
        self._persist_library_data()
        self._library_title_var.set("")
        self.refresh_list()
        self._select_document_by_title(title)

    def delete_document(self) -> None:
        listbox = self._controls.get("listbox")
        if not isinstance(listbox, tk.Listbox):
            return
        selection = listbox.curselection()
        if not selection:
            return
        index = selection[0]
        del self._library_data[index]
        self._persist_library_data()
        self.refresh_list()
        self._selected_title.set("")
        notes_text = self._controls.get("notes_text")
        if isinstance(notes_text, tk.Text):
            notes_text.delete("1.0", tk.END)

    def save_notes(self, widget: tk.Text) -> None:
        listbox = self._controls.get("listbox")
        if not isinstance(listbox, tk.Listbox):
            return
        selection = listbox.curselection()
        if not selection:
            return
        index = selection[0]
        self._library_data[index]["notes"] = widget.get("1.0", tk.END).rstrip()
        self._persist_library_data()

    def clear_notes(self, widget: tk.Text) -> None:
        widget.delete("1.0", tk.END)

    # Selection handling
    def _on_document_select(self, event: tk.Event) -> None:
        widget = event.widget
        if not isinstance(widget, tk.Listbox):
            return
        selection = widget.curselection()
        if not selection:
            return
        index = selection[0]
        doc = self._library_data[index]
        self._selected_title.set(doc.get("title", ""))
        notes_text = self._controls.get("notes_text")
        if isinstance(notes_text, tk.Text):
            notes_text.delete("1.0", tk.END)
            notes_text.insert("1.0", doc.get("notes", ""))

    def _select_document_by_title(self, title: str) -> None:
        listbox = self._controls.get("listbox")
        if not isinstance(listbox, tk.Listbox):
            return
        for index, doc in enumerate(self._library_data):
            if doc.get("title") == title:
                listbox.selection_clear(0, tk.END)
                listbox.selection_set(index)
                listbox.see(index)
                self._selected_title.set(title)
                listbox.event_generate("<<ListboxSelect>>")
                break

    # Theming
    def apply_theme(self) -> None:
        palette = self._palette_provider()
        listbox = self._controls.get("listbox")
        if isinstance(listbox, tk.Listbox):
            listbox.configure(
                bg=palette["surface"],
                fg=palette["foreground"],
                selectbackground=palette["accent"],
                selectforeground=palette["surface"],
                highlightbackground=palette["border"],
                highlightcolor=palette["border"],
            )

        notes_text = self._controls.get("notes_text")
        if isinstance(notes_text, tk.Text):
            notes_text.configure(
                bg=palette["surface"],
                fg=palette["foreground"],
                insertbackground=palette["accent"],
                highlightbackground=palette["border"],
                highlightcolor=palette["border"],
            )
