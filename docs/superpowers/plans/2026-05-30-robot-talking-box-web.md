# กล่องพูดได้ (เวอร์ชันเว็บ) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ทำให้หุ่น "กล่องพูดได้" ใช้งานได้จริงบนคอม — พูดหรือพิมพ์คำถามเรื่องวิทยาลัย แล้วหุ่นพูดตอบ + แสดงคำตอบบนจอ + ใบหน้าแสดงอารมณ์ โดยตอบจากฐานข้อมูลเท่านั้น (ไม่ตอบมั่ว)

**Architecture:** เว็บแอป 3 ชั้น — เบราว์เซอร์ 2 หน้า (จอใบหน้า display-only + จอเนื้อหาที่คุมไมค์/พิมพ์/แชท/พูด) คุยกับเซิร์ฟเวอร์ Flask บางๆ ที่เรียก "สมอง" เดิม (`ask_ai`) และเก็บสถานะกลางให้ 2 จอ sync กันผ่าน polling เสียงไทยฟัง/พูดด้วย Web Speech API ในเบราว์เซอร์ (ฟรี) สมองเดิม (`ai.py`/`database.py`/`college_data.json`) ไม่แตะ

**Tech Stack:** Python 3.14 + Flask · HTML/CSS/JS ล้วน (ไม่ใช้ Node) · Web Speech API (`SpeechRecognition` + `speechSynthesis`, `th-TH`) · pytest (เทสต์เซิร์ฟเวอร์)

**อ้างอิงสเปก:** `docs/superpowers/specs/2026-05-29-robot-talking-box-web-design.md`
**ฐาน UI:** `mockups/face.html`, `mockups/screen.html` (ดีไซน์ผ่านแล้ว — งานหน้าบ้านคือ "ก๊อปจาก mockup แล้วถอดส่วน demo ออก + ต่อสายเข้าเซิร์ฟเวอร์")

---

## หมายเหตุเครื่องนี้ (Windows) — ใช้ทุกคำสั่ง

Python ไม่อยู่ใน PATH ต้องเรียก full path เสมอ และตั้ง UTF-8 ก่อนรัน (ดู memory `python-env-windows`).
รันคำสั่งทั้งหมด **จากโฟลเดอร์ `robot/`** ใน PowerShell:

```powershell
$py = "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe"
$env:PYTHONUTF8 = "1"; $env:PYTHONIOENCODING = "utf-8"
# ตัวอย่าง:  & $py -m pytest web/test_server.py -v
```

> เทสต์ทั้งหมด mock `ask_ai` จึง **ไม่ยิง API จริง / ไม่ใช้เน็ต / ไม่กินโควตา**

---

## File Structure

ของเดิม (สมอง) — **ไม่แตะ:** `robot/ai.py`, `robot/database.py`, `robot/college_data.json`

| ไฟล์ | สร้าง/แก้ | หน้าที่ |
|------|----------|---------|
| `robot/config.py` | แก้ (เพิ่มท้ายไฟล์) | เพิ่ม `WEB_HOST`, `WEB_PORT`, `SPEECH_LANG` |
| `robot/requirements.txt` | แก้ | เพิ่ม `flask` |
| `robot/web/server.py` | สร้าง | Flask: เสิร์ฟ 2 หน้า + `/ask` (เรียก `ask_ai`) + `/state` (เก็บ/แจกสถานะ) |
| `robot/web/test_server.py` | สร้าง | เทสต์เซิร์ฟเวอร์ (Flask test client, mock `ask_ai`) |
| `robot/web/static/face.html` | สร้าง (จาก mockup) | จอใบหน้า markup+CSS, ลิงก์ `face.js` |
| `robot/web/static/face.js` | สร้าง | poll `/state` → แสดงอารมณ์ใบหน้า |
| `robot/web/static/screen.html` | สร้าง (จาก mockup) | จอเนื้อหา markup+CSS, ลิงก์ `screen.js` |
| `robot/web/static/screen.js` | สร้าง | ไมค์ (STT) + พิมพ์ + เรียก `/ask` + พูด (TTS) + แจ้ง `/state` |
| `robot/web/run_web.bat` | สร้าง | ดับเบิลคลิกเปิดเซิร์ฟเวอร์ (ตั้ง UTF-8 + full python path) |
| `robot/README.md` | แก้ | เพิ่มวิธีรันเวอร์ชันเว็บ |

