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

        # Configure overall grid: top navigation row and content row.
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._style = ttk.Style(self)
        self._style.theme_use("clam")

        self._current_theme = tk.StringVar(value="light")
        self._apply_theme()

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
            "library": self._create_placeholder(content_frame, "文献库页面（待实现）"),
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


def main() -> None:
    app = RelationshipApp()
    app.mainloop()


if __name__ == "__main__":
    main()
