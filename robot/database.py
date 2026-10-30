import json
from pathlib import Path

import config
from config import COLLEGE_DATA_PATH


def load_college_data() -> dict:
    with open(COLLEGE_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_saraburi_data() -> dict:
    # อ่าน path ตอนเรียก (ไม่ผูกตอน import) — ไม่มีไฟล์ก็คืน {} ให้ระบบรันต่อได้
    path = Path(config.SARABURI_DATA_PATH)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_for_prompt(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def _without_photos(data):
    """สำเนาข้อมูลที่ตัดฟิลด์ "รูป" ออก — ชื่อไฟล์รูปมีไว้ให้หน้าจอ AI ไม่ต้องรู้"""
    if isinstance(data, dict):
        return {k: _without_photos(v) for k, v in data.items() if k != "รูป"}
    if isinstance(data, list):
        return [_without_photos(v) for v in data]
    return data


def format_all_data(college_data: dict, saraburi_data: dict) -> str:
    parts = ["ข้อมูลวิทยาลัย:\n" + format_for_prompt(college_data)]
    if saraburi_data:
        parts.append("ข้อมูลจังหวัดสระบุรี:\n" + format_for_prompt(_without_photos(saraburi_data)))
    return "\n\n".join(parts)