> **CSS อยู่ inline ในแต่ละ .html** (face/screen หน้าตาคนละโทน ไม่ค่อย overlap — เก็บไว้ในไฟล์ตัวเองอ่านง่ายกว่า แยกเฉพาะ JS ออกมา) ถือเป็นการปรับเล็กน้อยจากสเปกที่เขียน `style.css` ร่วม

---

## Task 1: เพิ่ม dependency + ค่า config เว็บ

**Files:**
- Modify: `robot/requirements.txt`
- Modify: `robot/config.py` (เพิ่มท้ายไฟล์)

- [ ] **Step 1: เพิ่ม flask ใน requirements.txt**

แก้บล็อก "เฟส 1-2" ให้เป็น:

```
# เฟส 1-2
anthropic>=0.40.0          # ใช้เมื่อ AI_PROVIDER = "claude"
google-genai>=1.0.0        # ใช้เมื่อ AI_PROVIDER = "gemini" (ฟรี)
python-dotenv>=1.0.0
flask>=3.0.0               # เซิร์ฟเวอร์เว็บของกล่องพูดได้
```

- [ ] **Step 2: เพิ่มค่า config เว็บ** ต่อท้าย `robot/config.py`

```python

# --- ตั้งค่าเว็บ (เฟสกล่องพูดได้) ---
WEB_HOST = "127.0.0.1"     # เปิดเฉพาะเครื่องตัวเอง
WEB_PORT = 5000
SPEECH_LANG = "th-TH"      # ภาษาเสียงฟัง/พูดในเบราว์เซอร์
```

- [ ] **Step 3: ติดตั้ง flask + pytest**

```powershell
& $py -m pip install flask pytest
```
Expected: ลงท้าย `Successfully installed flask-... pytest-...` (ถ้าเจอ UnicodeEncodeError ตอน print ไม่เป็นไร ติดตั้งสำเร็จแล้ว)

- [ ] **Step 4: ยืนยัน config โหลดได้** (รันจาก `robot/`)

```powershell
& $py -c "import config; print(config.WEB_PORT, config.SPEECH_LANG)"
```
Expected: `5000 th-TH`

- [ ] **Step 5: Commit**

```powershell
git add robot/requirements.txt robot/config.py
git commit -m "feat(web): add flask dependency and web config values

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 2: เซิร์ฟเวอร์ + endpoint `/state` (เก็บ/แจกสถานะ)

**Files:**
- Create: `robot/web/server.py`
- Create: `robot/web/test_server.py`

- [ ] **Step 1: เขียนเทสต์ที่ยังไม่ผ่าน** — สร้าง `robot/web/test_server.py`

```python
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
```

- [ ] **Step 2: รันเทสต์ ดูว่า fail**

```powershell
& $py -m pytest web/test_server.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'server'` (ยังไม่ได้สร้าง)

- [ ] **Step 3: สร้าง `robot/web/server.py`** (เฉพาะโครง + `/state`)

```python
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


@app.route("/state", methods=["GET", "POST"])
def state_endpoint():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        new = data.get("state")
        if new:
            state["value"] = new
        return jsonify(ok=True, state=state["value"])
    return jsonify(state=state["value"])


def main():
    print(f"เปิดหุ่นที่  http://{config.WEB_HOST}:{config.WEB_PORT}/screen  และ  /face")
    app.run(host=config.WEB_HOST, port=config.WEB_PORT, threaded=True)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: รันเทสต์ ดูว่าผ่าน**

```powershell
& $py -m pytest web/test_server.py -v
```
Expected: PASS 2 ตัว (`test_state_default_is_idle`, `test_post_state_updates_value`)

