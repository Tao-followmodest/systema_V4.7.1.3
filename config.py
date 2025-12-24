# 全局常量、路径定义（DATA_DIR、文件路径、天干地支等）

# config.py
"""
Systema 全局配置与常量定义
包含数据目录、文件路径、最大数量、天干地支等
"""

from pathlib import Path
import sys

# ===================== 数据存储相关 =====================
DATA_DIR = Path("data")
SCENES_FILE = DATA_DIR / "scenes.json"      # 场景字段定义
FLAGS_FILE = DATA_DIR / "flags.json"        # Flag 任务数据
NOTES_FILE = DATA_DIR / "notes.json"        # 便签笔记数据（你之前用 sticky_notes.json，这里统一改成 notes.json）

# 每个场景的独立数据文件目录（CSV）
TABLES_DIR = DATA_DIR / "tables"

# 最大数量限制
MAX_SCENES = 6
MAX_FLAGS = 6
MAX_NOTES = 10

# ===================== 天干地支（用于默认名称） =====================
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI_SCENE = ["子", "丑", "寅", "卯", "辰", "巳"]      # Mode 0 场景默认名称
DIZHI_FLAG = ["午", "未", "申", "酉", "戌", "亥"]       # Mode 1 Flag 默认名称

# ===================== PyQt6 相关 =====================
PYQT6_AVAILABLE = False
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtGui import QFont
    PYQT6_AVAILABLE = True
except ImportError:
    pass

# ===================== 工具函数（可选放这里或移到 data_utils） =====================
def ensure_data_dir():
    """确保 data 目录及其子目录存在"""
    DATA_DIR.mkdir(exist_ok=True)
    TABLES_DIR.mkdir(exist_ok=True)

# ===================== 字体设置（全局） =====================
def get_default_font():
    """返回适合当前平台的默认字体"""
    if sys.platform.startswith('win'):
        return QFont("Microsoft YaHei", 9)
    else:
        return QFont("Sans Serif", 10)