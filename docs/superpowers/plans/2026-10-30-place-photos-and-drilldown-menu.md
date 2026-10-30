# Place Photos + Drill-down Menu Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ให้คำตอบเรื่องที่เที่ยว/ของฝากสระบุรีมีรูปสถานที่ต่อท้าย และให้ปุ่ม 🏞️/🛍️ เปิดเมนูกดแตกหมวด (หมวด → รายชื่อ → การ์ดรายละเอียด) โดยไม่เรียก AI เพิ่ม

**Architecture:** โมดูลใหม่ `robot/web/places.py` อ่าน `saraburi_data.json` แล้วทำ 2 อย่าง: `photos_for()` จับชื่อสถานที่ในคำถาม/คำตอบเป็นรายการรูป และ `menu_tree()` สร้างโครงเมนู เซิร์ฟเวอร์เติม `photos` ใน `/ask` และบรรทัดจบของ `/ask/stream` และเพิ่ม `GET /menu` หน้าจอ `screen.js` โหลด `/menu` ครั้งเดียวแล้ววาดเมนูเป็นข้อความของหุ่นในแชท รูปเป็นไฟล์ในเครื่องที่ `robot/web/static/places/` หามาจาก Wikimedia Commons

**Tech Stack:** Python · Flask · pytest · Pillow 13 (ย่อรูป) · HTML/JS/CSS ล้วน

**Spec:** `docs/superpowers/specs/2026-10-30-place-photos-and-drilldown-menu-design.md`

## Global Constraints

- Python: `& "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe"` ตั้ง `$env:PYTHONUTF8=1` ก่อนรัน (ไม่มี `python` ใน PATH)
- รันเทสต์ทั้งหมดจาก `robot/`: `python -m pytest -q` ตอนเริ่มผ่าน 37 ข้อ ทุกข้อเดิมต้องยังผ่าน
- ห้ามแตะกฎกันตอบมั่วใน `ai.py` และไม่เพิ่มจำนวนครั้งที่เรียก AI: ถาม 1 ครั้ง = เรียก AI 1 ครั้ง, กดเมนู = 0 ครั้ง
- ไม่ดึงรูปจากเน็ตตอนรันจริง ไม่ให้ AI สร้างหรือดูรูป
- รูปไม่ตรงสถานที่ = พัง ถ้าไม่แน่ใจว่าเป็นรูปของที่นั้นจริง ไม่ใส่รูป
- รูป: เฉพาะ CC0 / CC BY / CC BY-SA / Public Domain, JPEG กว้าง ≤ 1024px, ไฟล์ละ ≤ ~250KB, เครดิตใน `robot/web/static/places/CREDITS.md`
- ฟิลด์ใหม่ใน JSON (`รูป`, `ชื่ออังกฤษ`, `ชื่อเรียกอื่น`) ไม่บังคับทุกตัว รายการที่ไม่มีต้องใช้งานได้
- คำถามเรื่องวิทยาลัยต้องไม่มีรูปที่เที่ยว และ `wants_map` + แผนผังเดิมทำงานเหมือนเดิม
- ปุ่มบนจอสัมผัสสูงอย่างน้อย 48px, เข้ากับโทนมืด/สว่างเดิม, รองรับ TH/EN (ไม่มีชื่ออังกฤษ → แสดงชื่อไทย; `จุดเด่น` มีแต่ภาษาไทย แสดงไทยทั้งสองโหมด)
- ทดสอบหน้าจอห้ามเรียก Gemini จริง (โควตา 20/วัน) ให้ override `fetch` ในหน้า
- commit ข้อความไทยด้วย `git commit -F <ไฟล์ UTF-8>` ทำบน branch `feat/place-photos-menu`

## Review Focus