- [ ] **Step 5: Commit**

```powershell
git add robot/web/server.py robot/web/test_server.py
git commit -m "feat(web): flask server skeleton with /state endpoint

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 3: endpoint `/ask` — เรียกสมองเดิม + กันพลาด

**Files:**
- Modify: `robot/web/server.py` (เพิ่ม route `/ask`)
- Modify: `robot/web/test_server.py` (เพิ่มเทสต์)

- [ ] **Step 1: เพิ่มเทสต์** ต่อท้าย `robot/web/test_server.py`

```python
def test_ask_returns_answer_and_sets_answering(monkeypatch):
    c = make_client()
    # mock สมองไม่ให้ยิง API จริง (monkeypatch คืนค่าเดิมให้อัตโนมัติหลังจบเทสต์)
    monkeypatch.setattr(server, "ask_ai", lambda question, data: f"ตอบ: {question}")
    r = c.post("/ask", json={"question": "เปิดสอนอะไร"})
    assert r.status_code == 200
    assert r.get_json()["answer"] == "ตอบ: เปิดสอนอะไร"
    assert server.state["value"] == "answering"


def test_ask_error_sets_error_state_and_500(monkeypatch):
    c = make_client()

    def boom(question, data):
        raise RuntimeError("เน็ตล่ม")

    monkeypatch.setattr(server, "ask_ai", boom)
    r = c.post("/ask", json={"question": "x"})
    assert r.status_code == 500
    assert "error" in r.get_json()
    assert server.state["value"] == "error"
```

- [ ] **Step 2: รันเทสต์ใหม่ ดูว่า 2 ตัวใหม่ fail**

```powershell
& $py -m pytest web/test_server.py -v
```
Expected: FAIL ที่ 2 ตัวใหม่ (404 เพราะยังไม่มี route `/ask`)

- [ ] **Step 3: เพิ่ม route `/ask`** ใน `robot/web/server.py` (วางก่อน `def main()`)

```python
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
```

- [ ] **Step 4: รันเทสต์ ดูว่าผ่านหมด**

```powershell
& $py -m pytest web/test_server.py -v
```
Expected: PASS ทั้ง 4 ตัว

- [ ] **Step 5: Commit**

```powershell
git add robot/web/server.py robot/web/test_server.py
git commit -m "feat(web): add /ask endpoint calling ask_ai with error handling

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 4: เสิร์ฟ 2 หน้าเว็บ (จาก mockup) + เทสต์ว่าหน้าเสิร์ฟได้

**Files:**
- Modify: `robot/web/server.py` (เพิ่ม route `/`, `/screen`, `/face`)
- Create: `robot/web/static/face.html` (ก๊อปจาก `mockups/face.html`)
- Create: `robot/web/static/screen.html` (ก๊อปจาก `mockups/screen.html`)
- Modify: `robot/web/test_server.py` (เพิ่มเทสต์ serving)

- [ ] **Step 1: เพิ่มเทสต์ serving** ต่อท้าย `robot/web/test_server.py`

```python
def test_pages_are_served():
    c = make_client()
    face = c.get("/face")
    screen = c.get("/screen")
    assert face.status_code == 200
    assert b"eye-ball" in face.data        # มาร์กเกอร์ของจอใบหน้า
    assert screen.status_code == 200
    assert b'id="mic"' in screen.data      # มาร์กเกอร์ของจอเนื้อหา
```

- [ ] **Step 2: รันเทสต์ ดูว่า fail** (ยังไม่มีไฟล์ html + route)

```powershell
& $py -m pytest web/test_server.py::test_pages_are_served -v
```
Expected: FAIL (404)

- [ ] **Step 3: เพิ่ม route เสิร์ฟหน้า** ใน `robot/web/server.py` (วางก่อน `/state`)

```python
@app.get("/")
@app.get("/screen")
def screen_page():
    return send_from_directory(STATIC_DIR, "screen.html")


@app.get("/face")
def face_page():
    return send_from_directory(STATIC_DIR, "face.html")
```

