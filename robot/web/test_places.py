"""
เทสต์ตัวจับคู่รูปสถานที่ + โครงเมนู — ใช้ข้อมูลจำลอง ไม่พึ่งรูปจริง
รันจากโฟลเดอร์ robot/:  & $py -m pytest web/test_places.py -v
"""
import pytest

from places import photos_for, menu_tree

DATA = {
    "ท่องเที่ยวสระบุรี": {
        "น้ำตก": [
            {"ชื่อ": "น้ำตกเจ็ดสาวน้อย", "อำเภอ": "มวกเหล็ก", "จุดเด่น": "น้ำตก 7 ชั้น",
             "รูป": "jedsaonoi.jpg", "ชื่ออังกฤษ": "Jet Sao Noi Waterfall", "ชื่อเรียกอื่น": ["เจ็ดสาวน้อย"]},
            {"ชื่อ": "น้ำตกมวกเหล็ก", "อำเภอ": "มวกเหล็ก", "จุดเด่น": "เย็นสบาย", "รูป": "muaklek.jpg"},
        ],
        "วัดและสถานที่ศักดิ์สิทธิ์": [
            {"ชื่อ": "วัดพระพุทธบาท", "อำเภอ": "พระพุทธบาท", "จุดเด่น": "รอยพระพุทธบาท", "รูป": "buddhabat.jpg"},
        ],
        "ธรรมชาติและสวน": [
            {"ชื่อ": "ไร่กุสุมา", "อำเภอ": "เมืองสระบุรี", "จุดเด่น": "ไร่", "รูป": "kusuma.jpg"},
        ],
        "ตลาดและแหล่งช้อป": [
            {"ชื่อ": "ตลาดท่าน้ำแก่งคอย", "อำเภอ": "แก่งคอย", "จุดเด่น": "ตลาดริมน้ำ", "รูป": "kaengkhoi.jpg"},
        ],
        "ใกล้วิทยาลัย_อำเภอบ้านหมอ": [
            {"ชื่อ": "ตลาดท่าน้ำแก่งคอย", "อำเภอ": "แก่งคอย", "จุดเด่น": "ตลาดริมน้ำ", "รูป": "kaengkhoi.jpg"},
        ],
    },
    "OTOP_สระบุรี": {
        "อาหารและขนม": [
            {"ชื่อ": "หมูทุบไร้มัน", "อำเภอ": "เมืองสระบุรี", "จุดเด่น": "หมูทุบ"},
        ],
    },
}


@pytest.fixture
def DIR(tmp_path):
    # มีไฟล์จริงทุกรูป ยกเว้น kusuma.jpg (ทดสอบกรณี JSON อ้างรูปที่ไม่มีไฟล์)
    for name in ("jedsaonoi.jpg", "muaklek.jpg", "buddhabat.jpg", "kaengkhoi.jpg"):
        (tmp_path / name).write_bytes(b"")
    return tmp_path


def test_name_in_question_gives_that_photo_only(DIR):
    p = photos_for("น้ำตกเจ็ดสาวน้อยไปยังไง", "มีน้ำตกมวกเหล็กด้วยนะ", DATA, places_dir=DIR)
    assert [x["src"] for x in p] == ["/static/places/jedsaonoi.jpg"]


def test_alias_matches(DIR):
    assert photos_for("เจ็ดสาวน้อยสวยไหม", "", DATA, places_dir=DIR)[0]["name"] == "น้ำตกเจ็ดสาวน้อย"


def test_broad_question_uses_answer_order_max_three(DIR):
    ans = "แนะนำ วัดพระพุทธบาท ตลาดท่าน้ำแก่งคอย น้ำตกมวกเหล็ก และ น้ำตกเจ็ดสาวน้อย"
    p = photos_for("สระบุรีมีที่เที่ยวที่ไหนบ้าง", ans, DATA, places_dir=DIR)
    assert [x["name"] for x in p] == ["วัดพระพุทธบาท", "ตลาดท่าน้ำแก่งคอย", "น้ำตกมวกเหล็ก"]


def test_no_names_gives_empty(DIR):
    assert photos_for("เปิดสอนสาขาอะไรบ้าง", "มีช่างยนต์ ช่างไฟฟ้า", DATA, places_dir=DIR) == []


def test_missing_file_not_returned(DIR):
    assert photos_for("ไร่กุสุมาเป็นยังไง", "", DATA, places_dir=DIR) == []


def test_district_name_does_not_match_place(DIR):
    assert photos_for("อำเภอมวกเหล็กมีอะไรบ้าง", "", DATA, places_dir=DIR) == []
    assert photos_for("อำเภอพระพุทธบาทอยู่ไหน", "", DATA, places_dir=DIR) == []


def test_duplicate_entry_appears_once(DIR):
    p = photos_for("ตลาดท่าน้ำแก่งคอย ตลาดท่าน้ำแก่งคอย", "", DATA, places_dir=DIR)
    assert len(p) == 1


def test_english_answer_case_insensitive_and_caption_lang(DIR):
    p = photos_for("Where to visit?", "Try JET SAO NOI waterfall!", DATA, lang="en", places_dir=DIR)
    assert p[0]["name"] == "Jet Sao Noi Waterfall"
    assert photos_for("น้ำตกเจ็ดสาวน้อย", "", DATA, lang="th", places_dir=DIR)[0]["caption"] == "มวกเหล็ก"


def test_menu_tree_shape(DIR):
    m = menu_tree(DATA, places_dir=DIR)
    assert set(m) == {"trips", "souvenirs"}
    assert [c["key"] for c in m["trips"]["categories"]] == list(DATA["ท่องเที่ยวสระบุรี"])
    item = m["trips"]["categories"][0]["items"][0]
    assert item["name"] == {"th": "น้ำตกเจ็ดสาวน้อย", "en": "Jet Sao Noi Waterfall"}
    assert item["photo"] == "/static/places/jedsaonoi.jpg"
    otop = m["souvenirs"]["categories"][0]["items"][0]
    assert otop["photo"] is None and otop["name"]["en"] == "หมูทุบไร้มัน"   # ไม่มีชื่ออังกฤษ → ไทย


def test_menu_tree_empty_data(DIR):
    assert menu_tree({}, places_dir=DIR) == {
        "trips": {"label": {"th": "ที่เที่ยวสระบุรี", "en": "Places to visit"}, "categories": []},
        "souvenirs": {"label": {"th": "ของฝากสระบุรี", "en": "Souvenirs"}, "categories": []}}
