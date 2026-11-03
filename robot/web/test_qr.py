"""
เทสต์สแกน QR — รันจากโฟลเดอร์ robot/:  & $py -m pytest web/test_qr.py -v
"""
import json
from pathlib import Path

from qr import load_qr_codes, resolve

ROBOT_DIR = Path(__file__).resolve().parent.parent


def write(tmp_path, data):
    p = tmp_path / "qr.json"
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return p


def test_missing_file_is_empty(tmp_path):
    assert load_qr_codes(tmp_path / "nope.json") == {}


def test_broken_json_is_empty(tmp_path):
    p = tmp_path / "qr.json"
    p.write_text("{ไม่ใช่ json", encoding="utf-8")
    assert load_qr_codes(p) == {}


def test_question_and_answer_entries(tmp_path):
    codes = load_qr_codes(write(tmp_path, {
        "_คำอธิบาย": "ข้าม",
        "TL-A": {"ชื่อ": "ห้อง A", "คำถาม": "ห้อง A อยู่ไหน", "คำถามอังกฤษ": "Where is room A?"},
        "TL-B": {"คำตอบ": "สวัสดี"},
        "TL-OFF": {"คำตอบ": "x", "เปิด": False},
        "TL-BAD": {"ชื่อ": "ไม่มีอะไร"},
        "TL-NOTDICT": "x",
    }))
    assert set(codes) == {"TL-A", "TL-B"}
    assert resolve("TL-A", codes) == {"label": "ห้อง A", "question": "ห้อง A อยู่ไหน"}
    assert resolve("TL-A", codes, "en") == {"label": "ห้อง A", "question": "Where is room A?"}
    assert resolve("TL-B", codes) == {"label": "TL-B", "answer": "สวัสดี"}
    assert resolve("TL-B", codes, "en") == {"label": "TL-B", "answer": "สวัสดี"}   # ไม่มีอังกฤษ → ไทย


def test_code_match_ignores_case_and_spaces(tmp_path):
    codes = load_qr_codes(write(tmp_path, {"tl-a": {"คำตอบ": "ok"}}))
    assert resolve("  TL-A\n", codes)["answer"] == "ok"
    assert resolve("tl-a", codes)["answer"] == "ok"


def test_unknown_code_is_none(tmp_path):
    assert resolve("TL-NONE", load_qr_codes(write(tmp_path, {}))) is None
    assert resolve("", {}) is None


def test_fixed_answer_wins_over_question(tmp_path):
    codes = load_qr_codes(write(tmp_path, {"X": {"คำถาม": "q", "คำตอบ": "a"}}))
    assert resolve("X", codes) == {"label": "X", "answer": "a"}


def test_real_file_is_valid():
    raw = json.loads((ROBOT_DIR / "qr_codes.json").read_text(encoding="utf-8"))
    codes = load_qr_codes(ROBOT_DIR / "qr_codes.json")
    assert len(codes) == len([k for k in raw if not k.startswith("_")])
    for code in codes:
        assert code.isascii(), f"{code}: รหัสต้องเป็นภาษาอังกฤษ/ตัวเลข (เครื่องสแกนพิมพ์ไทยเพี้ยน)"
