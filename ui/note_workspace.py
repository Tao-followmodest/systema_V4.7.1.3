# Mode 2 便签笔记工作区

# ui/note_workspace.py
"""
Mode 2 - 便签笔记工作区
包含标题输入、内容编辑、自动保存、时间日志等
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QGroupBox, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from config import PYQT6_AVAILABLE
from data_utils import save_notes
from time_utils import format_datetime
from .base_workspace import BaseWorkspace

if not PYQT6_AVAILABLE:
    class NoteWorkspace(BaseWorkspace):
        def __init__(self, parent=None):
            super().__init__(parent)
else:
    class NoteWorkspace(BaseWorkspace):
        """便签笔记工作区"""
        def __init__(self, parent=None):
            super().__init__(parent)
            self.title_entry = None
            self.content_text = None
            self.log_label = None
            self.auto_save_timer = None

        def build_ui(self):
            if self.ui_built:
                return
            self.ui_built = True

            layout = QVBoxLayout(self)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(15)

            # 标题
            title_label = QLabel("标题：")
            title_label.setFont(QFont("", 15, QFont.Weight.Bold))
            layout.addWidget(title_label)

            self.title_entry = QLineEdit()
            self.title_entry.setFont(QFont("", 15))
            self.title_entry.textChanged.connect(self.auto_save_draft)
            layout.addWidget(self.title_entry)

            # 内容
            content_label = QLabel("内容：")
            content_label.setFont(QFont("", 15, QFont.Weight.Bold))
            layout.addWidget(content_label)

            self.content_text = QTextEdit()
            self.content_text.setPlaceholderText("在这里写下你的想法、笔记...")
            self.content_text.setFont(QFont("", 12))
            self.content_text.textChanged.connect(self.auto_save_draft)
            layout.addWidget(self.content_text, stretch=1)

            # 时间日志
            log_group = QGroupBox("时间记录")
            log_layout = QVBoxLayout()
            self.log_label = QLabel("创建时间：N/A\n更新时间：N/A")
            self.log_label.setStyleSheet("color: gray; font-size: 11px;")
            log_layout.addWidget(self.log_label)
            log_group.setLayout(log_layout)
            layout.addWidget(log_group)

            layout.addStretch()

        def refresh_ui(self):
            main_window = self.window()
            if not hasattr(main_window, 'notes') or main_window.current_mode != 2:
                return

            note = main_window.notes[main_window.current_note_index]

            # 标题
            self.title_entry.setText(note.get("title", ""))

            # 内容（防止切换时丢失当前编辑）
            current_content = self.content_text.toPlainText().strip()
            saved_content = note.get("content", "").strip()
            if current_content != saved_content:
                self.content_text.setPlainText(saved_content)

            # 时间日志
            log_text = f"创建时间：{format_datetime(note.get('created_at', ''))}\n"
            log_text += f"更新时间：{format_datetime(note.get('updated_at', ''))}\n"
            if note.get("finished_at"):
                log_text += f"完成时间：{format_datetime(note.get('finished_at'))}"
            elif note.get("discarded_at"):
                log_text += f"废止时间：{format_datetime(note.get('discarded_at'))}"
            self.log_label.setText(log_text)

            # 启用/禁用编辑（根据状态）
            editable = note["status"] == "active"
            self.title_entry.setReadOnly(not editable)
            self.content_text.setReadOnly(not editable)

        def auto_save_draft(self):
            """内容或标题变更时自动保存（防抖）"""
            if not self.auto_save_timer:
                self.auto_save_timer = QTimer(self)
                self.auto_save_timer.setSingleShot(True)
                self.auto_save_timer.timeout.connect(self._perform_auto_save)

            self.auto_save_timer.start(500)  # 500ms 防抖

        def _perform_auto_save(self):
            main_window = self.window()
            if not hasattr(main_window, 'notes'):
                return

            note = main_window.notes[main_window.current_note_index]

            new_title = self.title_entry.text().strip()
            new_content = self.content_text.toPlainText().strip()

            changed = False
            if new_title != note.get("title", "").strip():
                note["title"] = new_title
                changed = True

            if new_content != note.get("content", "").strip():
                note["content"] = new_content
                changed = True

            if changed:
                note["updated_at"] = datetime.now().isoformat()
                save_notes(main_window.notes)
                # 可选：更新日志
                self.log_label.setText(
                    f"创建时间：{format_datetime(note.get('created_at', ''))}\n"
                    f"更新时间：{format_datetime(note['updated_at'])}"
                )
                main_window.statusBar().showMessage("便签已自动保存", 2000)

        # ===================== 通用操作实现 =====================
        def rename_current(self):
            pass  # 后续实现：重命名便签

        def move_up_current(self):
            pass

        def move_down_current(self):
            pass

        def clear_current(self):
            pass