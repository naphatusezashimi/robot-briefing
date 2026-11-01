"""
ประกาศตามเวลา — อ่านรายการจาก robot/announcements.json (แก้ไฟล์แล้วมีผลเลย ไม่ต้องปิดเปิดเซิร์ฟเวอร์)

รูปแบบไฟล์ (รายการละก้อน):
  {"เวลา": "08:00", "ข้อความ": "ข้อความที่หุ่นจะพูด",
   "ข้อความอังกฤษ": "(ไม่ใส่ก็ได้) ใช้ตอนจอเป็นภาษาอังกฤษ",
   "วัน": "ทุกวัน" | "จันทร์-ศุกร์" | ["เสาร์", "อาทิตย์"]   (ไม่ใส่ = ทุกวัน),
   "เปิด": true   (ใส่ false เพื่อปิดชั่วคราว)}
"""
import json
import re
from pathlib import Path

DAYS = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]   # ตรงกับ datetime.weekday()
_ALIASES = {"พฤหัส": 3}
_TIME = re.compile(r"^\s*(\d{1,2}):(\d{2})\s*$")


def _days(value):
    """แปลงช่อง "วัน" เป็นเซตของเลขวัน (0=จันทร์) คืน None ถ้าเขียนผิด"""
    if value in (None, "", "ทุกวัน"):
        return set(range(7))
    if value == "จันทร์-ศุกร์":
        return set(range(5))
    if value == "เสาร์-อาทิตย์":
        return {5, 6}
    if isinstance(value, str):
        value = [value]
    out = set()
    for d in value if isinstance(value, list) else []:
        d = str(d).strip()
        if d in DAYS:
            out.add(DAYS.index(d))
        elif d in _ALIASES:
            out.add(_ALIASES[d])
        else:
            return None
    return out or None


def load_announcements(path):
    """อ่านไฟล์ประกาศ — รายการที่เขียนผิดจะถูกข้ามพร้อมพิมพ์เตือน (ไม่ทำให้เซิร์ฟเวอร์ล่ม)"""
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []
    except (OSError, ValueError) as e:
        print(f"[announce] ⚠ อ่าน {path} ไม่ได้: {e}", flush=True)
        return []
    items = []
    for i, a in enumerate(raw if isinstance(raw, list) else []):
        if not isinstance(a, dict):
            continue
        m = _TIME.match(str(a.get("เวลา", "")))
        text = str(a.get("ข้อความ", "")).strip()
        days = _days(a.get("วัน"))
        if not m or int(m[1]) > 23 or int(m[2]) > 59 or not text or days is None:
            print(f"[announce] ⚠ ข้ามรายการที่ {i + 1} (เวลา/ข้อความ/วัน เขียนไม่ถูก): {a}", flush=True)
            continue
        items.append({
            "index": i,
            "time": f"{int(m[1]):02d}:{m[2]}",
            "text": text,
            "text_en": str(a.get("ข้อความอังกฤษ", "")).strip(),
            "days": days,
            "enabled": a.get("เปิด", True) is not False,
        })
    return items


def due_announcements(items, now):
    """ประกาศที่ถึงเวลาในนาทีนี้ — id ไม่ซ้ำกันในแต่ละวัน (จอใช้กันพูดซ้ำ)"""
    hhmm, date = now.strftime("%H:%M"), now.strftime("%Y-%m-%d")
    return [
        {"id": f"{date} {a['time']} #{a['index']}", "text": a["text"], "text_en": a["text_en"]}
        for a in items
        if a["enabled"] and a["time"] == hhmm and now.weekday() in a["days"]
    ]