- [ ] **Step 4: สร้าง `robot/web/static/face.html` จาก mockup**

ก๊อปเนื้อหา `mockups/face.html` มาทั้งหมด แล้วแก้ 3 จุด:
1. แท็ก body: `<body class="state-idle">` → `<body class="page-face state-idle">`
2. **ลบ** บล็อกแผง demo ทั้งก้อน: `<div class="demo"> ... </div>` และ `<div class="hint">...</div>`
3. **ลบ** บล็อก `<script> ... </script>` ทั้งหมด แล้วใส่แทนด้วย:
   ```html
   <script src="/static/face.js"></script>
   ```
(CSS เดิมใน `<style>` เก็บไว้เหมือนเดิม — กฎ `.demo`/`.hint` ที่ไม่ถูกใช้แล้วจะลบหรือคงไว้ก็ได้)

- [ ] **Step 5: สร้าง `robot/web/static/screen.html` จาก mockup**

ก๊อปเนื้อหา `mockups/screen.html` มาทั้งหมด แล้วแก้:
1. แท็ก body: `<body class="state-idle">` → `<body class="page-screen state-idle">`
2. **ลบ** `<div class="tag">...</div>` และ `<div class="demo"> ... </div>`
3. ใน `<main class="chat" id="chat">` **ลบฟองตัวอย่าง 2 อันหลัง** (อัน `msg user` "วิทยาลัยเปิดสอนสาขาอะไรบ้าง" และ `msg bot` ที่ตอบ) — **เก็บเฉพาะฟองทักทายอันแรก** ของบอท
4. **ลบ** บล็อก `<script> ... </script>` ทั้งหมด แล้วใส่แทนด้วย:
   ```html
   <script src="/static/screen.js"></script>
   ```

- [ ] **Step 6: รันเทสต์ ดูว่าผ่าน**

```powershell
& $py -m pytest web/test_server.py -v
```
Expected: PASS ทั้ง 5 ตัว

- [ ] **Step 7: Commit**

```powershell
git add robot/web/server.py robot/web/static/face.html robot/web/static/screen.html robot/web/test_server.py
git commit -m "feat(web): serve face and screen pages from mockup-derived html

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 5: `face.js` — จอใบหน้า poll สถานะมาแสดงอารมณ์

**Files:**
- Create: `robot/web/static/face.js`

- [ ] **Step 1: สร้าง `robot/web/static/face.js`**

```javascript
// จอใบหน้า: ดึงสถานะจากเซิร์ฟเวอร์มาแสดงอารมณ์ (อ่านอย่างเดียว ไม่ยุ่งเสียง/สมอง)
const LABELS = {
  idle: "พร้อมรับคำถาม", listening: "กำลังฟัง…", thinking: "กำลังคิด…",
  answering: "กำลังตอบ", error: "ขออภัย เกิดข้อผิดพลาด",
};
const txt = document.querySelector(".status-text");
let current = null;

function apply(state) {
  if (state === current) return;
  current = state;
  document.body.className = "page-face state-" + state;
  if (txt) txt.textContent = LABELS[state] || state;
}

async function poll() {
  try {
    const r = await fetch("/state");
    const d = await r.json();
    if (d && d.state) apply(d.state);
  } catch (e) {
    /* เซิร์ฟเวอร์ยังไม่พร้อม ค่อยลองใหม่รอบหน้า */
  }
}

