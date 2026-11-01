"""
เทสต์ประกาศตามเวลา
รันจากโฟลเดอร์ robot/:  python -m pytest web/test_announce.py -v
"""
import json
from datetime import datetime

from announce import load_announcements, due_announcements

MON_8 = datetime(2026, 11, 2, 8, 0, 30)    # จันทร์ 08:00
SAT_8 = datetime(2026, 11, 7, 8, 0, 10)    # เสาร์ 08:00


def write(tmp_path, items):
    p = tmp_path / "announcements.json"
    p.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
    return p


def test_missing_file_means_no_announcements(tmp_path):
    assert load_announcements(tmp_path / "nope.json") == []


def test_broken_json_means_no_announcements(tmp_path):
    p = tmp_path / "announcements.json"
    p.write_text("{ไม่ใช่ json", encoding="utf-8")
    assert load_announcements(p) == []


def test_bad_entries_skipped(tmp_path):
    p = write(tmp_path, [
        {"เวลา": "8:00", "ข้อความ": "ok"},          # 8:00 ก็ใช้ได้
        {"เวลา": "25:00", "ข้อความ": "เวลาผิด"},
        {"เวลา": "09:00"},                           # ไม่มีข้อความ
        "ไม่ใช่ object",
    ])
    items = load_announcements(p)
    assert [a["time"] for a in items] == ["08:00"]


def test_due_at_matching_minute(tmp_path):
    items = load_announcements(write(tmp_path, [
        {"เวลา": "08:00", "ข้อความ": "สวัสดีตอนเช้า", "ข้อความอังกฤษ": "Good morning"},
        {"เวลา": "12:00", "ข้อความ": "พักเที่ยง"},
    ]))
    due = due_announcements(items, MON_8)
    assert len(due) == 1
    assert due[0]["text"] == "สวัสดีตอนเช้า"
    assert due[0]["text_en"] == "Good morning"
    assert due[0]["id"] == "2026-11-02 08:00 #0"
    assert due_announcements(items, datetime(2026, 11, 2, 8, 1)) == []


def test_weekdays_only(tmp_path):
    items = load_announcements(write(tmp_path, [{"เวลา": "08:00", "ข้อความ": "เข้าแถว", "วัน": "จันทร์-ศุกร์"}]))
    assert len(due_announcements(items, MON_8)) == 1
    assert due_announcements(items, SAT_8) == []


def test_day_list(tmp_path):
    items = load_announcements(write(tmp_path, [{"เวลา": "08:00", "ข้อความ": "x", "วัน": ["เสาร์", "อาทิตย์"]}]))
    assert due_announcements(items, MON_8) == []
    assert len(due_announcements(items, SAT_8)) == 1


def test_disabled_entry(tmp_path):
    items = load_announcements(write(tmp_path, [{"เวลา": "08:00", "ข้อความ": "x", "เปิด": False}]))
    assert due_announcements(items, MON_8) == []