1. **ชื่อซ้อนกัน / ชื่ออำเภอ:** ถาม "อำเภอมวกเหล็กมีอะไรเที่ยว" ต้องไม่ได้รูปน้ำตกมวกเหล็ก, ถาม "อำเภอพระพุทธบาท" ต้องไม่ได้รูปวัดพระพุทธบาท แต่ "น้ำตกมวกเหล็ก" ต้องได้ → เทสต์ใน Task 1 + เทสต์ข้อมูลใน Task 3 (ชื่อเรียกอื่นห้ามซ้ำชื่ออำเภอ)
2. **รายการซ้ำข้ามหมวด:** `ตลาดท่าน้ำแก่งคอย` และ `วัดถ้ำพระโพธิสัตว์` อยู่ 2 หมวด ต้องได้รูปเดียว ไม่ซ้ำในผลลัพธ์ และใช้ไฟล์รูปเดียวกัน → เทสต์ใน Task 1 + Task 3
3. **คำตอบภาษาอังกฤษ:** AI ตอบ "Jet Sao Noi Waterfall" ตัวพิมพ์ต่างจากข้อมูล ต้องยังจับได้ (ไม่สนตัวพิมพ์) และ caption ใช้ชื่ออังกฤษ → เทสต์ใน Task 1
4. **`/menu` โหลดไม่ได้ / ไม่มีข้อมูลสระบุรี:** ปุ่ม 🏞️/🛍️ ต้องกลับไปถาม AI แบบเดิม ไม่ใช่กดแล้วเงียบ, `/menu` ตอนข้อมูลว่างต้องคืนโครงที่มีหมวดว่าง ไม่ 500 → เทสต์ใน Task 2 + ตรวจใน Task 4
5. **กดเมนูระหว่างหุ่นกำลังตอบ:** ต้องถูกกันเหมือนชิปอื่น (`busy()`) ไม่ให้การ์ดแทรกกลางคำตอบที่กำลังไหล และกดเมนูต้องไม่เปลี่ยนสถานะจอหน้า → ตรวจใน Task 4

---

### Task 1: โมดูลจับคู่รูป + โครงเมนู (`places.py`)

**Files:**
- Create: `robot/web/places.py`
- Test: `robot/web/test_places.py`

**Interfaces:**
- Consumes: โครง `saraburi_data.json` เดิม: `{"ท่องเที่ยวสระบุรี": {หมวด: [รายการ]}, "OTOP_สระบุรี": {หมวด: [รายการ]}}` รายการมี `ชื่อ`, `อำเภอ`, `จุดเด่น` และ (ใหม่) `รูป`, `ชื่ออังกฤษ`, `ชื่อเรียกอื่น`
- Produces:
  - `PLACES_DIR: Path` = `robot/web/static/places`
  - `photos_for(question: str, answer: str, saraburi_data: dict, lang: str = "th", places_dir: Path = PLACES_DIR) -> list[dict]` แต่ละตัว `{"src": "/static/places/<ไฟล์>", "name": str, "caption": str}` ไม่เกิน 3
  - `menu_tree(saraburi_data: dict, places_dir: Path = PLACES_DIR) -> dict` รูปร่าง:
    ```
    {"trips":     {"label": {"th": "ที่เที่ยวสระบุรี", "en": "Places to visit"}, "categories": [...]},
     "souvenirs": {"label": {"th": "ของฝากสระบุรี",  "en": "Souvenirs"},       "categories": [...]}}
    category = {"key": str, "label": {"th","en"}, "icon": str, "items": [item]}
    item     = {"name": {"th","en"}, "district": str, "highlight": str, "photo": "/static/places/x.jpg" | None}
    ```
    `trips` มาจาก `ท่องเที่ยวสระบุรี`, `souvenirs` มาจาก `OTOP_สระบุรี` ไม่มีคีย์ → `categories: []`

- [ ] **Step 1: เขียนเทสต์ที่ต้อง fail**

