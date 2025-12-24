# Mode 0 数据表格工作区

# ui/table_workspace.py
"""
Mode 0 - 数据表格工作区
包含 QTableView、列/行操作、导入导出 CSV、编辑模式等
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QHeaderView,
    QPushButton, QGroupBox, QScrollArea, QProgressBar,
    QMessageBox, QInputDialog, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QStandardItemModel, QStandardItem

from config import PYQT6_AVAILABLE
from data_utils import load_records, save_records
from .base_workspace import BaseWorkspace

if not PYQT6_AVAILABLE:
    class TableWorkspace(BaseWorkspace):
        def __init__(self, parent=None):
            super().__init__(parent)
else:
    class TableWorkspace(BaseWorkspace):
        """数据表格工作区"""
        def __init__(self, parent=None):
            super().__init__(parent)
            self.current_scene_name = None
            self.model = None
            self.table_view = None
            self.edit_mode_locked = True  # 默认锁定编辑

        def build_ui(self):
            if self.ui_built:
                return
            self.ui_built = True

            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 10, 10, 10)

            # 表格视图
            self.table_view = QTableView()
            self.table_view.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)  # 默认禁用编辑
            self.table_view.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
            self.table_view.setAlternatingRowColors(True)
            self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            layout.addWidget(self.table_view)

            # 底部操作区（示例，可扩展）
            bottom_layout = QHBoxLayout()
            btn_save = QPushButton("保存")
            btn_save.clicked.connect(self.save_table)
            bottom_layout.addWidget(btn_save)

            # ... 其他按钮（如批量添加列等）可在此添加
            layout.addLayout(bottom_layout)

        def refresh_ui(self):
            main_window = self.window()
            if not hasattr(main_window, 'scenes') or main_window.current_mode != 0:
                return

            scene_names = list(main_window.scenes.keys())
            if not scene_names:
                return

            idx = main_window.current_scene_index
            if idx >= len(scene_names):
                idx = 0
                main_window.current_scene_index = 0

            self.current_scene_name = scene_names[idx]
            fields = main_window.scenes[self.current_scene_name]
            records = load_records(self.current_scene_name, fields)

            self.load_data(fields, records)

            rows = self.model.rowCount() if self.model else 0
            cols = self.model.columnCount() if self.model else 0
            main_window.statusBar().showMessage(
                f"场景：{self.current_scene_name} | 共 {rows} 行 {cols} 列", 5000
            )

        def load_data(self, fields: list, records: list):
            """加载字段和记录到表格"""
            if not self.table_view:
                return

            self.model = QStandardItemModel()
            self.model.setHorizontalHeaderLabels(fields)

            for rec in records:
                row = [QStandardItem(str(rec.get(f, ""))) for f in fields]
                self.model.appendRow(row)

            self.table_view.setModel(self.model)

        def save_table(self):
            main_window = self.window()
            if not hasattr(main_window, 'scenes'):
                return

            fields = [self.model.headerData(i, Qt.Orientation.Horizontal) for i in range(self.model.columnCount())]
            records = []
            for row in range(self.model.rowCount()):
                rec = {fields[col]: self.model.item(row, col).text() for col in range(self.model.columnCount())}
                records.append(rec)

            save_records(self.current_scene_name, fields, records)
            main_window.scenes[self.current_scene_name] = fields
            from data_utils import save_scenes  # 延迟导入避免循环
            save_scenes(main_window.scenes)
            main_window.statusBar().showMessage(f"已保存场景：{self.current_scene_name}", 3000)

        # ===================== 通用操作实现 =====================
        def rename_current(self):
            pass  # 后续实现：重命名当前场景

        def move_up_current(self):
            pass

        def move_down_current(self):
            pass

        def clear_current(self):
            pass

        # ... 其他方法如 toggle_edit_mode、import_csv 等可在此添加