apply("idle");
setInterval(poll, 250);
```

- [ ] **Step 2: ทดสอบด้วยมือ** — รันเซิร์ฟเวอร์ (จาก `robot/`) แล้วเปิดจอใบหน้า

```powershell
& $py web/server.py
```
เปิดเบราว์เซอร์ (Chrome/Edge) ที่ `http://127.0.0.1:5000/face`
อีกหน้าต่าง PowerShell สั่งเปลี่ยนสถานะแล้วดูใบหน้าเปลี่ยน:
```powershell
curl.exe -X POST http://127.0.0.1:5000/state -H "Content-Type: application/json" -d "{\"state\":\"listening\"}"
curl.exe -X POST http://127.0.0.1:5000/state -H "Content-Type: application/json" -d "{\"state\":\"thinking\"}"
curl.exe -X POST http://127.0.0.1:5000/state -H "Content-Type: application/json" -d "{\"state\":\"error\"}"
```
Expected (สังเกตในเบราว์เซอร์): ตาเปลี่ยนสี/ท่าทางตามสถานะภายใน ~0.25 วิ (ฟัง=ฟ้าเบิ่ง, คิด=เหลืองมองขึ้น, ผิดพลาด=แดงหน้าเศร้า) แล้ว `Ctrl+C` ปิดเซิร์ฟเวอร์

- [ ] **Step 3: Commit**

```powershell
git add robot/web/static/face.js
git commit -m "feat(web): face screen polls /state to show emotion

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 6: `screen.js` — ไมค์/พิมพ์ → ถามสมอง → พูดตอบ (หัวใจ)

**Files:**
- Create: `robot/web/static/screen.js`

- [ ] **Step 1: สร้าง `robot/web/static/screen.js`**

```javascript
// จอเนื้อหา: คุมไมค์ (STT) + พิมพ์ → เรียก /ask → แสดงคำตอบ + พูด (TTS) + แจ้ง /state
const LABELS = {
  idle: "พร้อมรับคำถาม", listening: "กำลังฟัง…", thinking: "กำลังคิด…",
  answering: "กำลังตอบ", error: "เกิดข้อผิดพลาด",
};
const SPEECH_LANG = "th-TH";
const chat = document.getElementById("chat");
const ledText = document.querySelector(".led-text");
const ledDot = document.querySelector(".led .d");
const mic = document.getElementById("mic");
const micLabel = document.getElementById("micLabel");

// ---- สถานะ: อัปเดต UI ตัวเอง + แจ้งเซิร์ฟเวอร์ (ให้จอใบหน้า sync) ----
function setState(s) {
  document.body.className = "page-screen state-" + s;
  if (ledText) ledText.textContent = LABELS[s] || s;
  if (ledDot) ledDot.classList.toggle("live", s !== "idle");
  if (mic) mic.classList.toggle("live", s === "listening");
  if (micLabel) micLabel.textContent = s === "listening" ? "กำลังฟัง… (แตะเพื่อหยุด)" : "กดเพื่อพูด";
  fetch("/state", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ state: s }),
  }).catch(() => {});
}

// ---- ฟองข้อความ ----
function escapeHtml(s) { const d = document.createElement("div"); d.textContent = s; return d.innerHTML; }
function addMsg(role, text, opts = {}) {
  const m = document.createElement("div");
  m.className = "msg " + role;
  const tag = opts.voice ? '<span class="mic-tag">🎤 พูด</span>' : "";
  const ava = role === "bot" ? '<div class="ava"><i></i><i></i></div>' : "";
  m.innerHTML = ava + '<div class="bubble' + (opts.warn ? " warn" : "") + '">' + tag + escapeHtml(text) + "</div>";
  chat.appendChild(m); chat.scrollTop = chat.scrollHeight;
}
function typing(on) {
  let t = document.getElementById("typing");
  if (on && !t) {
    t = document.createElement("div"); t.id = "typing"; t.className = "msg bot typing";
    t.innerHTML = '<div class="ava"><i></i><i></i></div><div class="bubble"><i></i><i></i><i></i></div>';
    chat.appendChild(t); chat.scrollTop = chat.scrollHeight;
  } else if (!on && t) { t.remove(); }
}

// ---- พูดออกเสียง (TTS) ----
function speak(text, onEnd) {
  if (!("speechSynthesis" in window)) { if (onEnd) onEnd(); return; }
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = SPEECH_LANG;
  const thVoice = window.speechSynthesis.getVoices().find(v => v.lang && v.lang.toLowerCase().startsWith("th"));
  if (thVoice) u.voice = thVoice;
  u.onend = () => onEnd && onEnd();
  u.onerror = () => onEnd && onEnd();
  window.speechSynthesis.speak(u);
}

