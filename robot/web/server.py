"""
เซิร์ฟเวอร์เว็บของหุ่น "กล่องพูดได้"
รัน:  & $py web/server.py   (หรือดับเบิลคลิก web/run_web.bat)
หน้าที่: เสิร์ฟ 2 หน้า (จอใบหน้า + จอเนื้อหา), รับคำถามแล้วเรียกสมองเดิม (ask_ai),
และเก็บ/แจกสถานะกลางให้ 2 จอ sync กัน
"""
import os
import sys
from pathlib import Path

ROBOT_DIR = Path(__file__).resolve().parent.parent   # โฟลเดอร์ robot/
sys.path.insert(0, str(ROBOT_DIR))                   # ให้ import ai/database/config ได้
os.chdir(ROBOT_DIR)                                  # ให้ .env + college_data.json (path relative) ทำงาน

# คอนโซล Windows ที่ไม่ใช่ UTF-8 (cp1252) จะ crash ตอน print ภาษาไทย
# ถ้ารันตรงๆ โดยไม่ผ่าน run_web.bat — บังคับ UTF-8 ที่นี่เลยให้รันได้ทุกทาง
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

from flask import Flask, request, jsonify, send_from_directory, Response  # noqa: E402
import config                                                   # noqa: E402
from database import load_college_data, load_saraburi_data      # noqa: E402
from ai import ask_ai, ask_ai_stream, is_quota_error, speak_wav                            # noqa: E402
from wayfinding import wants_map                               # noqa: E402
from places import photos_for, menu_tree                       # noqa: E402
import json                                                    # noqa: E402
import queue                                                   # noqa: E402
from gpio_btn import GpioButton                                # noqa: E402
from arm import Arm                                            # noqa: E402
from stats import Stats                                        # noqa: E402
from announce import load_announcements, due_announcements    # noqa: E402
from qr import load_qr_codes, resolve as resolve_qr            # noqa: E402
from answer_cache import AnswerCache, replay_pieces            # noqa: E402
from datetime import datetime                                  # noqa: E402

STATIC_DIR = Path(__file__).resolve().parent / "static"
VIDEO_DIR = STATIC_DIR / "videos"          # วิดีโอโหมดรอ — วางไฟล์ .mp4/.webm ในนี้
VIDEO_EXTS = (".mp4", ".webm", ".ogv")
app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/static")

college_data = load_college_data()
saraburi_data = load_saraburi_data()
state = {"value": "idle", "lang": "th"}   # value: idle | greeting | listening | thinking | answering | error
LANGS = ("th", "en")                    # ภาษาที่จอเนื้อหาเลือก — จอใบหน้าใช้ตามนี้

button_queue: queue.Queue = queue.Queue()
_gpio = GpioButton(button_queue)
arm = Arm()
stats = Stats(ROBOT_DIR / config.STATS_DB_PATH)
# คำถามที่เคยตอบแล้ว ตอบซ้ำได้ทันที (แก้ไฟล์ข้อมูลเมื่อไหร่ คำตอบเก่าใช้ไม่ได้เอง)
answers = AnswerCache(config.ANSWER_CACHE_SECONDS, data_files=[
    ROBOT_DIR / config.COLLEGE_DATA_PATH, ROBOT_DIR / config.SARABURI_DATA_PATH, config.SAR_DATA_PATH])
_now = datetime.now   # แยกไว้ให้เทสต์แกล้งเปลี่ยนเวลาได้


def request_greet():
    """ให้หุ่นทักทาย (โบก + หน้ายิ้ม + พูด) — จอเนื้อหาได้สัญญาณ แล้วเรียก /greet กลับมาโบกแขน
    เซนเซอร์จับคน (เช่น อัลตราโซนิก) ในอนาคตให้เรียกฟังก์ชันนี้"""
    button_queue.put("greet")


