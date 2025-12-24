# 数据读写核心逻辑（load/save scenes/flags/notes/records 等）

# data_utils.py
"""
数据持久化核心工具
负责 scenes.json / flags.json / notes.json / 各个场景 CSV 的读写
"""

import json
from pathlib import Path
import csv
from datetime import datetime

from config import (
    DATA_DIR, SCENES_FILE, FLAGS_FILE, NOTES_FILE, TABLES_DIR,
    MAX_SCENES, MAX_FLAGS, MAX_NOTES,
    DIZHI_SCENE, DIZHI_FLAG, ensure_data_dir
)

# ===================== 通用工具 =====================
def get_scene_data_file(scene_name: str) -> Path:
    """获取指定场景的 CSV 数据文件路径"""
    return TABLES_DIR / f"{scene_name}.csv"

# ===================== Scenes (Mode 0 数据表格) =====================
def load_scenes():
    """
    加载 scenes.json，兼容旧版默认名称
    - 增加 try-except 和空文件处理，防止崩溃
    """
    scenes = {}
    raw_data = {}

    if SCENES_FILE.exists():
        try:
            with open(SCENES_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    raw_data = {}  # 空文件
                else:
                    raw_data = json.loads(content)
        except json.JSONDecodeError:
            print(f"警告: scenes.json 格式错误，已使用默认数据")
            raw_data = {}
        except Exception as e:
            print(f"加载 scenes.json 失败: {e}")
            raw_data = {}
    else:
        raw_data = {}

    # 兼容旧版未命名场景 → 地支命名
    temp_scenes = {}
    for i in range(MAX_SCENES):
        new_key = DIZHI_SCENE[i]
        old_default_key = f"未命名{i}"
        if new_key in raw_data:
            temp_scenes[new_key] = raw_data.pop(new_key)
        elif old_default_key in raw_data:
            temp_scenes[new_key] = raw_data.pop(old_default_key)
        else:
            temp_scenes[new_key] = ["标签1"]  # 默认一个标签

    # 剩余自定义场景
    for key, fields in raw_data.items():
        if key not in temp_scenes:
            temp_scenes[key] = fields

    # 排序：先固定地支顺序，再自定义
    final_scenes = {}
    for name in DIZHI_SCENE:
        if name in temp_scenes:
            final_scenes[name] = temp_scenes.pop(name)
    final_scenes.update(temp_scenes)  # 剩余自定义的

    # 限制最大数量
    return dict(list(final_scenes.items())[:MAX_SCENES])

def save_scenes(scenes):
    """保存 scenes.json"""
    with open(SCENES_FILE, "w", encoding="utf-8") as f:
        json.dump(scenes, f, ensure_ascii=False, indent=2)

def load_records(scene_name: str, fields: list) -> list:
    """加载指定场景的 CSV 数据记录"""
    path = get_scene_data_file(scene_name)
    records = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
    return records

def save_records(scene_name: str, fields: list, records: list):
    """保存指定场景的 CSV 数据"""
    path = get_scene_data_file(scene_name)
    with open(path, "w", encoding="utf-8", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)

# ===================== Flags (Mode 1 Flag 任务) =====================
def load_flags():
    """加载 flags.json，兼容旧版默认名称"""
    ensure_data_dir()
    flags = []
    if FLAGS_FILE.exists():
        try:
            with open(FLAGS_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    data = []  # 空文件
                else:
                    data = json.loads(content)
        except json.JSONDecodeError:
            print(f"警告: flags.json 格式错误，已使用默认数据")
            data = []
        except Exception as e:
            print(f"加载 flags.json 失败: {e}")
            data = []
    else:
        data = []

    # 补全到 MAX_FLAGS 个 Flag
    for i in range(MAX_FLAGS):
        item = data[i] if i < len(data) else {}
        default_name = DIZHI_FLAG[i]
        if "name" not in item or item["name"].startswith("Flag"):
            item["name"] = default_name
        # 默认字段...
        item.setdefault("target_time", "")
        item.setdefault("start_time", "")
        item.setdefault("content", "")
        item.setdefault("status", "active")
        item.setdefault("finished_at", "")
        item.setdefault("discarded_at", "")
        item.setdefault("span_seconds", 0)
        item.setdefault("running", False)
        item.setdefault("paused", False)
        item.setdefault("paused_duration", 0)
        item.setdefault("pause_start_time", None)
        flags.append(item)

    # 如果不足 MAX_FLAGS，补齐默认
    while len(flags) < MAX_FLAGS:
        flags.append({
            "name": DIZHI_FLAG[len(flags)],
            "target_time": "", "start_time": "", "content": "",
            "status": "active", "finished_at": "", "discarded_at": "",
            "span_seconds": 0, "running": False, "paused": False,
            "paused_duration": 0, "pause_start_time": None
        })

    return flags

def save_flags(flags):
    """保存 flags.json"""
    with open(FLAGS_FILE, "w", encoding="utf-8") as f:
        json.dump(flags, f, ensure_ascii=False, indent=2)

# ===================== Notes (Mode 2 便签笔记) =====================
def load_notes():
    """加载 notes.json，兼容旧版 sticky_notes.json"""
    ensure_data_dir()
    notes = []
    if NOTES_FILE.exists():
        try:
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    data = []  # 空文件
                else:
                    data = json.loads(content)
        except json.JSONDecodeError:
            print(f"警告: notes.json 格式错误，已使用默认数据")
            data = []
        except Exception as e:
            print(f"加载 notes.json 失败: {e}")
            data = []
    else:
        data = []

    # 补全到 MAX_NOTES 个 Note
    for i in range(MAX_NOTES):
        item = data[i] if i < len(data) else {}
        default_label = f"便签{i+1}"
        item.setdefault("display_name", default_label)
        item.setdefault("title", "")
        item.setdefault("content", "")
        item.setdefault("status", "active")
        item.setdefault("created_at", datetime.now().isoformat())
        item.setdefault("updated_at", datetime.now().isoformat())
        item.setdefault("finished_at", "")
        item.setdefault("discarded_at", "")
        notes.append(item)

    # 如果不足 MAX_NOTES，补齐默认
    while len(notes) < MAX_NOTES:
        i = len(notes)
        notes.append({
            "display_name": f"便签{i+1}",
            "title": "",
            "content": "",
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "finished_at": "",
            "discarded_at": ""
        })

    return notes

def save_notes(notes):
    """保存 notes.json"""
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)