ใช้ข้อมูลจำลองใน fixture + `tmp_path` เป็น `places_dir` (สร้างไฟล์ .jpg เปล่าเฉพาะที่ต้องการให้ "มีรูป") ไม่พึ่งรูปจริง ข้อมูลจำลองต้องมี: `น้ำตกเจ็ดสาวน้อย` (อำเภอ มวกเหล็ก, รูป jedsaonoi.jpg, ชื่ออังกฤษ "Jet Sao Noi Waterfall", ชื่อเรียกอื่น ["เจ็ดสาวน้อย"]), `น้ำตกมวกเหล็ก` (อำเภอ มวกเหล็ก, รูป muaklek.jpg), `วัดพระพุทธบาท` (อำเภอ พระพุทธบาท, รูป buddhabat.jpg), `ตลาดท่าน้ำแก่งคอย` ใน 2 หมวด (รูป kaengkhoi.jpg ทั้งคู่), `ไร่กุสุมา` มี `รูป` แต่**ไม่มีไฟล์**, และ OTOP `หมูทุบไร้มัน` ไม่มีรูป

```python
def test_name_in_question_gives_that_photo_only():
    p = photos_for("น้ำตกเจ็ดสาวน้อยไปยังไง", "มีน้ำตกมวกเหล็กด้วยนะ", DATA, places_dir=DIR)
    assert [x["src"] for x in p] == ["/static/places/jedsaonoi.jpg"]

def test_alias_matches():
    assert photos_for("เจ็ดสาวน้อยสวยไหม", "", DATA, places_dir=DIR)[0]["name"] == "น้ำตกเจ็ดสาวน้อย"

def test_broad_question_uses_answer_order_max_three():
    ans = "แนะนำ วัดพระพุทธบาท ตลาดท่าน้ำแก่งคอย น้ำตกมวกเหล็ก และ น้ำตกเจ็ดสาวน้อย"
    p = photos_for("สระบุรีมีที่เที่ยวที่ไหนบ้าง", ans, DATA, places_dir=DIR)
    assert [x["name"] for x in p] == ["วัดพระพุทธบาท", "ตลาดท่าน้ำแก่งคอย", "น้ำตกมวกเหล็ก"]

def test_no_names_gives_empty():
    assert photos_for("เปิดสอนสาขาอะไรบ้าง", "มีช่างยนต์ ช่างไฟฟ้า", DATA, places_dir=DIR) == []

def test_missing_file_not_returned():
    assert photos_for("ไร่กุสุมาเป็นยังไง", "", DATA, places_dir=DIR) == []

def test_district_name_does_not_match_place():
    assert photos_for("อำเภอมวกเหล็กมีอะไรบ้าง", "", DATA, places_dir=DIR) == []
    assert photos_for("อำเภอพระพุทธบาทอยู่ไหน", "", DATA, places_dir=DIR) == []

def test_duplicate_entry_appears_once():
    p = photos_for("ตลาดท่าน้ำแก่งคอย ตลาดท่าน้ำแก่งคอย", "", DATA, places_dir=DIR)
    assert len(p) == 1

def test_english_answer_case_insensitive_and_caption_lang():
    p = photos_for("Where to visit?", "Try JET SAO NOI waterfall!", DATA, lang="en", places_dir=DIR)
    assert p[0]["name"] == "Jet Sao Noi Waterfall"
    assert photos_for("น้ำตกเจ็ดสาวน้อย", "", DATA, lang="th", places_dir=DIR)[0]["caption"] == "มวกเหล็ก"

def test_menu_tree_shape():
    m = menu_tree(DATA, places_dir=DIR)
    assert set(m) == {"trips", "souvenirs"}
    assert [c["key"] for c in m["trips"]["categories"]] == list(DATA["ท่องเที่ยวสระบุรี"])
    item = m["trips"]["categories"][0]["items"][0]
    assert item["name"] == {"th": "น้ำตกเจ็ดสาวน้อย", "en": "Jet Sao Noi Waterfall"}
    assert item["photo"] == "/static/places/jedsaonoi.jpg"
    otop = m["souvenirs"]["categories"][0]["items"][0]
    assert otop["photo"] is None and otop["name"]["en"] == "หมูทุบไร้มัน"   # ไม่มีชื่ออังกฤษ → ไทย

def test_menu_tree_empty_data():
    assert menu_tree({}, places_dir=DIR) == {
        "trips": {"label": {"th": "ที่เที่ยวสระบุรี", "en": "Places to visit"}, "categories": []},
        "souvenirs": {"label": {"th": "ของฝากสระบุรี", "en": "Souvenirs"}, "categories": []}}
```

