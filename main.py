# 程序唯一入口：创建 QApplication、启动主窗口

# main.py
"""
Systema 程序唯一入口
负责创建 QApplication、初始化主窗口并启动事件循环
"""

import sys

from config import PYQT6_AVAILABLE, get_default_font

if not PYQT6_AVAILABLE:
    print("警告: 未安装 PyQt6，整个程序将无法运行。请运行：pip install PyQt6")
    sys.exit(1)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

from ui.personal_db_gui import PersonalDBGUI

def get_qapp():
    """获取或创建唯一的 QApplication 实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        # 设置全局字体
        font = get_default_font()
        app.setFont(font)
    return app

if __name__ == "__main__":
    app = get_qapp()
    if app:
        window = PersonalDBGUI()
        window.show()
        sys.exit(app.exec())