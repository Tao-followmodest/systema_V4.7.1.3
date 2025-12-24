# 时间处理工具（format_datetime、format_timedelta 等）

# time_utils.py
"""
时间处理工具函数
包括格式化显示、时间差计算、跨度转换等
"""

from datetime import datetime, timedelta

def format_datetime(iso_str: str) -> str:
    """将 ISO 格式字符串转换为友好显示（无秒则省略）"""
    if not iso_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(iso_str)
        if dt.second == 0:
            return dt.strftime("%Y-%m-%d %H:%M")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return iso_str

def format_timedelta(td: timedelta) -> str:
    """将 timedelta 转换为友好字符串（天/小时/分钟/秒）"""
    if td.total_seconds() < 0:
        return "0秒"
    total_seconds = int(td.total_seconds())
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    parts = []
    if days: parts.append(f"{days}天")
    if hours: parts.append(f"{hours}小时")
    if minutes: parts.append(f"{minutes}分")
    if seconds: parts.append(f"{seconds}秒")
    return " ".join(parts) if parts else "0秒"

def seconds_to_span_str(seconds: int) -> str:
    """将总秒数转换为跨度字符串（天/小时/分钟/秒）"""
    return format_timedelta(timedelta(seconds=seconds))

def calculate_span_seconds(start_iso: str, target_iso: str) -> int:
    """计算起始到截止的总秒数"""
    if not start_iso or not target_iso:
        return 0
    try:
        start = datetime.fromisoformat(start_iso)
        target = datetime.fromisoformat(target_iso)
        if target <= start:
            return 0
        return int((target - start).total_seconds())
    except:
        return 0