- [ ] **Step 2: รันให้เห็นว่า fail**

Run (จาก `robot/`): `python -m pytest web/test_places.py -v`
Expected: FAIL `ModuleNotFoundError: No module named 'places'`

- [ ] **Step 3: เขียน `robot/web/places.py`**

- รวมรายการทั้งสองส่วนเป็นลิสต์เดียว ตัดซ้ำด้วย `ชื่อ` (เก็บตัวแรก)
- ชื่อที่ใช้จับของแต่ละรายการ = `ชื่อ` + `ชื่ออังกฤษ` + `ชื่อเรียกอื่น` เทียบแบบ `.lower()` (ภาษาไทยไม่มีช่องว่างคั่นคำ "ทั้งคำ" จึงหมายถึงวิธีนี้):

```
หาทุกตำแหน่งของทุกชื่อในข้อความ (lowercase)
เรียงตามความยาวชื่อจากยาวไปสั้น; ช่วงไหนทับช่วงที่จับไปแล้ว ทิ้ง
เหลือ: รายการที่จับได้ เรียงตามตำแหน่งแรกที่พบ ตัดซ้ำ
```
- ใช้ชุดจากคำถามก่อน ว่างค่อยใช้จากคำตอบ แล้วกรองเฉพาะที่ `places_dir / รูป` มีอยู่จริง ตัดที่ 3
- ไม่จับจากฟิลด์ `อำเภอ` เลย (ใช้แค่เป็น caption)
- ป้ายหมวดย่อ (ไม่อยู่ในตาราง → ใช้คีย์เดิมแทน `_` ด้วยช่องว่าง, ไอคอน 📌):

| คีย์ในไฟล์ | th | en | icon |
|---|---|---|---|
| น้ำตก | น้ำตก | Waterfalls | 💧 |
| วัดและสถานที่ศักดิ์สิทธิ์ | วัด | Temples | 🛕 |
| ธรรมชาติและสวน | ธรรมชาติ | Nature | 🌻 |
| ตลาดและแหล่งช้อป | ตลาด | Markets | 🛒 |
| ใกล้วิทยาลัย_อำเภอบ้านหมอ | ใกล้วิทยาลัย | Near the college | 📍 |
| อาหารและขนม | อาหาร-ขนม | Food & snacks | 🍯 |
| งานหัตถกรรม | หัตถกรรม | Handicrafts | 🧺 |
| สมุนไพรและสุขภาพ | สมุนไพร | Herbal | 🌿 |

- ใน `menu_tree` ให้ `photo` เป็น `None` ถ้าไฟล์ไม่มีจริง

- [ ] **Step 4: รันให้ผ่าน**

Run: `python -m pytest web/test_places.py -v` → 10 passed; `python -m pytest -q` → 47 passed

- [ ] **Step 5: Commit** — `feat: โมดูลจับคู่รูปสถานที่ + โครงเมนูสระบุรี`

---

### Task 2: เซิร์ฟเวอร์ส่ง `photos` + `GET /menu`

**Files:**
- Modify: `robot/web/server.py` (`ask()`, `ask_stream()`, เพิ่ม route `/menu`)
- Test: `robot/web/test_server.py`

