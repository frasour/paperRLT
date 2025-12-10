# paperRLT

A starter GUI skeleton for building a Windows executable that visualizes relationships between documents.

## Features
- Two-part layout with a left-aligned navigation bar ("文献库", "树状关系", "网状关系", "设置", "其它功能") using fixed-width buttons for consistent spacing.
- 文献库页面提供左右分栏（2:3）视图：左侧含“添加/删除”与文献列表，右侧展示选中文献的详细笔记。
- 文献列表与笔记内容持久化到 `library_data.json`，允许添加、删除与保存笔记，并提供清空文本的快捷操作。
- Settings 页面包含全局浅/深色主题切换，自动更新各控件配色。
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
- Replace placeholder views with actual data-driven components.
- Integrate file ingestion and graph visualization for tree and network relationships.
- Extend settings with additional configuration options as functionality grows.
