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

from flask import Flask, request, jsonify, send_from_directory  # noqa: E402
import config                                                   # noqa: E402
from database import load_college_data                          # noqa: E402
from ai import ask_ai                                           # noqa: E402
from wayfinding import wants_map                               # noqa: E402

STATIC_DIR = Path(__file__).resolve().parent / "static"
app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/static")

college_data = load_college_data()
state = {"value": "idle"}   # idle | listening | thinking | answering | error


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
        return jsonify(ok=True, state=state["value"])
    return jsonify(state=state["value"])


@app.post("/ask")
def ask():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    problem = missing_key_error()
    if problem:
        state["value"] = "error"
        return jsonify(error=problem), 500
    state["value"] = "thinking"
    try:
        answer = ask_ai(question, college_data)   # สมองเดิม — กฎกันตอบมั่วอยู่ในนี้
        state["value"] = "answering"
        result = {"answer": answer}
        if wants_map(question):
            result["image"] = "/static/map.jpg"
        return jsonify(**result)
    except Exception as e:
        state["value"] = "error"
        return jsonify(error=str(e)), 500


def main():
    problem = missing_key_error()
    if problem:
        print("!" * 70)
        print("⚠  " + problem)
        print("!" * 70)
    print(f"เปิดหุ่นที่  http://{config.WEB_HOST}:{config.WEB_PORT}/screen  และ  /face")
    app.run(host=config.WEB_HOST, port=config.WEB_PORT, threaded=True)


if __name__ == "__main__":
    main()
