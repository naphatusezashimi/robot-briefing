"""
เทสต์เซิร์ฟเวอร์เว็บ — Flask test client + mock ask_ai (ไม่ยิง API จริง)
รันจากโฟลเดอร์ robot/:  & $py -m pytest web/test_server.py -v
"""
import pytest

import server  # web/ ถูกใส่ใน sys.path โดย pytest (prepend import mode)
from stats import Stats


@pytest.fixture(autouse=True)
def temp_stats(tmp_path, monkeypatch):
    """ทุกเทสต์ใช้ฐานสถิติชั่วคราว ไม่เขียนลง robot/stats.db ตัวจริง"""
    st = Stats(tmp_path / "stats.db")
    monkeypatch.setattr(server, "stats", st)
    return st


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


# ---------- คำตอบแบบทยอยไหล (/ask/stream) ----------

import json as _json


def _lines(r):
    return [_json.loads(l) for l in r.get_data(as_text=True).splitlines() if l.strip()]


def test_ask_stream_sends_pieces_then_done(monkeypatch):
    c = make_client()
    set_valid_key(monkeypatch)
    monkeypatch.setattr(server, "ask_ai_stream", lambda q, c_, s, lang="th": iter(["สวัส", "ดีค่ะ"]))
    monkeypatch.setattr(server, "wants_map", lambda q: False)
    r = c.post("/ask/stream", json={"question": "hi"})
    assert r.status_code == 200
    assert _lines(r) == [{"t": "สวัส"}, {"t": "ดีค่ะ"}, {"done": True, "image": None, "photos": []}]
    assert server.state["value"] == "answering"


def test_ask_stream_passes_language_and_map(monkeypatch):
    c = make_client()
    set_valid_key(monkeypatch)
    seen = []
    monkeypatch.setattr(server, "ask_ai_stream", lambda q, c_, s, lang="th": seen.append(lang) or iter(["x"]))
    r = c.post("/ask/stream", json={"question": "Where is the canteen?", "lang": "en"})
    assert seen == ["en"]
    assert _lines(r)[-1] == {"done": True, "image": "/static/map.jpg", "photos": []}


def test_ask_stream_error_midway_keeps_text_and_reports(monkeypatch):
    c = make_client()
    set_valid_key(monkeypatch)

    def broken(q, c_, s, lang="th"):
        yield "ครึ่ง"
        raise RuntimeError("503 overloaded")

    monkeypatch.setattr(server, "ask_ai_stream", broken)
    lines = _lines(c.post("/ask/stream", json={"question": "x"}))
    assert lines[0] == {"t": "ครึ่ง"}
    assert "ยุ่ง" in lines[-1]["error"]          # 503 → ข้อความที่คนอ่านเข้าใจ
    assert server.state["value"] == "error"


