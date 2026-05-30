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

from flask import Flask, request, jsonify, send_from_directory  # noqa: E402
import config                                                   # noqa: E402
from database import load_college_data                          # noqa: E402
from ai import ask_ai                                           # noqa: E402

STATIC_DIR = Path(__file__).resolve().parent / "static"
app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/static")

college_data = load_college_data()
state = {"value": "idle"}   # idle | listening | thinking | answering | error


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
    state["value"] = "thinking"
    try:
        answer = ask_ai(question, college_data)   # สมองเดิม — กฎกันตอบมั่วอยู่ในนี้
        state["value"] = "answering"
        return jsonify(answer=answer)
    except Exception as e:
        state["value"] = "error"
        return jsonify(error=str(e)), 500


def main():
    print(f"เปิดหุ่นที่  http://{config.WEB_HOST}:{config.WEB_PORT}/screen  และ  /face")
    app.run(host=config.WEB_HOST, port=config.WEB_PORT, threaded=True)


if __name__ == "__main__":
    main()
