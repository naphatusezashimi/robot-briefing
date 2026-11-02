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


def test_sar_2568_included_without_internal_sections():
    from database import load_sar_text
    sar = load_sar_text()
    assert "คลังคำถาม-คำตอบ (266 ข้อ)" in sar
    assert "Fact Sheet" in sar
    # ส่วนข้อมูลภายในของเอกสารต้นฉบับไม่ส่งให้หุ่น
    assert "จุดที่ควรพัฒนาและแผนปี 2569 (ข้อมูลภายใน)" not in sar
    assert "ข้อความที่ขัดกัน" not in sar
    assert "รายงาน SAR ปีการศึกษา 2568" in format_all_data({}, {})


def test_programs_follow_sar_2568():
    progs = load_college_data()["หลักสูตรที่เปิดสอน"]
    pvc = [k for k in progs["ปวช"] if not k.startswith("_")]
    pvs = [k for k in progs["ปวส"] if not k.startswith("_")]
    assert len(pvc) == 13 and len(pvs) == 13
    assert "ยานยนต์ไฟฟ้า" in pvc and "เมคคาทรอนิกส์และหุ่นยนต์" in pvs
    assert "สาขาวิชาเครื่องมือกลและซ่อมบำรุง" not in progs["ปวช"]   # ชื่อเดิมจากเว็บไซต์
