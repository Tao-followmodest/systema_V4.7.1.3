# Mode 1 Flag 任务工作区

# ui/flag_workspace.py
"""
Mode 1 - Flag 任务工作区
包含时间设置、运行控制、进度条、倒计时、内容编辑等
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QPushButton, QProgressBar, QTextEdit, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from config import PYQT6_AVAILABLE
from data_utils import save_flags
from time_utils import format_datetime, format_timedelta, seconds_to_span_str
from .base_workspace import BaseWorkspace

if not PYQT6_AVAILABLE:
    class FlagWorkspace(BaseWorkspace):
        def __init__(self, parent=None):
            super().__init__(parent)
else:
    class FlagWorkspace(BaseWorkspace):
        """Flag 任务工作区"""
        def __init__(self, parent=None):
            super().__init__(parent)
            self.core_widgets = {}  # name, start, target, span, elapsed, countdown 等 QLabel
            self.pb = None
            self.pb_label = None
            self.run_btn = None
            self.content_text = None
            self.timer = QTimer(self)  # 用于实时更新进度
            self.timer.timeout.connect(self.update_progress)

        def build_ui(self):
            if self.ui_built:
                return
            self.ui_built = True

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            container = QWidget()
            scroll.setWidget(container)
            main_layout = QVBoxLayout(container)
            main_layout.setContentsMargins(20, 20, 20, 20)
            main_layout.setSpacing(15)
            layout = QVBoxLayout(self)
            layout.addWidget(scroll)

            # === 标题区 ===
            title_layout = QHBoxLayout()
            name_label = QLabel("Flag 名称：")
            name_label.setFont(QFont("", 12, QFont.Weight.Bold))
            self.core_widgets['name'] = QLabel("加载中...")
            self.core_widgets['name'].setFont(QFont("", 14, QFont.Weight.Bold))
            title_layout.addWidget(name_label)
            title_layout.addWidget(self.core_widgets['name'])
            title_layout.addStretch()
            main_layout.addLayout(title_layout)

            # === 时间设置区 ===
            time_group = QGroupBox("时间设置")
            time_layout = QGridLayout()
            labels = ["起始时间：", "截止时间：", "总跨度："]
            keys = ['start', 'target', 'span']
            for i, (text, key) in enumerate(zip(labels, keys)):
                time_layout.addWidget(QLabel(text), i, 0)
                lbl = QLabel("null")
                self.core_widgets[key] = lbl
                time_layout.addWidget(lbl, i, 1)
                btn = QPushButton("设置")
                # 后续在 personal_db_gui 中连接具体设置方法
                time_layout.addWidget(btn, i, 2)
            time_group.setLayout(time_layout)
            main_layout.addWidget(time_group)

            # === 运行控制与进度 ===
            control_group = QGroupBox("运行控制与进度")
            control_layout = QVBoxLayout()
            run_layout = QHBoxLayout()
            self.run_btn = QPushButton("开始运行")
            self.run_btn.setEnabled(False)
            # 后续在 personal_db_gui 中连接 self.window().toggle_flag_running
            run_layout.addWidget(self.run_btn)
            run_layout.addStretch()
            self.pb = QProgressBar()
            self.pb.setRange(0, 100)
            self.pb.setValue(0)
            self.pb.setTextVisible(False)
            run_layout.addWidget(self.pb)
            self.pb_label = QLabel("总进度: 0.00%")
            run_layout.addWidget(self.pb_label)
            control_layout.addLayout(run_layout)
            control_group.setLayout(control_layout)
            main_layout.addWidget(control_group)

            # === 内容编辑区 ===
            content_group = QGroupBox("内容")
            content_layout = QVBoxLayout()
            self.content_text = QTextEdit()
            self.content_text.setPlaceholderText("在这里写下你的想法、笔记...")
            # 后续连接 auto_save_draft
            content_layout.addWidget(self.content_text)
            content_group.setLayout(content_layout)
            main_layout.addWidget(content_group)

            # === 时间日志 ===
            log_group = QGroupBox("时间记录")
            log_layout = QVBoxLayout()
            self.log_label = QLabel("创建时间：N/A\n更新时间：N/A")
            self.log_label.setStyleSheet("color: gray; font-size: 11px;")
            log_layout.addWidget(self.log_label)
            log_group.setLayout(log_layout)
            main_layout.addWidget(log_group)

            main_layout.addStretch()

        def refresh_ui(self):
            main_window = self.window()
            if not hasattr(main_window, 'flags') or main_window.current_mode != 1:
                return

            flag = main_window.flags[main_window.current_flag_index]
            self.core_widgets['name'].setText(flag.get("name", "未命名"))

            self.core_widgets['start'].setText(format_datetime(flag.get("start_time", "")))
            self.core_widgets['target'].setText(format_datetime(flag.get("target_time", "")))
            self.core_widgets['span'].setText(seconds_to_span_str(flag.get("span_seconds", 0)))

            self.content_text.setPlainText(flag.get("content", ""))

            # 更新日志（创建/更新/完成/废止时间）
            log_text = f"创建时间：{format_datetime(flag.get('created_at', ''))}\n"
            log_text += f"更新时间：{format_datetime(flag.get('updated_at', ''))}\n"
            if flag.get("finished_at"):
                log_text += f"完成时间：{format_datetime(flag.get('finished_at'))}"
            elif flag.get("discarded_at"):
                log_text += f"废止时间：{format_datetime(flag.get('discarded_at'))}"
            self.log_label.setText(log_text)

            # 更新进度条（简单示例，后续完善计算逻辑）
            self.update_progress()

            # 启用/禁用运行按钮
            self.run_btn.setEnabled(flag["status"] == "active")

        def update_progress(self):
            """定时更新进度（示例逻辑，后续完善）"""
            # TODO: 计算 elapsed, countdown, percent 等
            self.pb.setValue(0)  # 占位
            self.pb_label.setText("总进度: 0.00%")

        # ===================== 通用操作实现 =====================
        def rename_current(self):
            pass  # 后续实现：重命名 Flag

        def move_up_current(self):
            pass

        def move_down_current(self):
            pass

        def clear_current(self):
            pass