def _make_sse_stream():
    yield "data: connected\n\n"
    while True:
        try:
            evt = button_queue.get(timeout=15)
            yield f"data: {evt}\n\n"
        except queue.Empty:
            yield ": heartbeat\n\n"


@app.get("/events")
def events():
    return Response(
        _make_sse_stream(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def missing_key_error():
    """เช็กว่า key ของเจ้า AI ที่เลือกใน config พร้อมใช้หรือยัง
    คืนข้อความวิธีแก้ (ภาษาไทย) ถ้ายังไม่พร้อม / คืน None ถ้าพร้อม"""
    if config.AI_PROVIDER == "claude":
        key, name, url = config.ANTHROPIC_API_KEY, "ANTHROPIC_API_KEY", "https://console.anthropic.com"
    else:
        key, name, url = config.GEMINI_API_KEY, "GEMINI_API_KEY", "https://aistudio.google.com/apikey"
    if not key.strip() or "xxxx" in key:   # ว่าง หรือยังเป็นค่าตัวอย่างจาก .env.example
        return (
            f"ยังไม่ได้ตั้งค่า {name} — เปิดไฟล์ robot/.env "
            f"(ถ้ายังไม่มี ให้คัดลอก .env.example เป็น .env) แล้วใส่ {name}=คีย์จริง "
            f"ขอคีย์ได้ที่ {url} จากนั้นปิดแล้วเปิดเซิร์ฟเวอร์ใหม่"
        )
    return None


@app.get("/")
@app.get("/screen")
def screen_page():
    return send_from_directory(STATIC_DIR, "screen.html")


@app.get("/face")
def face_page():
    return send_from_directory(STATIC_DIR, "face.html")


@app.route("/state", methods=["GET", "POST"])
def state_endpoint():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        new = data.get("state")
        if new:
            state["value"] = new
        if data.get("lang") in LANGS:
            state["lang"] = data["lang"]
        return jsonify(ok=True, state=state["value"], lang=state["lang"])
    return jsonify(state=state["value"], lang=state["lang"])


@app.post("/ask")
def ask():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    lang = data.get("lang") if data.get("lang") in LANGS else "th"
    problem = missing_key_error()
    if problem:
        state["value"] = "error"
        return jsonify(error=problem), 500
    stats.log_question(question, lang)
    state["value"] = "thinking"
    try:
        answer = answers.get(question, lang)
        if answer is None:
            answer = ask_ai(question, college_data, saraburi_data, lang=lang)   # สมองเดิม — กฎกันตอบมั่วอยู่ในนี้
            answers.put(question, lang, answer)
        state["value"] = "answering"
        result = {"answer": answer, "photos": []}
        if wants_map(question):
            result["image"] = "/static/map.jpg"   # ถามทางในวิทยาลัย → แผนผัง ไม่ต้องหารูปที่เที่ยว
        else:
            result["photos"] = photos_for(question, answer, saraburi_data, lang=lang)
        return jsonify(**result)
    except Exception as e:
        state["value"] = "error"
        return jsonify(error=str(e)), 500


_FRIENDLY = {
    "quota": {
        "th": "วันนี้มีคนถามเยอะจนโควตา AI หมดแล้วครับ 😅 ลองใหม่พรุ่งนี้ หรือติดต่อเจ้าหน้าที่ได้ที่ 0-3628-1295 นะครับ",
        "en": "So many questions today that the AI quota ran out 😅 Please try again tomorrow, or call our staff at 0-3628-1295.",
    },
    "busy": {
        "th": "ตอนนี้ระบบ AI ยุ่งมากครับ ⏳ รอสักครู่แล้วถามใหม่อีกครั้งนะครับ",
        "en": "The AI service is very busy right now ⏳ Please wait a moment and ask again.",
    },
}


def friendly_error(e: Exception, lang: str) -> str:
    """แปลง error ที่เจอบ่อยจาก AI ให้คนหน้าจออ่านเข้าใจ (อันอื่นโชว์ตามจริงไว้แก้ปัญหา)"""
    msg = str(e)
    if is_quota_error(e):
        return _FRIENDLY["quota"][lang]
    if "UNAVAILABLE" in msg or "503" in msg or "overloaded" in msg.lower() or "529" in msg:
        return _FRIENDLY["busy"][lang]
    return msg


@app.post("/ask/stream")
def ask_stream():
    """เหมือน /ask แต่ทยอยส่งคำตอบ — ส่งเป็น JSON บรรทัดละก้อน (NDJSON):
    {"t": "ข้อความท่อนใหม่"} ... แล้วจบด้วย {"done": true, "image": ..., "photos": [...]} หรือ {"error": "..."}"""
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    lang = data.get("lang") if data.get("lang") in LANGS else "th"
    problem = missing_key_error()
    if problem:
        state["value"] = "error"
        return jsonify(error=problem), 500
    stats.log_question(question, lang)
    state["value"] = "thinking"
    image = "/static/map.jpg" if wants_map(question) else None

    def generate():
        line = lambda obj: json.dumps(obj, ensure_ascii=False) + "\n"   # noqa: E731
        pieces = []
        try:
            cached = answers.get(question, lang)
            source = replay_pieces(cached) if cached else ask_ai_stream(question, college_data, saraburi_data, lang=lang)
            for piece in source:
                state["value"] = "answering"
                pieces.append(piece)
                yield line({"t": piece})
            state["value"] = "answering"
            if not cached:
                answers.put(question, lang, "".join(pieces))   # ตอบครบแล้วค่อยจำ (ขาดกลางทางไม่จำ)
            # หารูปจากคำตอบที่ต่อครบแล้ว (ชื่อสถานที่อาจถูกตัดคร่อมสองท่อน)
            photos = [] if image else photos_for(question, "".join(pieces), saraburi_data, lang=lang)
            yield line({"done": True, "image": image, "photos": photos})
        except Exception as e:
            state["value"] = "error"
            print(f"[ask/stream] {e}")   # ข้อความเต็มไว้ดูในหน้าต่างเซิร์ฟเวอร์
            yield line({"error": friendly_error(e, lang)})

    return Response(generate(), mimetype="application/x-ndjson",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.post("/greet")
def greet():
    """โบกมือ 1 รอบ (จอเนื้อหาเป็นคนเรียก พร้อมกับพูดคำทักทายเอง)"""
    return jsonify(ok=True, waving=arm.wave())


# ---- เสียงพูด AI: GET /tts?lang=th&text=… → ไฟล์เสียง (หน้าจอใช้ <audio src> เล่นได้ทันทีที่ท่อนแรกมาถึง) ----
# edge  : MP3 ทยอยส่งระหว่างสร้าง (ท่อนแรกราว 1–2 วิ)
# gemini: WAV ทั้งไฟล์ (ต้องรอสร้างเสร็จ)
# ทุกเสียงที่สร้างแล้วเก็บไฟล์ไว้ใช้ซ้ำ เช่น คำทักทาย/ประกาศ ไม่ต้องสร้างใหม่ทุกครั้ง
TTS_MAX_CHARS = 600
TTS_CACHE_FILES = 300                  # เก็บเสียงล่าสุดไม่เกินเท่านี้ไฟล์
TTS_QUOTA_COOLDOWN = 10 * 60           # (gemini) โควตาเสียงหมด → พัก 10 นาที ระหว่างนั้นหน้าจอใช้เสียงในเครื่อง
_tts_off_until = 0.0


def _tts_cache_path(text: str, lang: str) -> Path:
    import hashlib
    if config.VOICE_ENGINE == "gemini":
        voice, ext = config.GEMINI_TTS_VOICE, "wav"
    else:
        voice = config.EDGE_TTS_VOICE_EN if lang == "en" else config.EDGE_TTS_VOICE
        voice, ext = f"{voice}{config.EDGE_TTS_RATE}", "mp3"
    h = hashlib.sha1(f"v3|{config.VOICE_ENGINE}|{voice}|{lang}|{text}".encode("utf-8")).hexdigest()
    return Path(config.TTS_CACHE_DIR) / f"{h}.{ext}"


def _prune_tts_cache() -> None:
    files = sorted(Path(config.TTS_CACHE_DIR).glob("*.*"), key=lambda f: f.stat().st_mtime)
    for f in files[:-TTS_CACHE_FILES]:
        f.unlink(missing_ok=True)


def _save_tts(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".part")
    tmp.write_bytes(data)
    tmp.replace(path)
    _prune_tts_cache()


def edge_mp3_stream(text: str, lang: str):
    """ข้อความ → MP3 ทยอยเป็นท่อน (edge-tts เป็น async — วน event loop เองทีละท่อน)"""
    import asyncio
    import edge_tts
    voice = config.EDGE_TTS_VOICE_EN if lang == "en" else config.EDGE_TTS_VOICE
    agen = edge_tts.Communicate(text, voice, rate=config.EDGE_TTS_RATE).stream()
    loop = asyncio.new_event_loop()
    try:
        while True:
            try:
                chunk = loop.run_until_complete(agen.__anext__())
            except StopAsyncIteration:
                break
            if chunk.get("type") == "audio" and chunk.get("data"):
                yield chunk["data"]
    finally:
        loop.run_until_complete(agen.aclose())
        loop.close()


@app.get("/tts")
def tts():
    global _tts_off_until
    import time
    text = (request.args.get("text") or "").strip()
    lang = request.args.get("lang") if request.args.get("lang") in LANGS else "th"
    if not config.AI_VOICE:
        return jsonify(error="ปิดเสียง AI อยู่ (AI_VOICE = False)"), 404
    if not text or len(text) > TTS_MAX_CHARS:
        return jsonify(error=f"ข้อความต้องยาว 1–{TTS_MAX_CHARS} ตัวอักษร"), 400
    path = _tts_cache_path(text, lang)
    mime = "audio/wav" if path.suffix == ".wav" else "audio/mpeg"
    if path.exists():
        path.touch()
        return send_from_directory(path.parent, path.name, mimetype=mime)

    if config.VOICE_ENGINE == "gemini":
        if time.time() < _tts_off_until or missing_key_error():
            return jsonify(error="เสียง AI ใช้ไม่ได้ชั่วคราว"), 503
        try:
            wav = speak_wav(text, lang)
        except Exception as e:
            if is_quota_error(e):
                _tts_off_until = time.time() + TTS_QUOTA_COOLDOWN
            print("TTS error:", str(e)[:200])
            return jsonify(error="สร้างเสียงไม่สำเร็จ"), 503
        _save_tts(path, wav)
        return Response(wav, mimetype=mime)

    # edge: ขอท่อนแรกก่อนตอบ — ถ้าเชื่อมต่อไม่ได้ จะได้ตอบ 503 ให้หน้าจอใช้เสียงในเครื่องแทน
    stream = edge_mp3_stream(text, lang)
    try:
        first = next(stream)
    except Exception as e:
        print("TTS error:", str(e)[:200])
        return jsonify(error="สร้างเสียงไม่สำเร็จ"), 503

    def gen():
        got = [first]
        yield first
        try:
            for piece in stream:
                got.append(piece)
                yield piece
        except Exception as e:
            print("TTS error:", str(e)[:200])
            return
        _save_tts(path, b"".join(got))

    return Response(gen(), mimetype=mime, headers={"Cache-Control": "no-store"})


@app.post("/rate")
def rate():
    """ให้ดาว 1–5 กับคำตอบ (จอเนื้อหาส่งมาพร้อมคำถามของคำตอบนั้น)"""
    data = request.get_json(silent=True) or {}
    lang = data.get("lang") if data.get("lang") in LANGS else "th"
    try:
        stats.add_rating(data.get("stars"), data.get("question"), lang)
    except ValueError as e:
        return jsonify(ok=False, error=str(e)), 400
    return jsonify(ok=True)


@app.get("/stats")
def stats_page():
    """หน้าสถิติ (เปิดจากคอม/มือถือ เช่น http://<ip ของ Pi>:5000/stats)"""
    return send_from_directory(STATIC_DIR, "stats.html")


@app.get("/stats.json")
def stats_json():
    return jsonify(stats.summary(now=_now()))


@app.get("/attract")
def attract():
    """รายชื่อวิดีโอโหมดรอ + ว่างกี่วินาทีถึงเริ่มเล่น"""
    videos = []
    if VIDEO_DIR.is_dir():
        videos = [f"/static/videos/{f.name}" for f in sorted(VIDEO_DIR.iterdir())
                  if f.is_file() and f.suffix.lower() in VIDEO_EXTS]
    return jsonify(videos=videos, after=config.IDLE_VIDEO_SECONDS)


@app.get("/announcements/due")
def announcements_due():
    """ประกาศที่ถึงเวลาในนาทีนี้ — จอเนื้อหาถามทุก ~15 วินาที แล้วจำ id ที่พูดไปแล้ว"""
    items = load_announcements(ROBOT_DIR / config.ANNOUNCEMENTS_PATH)
    return jsonify(due=due_announcements(items, _now()))


@app.get("/qr")
def qr():
    """รหัสจากเครื่องสแกน QR → {"label", "question"} (จอส่งต่อให้ /ask/stream) หรือ {"label", "answer"} (พูดเลย)
    ไม่รู้จักรหัส → 404 — อ่านไฟล์ใหม่ทุกครั้ง แก้ qr_codes.json แล้วมีผลเลย"""
    lang = request.args.get("lang") if request.args.get("lang") in LANGS else "th"
    code = request.args.get("code", "")
    hit = resolve_qr(code, load_qr_codes(ROBOT_DIR / config.QR_CODES_PATH), lang)
    if not hit:
        print(f"[qr] ไม่รู้จักรหัส {code!r}", flush=True)   # ไว้ดูว่า QR ไหนยังไม่ได้ใส่ในไฟล์
        return jsonify(error="unknown"), 404
    if "answer" in hit:   # คำตอบตายตัวไม่ผ่าน /ask จึงนับสถิติที่นี่
        stats.log_question(f"[QR] {hit['label']}", lang)
    return jsonify(**hit)


@app.get("/menu")
def menu():
    """โครงเมนูที่เที่ยว/ของฝาก — หน้าจอโหลดครั้งเดียว ไม่เรียก AI"""
    return jsonify(menu_tree(saraburi_data))


def lan_ips():
    """IP ของเครื่องนี้ในวง Wi-Fi/LAN (ไว้บอกว่าเครื่องอื่นต้องพิมพ์อะไร)"""
    import socket
    ips = set()
    try:   # วิธีนี้ไม่ส่งข้อมูลออกจริง แค่ถามระบบว่าจะออกเน็ตทางการ์ดไหน
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ips.add(s.getsockname()[0])
    except OSError:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ips.add(info[4][0])
    except OSError:
        pass
    return sorted(ip for ip in ips if not ip.startswith("127."))


def main():
    problem = missing_key_error()
    if problem:
        print("!" * 70)
        print("⚠  " + problem)
        print("!" * 70)
    port = config.WEB_PORT
    print(f"เปิดหุ่นที่  http://127.0.0.1:{port}/screen  และ  /face")
    if config.WEB_HOST == "0.0.0.0":
        for ip in lan_ips():
            print(f"มือถือ/คอมเครื่องอื่น (Wi-Fi เดียวกัน) ดูสถิติที่  http://{ip}:{port}/stats")
    app.run(host=config.WEB_HOST, port=config.WEB_PORT, threaded=True)


if __name__ == "__main__":
    main()
