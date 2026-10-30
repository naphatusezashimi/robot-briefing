"""
รูปสถานที่/ของฝากสระบุรี — จับชื่อในคำถาม/คำตอบเป็นรายการรูป และสร้างโครงเมนูกดแตกหมวด
ทั้งหมดอ่านจาก saraburi_data.json + ไฟล์รูปใน static/places/ (ไม่เรียก AI)
"""
from pathlib import Path

PLACES_DIR = Path(__file__).resolve().parent / "static" / "places"
MAX_PHOTOS = 3
_REFUSALS = ("ยังไม่มีข้อมูล", "don't have that information")   # ประโยคปฏิเสธตามกฎใน ai.py

_SECTIONS = {   # คีย์ในเมนู → (ส่วนในไฟล์ข้อมูล, ป้ายชื่อ)
    "trips": ("ท่องเที่ยวสระบุรี", {"th": "ที่เที่ยวสระบุรี", "en": "Places to visit"}),
    "souvenirs": ("OTOP_สระบุรี", {"th": "ของฝากสระบุรี", "en": "Souvenirs"}),
}

# ป้ายหมวดแบบสั้นให้พอดีปุ่มบนจอ (หมวดที่ไม่อยู่ในนี้ใช้ชื่อคีย์เดิม)
_CATEGORIES = {
    "น้ำตก": ("น้ำตก", "Waterfalls", "💧"),
    "วัดและสถานที่ศักดิ์สิทธิ์": ("วัด", "Temples", "🛕"),
    "ธรรมชาติและสวน": ("ธรรมชาติ", "Nature", "🌻"),
    "ตลาดและแหล่งช้อป": ("ตลาด", "Markets", "🛒"),
    "ใกล้วิทยาลัย_อำเภอบ้านหมอ": ("ใกล้วิทยาลัย", "Near the college", "📍"),
    "อาหารและขนม": ("อาหาร-ขนม", "Food & snacks", "🍯"),
    "งานหัตถกรรม": ("หัตถกรรม", "Handicrafts", "🧺"),
    "สมุนไพรและสุขภาพ": ("สมุนไพร", "Herbal", "🌿"),
}


def _entries(saraburi_data: dict) -> list[dict]:
    """ทุกรายการจากทั้งสองส่วน ตัดตัวซ้ำ (บางที่อยู่หลายหมวด) ด้วยชื่อไทย"""
    seen, out = set(), []
    for section, _ in _SECTIONS.values():
        for items in (saraburi_data.get(section) or {}).values():
            for e in items:
                if e.get("ชื่อ") and e["ชื่อ"] not in seen:
                    seen.add(e["ชื่อ"])
                    out.append(e)
    return out


def _photo_src(entry: dict, places_dir: Path):
    f = entry.get("รูป")
    return f"/static/places/{f}" if f and (Path(places_dir) / f).is_file() else None


def _name(entry: dict, lang: str) -> str:
    return (lang == "en" and entry.get("ชื่ออังกฤษ")) or entry["ชื่อ"]


def _find(text: str, entries: list[dict]) -> list[dict]:
    """รายการที่ชื่อ (ไทย/อังกฤษ/ชื่อเรียกอื่น) ปรากฏในข้อความ เรียงตามตำแหน่งที่เจอ
    ภาษาไทยไม่มีช่องว่างคั่นคำ จึงจับชื่อยาวก่อน แล้วไม่ให้ชื่อสั้นจับซ้อนในช่วงเดียวกัน"""
    low = text.lower()
    names = []
    for e in entries:
        for n in [e["ชื่อ"], e.get("ชื่ออังกฤษ"), *(e.get("ชื่อเรียกอื่น") or [])]:
            if n:
                names.append((n.lower(), e))
    names.sort(key=lambda x: -len(x[0]))
    taken, hits = [], []   # ช่วงที่ถูกจับแล้ว, (ตำแหน่ง, รายการ)
    for n, e in names:
        start = low.find(n)
        while start >= 0:
            end = start + len(n)
            if not any(start < b and a < end for a, b in taken):
                taken.append((start, end))
                hits.append((start, e))
            start = low.find(n, start + 1)
    out = []
    for _, e in sorted(hits, key=lambda h: h[0]):
        if e not in out:
            out.append(e)
    return out


def photos_for(question: str, answer: str, saraburi_data: dict, lang: str = "th",
               places_dir: Path = PLACES_DIR) -> list[dict]:
    """รูปที่จะต่อท้ายคำตอบ: ชื่อในคำถามก่อน ถ้าไม่มีค่อยใช้ชื่อในคำตอบ — เฉพาะที่มีไฟล์รูปจริง"""
    entries = _entries(saraburi_data)
    found = _find(question, entries)
    # คำตอบที่ปฏิเสธ (ไม่มีข้อมูลที่ถาม) แล้วแนะนำที่อื่น — รูปที่อื่นจะทำให้เข้าใจผิดว่าเป็นที่ที่ถาม
    if not found and not any(r in answer.lower() for r in _REFUSALS):
        found = _find(answer, entries)
    out = []
    for e in found:
        src = _photo_src(e, places_dir)
        if src:
            out.append({"src": src, "name": _name(e, lang), "caption": e.get("อำเภอ", "")})
    return out[:MAX_PHOTOS]


def menu_tree(saraburi_data: dict, places_dir: Path = PLACES_DIR) -> dict:
    """โครงเมนู ที่เที่ยว/ของฝาก → หมวด → รายการ ให้หน้าจอโหลดครั้งเดียว"""
    tree = {}
    for key, (section, label) in _SECTIONS.items():
        cats = []
        for cat, items in (saraburi_data.get(section) or {}).items():
            th, en, icon = _CATEGORIES.get(cat, (cat.replace("_", " "), cat.replace("_", " "), "📌"))
            cats.append({
                "key": cat, "label": {"th": th, "en": en}, "icon": icon,
                "items": [{
                    "name": {"th": e["ชื่อ"], "en": _name(e, "en")},
                    "district": e.get("อำเภอ", ""),
                    "highlight": e.get("จุดเด่น", ""),
                    "photo": _photo_src(e, places_dir),
                } for e in items if e.get("ชื่อ")],
            })
        tree[key] = {"label": label, "categories": cats}
    return tree
