# 主窗口类（QMainWindow）

# ui/personal_db_gui.py
"""
主窗口类（QMainWindow）
管理左侧列表、模式切换、堆栈页面、底部按钮组、菜单、快捷键等
"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QListWidget, QStackedWidget, QPushButton, QGroupBox,
    QButtonGroup, QStatusBar, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QKeySequence, QShortcut

from config import PYQT6_AVAILABLE, ensure_data_dir
from data_utils import load_scenes, load_flags, load_notes, save_scenes, save_flags, save_notes
from ui.welcome_widget import WelcomeWidget
from ui.base_workspace import BaseWorkspace
from ui.table_workspace import TableWorkspace
from ui.flag_workspace import FlagWorkspace
from ui.note_workspace import NoteWorkspace

if not PYQT6_AVAILABLE:
    class PersonalDBGUI(QWidget):
        def __init__(self):
            super().__init__()
else:
    class PersonalDBGUI(QMainWindow):
        """Systema 主窗口"""
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Systema V4.7")
            self.resize(1200, 800)

            # 数据预加载
            ensure_data_dir()
            self.scenes = load_scenes()
            self.flags = load_flags()
            self.notes = load_notes()

            # 当前状态
            self.current_mode = 0  # 0:table, 1:flag, 2:note
            self.current_scene_index = 0
            self.current_flag_index = 0
            self.current_note_index = 0

            # 主栈：欢迎页 + 主界面
            self.main_stack = QStackedWidget()
            self.setCentralWidget(self.main_stack)

            # 欢迎页
            self.welcome_widget = WelcomeWidget(self)
            self.main_stack.addWidget(self.welcome_widget)

            # 主界面容器（延迟构建）
            self.main_container = QWidget()
            self.main_stack.addWidget(self.main_container)

            # 默认显示欢迎页
            self.main_stack.setCurrentWidget(self.welcome_widget)

            # 工作区实例（延迟初始化）
            self.workspaces = [None] * 3

            # 底部按钮组
            self.bottom_groups = {}

            # 全局快捷键
            self.setup_global_shortcuts()

        def build_ui(self):
            """构建主界面"""
            if hasattr(self, '_ui_built') and self._ui_built:
                return
            self._ui_built = True

            self.main_stack.setCurrentWidget(self.main_container)

            layout = QHBoxLayout(self.main_container)
            splitter = QSplitter(Qt.Orientation.Horizontal)
            layout.addWidget(splitter)

            # 左侧面板
            left_panel = QWidget()
            left_layout = QVBoxLayout(left_panel)

            # 模式选择（按钮组）
            mode_group = QGroupBox("模式选择")
            mode_layout = QVBoxLayout()
            self.mode_button_group = QButtonGroup(self)
            self.btn_mode_table = QPushButton("数据记录")
            self.btn_mode_flag = QPushButton("Flag 任务")
            self.btn_mode_note = QPushButton("便签笔记")
            for btn in (self.btn_mode_table, self.btn_mode_flag, self.btn_mode_note):
                btn.setCheckable(True)
                btn.setMinimumHeight(40)
                mode_layout.addWidget(btn)
                self.mode_button_group.addButton(btn)
            mode_group.setLayout(mode_layout)
            left_layout.addWidget(mode_group)
            self.mode_button_group.setId(self.btn_mode_table, 0)
            self.mode_button_group.setId(self.btn_mode_flag, 1)
            self.mode_button_group.setId(self.btn_mode_note, 2)
            self.mode_button_group.idClicked.connect(self.switch_mode)

            # 列表导航
            list_group = QGroupBox("列表导航")
            list_layout = QVBoxLayout()
            self.left_list = QListWidget()
            self.left_list.itemClicked.connect(self.on_left_item_clicked)
            list_layout.addWidget(self.left_list)
            list_group.setLayout(list_layout)
            left_layout.addWidget(list_group, stretch=1)

            # 列表操作按钮
            btn_group = QGroupBox("列表操作")
            btn_layout = QVBoxLayout()
            self.btn_rename = QPushButton("重命名当前")
            self.btn_move_up = QPushButton("↑ 上移")
            self.btn_move_down = QPushButton("↓ 下移")
            self.btn_clear = QPushButton("清空当前")
            for btn in (self.btn_rename, self.btn_move_up, self.btn_move_down, self.btn_clear):
                btn_layout.addWidget(btn)
            btn_group.setLayout(btn_layout)
            left_layout.addWidget(btn_group)

            splitter.addWidget(left_panel)

            # 右侧工作区堆栈
            self.right_stack = QStackedWidget()
            splitter.addWidget(self.right_stack)

            # 初始化工作区
            self.workspaces[0] = TableWorkspace(self)
            self.workspaces[1] = FlagWorkspace(self)
            self.workspaces[2] = NoteWorkspace(self)
            for ws in self.workspaces:
                self.right_stack.addWidget(ws)

            # 底部操作栏（示例）
            bottom_layout = QHBoxLayout()
            self.bottom_groups = {
                "编辑操作": [QPushButton("进入编辑"), QPushButton("退出编辑")],
                "状态管理": [QPushButton("标记完成"), QPushButton("标记废止")],
                "本地存储": [QPushButton("保存到 TXT"), QPushButton("另存为")]
            }
            for group_name, buttons in self.bottom_groups.items():
                group = QGroupBox(group_name)
                g_layout = QHBoxLayout()
                for btn in buttons:
                    g_layout.addWidget(btn)
                group.setLayout(g_layout)
                bottom_layout.addWidget(group)
            main_layout.addLayout(bottom_layout)

            # 状态栏
            self.setStatusBar(QStatusBar())

            # 初始刷新
            self.switch_mode(0)  # 默认 Mode 0

        def switch_mode(self, mode_index: int):
            if mode_index == self.current_mode:
                return

            self.current_mode = mode_index

            # 同步模式按钮
            buttons = [self.btn_mode_table, self.btn_mode_flag, self.btn_mode_note]
            buttons[mode_index].setChecked(True)

            # 切换堆栈
            self.right_stack.setCurrentIndex(mode_index)

            # 刷新左侧列表
            self.refresh_left_list()

            # 刷新底部按钮状态
            self.update_bottom_buttons()

            # 刷新当前工作区（如果还没建 UI，就建）
            ws = self.workspaces[mode_index]
            if not ws.ui_built:
                ws.build_ui()
            ws.refresh_ui()

            mode_names = ["数据记录", "Flag 任务", "便签笔记"]
            self.statusBar().showMessage(f"已切换到：{mode_names[mode_index]} 模式")

        def refresh_left_list(self):
            self.left_list.clear()
            if self.current_mode == 0:
                for name in self.scenes.keys():
                    self.left_list.addItem(name)
                self.left_list.setCurrentRow(self.current_scene_index)
            elif self.current_mode == 1:
                for flag in self.flags:
                    name = flag.get("name", "未命名")
                    self.left_list.addItem(name)
                self.left_list.setCurrentRow(self.current_flag_index)
            elif self.current_mode == 2:
                for note in self.notes:
                    name = note.get("title", note.get("display_name", "未命名"))
                    self.left_list.addItem(name)
                self.left_list.setCurrentRow(self.current_note_index)

        def on_left_item_clicked(self, item):
            idx = self.left_list.row(item)
            if self.current_mode == 0:
                self.current_scene_index = idx
            elif self.current_mode == 1:
                self.current_flag_index = idx
            elif self.current_mode == 2:
                self.current_note_index = idx
            self.workspaces[self.current_mode].set_current_index(idx)

        def update_bottom_buttons(self):
            mode = self.current_mode
            groups = self.bottom_groups

            if mode == 0:
                groups["编辑操作"][0].setEnabled(True)
                groups["编辑操作"][1].setEnabled(True)
                for btn in groups["状态管理"] + groups["本地存储"]:
                    btn.setEnabled(False)
            else:
                groups["编辑操作"][0].setEnabled(False)
                groups["编辑操作"][1].setEnabled(False)
                for btn in groups["状态管理"] + groups["本地存储"]:
                    btn.setEnabled(True)

        def setup_global_shortcuts(self):
            # Ctrl+C / V / X / A 等全局快捷键（后续完善）
            pass

        # ... 其他方法如 toggle_edit_mode、save_all 等可在此添加