



systema/                          # 项目根目录
│
├── main.py                       # 程序唯一入口：创建 QApplication、启动主窗口
│
├── config.py                     # 全局常量、路径定义（DATA_DIR、文件路径、天干地支等）
│
├── data_utils.py                 # 数据读写核心逻辑（load/save scenes/flags/notes/records 等）
│
├── time_utils.py                 # 时间处理工具（format_datetime、format_timedelta 等）
│
├── data/                         # 运行时生成的数据目录（已正确使用 data/）
│   ├── flags.json                # Flag 任务数据
│   ├── notes.json                # 便签笔记数据
│   ├── tables.json               # 场景表格字段定义（可选）
│   ├── flags/                    # 每个 Flag 的独立文件（可选，未来扩展）
│   ├── notes/                    # 每个 Note 的独立文件（可选）
│   └── tables/                   # 每个场景的 CSV 文件（子目录，按场景名）
│
├── resources/                    # 非代码资源（你已正确添加）
│   └── menu.md                   # 菜单说明文档
│
└── ui/                           # 所有 UI 相关模块（完美包结构）
    ├── __init__.py               # 空文件，使 ui 成为 Python 包（可导入）
    ├── base_workspace.py         # 工作区基类（抽象公共方法）
    ├── components.py             # 可复用小组件（按钮、对话框等）
    ├── flag_workspace.py         # Mode 1 Flag 任务工作区
    ├── note_workspace.py         # Mode 2 便签笔记工作区
    ├── personal_db_gui.py        # 主窗口类（QMainWindow）
    ├── table_workspace.py        # Mode 0 数据表格工作区
    └── welcome_widget.py         # 启动欢迎页面