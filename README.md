# paperRLT

A starter GUI skeleton for building a Windows executable that visualizes relationships between documents.

## Features
- Two-part layout with a left-aligned navigation bar ("文献库", "树状关系", "网状关系", "设置", "其它功能") using fixed-width buttons for consistent spacing.
- 文献库页面现在提供左右两栏：左侧支持输入名称后添加文献、选中文献后删除，右侧显示可编辑的笔记并带有清空/保存按钮。
- 文献库数据（文献标题与笔记）以 `library_data.json` 持久化保存，便于后续功能复用。
- Bottom content area uses stacked placeholder pages for easy expansion.
- A settings page includes a light/dark theme toggle that recolors the entire UI.
- Built with Python `tkinter` to simplify packaging into a Windows `.exe` via tools such as `pyinstaller`.

## Getting Started
1. Ensure Python 3.10+ is installed.
2. Run the app locally:
   ```bash
   python main.py
   ```
3. To package as a Windows executable, install `pyinstaller` and run:
   ```bash
   pyinstaller --noconfirm --onedir --windowed main.py
   ```
   The generated executable will be available under `dist/main` on Windows.

## Next Steps
- Replace placeholder views with actual data-driven components for tree/network visualizations.
- Integrate file ingestion and graph visualization for tree and network relationships.
- Extend settings with additional configuration options as functionality grows.