**Interfaces:**
- Consumes: `photos_for`, `menu_tree` จาก Task 1 (import เป็นชื่อในโมดูล `server` เพื่อให้ monkeypatch ได้)
- Produces (หน้าจอ Task 4 ใช้):
  - `/ask` → `{"answer", "photos": [...], "image"?}` (`photos` มีเสมอ)
  - `/ask/stream` บรรทัดจบ → `{"done": true, "image": str|null, "photos": [...]}`
  - `GET /menu` → ผลของ `menu_tree(saraburi_data)`
  - กติกา: ถ้า `wants_map(question)` เป็น True → `photos = []` และไม่เรียก `photos_for`

- [ ] **Step 1: เขียน/แก้เทสต์**

- แก้ `test_ask_stream_sends_pieces_then_done` ให้บรรทัดสุดท้ายคาด `{"done": True, "image": None, "photos": []}`
- เพิ่ม:

```python
def test_ask_stream_done_has_photos_from_full_answer(monkeypatch):
    # stream แยกชื่อเป็น 2 ท่อน → ต้องคำนวณจากคำตอบที่ต่อครบแล้ว
    c = make_client(); set_valid_key(monkeypatch)
    monkeypatch.setattr(server, "ask_ai_stream", lambda q, c_, s, lang="th": iter(["ไปน้ำตกเจ็ด", "สาวน้อยค่ะ"]))
    seen = []
    monkeypatch.setattr(server, "photos_for", lambda q, a, d, lang="th": seen.append((q, a, lang)) or [{"src": "/static/places/a.jpg", "name": "n", "caption": "c"}])
    last = _lines(c.post("/ask/stream", json={"question": "เที่ยวไหนดี"}))[-1]
    assert seen == [("เที่ยวไหนดี", "ไปน้ำตกเจ็ดสาวน้อยค่ะ", "th")]
    assert last["photos"][0]["src"] == "/static/places/a.jpg"

def test_ask_includes_photos(monkeypatch):      # /ask → photos ตามที่ photos_for คืน, lang ส่งต่อ
def test_map_question_has_map_and_no_photos(monkeypatch):
    # wants_map True → image = map.jpg, photos == [], photos_for ไม่ถูกเรียก (ทั้ง /ask และ /ask/stream)
def test_menu_endpoint_returns_tree_without_ai(monkeypatch):
    # ask_ai / ask_ai_stream ถูกแทนด้วยฟังก์ชันที่ raise AssertionError
    # GET /menu → 200, keys == {"trips","souvenirs"}, หมวดของ trips ครบตามคีย์ใน server.saraburi_data["ท่องเที่ยวสระบุรี"]
def test_menu_endpoint_with_empty_data(monkeypatch):
    # monkeypatch server.saraburi_data = {} → 200 และ categories ว่างทั้งสองส่วน
```

- [ ] **Step 2: รันให้เห็นว่า fail** — `python -m pytest web/test_server.py -v` → เทสต์ใหม่ + เทสต์ที่แก้ FAIL

- [ ] **Step 3: แก้ `server.py`**

`ask_stream.generate()` เก็บท่อนไว้ต่อกันระหว่าง yield แล้วคำนวณ `photos` ก่อน yield บรรทัด done; บรรทัด error ไม่ต้องมี `photos` ส่วน `/menu` คืน `jsonify(menu_tree(saraburi_data))` อ่าน `saraburi_data` จาก module global ตอนเรียก (ให้ monkeypatch ได้)

- [ ] **Step 4: รันให้ผ่าน** — `python -m pytest -q` → 52 passed

- [ ] **Step 5: Commit** — `feat: ส่งรูปสถานที่ในคำตอบ + endpoint /menu`

---

### Task 3: หารูป + เติมข้อมูล + เครดิต

**Files:**
- Create: `robot/web/static/places/*.jpg`, `robot/web/static/places/CREDITS.md`
- Modify: `robot/saraburi_data.json` (เติม `รูป` / `ชื่ออังกฤษ` / `ชื่อเรียกอื่น`), `robot/database.py` (`format_all_data` ตัด `รูป`)
- Test: `robot/test_saraburi.py`
- Script ชั่วคราว (ไม่ commit): ใน scratchpad

