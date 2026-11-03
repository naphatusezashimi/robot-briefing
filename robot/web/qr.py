"""
สแกน QR — แปลงรหัสที่เครื่องสแกนอ่านได้ เป็นสิ่งที่หุ่นจะตอบ
อ่านจาก robot/qr_codes.json (แก้ไฟล์แล้วมีผลเลย ไม่ต้องปิดเปิดเซิร์ฟเวอร์)

รูปแบบไฟล์: {"รหัสใน QR": {...}, ...}  — รหัสควรเป็นภาษาอังกฤษ/ตัวเลข เช่น "TL-ROOM-301"
  แต่ละรหัสใส่อย่างใดอย่างหนึ่ง:
  "คำถาม": "ส่งให้ AI ตอบเหมือนคนถามเอง (ได้รูปสถานที่/แผนผังด้วย)"   + "คำถามอังกฤษ" (ไม่ใส่ก็ได้)
  "คำตอบ": "ข้อความตายตัว หุ่นพูดเลยไม่ต้องใช้ AI/เน็ต"               + "คำตอบอังกฤษ" (ไม่ใส่ก็ได้)
  "ชื่อ": "(ไม่ใส่ก็ได้) ป้ายที่โชว์ในแชตแทนรหัส เช่น ห้อง 301"
  "เปิด": true   (ใส่ false เพื่อปิดชั่วคราว)
"""
import json
from pathlib import Path


def _norm(code) -> str:
    """เครื่องสแกนบางรุ่นส่งตัวพิมพ์เล็ก/ใหญ่ไม่ตรง หรือมีช่องว่างติดมา — เทียบแบบไม่สนพวกนี้"""
    return str(code or "").strip().upper()


def load_qr_codes(path) -> dict:
    """อ่านไฟล์รหัส QR → {รหัสที่ normalize แล้ว: รายการ} — รายการที่เขียนผิดข้ามพร้อมพิมพ์เตือน"""
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except (OSError, ValueError) as e:
        print(f"[qr] ⚠ อ่าน {path} ไม่ได้: {e}", flush=True)
        return {}
    out = {}
    for code, e in (raw.items() if isinstance(raw, dict) else []):
        if str(code).startswith("_") or not isinstance(e, dict) or e.get("เปิด", True) is False:
            continue   # คีย์ขึ้นต้น _ = คำอธิบาย
        q, a = str(e.get("คำถาม", "")).strip(), str(e.get("คำตอบ", "")).strip()
        if not _norm(code) or not (q or a):
            print(f"[qr] ⚠ ข้ามรหัส {code!r} (ต้องมี คำถาม หรือ คำตอบ)", flush=True)
            continue
        out[_norm(code)] = {
            "label": str(e.get("ชื่อ", "")).strip(),
            "question": q, "question_en": str(e.get("คำถามอังกฤษ", "")).strip(),
            "answer": a, "answer_en": str(e.get("คำตอบอังกฤษ", "")).strip(),
        }
    return out


def resolve(code, codes: dict, lang: str = "th"):
    """รหัส → {"label", "question"} หรือ {"label", "answer"} ; ไม่รู้จัก → None
    ถ้ามีทั้งคำตอบตายตัวและคำถาม ใช้คำตอบตายตัว (เร็ว ไม่เปลืองโควตา)"""
    e = codes.get(_norm(code))
    if not e:
        return None
    en = lang == "en"
    label = e["label"] or _norm(code)
    if e["answer"]:
        return {"label": label, "answer": (en and e["answer_en"]) or e["answer"]}
    return {"label": label, "question": (en and e["question_en"]) or e["question"]}
