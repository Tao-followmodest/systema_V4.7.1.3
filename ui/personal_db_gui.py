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

from config import PYQT6_AVAILABLE, ensure_data_dir,TIANGAN,DIZHI_SCENE,DIZHI_FLAG
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
            self.edit_mode = False  # 默认锁定

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
            """构建主界面：左侧操作区贯通，右侧工作区+底部按钮"""
            if hasattr(self, '_ui_built') and self._ui_built:
                return
            self._ui_built = True

            self.main_stack.setCurrentWidget(self.main_container)

            # 主布局改为 QHBoxLayout，确保左侧能一通到底
            main_h_layout = QHBoxLayout(self.main_container)
            main_h_layout.setContentsMargins(5, 5, 5, 5)
            main_h_layout.setSpacing(10)

            # ================= 1. 左侧操作区 (贯通) =================
            left_panel = QWidget()
            left_panel.setFixedWidth(200)  # 对应绿色框线宽度
            left_layout = QVBoxLayout(left_panel)
            left_layout.setContentsMargins(0, 0, 0, 0)

            # (1) 模式选择
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

            # (2) 列表导航
            list_group = QGroupBox("列表导航")
            list_nav_layout = QVBoxLayout()
            self.left_list = QListWidget()
            self.left_list.itemClicked.connect(self.on_left_item_clicked)
            list_nav_layout.addWidget(self.left_list)
            list_group.setLayout(list_nav_layout)
            left_layout.addWidget(list_group, stretch=1)  # 占据剩余空间

            # (3) 列表操作
            op_group = QGroupBox("列表操作")
            op_layout = QVBoxLayout()  # 也可以改为 QGridLayout 实现 2x2
            self.btn_rename = QPushButton("重命名当前")
            self.btn_move_up = QPushButton("↑ 上移")
            self.btn_move_down = QPushButton("↓ 下移")
            self.btn_clear = QPushButton("清空当前")
            for btn in (self.btn_rename, self.btn_move_up, self.btn_move_down, self.btn_clear):
                op_layout.addWidget(btn)
            op_group.setLayout(op_layout)
            left_layout.addWidget(op_group)

            main_h_layout.addWidget(left_panel)

            # ================= 2. 右侧工作区 (内容 + 底部按钮) =================
            right_container = QWidget()
            right_v_layout = QVBoxLayout(right_container)
            right_v_layout.setContentsMargins(0, 0, 0, 0)

            # (1) 右侧工作区堆栈 (占据上方)
            self.right_stack = QStackedWidget()
            self.workspaces[0] = TableWorkspace(self)
            self.workspaces[1] = FlagWorkspace(self)
            self.workspaces[2] = NoteWorkspace(self)
            for ws in self.workspaces:
                self.right_stack.addWidget(ws)
            right_v_layout.addWidget(self.right_stack, stretch=1)

            # (2) 底部按钮栏 (红色框线区域：三组按钮，每组2个上下排列)
            bottom_bar = QWidget()
            bottom_bar.setFixedHeight(110)  # 限制高度
            bottom_h_layout = QHBoxLayout(bottom_bar)
            bottom_h_layout.setContentsMargins(0, 5, 0, 0)

            # 按钮配置
            btn_config = {
                "编辑操作": ["进入编辑", "退出编辑"],
                "状态管理": ["标记完成", "标记废止"],
                "本地存储": ["保存默认", "另存设置"]
            }
            self.bottom_groups = {}

            for group_name, btn_names in btn_config.items():
                group_box = QGroupBox(group_name)
                group_v_layout = QVBoxLayout(group_box)  # 组内上下排列
                group_v_layout.setSpacing(2)
                group_v_layout.setContentsMargins(5, 15, 5, 5)

                self.bottom_groups[group_name] = []
                for name in btn_names:
                    btn = QPushButton(name)
                    btn.setFixedHeight(30)
                    group_v_layout.addWidget(btn)
                    self.bottom_groups[group_name].append(btn)

                bottom_h_layout.addWidget(group_box)

            # === 重新映射按钮变量名以匹配后续逻辑 ===
            # 处理编辑操作组
            if "编辑操作" in self.bottom_groups:
                self.btn_enter_edit = self.bottom_groups["编辑操作"][0]
                self.btn_exit_edit = self.bottom_groups["编辑操作"][1]

            # 处理状态管理组
            if "状态管理" in self.bottom_groups:
                self.btn_complete = self.bottom_groups["状态管理"][0]
                self.btn_discard = self.bottom_groups["状态管理"][1]

            # 处理本地存储组
            if "本地存储" in self.bottom_groups:
                self.btn_save_txt = self.bottom_groups["本地存储"][0]
                self.btn_save_as = self.bottom_groups["本地存储"][1]

            # 映射列表操作按钮（这些已经在 self 中定义过，但需要重新指定到左侧面板的按钮上）
            # 注意：左侧面板的按钮在 build_ui 前半部分已经通过 self.btn_rename 等定义好了，不需要重新映射

            # 连接 Mode 2 专属功能
            self.btn_enter_edit.clicked.connect(self.enter_edit_mode)
            self.btn_exit_edit.clicked.connect(self.exit_edit_mode)
            self.btn_complete.clicked.connect(
                lambda: self.workspaces[2].mark_complete() if self.current_mode == 2 else None)
            self.btn_discard.clicked.connect(
                lambda: self.workspaces[2].mark_discard() if self.current_mode == 2 else None)
            self.btn_save_txt.clicked.connect(
                lambda: self.workspaces[2].export_txt() if self.current_mode == 2 else None)
            self.btn_save_as.clicked.connect(lambda: self.workspaces[2].export_as() if self.current_mode == 2 else None)
            right_v_layout.addWidget(bottom_bar)
            main_h_layout.addWidget(right_container)

            # 初始化后续逻辑
            self.mode_button_group.setId(self.btn_mode_table, 0)
            self.mode_button_group.setId(self.btn_mode_flag, 1)
            self.mode_button_group.setId(self.btn_mode_note, 2)
            self.mode_button_group.idClicked.connect(self.switch_mode)

            self.refresh_left_list()
            self.btn_mode_table.setChecked(True)
            self.switch_mode(0)
            self.setStatusBar(QStatusBar())

        def switch_mode(self, mode_index: int):
            if mode_index == self.current_mode:
                return

            self.current_mode = mode_index

            # 同步按钮
            buttons = [self.btn_mode_table, self.btn_mode_flag, self.btn_mode_note]
            buttons[mode_index].setChecked(True)

            # 切换堆栈
            self.right_stack.setCurrentIndex(mode_index)

            # 刷新左侧列表
            self.refresh_left_list()

            # 刷新底部按钮状态
            self.update_bottom_buttons()

            # 刷新当前工作区
            ws = self.workspaces[mode_index]
            if not ws.ui_built:
                ws.build_ui()
            ws.refresh_ui()

            mode_names = ["数据记录", "Flag 任务", "便签笔记"]
            self.statusBar().showMessage(f"已切换到：{mode_names[mode_index]} 模式")

            # 确保切换便签或模式时恢复锁定
            if hasattr(self, 'workspaces') and self.workspaces[self.current_mode]:
                if self.current_mode == 2:
                    self.workspaces[2].lock_edit()  # 切换时默认锁定

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
                for i, note in enumerate(self.notes):
                    # 强制逻辑：如果 display_name 是默认生成的“便签X”，则显示天干
                    name = note.get("display_name")
                    if not name or name.startswith("便签"):
                        name = TIANGAN[i]
                    item_widget = self.left_list.addItem(name)  # 注意：addItem 返回 None，要分两行写
                    item = self.left_list.item(self.left_list.count() - 1)
                    if note["status"] != "active":
                        item.setForeground(Qt.GlobalColor.gray)

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
            if not groups: return

            # 编辑操作按钮：Mode 0 和 Mode 2 都需要启用
            can_edit = (mode == 0 or mode == 2)
            groups["编辑操作"][0].setEnabled(can_edit)
            groups["编辑操作"][1].setEnabled(can_edit)

            # 状态管理和本地存储：仅 Mode 2 启用
            is_note_mode = (mode == 2)
            for btn in groups["状态管理"] + groups["本地存储"]:
                btn.setEnabled(is_note_mode)

        def enter_edit_mode(self):
            if self.current_mode == 2:
                self.workspaces[2].unlock_edit()

        def exit_edit_mode(self):
            if self.current_mode == 2:
                self.workspaces[2].lock_edit()

        def setup_global_shortcuts(self):
            # Ctrl+C / V / X / A 等全局快捷键（后续完善）
            pass

        # ... 其他方法如 toggle_edit_mode、save_all 等可在此添加