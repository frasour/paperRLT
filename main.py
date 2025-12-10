import tkinter as tk
from tkinter import ttk


class RelationshipApp(tk.Tk):
    """Main application window for relationship visualization."""

    def __init__(self) -> None:
        super().__init__()
        self.title("文献关系图谱")
        self.geometry("900x600")
        self.minsize(800, 500)

        # Configure overall grid: top navigation row and content row.
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_navigation()
        self._build_content_area()

    def _build_navigation(self) -> None:
        navigation_frame = ttk.Frame(self, padding=(10, 10, 10, 5))
        navigation_frame.grid(row=0, column=0, sticky="ew")
        navigation_frame.columnconfigure((0, 1, 2, 3), weight=1)

        buttons = [
            ("文献库", self._show_library),
            ("树状关系", self._show_tree_view),
            ("网状关系", self._show_graph_view),
            ("其它功能", self._show_placeholder),
        ]

        for index, (text, command) in enumerate(buttons):
            button = ttk.Button(navigation_frame, text=text, command=command)
            button.grid(row=0, column=index, padx=5, sticky="ew")

    def _build_content_area(self) -> None:
        content_frame = ttk.Frame(self, padding=10)
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)

        self._content_stack = {
            "library": self._create_placeholder(content_frame, "文献库页面（待实现）"),
            "tree": self._create_placeholder(content_frame, "树状关系页面（待实现）"),
            "graph": self._create_placeholder(content_frame, "网状关系页面（待实现）"),
            "other": self._create_placeholder(content_frame, "更多功能可在此扩展"),
        }

        self._active_content = None
        self._switch_content("library")

    def _create_placeholder(self, parent: ttk.Frame, text: str) -> ttk.Frame:
        frame = ttk.Frame(parent, relief=tk.RIDGE, padding=20)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        label = ttk.Label(frame, text=text, anchor="center", font=("Arial", 16))
        label.grid(row=0, column=0, sticky="nsew")
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

    def _show_placeholder(self) -> None:
        self._switch_content("other")


def main() -> None:
    app = RelationshipApp()
    app.mainloop()


if __name__ == "__main__":
    main()
