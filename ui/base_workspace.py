# 工作区基类（抽象公共方法）

# ui/base_workspace.py
"""
所有工作区的抽象基类
定义公共接口：build_ui(), refresh_ui(), 四个通用操作等
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt

from config import PYQT6_AVAILABLE

if not PYQT6_AVAILABLE:
    # 占位符（PyQt6 未安装时）
    class BaseWorkspace(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
else:
    class BaseWorkspace(QWidget):
        """工作区基类"""
        def __init__(self, parent=None):
            super().__init__(parent)
            self.current_mode = None  # 由主窗口设置：0=table, 1=flag, 2=note
            self.current_index = 0    # 当前选中的项索引（场景/Flag/Note）
            self.ui_built = False     # 是否已构建 UI（避免重复构建）

        def build_ui(self):
            """子类必须实现：构建工作区 UI"""
            raise NotImplementedError("子类必须实现 build_ui()")

        def refresh_ui(self):
            """子类必须实现：刷新当前选中项的数据"""
            raise NotImplementedError("子类必须实现 refresh_ui()")

        # ===================== 四个通用操作（左侧按钮调用） =====================
        def rename_current(self):
            """重命名当前项"""
            pass  # 子类实现

        def move_up_current(self):
            """上移当前项"""
            pass  # 子类实现

        def move_down_current(self):
            """下移当前项"""
            pass  # 子类实现

        def clear_current(self):
            """清空当前项"""
            pass  # 子类实现

        # ===================== 通用辅助方法 =====================
        def set_current_index(self, index: int):
            """设置当前选中索引"""
            self.current_index = index
            self.refresh_ui()

        def get_current_data(self):
            """获取当前选中项的数据（子类实现）"""
            raise NotImplementedError("子类必须实现 get_current_data()")