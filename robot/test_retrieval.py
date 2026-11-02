"""RAG แบบง่าย: ส่ง SAR ให้ AI เฉพาะส่วนที่เกี่ยวกับคำถาม"""
import pathlib

import config
import retrieval
from database import format_all_data

MD = pathlib.Path(config.SAR_DATA_PATH).read_text(encoding="utf-8")


def test_split_keeps_every_qa_item():
    chunks = retrieval.split_chunks(MD)
    qa = [c for c in chunks if retrieval._QA.search(c["text"].split("\n")[1] if "\n" in c["text"] else "")]
    assert len(qa) >= 266


def test_select_is_small_and_relevant():
    s = retrieval.select(MD, "ผู้อำนวยการชื่ออะไร", budget=9000)
    assert len(s) <= 9000 and "เฉลิมชนม์" in s
    s = retrieval.select(MD, "มีสาขายานยนต์ไฟฟ้าไหม")
    assert "ยานยนต์ไฟฟ้า" in s and "Fact Sheet" in s


def test_english_question_gets_main_sections():
    s = retrieval.select(MD, "What programs do you offer?")
    assert "ระดับ ปวช." in s and "Fact Sheet" in s


def test_prompt_with_question_is_much_shorter():
    full = format_all_data({}, {})
    rag = format_all_data({}, {}, question="ค่าเทอมเท่าไหร่")
    assert len(rag) < len(full) / 4
    assert "ข้อความที่ขัดกัน" not in rag   # ส่วนข้อมูลภายในยังไม่หลุดมา
