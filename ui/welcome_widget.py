# 启动欢迎页面

# ui/welcome_widget.py
"""
启动欢迎页面
显示标题、简介和“开始使用”按钮，点击后切换到主界面
"""
import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from config import PYQT6_AVAILABLE

if not PYQT6_AVAILABLE:
    # 占位符（如果 PyQt6 未安装）
    class WelcomeWidget(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
else:
    class WelcomeWidget(QWidget):
        """欢迎页面组件"""
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setStyleSheet("background-color: #f8f9fa;")

            layout = QVBoxLayout(self)
            layout.addStretch(1)

            # 标题
            title = QLabel("Systema V4.7")
            title.setFont(QFont("Microsoft YaHei" if sys.platform.startswith('win') else "Sans Serif", 28, QFont.Weight.Bold))
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)

            # 副标题
            subtitle = QLabel("个人数据 · 任务 · 笔记 一体化管理工具")
            subtitle.setFont(QFont("", 14))
            subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            subtitle.setStyleSheet("color: #666666; margin-bottom: 30px;")
            layout.addWidget(subtitle)

            # 开始按钮
            start_btn = QPushButton("开始使用")
            start_btn.setMinimumHeight(50)
            start_btn.setMinimumWidth(200)
            start_btn.setFont(QFont("", 12, QFont.Weight.Bold))
            start_btn.setStyleSheet("""
                QPushButton { background-color: #5cb85c; color: white; border-radius: 8px; padding: 10px; }
                QPushButton:hover { background-color: #4cae4c; }
            """)
            start_btn.clicked.connect(self.start_app)
            layout.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

            # 版本信息
            version_label = QLabel("版本 4.7 | Qt6 迁移版")
            version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            version_label.setStyleSheet("color: #888888; margin-top: 40px;")
            layout.addWidget(version_label)

            layout.addStretch(1)

        def start_app(self):
            """点击开始使用，切换到主界面"""
            main_window = self.window()
            if isinstance(main_window, PersonalDBGUI):
                main_window.build_ui()  # 直接调用主窗口方法
                main_window.main_stack.setCurrentWidget(main_window.main_container)