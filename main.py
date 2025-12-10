import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk


class RelationshipApp(tk.Tk):
    """Main application window for relationship visualization."""

    DEFAULT_BUTTON_WIDTH = 14
    MIN_BUTTON_WIDTH = 10
    LIBRARY_DATA_FILE = Path(__file__).with_name("library_data.json")

    def __init__(self) -> None:
        super().__init__()
        self.title("文献关系图谱")
        self.geometry("900x600")
        self.minsize(800, 500)

        # Configure overall grid: top navigation row and content row.
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._style = ttk.Style(self)
        self._style.theme_use("clam")

        self._current_theme = tk.StringVar(value="light")
        self._current_palette: dict[str, str] = {}
        self._library_items: list[dict[str, str]] = []
        self._library_widgets: dict[str, tk.Widget] = {}

        self._apply_theme()
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
        frame = ttk.Frame(parent, padding=10, style="Content.TFrame")
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=2)
        frame.columnconfigure(1, weight=3)
        frame.rowconfigure(1, weight=1)

        header = ttk.Label(frame, text="文献库", font=("Arial", 16, "bold"), style="Content.TLabel")
        header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        left_panel = ttk.Frame(frame, padding=(0, 6, 6, 0), style="Content.TFrame")
        left_panel.grid(row=1, column=0, sticky="nsew")
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(1, weight=1)

        controls = ttk.Frame(left_panel, padding=(0, 0, 0, 6), style="Content.TFrame")
        controls.grid(row=0, column=0, sticky="ew")
        controls.columnconfigure(1, weight=1)

        add_button = ttk.Button(controls, text="添加", command=self._add_library_item, style="Nav.TButton")
        add_button.grid(row=0, column=0, padx=(0, 4))

        entry = tk.Entry(controls, width=24)
        entry.grid(row=0, column=1, padx=4, sticky="ew")

        delete_button = ttk.Button(controls, text="删除", command=self._delete_library_item, style="Nav.TButton")
        delete_button.grid(row=0, column=2, padx=(4, 0))

        listbox = tk.Listbox(left_panel, exportselection=False)
        listbox.grid(row=1, column=0, sticky="nsew")
        listbox.bind("<<ListboxSelect>>", self._on_library_select)

        right_panel = ttk.Frame(frame, padding=(6, 6, 0, 0), style="Content.TFrame")
        right_panel.grid(row=1, column=1, sticky="nsew")
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)

        detail_label = ttk.Label(right_panel, text="文献笔记", font=("Arial", 13, "bold"), style="Content.TLabel")
        detail_label.grid(row=0, column=0, sticky="w", pady=(0, 4))

        note_text = tk.Text(right_panel, wrap=tk.WORD)
        note_text.grid(row=1, column=0, sticky="nsew")

        button_bar = ttk.Frame(right_panel, padding=(0, 6, 0, 0), style="Content.TFrame")
        button_bar.grid(row=2, column=0, sticky="e")

        clear_button = ttk.Button(button_bar, text="清空", command=self._clear_note, style="Nav.TButton")
        clear_button.grid(row=0, column=0, padx=(0, 6))

        save_button = ttk.Button(button_bar, text="保存", command=self._save_note, style="Nav.TButton")
        save_button.grid(row=0, column=1)

        self._library_widgets.update(
            {
                "entry": entry,
                "listbox": listbox,
                "note_text": note_text,
            }
        )

        self._refresh_library_list()
        self._apply_theme_to_library()
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

        self._current_palette = palette

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

        self._apply_theme_to_library()

    def _apply_theme_to_library(self) -> None:
        if not self._library_widgets:
            return

        palette = self._current_palette
        entry = self._library_widgets.get("entry")
        listbox = self._library_widgets.get("listbox")
        note_text = self._library_widgets.get("note_text")

        if entry:
            entry.configure(background=palette["surface"], foreground=palette["foreground"])
        if listbox:
            listbox.configure(
                background=palette["surface"],
                foreground=palette["foreground"],
                selectbackground=palette["accent"],
                selectforeground=palette["surface"],
                borderwidth=1,
                highlightbackground=palette["border"],
                highlightcolor=palette["border"],
            )
        if note_text:
            note_text.configure(
                background=palette["surface"],
                foreground=palette["foreground"],
                insertbackground=palette["foreground"],
                borderwidth=1,
                highlightbackground=palette["border"],
                highlightcolor=palette["border"],
            )

    def _load_library_data(self) -> None:
        if self.LIBRARY_DATA_FILE.exists():
            try:
                with self.LIBRARY_DATA_FILE.open("r", encoding="utf-8") as file:
                    data = json.load(file)
                self._library_items = [
                    {"title": item.get("title", ""), "note": item.get("note", "")}
                    for item in data
                    if isinstance(item, dict)
                ]
            except (json.JSONDecodeError, OSError):
                self._library_items = []
        else:
            self._library_items = []

    def _persist_library_data(self) -> None:
        try:
            with self.LIBRARY_DATA_FILE.open("w", encoding="utf-8") as file:
                json.dump(self._library_items, file, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def _refresh_library_list(self) -> None:
        listbox: tk.Listbox | None = self._library_widgets.get("listbox")  # type: ignore[assignment]
        if listbox is None:
            return
        listbox.delete(0, tk.END)
        for item in self._library_items:
            listbox.insert(tk.END, item.get("title", ""))

    def _add_library_item(self) -> None:
        entry: tk.Entry | None = self._library_widgets.get("entry")  # type: ignore[assignment]
        listbox: tk.Listbox | None = self._library_widgets.get("listbox")  # type: ignore[assignment]
        if entry is None or listbox is None:
            return

        title = entry.get().strip()
        if not title:
            return

        self._library_items.append({"title": title, "note": ""})
        self._persist_library_data()
        self._refresh_library_list()
        entry.delete(0, tk.END)
        listbox.selection_clear(0, tk.END)
        listbox.selection_set(tk.END)
        self._show_selected_note(len(self._library_items) - 1)

    def _delete_library_item(self) -> None:
        listbox: tk.Listbox | None = self._library_widgets.get("listbox")  # type: ignore[assignment]
        if listbox is None:
            return
        selection = listbox.curselection()
        if not selection:
            return
        index = selection[0]
        if 0 <= index < len(self._library_items):
            self._library_items.pop(index)
            self._persist_library_data()
            self._refresh_library_list()
            listbox.selection_clear(0, tk.END)
            self._clear_note_text()

    def _on_library_select(self, event: tk.Event[tk.Listbox]) -> None:  # type: ignore[type-arg]
        listbox: tk.Listbox = event.widget  # type: ignore[assignment]
        selection = listbox.curselection()
        if not selection:
            return
        index = selection[0]
        self._show_selected_note(index)

    def _show_selected_note(self, index: int) -> None:
        if not (0 <= index < len(self._library_items)):
            return
        note_text: tk.Text | None = self._library_widgets.get("note_text")  # type: ignore[assignment]
        if note_text is None:
            return
        self._clear_note_text()
        note_text.insert("1.0", self._library_items[index].get("note", ""))

    def _clear_note_text(self) -> None:
        note_text: tk.Text | None = self._library_widgets.get("note_text")  # type: ignore[assignment]
        if note_text is None:
            return
        note_text.delete("1.0", tk.END)

    def _save_note(self) -> None:
        listbox: tk.Listbox | None = self._library_widgets.get("listbox")  # type: ignore[assignment]
        note_text: tk.Text | None = self._library_widgets.get("note_text")  # type: ignore[assignment]
        if listbox is None or note_text is None:
            return
        selection = listbox.curselection()
        if not selection:
            return
        index = selection[0]
        if not (0 <= index < len(self._library_items)):
            return
        self._library_items[index]["note"] = note_text.get("1.0", tk.END).strip()
        self._persist_library_data()

    def _clear_note(self) -> None:
        listbox: tk.Listbox | None = self._library_widgets.get("listbox")  # type: ignore[assignment]
        if listbox is None:
            return
        selection = listbox.curselection()
        if not selection:
            return
        index = selection[0]
        if not (0 <= index < len(self._library_items)):
            return
        self._library_items[index]["note"] = ""
        self._persist_library_data()
        self._clear_note_text()


def main() -> None:
    app = RelationshipApp()
    app.mainloop()


if __name__ == "__main__":
    main()