**Interfaces:**
- Consumes: `PLACES_DIR` จาก Task 1
- Produces: ข้อมูลจริงที่ `photos_for`/`menu_tree` ใช้; `format_all_data(college_data, saraburi_data) -> str` signature เดิม แต่ไม่มีค่าของฟิลด์ `รูป`

- [ ] **Step 1: เขียนเทสต์ข้อมูลที่ต้อง fail**

```python
def test_every_photo_field_has_file():          # ทุก "รูป" → ไฟล์อยู่ใน web/static/places
def test_every_photo_file_has_credit():         # ทุก *.jpg ใน places/ ถูกพูดถึงชื่อไฟล์ใน CREDITS.md
def test_photo_files_small_enough():            # Pillow: width <= 1024 และ os.path.getsize <= 260_000
def test_aliases_never_equal_a_district():      # ชื่อเรียกอื่นทุกตัว ไม่ซ้ำค่า "อำเภอ" ใด ๆ, ไม่ใช่สตริงว่าง
def test_same_name_same_photo():                # รายการชื่อเดียวกันข้ามหมวด มี "รูป" เหมือนกัน (หรือไม่มีทั้งคู่)
def test_prompt_has_no_photo_filenames():
    text = format_all_data({}, load_saraburi_data())
    assert ".jpg" not in text and "น้ำตกเจ็ดสาวน้อย" in text
```
เทสต์ 2 ข้อแรกต้องเขียนให้ fail ได้จริงตอนยังไม่มีโฟลเดอร์/เครดิต (เช่น assert ว่าโฟลเดอร์มีอยู่และมีอย่างน้อย 1 รูป)

- [ ] **Step 2: รันให้เห็นว่า fail** — `python -m pytest test_saraburi.py -v`

- [ ] **Step 3: หารูปจาก Wikimedia Commons ทีละรายการ (24 รายการ ไม่นับที่ซ้ำ)**

- ค้น: `https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrsearch=<ชื่อไทย หรืออังกฤษ>&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=1024` (ลองทั้งชื่อไทย ชื่ออังกฤษ และหมวด Commons ของสถานที่)
- รับเฉพาะ `extmetadata.LicenseShortName` ที่เป็น CC0 / CC BY* / CC BY-SA* / Public domain
- ยืนยันว่าตรงสถานที่: ชื่อไฟล์ + `ImageDescription` + หมวดชี้ชื่อสถานที่นั้นชัด **และ**เปิดดูรูปเอง (Read) ว่าเห็นสิ่งที่ตรงกับ `จุดเด่น` (เช่น น้ำตกหลายชั้น, รอยพระพุทธบาท) ไม่ชัด = ไม่เอา
- ดาวน์โหลด `thumburl` ลงโฟลเดอร์ใหม่ใน scratchpad, ย่อด้วย Pillow เป็น RGB JPEG กว้าง ≤ 1024 quality ~82 (ลดจนไฟล์ ≤ 250KB) บันทึกลง `places/` ชื่อไฟล์ ASCII สั้น (เช่น `jedsaonoi.jpg`)
- `CREDITS.md`: ตาราง | ไฟล์ | รูปของ | ผู้ถ่าย (`Artist`) | สัญญาอนุญาต | ลิงก์หน้าไฟล์บน Commons |
- จดรายการที่หาไม่ได้ไว้รายงาน user ตอนจบ

- [ ] **Step 4: เติม JSON + ตัด `รูป` ออกจาก prompt**

