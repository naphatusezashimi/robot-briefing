"""
เทสต์ข้อมูลสระบุรี — database layer
รันจากโฟลเดอร์ robot/:  python -m pytest test_saraburi.py -v
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database import load_saraburi_data, format_all_data


def test_load_saraburi_data_returns_dict():
    data = load_saraburi_data()
    assert isinstance(data, dict)
    assert "ท่องเที่ยวสระบุรี" in data
    assert "OTOP_สระบุรี" in data


def test_load_saraburi_data_missing_file_returns_empty(tmp_path, monkeypatch):
    import config
    monkeypatch.setattr(config, "SARABURI_DATA_PATH", str(tmp_path / "nonexistent.json"))
    data = load_saraburi_data()
    assert data == {}


def test_format_all_data_includes_both_sources():
    college = {"ชื่อสถานศึกษา": "วิทยาลัยทดสอบ"}
    saraburi = {"ท่องเที่ยวสระบุรี": {"น้ำตก": []}}
    result = format_all_data(college, saraburi)
    assert "ข้อมูลวิทยาลัย" in result
    assert "ข้อมูลจังหวัดสระบุรี" in result
    assert "วิทยาลัยทดสอบ" in result
    assert "ท่องเที่ยวสระบุรี" in result


def test_format_all_data_empty_saraburi_omits_saraburi_section():
    college = {"ชื่อสถานศึกษา": "วิทยาลัยทดสอบ"}
    result = format_all_data(college, {})
    assert "ข้อมูลวิทยาลัย" in result
    assert "ข้อมูลจังหวัดสระบุรี" not in result
from unittest.mock import patch


def test_ask_ai_passes_saraburi_data_to_system_prompt(monkeypatch):
    """ตรวจว่า ask_ai ส่งข้อมูลทั้งสองเข้า system prompt"""
    import ai
    college = {"ชื่อสถานศึกษา": "ทดสอบ"}
    saraburi = {"ท่องเที่ยวสระบุรี": {}}
    captured = {}

    def fake_ask_gemini(question, c_data, s_data, lang="th"):
        captured["college"] = c_data
        captured["saraburi"] = s_data
        return "ตอบ"

    monkeypatch.setattr(ai, "_ask_gemini", fake_ask_gemini)
    monkeypatch.setattr(ai, "AI_PROVIDER", "gemini")
    ai.ask_ai("ถามอะไร", college, saraburi)
    assert captured["college"] == college
    assert captured["saraburi"] == saraburi


def test_english_mode_adds_english_rule_only_when_chosen():
    import ai
    assert "English" in ai._rules("en")
    assert ai._rules("th") == ai._SYSTEM_RULES
    assert "English" in ai._system_text({}, {}, "en")


# ---------- รูปสถานที่ ----------
import os
import re

PLACES = Path(__file__).parent / "web" / "static" / "places"


def _all_entries():
    data = load_saraburi_data()
    for section in ("ท่องเที่ยวสระบุรี", "OTOP_สระบุรี"):
        for items in data.get(section, {}).values():
            yield from items


def test_every_photo_field_has_file():
    photos = [e["รูป"] for e in _all_entries() if "รูป" in e]
    assert photos, "ยังไม่มีรายการไหนมีรูป"
    for f in photos:
        assert (PLACES / f).is_file(), f


def test_every_photo_file_has_credit():
    files = sorted(p.name for p in PLACES.glob("*.jpg"))
    assert files, "ยังไม่มีไฟล์รูปใน places/"
    credits = (PLACES / "CREDITS.md").read_text(encoding="utf-8")
    for f in files:
        assert f in credits, f"{f} ไม่มีเครดิต"


def test_photo_files_small_enough():
    from PIL import Image
    for p in PLACES.glob("*.jpg"):
        with Image.open(p) as im:
            assert im.width <= 1024, p.name
        assert os.path.getsize(p) <= 260_000, p.name


def test_aliases_never_equal_a_district():
    entries = list(_all_entries())
    districts = {e.get("อำเภอ") for e in entries}
    for e in entries:
        for a in e.get("ชื่อเรียกอื่น", []):
            assert a.strip(), e["ชื่อ"]
            assert a not in districts and f"อำเภอ{a}" not in districts, f"{e['ชื่อ']}: {a}"


def test_same_name_same_photo():
    seen = {}
    for e in _all_entries():
        assert seen.setdefault(e["ชื่อ"], e.get("รูป")) == e.get("รูป"), e["ชื่อ"]


def test_prompt_has_no_photo_filenames():
    text = format_all_data({}, load_saraburi_data())
    assert not re.search(r"\.jpe?g", text)
    assert "น้ำตกเจ็ดสาวน้อย" in text