// ---- ถาม-ตอบหลัก ----
async function ask(question, opts = {}) {
  question = (question || "").trim();
  if (!question) { setState("idle"); return; }
  addMsg("user", question, { voice: !!opts.voice });
  setState("thinking"); typing(true);
  try {
    const r = await fetch("/ask", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const d = await r.json();
    typing(false);
    if (!r.ok) throw new Error(d.error || "เซิร์ฟเวอร์ขัดข้อง");
    const answer = d.answer || "";
    addMsg("bot", answer);
    setState("answering");
    speak(answer, () => setState("idle"));
  } catch (e) {
    typing(false);
    addMsg("bot", "ขออภัยค่ะ ระบบขัดข้อง ลองใหม่อีกครั้งนะคะ", { warn: true });
    setState("error");
    setTimeout(() => setState("idle"), 2500);
  }
}

// ---- ไมค์ (STT) ----
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
let recog = null, listening = false;
if (SR) {
  recog = new SR();
  recog.lang = SPEECH_LANG; recog.interimResults = false; recog.maxAlternatives = 1;
  recog.onresult = (e) => { ask(e.results[0][0].transcript, { voice: true }); };
  recog.onerror = () => { listening = false; addMsg("bot", "ไม่ได้ยินค่ะ ลองพิมพ์คำถามดูไหมคะ 🙏", { warn: true }); setState("idle"); };
  recog.onend = () => { listening = false; if (document.body.classList.contains("state-listening")) setState("idle"); };
  mic.addEventListener("click", () => {
    if (listening) { recog.stop(); listening = false; setState("idle"); return; }
    setState("listening"); listening = true;
    try { recog.start(); } catch (e) { listening = false; setState("idle"); }
  });
} else {
  mic.style.display = "none";
  if (micLabel) micLabel.textContent = "พิมพ์คำถามด้านล่างได้เลย";
}

// ---- พิมพ์ (ตัวสำรอง) ----
document.getElementById("composer").addEventListener("submit", (e) => {
  e.preventDefault();
  const inp = document.getElementById("q");
  const q = inp.value; inp.value = "";
  ask(q, { voice: false });
});

setState("idle");
```

- [ ] **Step 2: ทดสอบ end-to-end ด้วยมือ** (ต้องมี `GEMINI_API_KEY` ใน `robot/.env` แล้ว)

```powershell
& $py web/server.py
```
เปิด `http://127.0.0.1:5000/screen` (Chrome/Edge):
1. **พิมพ์** "วิทยาลัยเปิดสอนสาขาอะไรบ้าง" กด Enter → ขึ้นฟองผู้ใช้ → "กำลังคิด…" → ฟองคำตอบจากสมองจริง + หุ่นพูดออกเสียงไทย
2. เปิด `http://127.0.0.1:5000/face` อีกหน้าต่างคู่กัน → ตอนถาม ใบหน้าเปลี่ยน คิด→ตอบ ตาม (sync ผ่าน /state)
3. กดปุ่ม **ไมค์** แล้วพูด → ได้คำถามจากเสียง + ตอบกลับ (Chrome/Edge เท่านั้น)

- [ ] **Step 3: ทดสอบหัวใจ "กันตอบมั่ว"**

พิมพ์ "มีหอพักไหม" → Expected: ตอบทำนอง "ยังไม่มีข้อมูล… ติดต่อเจ้าหน้าที่ โทร 0-3628-1295" (ไม่แต่งข้อมูลหอพักขึ้นมาเอง)
พิมพ์ "เบอร์โทรวิทยาลัย" → Expected: ตอบ "0-3628-1295" (ข้อมูลที่มีในฐานข้อมูล) แล้ว `Ctrl+C` ปิด

- [ ] **Step 4: Commit**

```powershell
git add robot/web/static/screen.js
git commit -m "feat(web): wire mic/text to /ask with Thai speech and state sync

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 7: สคริปต์รัน + README + เก็บงาน

**Files:**
- Create: `robot/web/run_web.bat`
- Modify: `robot/README.md`

- [ ] **Step 1: สร้าง `robot/web/run_web.bat`** (ดับเบิลคลิกเปิดเซิร์ฟเวอร์)

```bat
@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0\.."
"%LOCALAPPDATA%\Programs\Python\Python314\python.exe" web\server.py
pause
```

- [ ] **Step 2: ทดสอบ run_web.bat** — ดับเบิลคลิกไฟล์ (หรือรันใน PowerShell)

```powershell
& "$PWD\web\run_web.bat"
```
Expected: ขึ้น `เปิดหุ่นที่  http://127.0.0.1:5000/screen  และ  /face` แล้วเปิด `/screen` ในเบราว์เซอร์ใช้งานได้ → ปิดด้วย `Ctrl+C`

- [ ] **Step 3: เพิ่มวิธีรันเวอร์ชันเว็บใน `robot/README.md`** (เพิ่มหัวข้อใหม่ก่อน "## อัปเดตข้อมูลวิทยาลัย")

```markdown
## รันเวอร์ชัน "กล่องพูดได้" (เว็บ — พูด/พิมพ์ได้)

ติดตั้งเพิ่ม (ครั้งแรกครั้งเดียว): `pip install -r requirements.txt`

**วิธีง่ายสุด:** ดับเบิลคลิก `web/run_web.bat`
แล้วเปิดเบราว์เซอร์ (Chrome/Edge):
- จอเนื้อหา/แชท: http://127.0.0.1:5000/screen
- จอใบหน้า: http://127.0.0.1:5000/face

กดปุ่มไมค์เพื่อพูด หรือพิมพ์คำถามก็ได้ หุ่นจะตอบด้วยเสียงไทย + แสดงบนจอ
(ภาษาเสียงใช้ Web Speech API ของเบราว์เซอร์ — รองรับดีใน Chrome/Edge)
```

- [ ] **Step 4: รันเทสต์ทั้งหมดอีกรอบ ปิดท้าย**

```powershell
& $py -m pytest web/test_server.py -v
```
Expected: PASS ทั้ง 5 ตัว

- [ ] **Step 5: Commit**

```powershell
git add robot/web/run_web.bat robot/README.md
git commit -m "feat(web): add run_web.bat launcher and README instructions

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## เกณฑ์ว่าเสร็จ (Definition of Done)

- [ ] `& $py -m pytest web/test_server.py -v` ผ่านครบ 5 ตัว
- [ ] ดับเบิลคลิก `web/run_web.bat` แล้วเปิด `/screen` พิมพ์คำถามได้คำตอบจริงจากสมอง + หุ่นพูดออกเสียงไทย
- [ ] เปิด `/face` คู่กัน ใบหน้าเปลี่ยนอารมณ์ตามจังหวะ ฟัง→คิด→ตอบ
- [ ] กดไมค์พูดภาษาไทยใน Chrome/Edge แล้วได้คำถาม + คำตอบ
- [ ] เคสกันตอบมั่ว: ถามเรื่องไม่มีข้อมูล (หอพัก) หุ่นตอบ "ไม่มีข้อมูล + ติดต่อเจ้าหน้าที่" ไม่แต่งเอง
- [ ] เบราว์เซอร์ที่ไม่รองรับเสียง ปุ่มไมค์ซ่อน ใช้ช่องพิมพ์แทนได้
- [ ] สมองเดิม (`ai.py`/`database.py`/`college_data.json`) ไม่ถูกแก้

## ขอบเขตที่ไม่อยู่ในแผนนี้ (เฟสถัดไป)

ตัวกล่อง/ฮาร์ดแวร์จริง, แยก 2 จอกายภาพ, ไฟ LED จริง, อัปเกรด Google Cloud STT/TTS, เปิด kiosk อัตโนมัติตอนบูต, เก็บ log คำถาม-คำตอบ