- ทุกรายการ: `ชื่ออังกฤษ` (ชื่อที่ใช้กันจริง เช่น "Jet Sao Noi Waterfall", "Wat Phra Phutthabat") ใส่ได้แม้ไม่มีรูป
- `ชื่อเรียกอื่น` ใส่เฉพาะที่คนเรียกสั้นจริง และห้ามเป็นชื่ออำเภอ (เช่น `น้ำตกมวกเหล็ก` ห้ามมี "มวกเหล็ก") อาจใส่ตัวสะกดอังกฤษแบบอื่น (เช่น "Chet Sao Noi")
- `รูป` ใส่เฉพาะที่ได้รูปผ่าน Step 3, รายการซ้ำข้ามหมวดใส่ค่าเดียวกัน
- `database.format_all_data`: ทำสำเนาข้อมูลสระบุรีที่ตัดคีย์ `รูป` ทุกระดับก่อน `format_for_prompt` (ไม่แก้ dict ต้นฉบับ)

- [ ] **Step 5: รันให้ผ่าน** — `python -m pytest -q` → 58 passed

- [ ] **Step 6: Commit** — `feat: รูปสถานที่สระบุรี (Wikimedia Commons) + ชื่ออังกฤษ/ชื่อเรียกอื่น`

---

### Task 4: หน้าจอ — รูปในคำตอบ + เมนูกดแตกหมวด

**Files:**
- Modify: `robot/web/static/screen.html` (ชิป 2 ปุ่ม + CSS), `robot/web/static/screen.js`
- Test: `robot/web/test_server.py` (เช็กไฟล์หน้าจอแบบเดียวกับ `test_screen_chips_cover_college_and_saraburi`)

**Interfaces:**
- Consumes: `/ask/stream` บรรทัดจบมี `photos`, `GET /menu` (Task 2)
- Produces: —

- [ ] **Step 1: เขียนเทสต์ที่ต้อง fail**

```python
def test_screen_trip_and_souvenir_chips_open_menu():
    html = make_client().get("/screen").get_data(as_text=True)
    assert 'data-menu="trips"' in html and 'data-menu="souvenirs"' in html
    # ยังมี data-q ไว้เป็นทางสำรองตอน /menu โหลดไม่ได้
    assert 'data-q="สระบุรีมีที่เที่ยวที่ไหนบ้าง"' in html

def test_screen_js_uses_menu_and_photos():
    js = make_client().get("/static/screen.js").get_data(as_text=True)
    assert 'fetch("/menu")' in js and "photos" in js and "place-photo" in js
```

- [ ] **Step 2: รันให้เห็นว่า fail** — `python -m pytest web/test_server.py -v`

- [ ] **Step 3: แก้ `screen.html`**

- ชิป 🏞️/🛍️ เพิ่ม `data-menu="trips"` / `data-menu="souvenirs"` คง `data-q`/`data-q-en` เดิม (ชิปถูก clone ไป `sideQs`/`dockQs` อยู่แล้ว attribute ตามไปด้วย)
- CSS ใหม่ใช้ตัวแปรสีเดิม: `.place-photo` (รูปเดียว เต็มความกว้างบับเบิล max 420px, `cursor:zoom-in`), `.photo-row` (รูปเล็กเรียงแถว เลื่อนข้างได้ + figcaption), `.menu-grid` ปุ่มหมวด, `.menu-list` การ์ดรายการ (thumb 64px หรือไอคอนหมวด + ชื่อ + อำเภอ), `.place-card` (รูปใหญ่ + ชื่อ + อำเภอ + จุดเด่น), `.menu-nav` (ย้อนกลับ / หน้าแรก) ปุ่มทั้งหมด `min-height:48px`

- [ ] **Step 4: แก้ `screen.js`**

