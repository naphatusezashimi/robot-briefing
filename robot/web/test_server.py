"""
เทสต์เซิร์ฟเวอร์เว็บ — Flask test client + mock ask_ai (ไม่ยิง API จริง)
รันจากโฟลเดอร์ robot/:  & $py -m pytest web/test_server.py -v
"""
import server  # web/ ถูกใส่ใน sys.path โดย pytest (prepend import mode)


def make_client():
    server.app.config["TESTING"] = True
    server.state["value"] = "idle"
    return server.app.test_client()


def test_state_default_is_idle():
    c = make_client()
    r = c.get("/state")
    assert r.status_code == 200
    assert r.get_json()["state"] == "idle"


def test_post_state_updates_value():
    c = make_client()
    r = c.post("/state", json={"state": "listening"})
    assert r.get_json()["state"] == "listening"
    assert c.get("/state").get_json()["state"] == "listening"


def set_valid_key(monkeypatch):
    """ตั้ง key ปลอมที่ 'พร้อมใช้' — /ask ต้องมี key ก่อนถึงจะเรียกสมอง"""
    monkeypatch.setattr(server.config, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(server.config, "GEMINI_API_KEY", "test-key")


def test_ask_returns_answer_and_sets_answering(monkeypatch):
    c = make_client()
    set_valid_key(monkeypatch)
    # mock สมองไม่ให้ยิง API จริง (monkeypatch คืนค่าเดิมให้อัตโนมัติหลังจบเทสต์)
    monkeypatch.setattr(server, "ask_ai", lambda question, college_data, saraburi_data, lang="th": f"ตอบ: {question}")
    r = c.post("/ask", json={"question": "เปิดสอนอะไร"})
    assert r.status_code == 200
    assert r.get_json()["answer"] == "ตอบ: เปิดสอนอะไร"
    assert server.state["value"] == "answering"


def test_ask_error_sets_error_state_and_500(monkeypatch):
    c = make_client()
    set_valid_key(monkeypatch)

    def boom(question, college_data, saraburi_data, lang="th"):
        raise RuntimeError("เน็ตล่ม")

    monkeypatch.setattr(server, "ask_ai", boom)
    r = c.post("/ask", json={"question": "x"})
    assert r.status_code == 500
    assert "error" in r.get_json()
    assert server.state["value"] == "error"


def test_ask_without_api_key_returns_setup_instructions(monkeypatch):
    """key ว่าง → ต้องบอกวิธีตั้งค่าเป็นภาษาไทย และห้ามเรียกสมองจริง"""
    c = make_client()
    monkeypatch.setattr(server.config, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(server.config, "GEMINI_API_KEY", "")
    called = []
    monkeypatch.setattr(server, "ask_ai", lambda q, c, s, lang="th": called.append(q) or "x")
    r = c.post("/ask", json={"question": "เปิดสอนอะไร"})
    assert r.status_code == 500
    err = r.get_json()["error"]
    assert "GEMINI_API_KEY" in err
    assert ".env" in err
    assert called == []
    assert server.state["value"] == "error"


def test_ask_with_placeholder_key_returns_setup_instructions(monkeypatch):
    """key ยังเป็นค่าตัวอย่างจาก .env.example → ถือว่ายังไม่ได้ตั้งค่า"""
    c = make_client()
    monkeypatch.setattr(server.config, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(server.config, "GEMINI_API_KEY", "AIzaxxxxxxxxxxxxxxxxxxxxxxxx")
    monkeypatch.setattr(server, "ask_ai", lambda q, c, s, lang="th": "x")
    r = c.post("/ask", json={"question": "เปิดสอนอะไร"})
    assert r.status_code == 500
    assert "GEMINI_API_KEY" in r.get_json()["error"]


def test_pages_are_served():
    c = make_client()
    face = c.get("/face")
    screen = c.get("/screen")
    assert face.status_code == 200
    assert b"eye-ball" in face.data        # มาร์กเกอร์ของจอใบหน้า
    assert screen.status_code == 200
    assert b'id="mic"' in screen.data      # มาร์กเกอร์ของจอเนื้อหา


def test_logo_asset_served():
    c = make_client()
    r = c.get("/static/logo.jpg")
    assert r.status_code == 200
    assert r.data[:3] == b"\xff\xd8\xff"   # magic bytes ของไฟล์ JPEG


def test_screen_header_uses_real_logo():
    c = make_client()
    screen = c.get("/screen")
    assert screen.status_code == 200
    assert b"/static/logo.jpg" in screen.data   # header อ้างโลโก้จริง


def test_screen_has_quick_questions():
    """จอเนื้อหามีแถบคำถามยอดนิยมให้แตะถามได้"""
    c = make_client()
    screen = c.get("/screen")
    assert screen.status_code == 200
    html = screen.data.decode("utf-8")
    assert 'id="quickQs"' in html
    assert "คำถามยอดนิยม" in html
    assert html.count('class="chip"') >= 3      # มีปุ่มคำถามอย่างน้อย 3 ปุ่ม


# ---------- wayfinding ----------

import wayfinding


def test_wants_map_true_for_location_keywords():
    assert wayfinding.wants_map("สาขาอิเล็กทรอนิกส์อยู่ตึกไหน") is True
    assert wayfinding.wants_map("งานพัสดุอยู่อาคารไหน") is True
    assert wayfinding.wants_map("ห้องสมุดอยู่ที่ไหน") is True
    assert wayfinding.wants_map("ไปยังหอประชุมได้ยังไง") is True
    assert wayfinding.wants_map("แผนผังวิทยาลัยมีไหม") is True
    assert wayfinding.wants_map("โรงอาหารอยู่ตรงไหน") is True
    assert wayfinding.wants_map("ที่จอดรถอยู่ที่ไหน") is True


def test_wants_map_false_for_non_location():
    assert wayfinding.wants_map("ค่าเทอมเท่าไหร่") is False
    assert wayfinding.wants_map("เปิดสอนสาขาอะไรบ้าง") is False
    assert wayfinding.wants_map("สมัครเรียนต้องมีคุณสมบัติอะไร") is False
    assert wayfinding.wants_map("ติดต่อวิทยาลัยได้ช่องทางไหนบ้าง") is False
    assert wayfinding.wants_map("") is False
    assert wayfinding.wants_map("สาขานี้มีจุดเด่นอะไร") is False


def test_wants_map_false_for_off_campus_questions():
    """ถามที่เที่ยว/ของฝากนอกวิทยาลัย ต้องไม่แนบแผนผังวิทยาลัย แม้มีคำว่า 'ที่ไหน'"""
    assert wayfinding.wants_map("เสาไห้มีที่ไหนน่าเที่ยว") is False
    assert wayfinding.wants_map("สระบุรีมีที่เที่ยวที่ไหนบ้าง") is False
    assert wayfinding.wants_map("ซื้อของฝากได้ที่ไหน") is False
    assert wayfinding.wants_map("น้ำตกเจ็ดสาวน้อยไปยังไง") is False
    assert wayfinding.wants_map("ใกล้วิทยาลัยมีร้านอาหารอร่อยตรงไหนบ้าง") is False


# ---------- map asset ----------

def test_map_asset_served():
    c = make_client()
    r = c.get("/static/map.jpg")
    assert r.status_code == 200
    assert r.data[:3] == b"\xff\xd8\xff"  # JPEG magic bytes


# ---------- /ask + image ----------

def test_ask_location_question_includes_image(monkeypatch):
    c = make_client()
    set_valid_key(monkeypatch)
    monkeypatch.setattr(server, "ask_ai", lambda q, c, s, lang="th": "อาคาร 7 ครับ")
    monkeypatch.setattr(server, "wants_map", lambda q: True)
    r = c.post("/ask", json={"question": "สาขาอิเล็กทรอนิกส์อยู่ตึกไหน"})
    assert r.status_code == 200
    d = r.get_json()
    assert d["answer"] == "อาคาร 7 ครับ"
    assert d.get("image") == "/static/map.jpg"


def test_ask_non_location_question_no_image(monkeypatch):
    c = make_client()
    set_valid_key(monkeypatch)
    monkeypatch.setattr(server, "ask_ai", lambda q, c, s, lang="th": "ตอบ: ค่าเทอม")
    monkeypatch.setattr(server, "wants_map", lambda q: False)
    r = c.post("/ask", json={"question": "ค่าเทอมเท่าไหร่"})
    assert r.status_code == 200
    d = r.get_json()
    assert d["answer"] == "ตอบ: ค่าเทอม"
    assert "image" not in d


# ---------- map chip ----------

def test_screen_has_map_chip():
    c = make_client()
    screen = c.get("/screen")
    assert screen.status_code == 200
    html = screen.data.decode("utf-8")
    assert "แผนผังวิทยาลัย" in html
    assert 'data-action="showMap"' in html


def test_screen_chips_cover_college_and_saraburi():
    html = make_client().get("/screen").data.decode("utf-8")
    assert "ค่าเทอมเท่าไหร่" not in html          # ไม่มีข้อมูลค่าเทอม กดแล้วได้แค่ "ติดต่อเจ้าหน้าที่"
    assert 'data-q="สระบุรีมีที่เที่ยวที่ไหนบ้าง"' in html
    assert 'data-q="ติดต่อวิทยาลัยได้ช่องทางไหนบ้าง"' in html


# ---------- gpio_btn ----------

import queue as _queue
import gpio_btn


def test_gpio_btn_init_simulator_mode():
    """SIMULATOR_MODE=True: init ต้องไม่ crash และ queue ต้องว่าง"""
    q = _queue.Queue()
    btn = gpio_btn.GpioButton(q)
    assert q.empty()


# ---------- SSE /events ----------


def test_events_endpoint_returns_stream(monkeypatch):
    """/events ต้องคืน text/event-stream และเริ่มด้วย 'data: connected'"""
    def finite_stream():
        yield "data: connected\n\n"
    monkeypatch.setattr(server, "_make_sse_stream", finite_stream)
    c = make_client()
    r = c.get("/events")
    assert r.status_code == 200
    assert "text/event-stream" in r.content_type
    assert b"data: connected" in r.data


# ---------- ภาษา (th/en) ----------

def test_state_carries_language_for_face():
    """จอเนื้อหาเลือกภาษา → เซิร์ฟเวอร์จำไว้ → จอใบหน้าอ่านจาก GET /state"""
    c = make_client()
    server.state["lang"] = "th"
    assert c.get("/state").get_json()["lang"] == "th"
    r = c.post("/state", json={"state": "idle", "lang": "en"})
    assert r.get_json()["lang"] == "en"
    assert c.get("/state").get_json()["lang"] == "en"
    c.post("/state", json={"state": "idle", "lang": "fr"})   # ภาษาที่ไม่รองรับ ไม่เปลี่ยน
    assert c.get("/state").get_json()["lang"] == "en"
    server.state["lang"] = "th"


def test_ask_passes_language_to_ai(monkeypatch):
    c = make_client()
    set_valid_key(monkeypatch)
    seen = []
    monkeypatch.setattr(server, "ask_ai", lambda q, c_, s, lang="th": seen.append(lang) or "ok")
    c.post("/ask", json={"question": "hello", "lang": "en"})
    c.post("/ask", json={"question": "สวัสดี"})                 # ไม่ส่ง lang = ไทย
    c.post("/ask", json={"question": "x", "lang": "evil"})      # ค่าแปลก = ไทย
    assert seen == ["en", "th", "th"]


def test_wants_map_english_questions():
    assert wayfinding.wants_map("Where is the canteen?") is True
    assert wayfinding.wants_map("Can I see the campus map?") is True
    assert wayfinding.wants_map("Where is the electronics building?") is True
    assert wayfinding.wants_map("Where is the workshop?") is True
    assert wayfinding.wants_map("What are the places to visit in Saraburi?") is False
    assert wayfinding.wants_map("Where can I buy souvenirs?") is False
    assert wayfinding.wants_map("What programs does the college offer?") is False


def test_screen_has_language_and_theme_switches():
    html = make_client().get("/screen").data.decode("utf-8")
    assert 'data-lang="en"' in html
    assert 'id="themeBtn"' in html
    assert 'data-q-en="What are the places to visit in Saraburi?"' in html