def test_ask_stream_without_key_returns_500(monkeypatch):
    c = make_client()
    monkeypatch.setattr(server.config, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(server.config, "GEMINI_API_KEY", "")
    r = c.post("/ask/stream", json={"question": "x"})
    assert r.status_code == 500
    assert "GEMINI_API_KEY" in r.get_json()["error"]


def test_friendly_error_messages():
    quota = RuntimeError("429 RESOURCE_EXHAUSTED. quota exceeded")
    assert "โควตา" in server.friendly_error(quota, "th")
    assert "quota" in server.friendly_error(quota, "en")
    assert "busy" in server.friendly_error(RuntimeError("503 UNAVAILABLE"), "en")
    assert server.friendly_error(RuntimeError("อื่น ๆ"), "th") == "อื่น ๆ"


# ---------- รูปสถานที่ + เมนู ----------

PHOTO = {"src": "/static/places/a.jpg", "name": "n", "caption": "c"}


def test_ask_stream_done_has_photos_from_full_answer(monkeypatch):
    # stream แยกชื่อเป็น 2 ท่อน → ต้องคำนวณจากคำตอบที่ต่อครบแล้ว
    c = make_client()
    set_valid_key(monkeypatch)
    monkeypatch.setattr(server, "ask_ai_stream", lambda q, c_, s, lang="th": iter(["ไปน้ำตกเจ็ด", "สาวน้อยค่ะ"]))
    monkeypatch.setattr(server, "wants_map", lambda q: False)
    seen = []
    monkeypatch.setattr(server, "photos_for", lambda q, a, d, lang="th": seen.append((q, a, lang)) or [PHOTO])
    last = _lines(c.post("/ask/stream", json={"question": "เที่ยวไหนดี"}))[-1]
    assert seen == [("เที่ยวไหนดี", "ไปน้ำตกเจ็ดสาวน้อยค่ะ", "th")]
    assert last["photos"] == [PHOTO]


def test_ask_includes_photos(monkeypatch):
    c = make_client()
    set_valid_key(monkeypatch)
    monkeypatch.setattr(server, "ask_ai", lambda q, c_, s, lang="th": "Jet Sao Noi")
    monkeypatch.setattr(server, "wants_map", lambda q: False)
    seen = []
    monkeypatch.setattr(server, "photos_for", lambda q, a, d, lang="th": seen.append(lang) or [PHOTO])
    d = c.post("/ask", json={"question": "where?", "lang": "en"}).get_json()
    assert d["photos"] == [PHOTO]
    assert seen == ["en"]


def test_map_question_has_map_and_no_photos(monkeypatch):
    c = make_client()
    set_valid_key(monkeypatch)
    monkeypatch.setattr(server, "ask_ai", lambda q, c_, s, lang="th": "อาคาร 7")
    monkeypatch.setattr(server, "ask_ai_stream", lambda q, c_, s, lang="th": iter(["อาคาร 7"]))
    monkeypatch.setattr(server, "wants_map", lambda q: True)

    def no_photos(*a, **k):
        raise AssertionError("ไม่ควรหารูปที่เที่ยวตอนโชว์แผนผัง")

    monkeypatch.setattr(server, "photos_for", no_photos)
    d = c.post("/ask", json={"question": "โรงอาหารอยู่ไหน"}).get_json()
    assert d["image"] == "/static/map.jpg" and d["photos"] == []
    last = _lines(c.post("/ask/stream", json={"question": "โรงอาหารอยู่ไหน"}))[-1]
    assert last == {"done": True, "image": "/static/map.jpg", "photos": []}


def _no_ai(*a, **k):
    raise AssertionError("เมนูห้ามเรียก AI")


def test_menu_endpoint_returns_tree_without_ai(monkeypatch):
    monkeypatch.setattr(server, "ask_ai", _no_ai)
    monkeypatch.setattr(server, "ask_ai_stream", _no_ai)
    r = make_client().get("/menu")
    assert r.status_code == 200
    m = r.get_json()
    assert set(m) == {"trips", "souvenirs"}
    assert [c["key"] for c in m["trips"]["categories"]] == list(server.saraburi_data["ท่องเที่ยวสระบุรี"])


def test_menu_endpoint_with_empty_data(monkeypatch):
    monkeypatch.setattr(server, "saraburi_data", {})
    m = make_client().get("/menu").get_json()
    assert m["trips"]["categories"] == [] and m["souvenirs"]["categories"] == []


def test_screen_trip_and_souvenir_chips_open_menu():
    html = make_client().get("/screen").get_data(as_text=True)
    assert 'data-menu="trips"' in html and 'data-menu="souvenirs"' in html
    # ยังมี data-q ไว้เป็นทางสำรองตอน /menu โหลดไม่ได้
    assert 'data-q="สระบุรีมีที่เที่ยวที่ไหนบ้าง"' in html


def test_screen_js_uses_menu_and_photos():
    js = make_client().get("/static/screen.js").get_data(as_text=True)
    assert 'fetch("/menu")' in js and "photos" in js and "place-photo" in js


# ---- ทักทาย: แขนโบก + หน้าหุ่น + คำทัก ----
class FakeArm:
    def __init__(self, ok=True):
        self.calls = 0
        self.ok = ok

    def wave(self):
        self.calls += 1
        return self.ok


def test_greet_waves_arm(monkeypatch):
    c = make_client()
    arm = FakeArm()
    monkeypatch.setattr(server, "arm", arm)
    r = c.post("/greet")
    assert r.status_code == 200
    assert r.get_json() == {"ok": True, "waving": True}
    assert arm.calls == 1


def test_greet_while_arm_busy_reports_not_waving(monkeypatch):
    c = make_client()
    monkeypatch.setattr(server, "arm", FakeArm(ok=False))
    assert c.post("/greet").get_json()["waving"] is False


def test_request_greet_pushes_event_to_screen():
    """เซนเซอร์ (เช่น อัลตราโซนิก) เรียก request_greet() → จอได้สัญญาณ greet ทาง /events"""
    while not server.button_queue.empty():
        server.button_queue.get_nowait()
    server.request_greet()
    assert server.button_queue.get_nowait() == "greet"


def test_face_has_greeting_mood():
    c = make_client()
    html = c.get("/face").data.decode("utf-8")
    assert "state-greeting" in html
    js = c.get("/static/face.js").data.decode("utf-8")
    assert "greeting" in js


def test_face_shows_waving_hand_when_greeting():
    """บนคอมไม่มีแขนจริง — หน้าหุ่นต้องมีมือโบกให้เห็นตอนทักทาย"""
    html = make_client().get("/face").data.decode("utf-8")
    assert 'class="hand"' in html
    assert "body.state-greeting .hand" in html


def test_screen_greets_as_male_tl_bot():
    c = make_client()
    js = c.get("/static/screen.js").data.decode("utf-8")
    assert "ผมชื่อทีแอลบอท" in js
    assert "หนู" not in js and "ค่ะ" not in js
    assert "/greet" in js


# ---- สถิติ: เก็บคำถาม + ให้ดาว ----
def test_ask_stream_logs_question(monkeypatch, temp_stats):
    c = make_client()
    set_valid_key(monkeypatch)
    monkeypatch.setattr(server, "ask_ai_stream", lambda q, c_, s, lang="th": iter(["ok"]))
    monkeypatch.setattr(server, "wants_map", lambda q: False)
    c.post("/ask/stream", json={"question": "สาขาอะไรบ้าง"}).get_data()
    assert temp_stats.summary()["top"] == [{"question": "สาขาอะไรบ้าง", "count": 1}]


def test_rate_saves_stars(temp_stats):
    c = make_client()
    r = c.post("/rate", json={"stars": 4, "question": "ติดต่อยังไง", "lang": "th"})
    assert r.status_code == 200
    s = temp_stats.summary()
    assert s["ratings_total"] == 1 and s["average"] == 4


def test_rate_rejects_bad_stars(temp_stats):
    c = make_client()
    for bad in (0, 6, "5", None):
        assert c.post("/rate", json={"stars": bad, "question": "q"}).status_code == 400
    assert temp_stats.summary()["ratings_total"] == 0


def test_stats_page_and_json(temp_stats):
    c = make_client()
    temp_stats.add_rating(5, "q", "th")
    assert c.get("/stats").status_code == 200
    assert c.get("/stats.json").get_json()["ratings_total"] == 1


def test_screen_has_star_rating():
    js = make_client().get("/static/screen.js").data.decode("utf-8")
    assert "/rate" in js


# ---- โหมดรอ: วิดีโอวน ----
def test_attract_lists_videos(tmp_path, monkeypatch):
    vids = tmp_path / "videos"
    vids.mkdir()
    (vids / "b.mp4").write_bytes(b"x")
    (vids / "a.webm").write_bytes(b"x")
    (vids / "readme.txt").write_text("ไม่ใช่วิดีโอ", encoding="utf-8")
    monkeypatch.setattr(server, "VIDEO_DIR", vids)
    monkeypatch.setattr(server.config, "IDLE_VIDEO_SECONDS", 90)
    d = make_client().get("/attract").get_json()
    assert d["videos"] == ["/static/videos/a.webm", "/static/videos/b.mp4"]
    assert d["after"] == 90


def test_attract_without_video_folder(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "VIDEO_DIR", tmp_path / "ไม่มี")
    assert make_client().get("/attract").get_json()["videos"] == []


# ---- ประกาศตามเวลา ----
def test_announcements_due(tmp_path, monkeypatch):
    import json
    from datetime import datetime
    p = tmp_path / "announcements.json"
    p.write_text(json.dumps([{"เวลา": "08:00", "ข้อความ": "สวัสดีตอนเช้าค่ะ"}], ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(server.config, "ANNOUNCEMENTS_PATH", str(p))
    monkeypatch.setattr(server, "_now", lambda: datetime(2026, 11, 2, 8, 0, 5))
    d = make_client().get("/announcements/due").get_json()
    assert [a["text"] for a in d["due"]] == ["สวัสดีตอนเช้าค่ะ"]
    monkeypatch.setattr(server, "_now", lambda: datetime(2026, 11, 2, 9, 0, 5))
    assert make_client().get("/announcements/due").get_json()["due"] == []


# ---- /tts: เสียงพูด AI ----
@pytest.fixture
def tts_env(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(server.config, "TTS_CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(server.config, "AI_VOICE", True)
    monkeypatch.setattr(server.config, "VOICE_ENGINE", "edge")

    def fake_edge(text, lang):
        calls.append((text, lang))
        yield b"ID3"
        yield b"mp3data"
    monkeypatch.setattr(server, "edge_mp3_stream", fake_edge)
    return calls


def test_tts_streams_mp3_and_caches(tts_env):
    c = make_client()
    r = c.get("/tts", query_string={"text": "สวัสดีครับ", "lang": "th"})
    assert r.status_code == 200 and r.mimetype == "audio/mpeg" and r.get_data() == b"ID3mp3data"
    r2 = c.get("/tts", query_string={"text": "สวัสดีครับ", "lang": "th"})
    assert r2.status_code == 200 and r2.get_data() == b"ID3mp3data"
    assert tts_env == [("สวัสดีครับ", "th")]   # ครั้งที่สองใช้ไฟล์ที่เก็บไว้ ไม่สร้างซ้ำ


def test_tts_rejects_empty_or_too_long(tts_env):
    c = make_client()
    assert c.get("/tts", query_string={"text": ""}).status_code == 400
    assert c.get("/tts", query_string={"text": "ก" * 601}).status_code == 400


def test_tts_edge_failure_returns_503(tts_env, monkeypatch):
    def broken(text, lang):
        raise ConnectionError("no internet")
        yield b""
    monkeypatch.setattr(server, "edge_mp3_stream", broken)
    assert make_client().get("/tts", query_string={"text": "สวัสดี"}).status_code == 503


def test_tts_disabled_by_config(tts_env, monkeypatch):
    monkeypatch.setattr(server.config, "AI_VOICE", False)
    assert make_client().get("/tts", query_string={"text": "สวัสดี"}).status_code == 404


def test_tts_gemini_engine_quota_cools_down(tts_env, monkeypatch):
    monkeypatch.setattr(server.config, "VOICE_ENGINE", "gemini")
    monkeypatch.setattr(server.config, "GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(server, "_tts_off_until", 0.0)
    hits = []

    def boom(text, lang):
        hits.append(text)
        raise RuntimeError("429 RESOURCE_EXHAUSTED")
    monkeypatch.setattr(server, "speak_wav", boom)
    c = make_client()
    assert c.get("/tts", query_string={"text": "หนึ่ง"}).status_code == 503
    assert c.get("/tts", query_string={"text": "สอง"}).status_code == 503
    assert hits == ["หนึ่ง"]


def test_gemini_voice_gets_only_the_text(monkeypatch):
    import ai
    seen = []

    class Models:
        def generate_content_stream(self, model, contents, config):
            seen.append(contents)
            part = type("P", (), {"inline_data": type("D", (), {"data": b"\x00\x00"})()})()
            yield type("C", (), {"candidates": [type("X", (), {"content": type("Y", (), {"parts": [part]})()})()]})()
    monkeypatch.setattr(ai, "_gemini_client", lambda key: type("Cl", (), {"models": Models()})())
    assert b"".join(ai.speak_pcm_stream("สวัสดีครับ", "th")) == b"\x00\x00"
    assert seen == ["สวัสดีครับ"]   # ไม่มีคำสั่งนำหน้า (เคยโดนอ่านออกเสียง)


def test_screen_uses_ai_voice_with_local_fallback():
    js = make_client().get("/static/screen.js").data.decode("utf-8")
    assert "/tts?lang=" in js and "localSpeak" in js and "TTS_TIMEOUT_MS" in js
    assert "startAttract()" in js   # เปิดหน้าเว็บมาเข้าโหมดรอ
