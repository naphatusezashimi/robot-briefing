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

    def fake_ask_gemini(question, c_data, s_data):
        captured["college"] = c_data
        captured["saraburi"] = s_data
        return "ตอบ"

    monkeypatch.setattr(ai, "_ask_gemini", fake_ask_gemini)
    monkeypatch.setattr(ai, "AI_PROVIDER", "gemini")
    ai.ask_ai("ถามอะไร", college, saraburi)
    assert captured["college"] == college
    assert captured["saraburi"] == saraburi