- `T.th` / `T.en` เพิ่มข้อความ: `menuPick` ("เลือกหมวดได้เลยค่ะ 👇" / "Pick a category 👇"), `menuItems` ("{cat} มีที่นี่ค่ะ" / "Here are the {cat}"), `back` ("ย้อนกลับ"/"Back"), `home` ("หน้าแรก"/"Home"), `districtLabel` ("อ." / "District:")
- โหลด `fetch("/menu")` ครั้งเดียวตอนเริ่ม เก็บใน `menuData` (ล้มเหลว → `null`)
- `renderBot`: `opts.photos` 1 รูป → `<img class="place-photo">` + ชื่อ; หลายรูป → `.photo-row`; ข้อความทุกตัว `escapeHtml`; `ask()` ส่ง `photos: end.photos || []` ให้ `tw.finish`
- เมนูเป็นข้อความหุ่นในแชท (ต่อท้ายเรื่อย ๆ) และก่อนแต่ละชั้นใส่บับเบิลผู้ใช้เป็นป้ายที่กด:
  - `openMenu(section)` → ข้อความ `menuPick` + ปุ่มหมวด `data-menu-cat="<section>:<i>"`
  - `openCategory(section, i)` → การ์ดรายการ `data-menu-item="<section>:<i>:<j>"` + ปุ่ม `data-menu="<section>"` (ย้อนกลับ) + `data-action="newChat"` (หน้าแรก)
  - `openItem(section, i, j)` → `.place-card` + ปุ่ม `data-menu-cat="<section>:<i>"` (ย้อนกลับ) + หน้าแรก
  - ใช้ภาษาปัจจุบัน `lang` ตอนวาด, ไม่เรียก `setState`, ไม่ `speak`, ไม่ `fetch` อะไรนอกจาก `/menu` ตอนเริ่ม
- ตัวจับคลิกเดิม: ขยาย selector เป็น `[data-q], [data-action], [data-menu], [data-menu-cat], [data-menu-item]` ลำดับ: `newChat` → `busy()` กัน → `data-menu*` (ถ้า `menuData` เป็น `null` และปุ่มมี `data-q` → ตกไป `ask()` เดิม) → `showMap` → `ask`
- lightbox: เปิดได้ทั้ง `.map-thumb` และ `.place-photo` (รวมรูปใน `.photo-row` และ `.place-card`)

- [ ] **Step 5: รันเทสต์** — `python -m pytest -q` → 60 passed

- [ ] **Step 6: ตรวจบนหน้าจอจริง (ไม่เรียก Gemini)**

รัน `web/server.py` แล้วขับ Chrome headless ผ่าน DevTools ด้วยสคริปต์ Node 24 ใน scratchpad (อย่าใช้ `--virtual-time-budget` เพราะค้างที่ SSE `/events`) ที่ 1280×800 และ 800×480, ทั้งโหมดมืด/สว่าง และ TH/EN ถ่ายภาพ:
1. กด 🏞️ → หมวด → น้ำตก → รายการมีรูปเล็ก → กดเจ็ดสาวน้อย → การ์ดรูปใหญ่ → กดรูปขยาย lightbox → ย้อนกลับ → หน้าแรก
2. กด 🛍️ → อาหาร-ขนม → รายการที่ไม่มีรูปแสดงไอคอน
3. override `window.fetch` สำหรับ `/ask/stream` ให้คืน NDJSON จำลอง (`{"t":...}` + `{"done":true,"image":null,"photos":[...รูปจริง 1 และ 3 รูป]}`) แล้วถาม → รูปขึ้นใต้คำตอบถูกแบบ
4. override `/menu` ให้ 500 → กด 🏞️ แล้วต้องเรียก `/ask/stream` (ทางสำรอง)
5. ระหว่างคำตอบจำลองกำลังไหล กดเมนู → ไม่มีอะไรเกิด; เช็ก `/state` ว่าการกดเมนูไม่เปลี่ยนสถานะ
ดูภาพเองทุกภาพก่อนสรุป

- [ ] **Step 7: Commit** — `feat: จอแสดงรูปสถานที่ในคำตอบ + เมนูกดแตกหมวดที่เที่ยว/ของฝาก`

---

### หลังจบทุก task

- `python -m pytest -q` ผ่านทั้งหมด, push branch, เปิด PR, แนบภาพหน้าจอ
- รายงาน user: รายการไหนมีรูป/ไม่มีรูป (+ เหตุผลสั้น ๆ) และอัปเดต memory
