import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk


class RelationshipApp(tk.Tk):
    """Main application window for relationship visualization."""

    DEFAULT_BUTTON_WIDTH = 14
    MIN_BUTTON_WIDTH = 10

    def __init__(self) -> None:
        super().__init__()
        self.title("文献关系图谱")
        self.geometry("900x600")
        self.minsize(800, 500)

        self._data_file = Path("library_data.json")
        self._library_data: list[dict[str, str]] = []
        self._selected_title = tk.StringVar(value="")
        self._library_title_var = tk.StringVar(value="")

        # Configure overall grid: top navigation row and content row.
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._style = ttk.Style(self)
        self._style.theme_use("clam")

        self._current_theme = tk.StringVar(value="light")
        self._apply_theme()

        self._library_controls: dict[str, tk.Widget | ttk.Widget] = {}
        self._load_library_data()

        self._build_navigation()
        self._build_content_area()

    def _build_navigation(self) -> None:
        navigation_frame = ttk.Frame(self, padding=(10, 10, 10, 5), style="Nav.TFrame")
        navigation_frame.grid(row=0, column=0, sticky="w")

        buttons = [
            ("文献库", self._show_library),
            ("树状关系", self._show_tree_view),
            ("网状关系", self._show_graph_view),
            ("设置", self._show_settings),
            ("其它功能", self._show_placeholder),
        ]

        width_in_chars = max(self.DEFAULT_BUTTON_WIDTH, self.MIN_BUTTON_WIDTH)

        for index, (text, command) in enumerate(buttons):
            navigation_frame.columnconfigure(index, minsize=width_in_chars * 7)
            button = ttk.Button(
                navigation_frame,
                text=text,
                command=command,
                width=width_in_chars,
                style="Nav.TButton",
            )
            button.grid(row=0, column=index, padx=(0 if index == 0 else 6, 6), pady=2, sticky="w")

    def _build_content_area(self) -> None:
        content_frame = ttk.Frame(self, padding=10, style="App.TFrame")
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)

        self._content_stack = {
            "library": self._create_library(content_frame),
            "tree": self._create_placeholder(content_frame, "树状关系页面（待实现）"),
            "graph": self._create_placeholder(content_frame, "网状关系页面（待实现）"),
            "settings": self._create_settings(content_frame),
            "other": self._create_placeholder(content_frame, "更多功能可在此扩展"),
        }

        self._active_content = None
        self._switch_content("library")

    def _create_placeholder(self, parent: ttk.Frame, text: str) -> ttk.Frame:
        frame = ttk.Frame(parent, relief=tk.RIDGE, padding=20, style="Content.TFrame")
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        label = ttk.Label(frame, text=text, anchor="center", font=("Arial", 16), style="Content.TLabel")
        label.grid(row=0, column=0, sticky="nsew")
        return frame

    def _create_settings(self, parent: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(parent, padding=20, style="Content.TFrame")
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=2)

        header = ttk.Label(frame, text="设置", font=("Arial", 18, "bold"), style="Content.TLabel")
        header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        theme_label = ttk.Label(frame, text="主题切换：", style="Content.TLabel", font=("Arial", 12))
        theme_label.grid(row=1, column=0, sticky="w", pady=6)

        theme_toggle = ttk.Checkbutton(
            frame,
            text="暗色模式",
            variable=self._current_theme,
            onvalue="dark",
            offvalue="light",
            command=self._apply_theme,
            style="Toggle.TCheckbutton",
        )
        theme_toggle.grid(row=1, column=1, sticky="w", pady=6)
        return frame

    def _create_library(self, parent: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(parent, padding=12, style="Content.TFrame")
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=2)
        frame.columnconfigure(1, weight=3)
        frame.rowconfigure(0, weight=1)

        # Left column: controls and document list
        left = ttk.Frame(frame, padding=(0, 0, 8, 0), style="Content.TFrame")
        left.grid(row=0, column=0, sticky="nsew")
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)

        controls = ttk.Frame(left, padding=(0, 0, 0, 6), style="Content.TFrame")
        controls.grid(row=0, column=0, sticky="ew")
        controls.columnconfigure(1, weight=1)

        add_btn = ttk.Button(controls, text="添加", command=self._add_document, style="Nav.TButton")
        add_btn.grid(row=0, column=0, padx=(0, 6))

        title_entry = ttk.Entry(controls, textvariable=self._library_title_var)
        title_entry.grid(row=0, column=1, sticky="ew")

        del_btn = ttk.Button(controls, text="删除", command=self._delete_document, style="Nav.TButton")
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

        # Right column: notes editor
        right = ttk.Frame(frame, padding=(8, 0, 0, 0), style="Content.TFrame")
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

        clear_btn = ttk.Button(actions, text="清空", command=lambda: self._clear_notes(notes_text), style="Nav.TButton")
        clear_btn.grid(row=0, column=0, padx=(0, 6))

        save_btn = ttk.Button(actions, text="保存", command=lambda: self._save_notes(notes_text), style="Nav.TButton")
        save_btn.grid(row=0, column=1)

        self._library_controls = {
            "listbox": listbox,
            "notes_text": notes_text,
            "title_entry": title_entry,
        }

        self._refresh_library_list()
        self._apply_library_theme()
        return frame

    def _switch_content(self, key: str) -> None:
        if self._active_content:
            self._active_content.grid_remove()
        self._active_content = self._content_stack[key]
        self._active_content.grid()  # type: ignore[no-untyped-call]

    def _show_library(self) -> None:
        self._switch_content("library")

    def _show_tree_view(self) -> None:
        self._switch_content("tree")

    def _show_graph_view(self) -> None:
        self._switch_content("graph")

    def _show_settings(self) -> None:
        self._switch_content("settings")

    def _show_placeholder(self) -> None:
        self._switch_content("other")

    def _apply_theme(self) -> None:
        theme = self._current_theme.get()
        palette = {
            "light": {
                "background": "#f5f7fa",
                "surface": "#ffffff",
                "foreground": "#1f2933",
                "muted": "#52606d",
                "accent": "#2563eb",
                "border": "#d7dde5",
            },
            "dark": {
                "background": "#0f172a",
                "surface": "#1f2937",
                "foreground": "#e5e7eb",
                "muted": "#cbd5e1",
                "accent": "#60a5fa",
                "border": "#334155",
            },
        }[theme]

        self.configure(bg=palette["background"])

        self._style.configure(
            "Nav.TFrame",
            background=palette["background"],
            borderwidth=0,
        )
        self._style.configure(
            "App.TFrame",
            background=palette["background"],
        )
        self._style.configure(
            "Nav.TButton",
            background=palette["surface"],
            foreground=palette["foreground"],
            bordercolor=palette["border"],
            relief=tk.FLAT,
            padding=(12, 6),
        )
        self._style.map(
            "Nav.TButton",
            background=[("active", palette["accent"]), ("pressed", palette["accent"])],
            foreground=[("active", palette["surface"]), ("pressed", palette["surface"])],
        )

        self._style.configure(
            "Content.TFrame",
            background=palette["surface"],
            bordercolor=palette["border"],
            relief=tk.RIDGE,
        )
        self._style.configure(
            "Content.TLabel",
            background=palette["surface"],
            foreground=palette["foreground"],
        )
        self._style.configure(
            "Toggle.TCheckbutton",
            background=palette["surface"],
            foreground=palette["foreground"],
            indicatorcolor=palette["border"],
            padding=4,
        )

        self._apply_library_theme()

    def _apply_library_theme(self) -> None:
        if not self._library_controls:
            return

        theme = self._current_theme.get()
        palette = {
            "light": {
                "background": "#f5f7fa",
                "surface": "#ffffff",
                "foreground": "#1f2933",
                "accent": "#2563eb",
                "border": "#d7dde5",
            },
            "dark": {
                "background": "#0f172a",
                "surface": "#1f2937",
                "foreground": "#e5e7eb",
                "accent": "#60a5fa",
                "border": "#334155",
            },
        }[theme]

        listbox = self._library_controls.get("listbox")
        if isinstance(listbox, tk.Listbox):
            listbox.configure(
                bg=palette["surface"],
                fg=palette["foreground"],
                selectbackground=palette["accent"],
                selectforeground=palette["surface"],
                highlightbackground=palette["border"],
                highlightcolor=palette["border"],
            )

        notes_text = self._library_controls.get("notes_text")
        if isinstance(notes_text, tk.Text):
            notes_text.configure(
                bg=palette["surface"],
                fg=palette["foreground"],
                insertbackground=palette["accent"],
                highlightbackground=palette["border"],
                highlightcolor=palette["border"],
            )

    def _load_library_data(self) -> None:
        if self._data_file.exists():
            try:
                self._library_data = json.loads(self._data_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self._library_data = []

    def _persist_library_data(self) -> None:
        self._data_file.write_text(json.dumps(self._library_data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _refresh_library_list(self) -> None:
        listbox = self._library_controls.get("listbox")
        if not isinstance(listbox, tk.Listbox):
            return
        listbox.delete(0, tk.END)
        for doc in self._library_data:
            listbox.insert(tk.END, doc.get("title", ""))

    def _add_document(self) -> None:
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
        self._refresh_library_list()
        self._select_document_by_title(title)

    def _delete_document(self) -> None:
        listbox = self._library_controls.get("listbox")
        if not isinstance(listbox, tk.Listbox):
            return
        selection = listbox.curselection()
        if not selection:
            return
        index = selection[0]
        del self._library_data[index]
        self._persist_library_data()
        self._refresh_library_list()
        self._selected_title.set("")
        notes_text = self._library_controls.get("notes_text")
        if isinstance(notes_text, tk.Text):
            notes_text.delete("1.0", tk.END)

    def _on_document_select(self, event: tk.Event[tk.Listbox]) -> None:
        widget = event.widget
        if not isinstance(widget, tk.Listbox):
            return
        selection = widget.curselection()
        if not selection:
            return
        index = selection[0]
        doc = self._library_data[index]
        self._selected_title.set(doc.get("title", ""))
        notes_text = self._library_controls.get("notes_text")
        if isinstance(notes_text, tk.Text):
            notes_text.delete("1.0", tk.END)
            notes_text.insert("1.0", doc.get("notes", ""))

    def _select_document_by_title(self, title: str) -> None:
        listbox = self._library_controls.get("listbox")
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

    def _save_notes(self, widget: tk.Text) -> None:
        listbox = self._library_controls.get("listbox")
        if not isinstance(listbox, tk.Listbox):
            return
        selection = listbox.curselection()
        if not selection:
            return
        index = selection[0]
        self._library_data[index]["notes"] = widget.get("1.0", tk.END).rstrip()
        self._persist_library_data()

    def _clear_notes(self, widget: tk.Text) -> None:
        widget.delete("1.0", tk.END)


def main() -> None:
    app = RelationshipApp()
    app.mainloop()


if __name__ == "__main__":
    main()
