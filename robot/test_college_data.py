"""
เทสต์ข้อมูลวิทยาลัย — ผู้บริหารสถานศึกษา
รันจากโฟลเดอร์ robot/:  python -m pytest test_college_data.py -v
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database import load_college_data, format_all_data


def test_college_data_has_director_name():
    data = load_college_data()
    assert data["ผู้บริหารสถานศึกษา"]["ผู้อำนวยการ"]["ชื่อ"] == "นายเฉลิมชนม์ เวทสรากุล"
    assert len(data["ผู้บริหารสถานศึกษา"]["รองผู้อำนวยการ"]) == 4


def test_director_name_reaches_ai_prompt():
    result = format_all_data(load_college_data(), {})
    assert "นายเฉลิมชนม์ เวทสรากุล" in result
