# Phase 2: Web Interface Production Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ทำให้ web interface ทำงานบน Raspberry Pi 5 แบบ production — บูทแล้วระบบ start อัตโนมัติ, ปุ่ม GPIO บนตัวหุ่น trigger STT ได้, Chromium เปิด fullscreen kiosk

**Architecture:** GPIO button ถูกตรวจจับใน Python thread → ส่ง event เข้า `queue.Queue` → `/events` SSE endpoint ส่งให้ browser → `screen.js` รับแล้ว trigger `mic.click()`. Systemd service เริ่ม Flask ทุกครั้งที่ Pi บูท, LXDE autostart เปิด Chromium kiosk fullscreen

**Tech Stack:** Python 3.14, Flask, RPi.GPIO (Pi เท่านั้น), pytest, vanilla JS, systemd, LXDE

## Global Constraints

- รันเทสต์จากโฟลเดอร์ `robot/`: `python -m pytest web/test_server.py -v`
- `SIMULATOR_MODE = True` ใน `config.py` ตลอดการพัฒนาบน Windows — ห้าม import RPi.GPIO ที่ top-level
- ไม่แตะ `ai.py`, `face.html`, `face.js`, `wayfinding.py`, `database.py`
- ทุก commit ต้องผ่าน tests ทั้งหมด (ปัจจุบัน 16 tests)
- ไฟล์ autostart (`robot.service`, `robot-kiosk.desktop`, `install_autostart.sh`) ไม่มี unit test — test ด้วยการอ่านเนื้อหาแทน

---

## File Map

| ไฟล์ | สถานะ | บทบาท |
|------|-------|-------|
| `robot/config.py` | แก้ | เพิ่ม `GPIO_BUTTON_PIN = 18` |
| `robot/web/gpio_btn.py` | ใหม่ | `GpioButton` class: ตรวจ GPIO pin, push "mic-start" เข้า queue |
| `robot/web/server.py` | แก้ | เพิ่ม `button_queue`, `_make_sse_stream()`, route `/events` |
| `robot/web/static/screen.js` | แก้ | เพิ่ม `EventSource('/events')` listener ท้ายไฟล์ |
| `robot/web/robot.service` | ใหม่ | systemd unit เริ่ม Flask อัตโนมัติตอนบูท |
| `robot/web/robot-kiosk.desktop` | ใหม่ | LXDE autostart เปิด Chromium fullscreen kiosk |
| `robot/web/install_autostart.sh` | ใหม่ | script ติดตั้งทั้ง 2 ไฟล์บน Pi ครั้งเดียว |
| `robot/web/test_server.py` | แก้ | เพิ่ม 2 tests: gpio_btn init + /events endpoint |

---

### Task 1: gpio_btn.py + GPIO_BUTTON_PIN ใน config

**Files:**
- Modify: `robot/config.py`
- Create: `robot/web/gpio_btn.py`
- Modify: `robot/web/test_server.py`

**Interfaces:**
- Produces: `GpioButton(queue: queue.Queue, debounce_ms: int = 50)` — class ที่ import ได้จาก `gpio_btn`

- [ ] **Step 1: เขียน failing test**

เพิ่มท้าย `robot/web/test_server.py`:

```python
# ---------- gpio_btn ----------

import queue as _queue
import gpio_btn


def test_gpio_btn_init_simulator_mode():
    """SIMULATOR_MODE=True: init ต้องไม่ crash และ queue ต้องว่าง"""
    q = _queue.Queue()
    btn = gpio_btn.GpioButton(q)
    assert q.empty()
```

- [ ] **Step 2: รันเทสต์เพื่อดูว่า fail**

```
cd robot
python -m pytest web/test_server.py::test_gpio_btn_init_simulator_mode -v
```

Expected: `FAILED` — `ModuleNotFoundError: No module named 'gpio_btn'`

- [ ] **Step 3: เพิ่ม GPIO_BUTTON_PIN ใน robot/config.py**

เพิ่มหลัง `SPEECH_LANG = "th-TH"`:

```python
# --- ตั้งค่า GPIO (เฟส 2) ---
GPIO_BUTTON_PIN = 18  # BCM pin สำหรับปุ่มกายภาพ (เปลี่ยนได้)
```

- [ ] **Step 4: สร้าง robot/web/gpio_btn.py**

```python
import queue
from config import SIMULATOR_MODE, GPIO_BUTTON_PIN


class GpioButton:
    """ตรวจปุ่ม GPIO และ push "mic-start" เข้า queue เมื่อกด
    SIMULATOR_MODE=True: ไม่ทำอะไร (ใช้ปุ่มบน touchscreen แทน)
    """

    def __init__(self, event_queue: queue.Queue, debounce_ms: int = 50):
        self._q = event_queue
        if SIMULATOR_MODE:
            return
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(GPIO_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            GPIO_BUTTON_PIN,
            GPIO.FALLING,
            callback=self._on_press,
            bouncetime=debounce_ms,
        )

    def _on_press(self, channel):
        self._q.put("mic-start")
```

- [ ] **Step 5: รันเทสต์ใหม่เพื่อดูว่า pass**

```
cd robot
python -m pytest web/test_server.py::test_gpio_btn_init_simulator_mode -v
```

Expected: `1 passed`

- [ ] **Step 6: รันเทสต์ทั้งหมดเพื่อให้มั่นใจว่าไม่พัง**

```
cd robot
python -m pytest web/test_server.py -v
```

Expected: `17 passed`

- [ ] **Step 7: Commit**

```bash
git add robot/config.py robot/web/gpio_btn.py robot/web/test_server.py
git commit -m "feat(web): add GpioButton class + GPIO_BUTTON_PIN config"
```

---

### Task 2: /events SSE endpoint ใน server.py

**Files:**
- Modify: `robot/web/server.py`
- Modify: `robot/web/test_server.py`

**Interfaces:**
- Consumes: `GpioButton` จาก `gpio_btn` (Task 1)
- Produces: `GET /events` → `text/event-stream`; `server._make_sse_stream` (patchable ใน tests); `server.button_queue` (global `queue.Queue`)

- [ ] **Step 1: เขียน failing test**

เพิ่มท้าย `robot/web/test_server.py` (หลัง gpio_btn section):

```python
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
```

- [ ] **Step 2: รันเทสต์เพื่อดูว่า fail**

```
cd robot
python -m pytest web/test_server.py::test_events_endpoint_returns_stream -v
```

Expected: `FAILED` — `AttributeError: module 'server' has no attribute '_make_sse_stream'`

- [ ] **Step 3: แก้ robot/web/server.py**

เพิ่ม import ต่อจากบรรทัด `from wayfinding import wants_map`:

```python
import queue                                                       # noqa: E402
from gpio_btn import GpioButton                                    # noqa: E402
from flask import Response                                         # noqa: E402 (เพิ่มใน import flask บรรทัดเดิม)
```

**หมายเหตุ:** บรรทัด `from flask import ...` มีอยู่แล้ว ให้เพิ่ม `Response` เข้าไปในบรรทัดเดิม:

```python
from flask import Flask, request, jsonify, send_from_directory, Response  # noqa: E402
```

เพิ่มหลังบรรทัด `college_data = load_college_data()`:

```python
button_queue: queue.Queue = queue.Queue()
_gpio = GpioButton(button_queue)


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
```

- [ ] **Step 4: รันเทสต์ใหม่เพื่อดูว่า pass**

```
cd robot
python -m pytest web/test_server.py::test_events_endpoint_returns_stream -v
```

Expected: `1 passed`

- [ ] **Step 5: รันเทสต์ทั้งหมด**

```
cd robot
python -m pytest web/test_server.py -v
```

Expected: `18 passed`

- [ ] **Step 6: Commit**

```bash
git add robot/web/server.py robot/web/test_server.py
git commit -m "feat(web): add /events SSE endpoint for GPIO button bridge"
```

---

### Task 3: screen.js — EventSource listener

**Files:**
- Modify: `robot/web/static/screen.js`

**Interfaces:**
- Consumes: `GET /events` SSE จาก server (Task 2); `mic` element, `listening` variable, body classList จาก screen.js ที่มีอยู่แล้ว

- [ ] **Step 1: เพิ่ม EventSource listener ท้าย robot/web/static/screen.js**

เพิ่มต่อจาก lightbox block สุดท้าย (หลังบรรทัด `}` ปิด if lightbox):

```js
// ---- GPIO button via SSE ----
const evtSrc = new EventSource("/events");
evtSrc.onmessage = (e) => {
  if (
    e.data === "mic-start" &&
    !listening &&
    !document.body.classList.contains("state-thinking")
  ) {
    mic.click();
  }
};
```

- [ ] **Step 2: รันเทสต์ทั้งหมดเพื่อให้มั่นใจว่าไม่พัง**

```
cd robot
python -m pytest web/test_server.py -v
```

Expected: `18 passed` (ไม่มี test ใหม่ — JS ไม่มี unit test ในโปรเจกต์นี้)

- [ ] **Step 3: Commit**

```bash
git add robot/web/static/screen.js
git commit -m "feat(web): screen.js listens to /events SSE for GPIO button trigger"
```

---

### Task 4: Autostart files สำหรับ Pi

**Files:**
- Create: `robot/web/robot.service`
- Create: `robot/web/robot-kiosk.desktop`
- Create: `robot/web/install_autostart.sh`

ไม่มี unit test — ไฟล์เหล่านี้เป็น OS-level config ที่ test จริงได้บน Pi เท่านั้น

- [ ] **Step 1: สร้าง robot/web/robot.service**

```ini
[Unit]
Description=Robot Briefing Web Server
After=network.target

[Service]
WorkingDirectory=/home/pi/robot-briefing/robot/web
ExecStart=/usr/bin/python3 server.py
Restart=always
RestartSec=3
User=pi
EnvironmentFile=/home/pi/robot-briefing/.env

[Install]
WantedBy=multi-user.target
```

- [ ] **Step 2: สร้าง robot/web/robot-kiosk.desktop**

```ini
[Desktop Entry]
Type=Application
Name=Robot Kiosk
Exec=bash -c "sleep 5 && chromium-browser --kiosk --noerrdialogs --disable-infobars --disable-session-crashed-bubble http://localhost:5000/screen"
```

`sleep 5` ให้เวลา Flask start ก่อน Chromium เปิด

- [ ] **Step 3: สร้าง robot/web/install_autostart.sh**

```bash
#!/bin/bash
# รันบน Pi ครั้งเดียว:  bash robot/web/install_autostart.sh
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "[1/3] ติดตั้ง systemd service..."
sudo cp "$SCRIPT_DIR/robot.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable robot.service
sudo systemctl start robot.service

echo "[2/3] ติดตั้ง Chromium kiosk autostart..."
mkdir -p ~/.config/autostart
cp "$SCRIPT_DIR/robot-kiosk.desktop" ~/.config/autostart/

echo "[3/3] ติดตั้ง RPi.GPIO (ถ้ายังไม่มี)..."
pip install RPi.GPIO --quiet

echo "Done. รัน 'sudo reboot' เพื่อทดสอบ autostart เต็มรูปแบบ"
```

- [ ] **Step 4: รันเทสต์ทั้งหมดเพื่อให้มั่นใจว่าไม่พัง**

```
cd robot
python -m pytest web/test_server.py -v
```

Expected: `18 passed`

- [ ] **Step 5: Commit**

```bash
git add robot/web/robot.service robot/web/robot-kiosk.desktop robot/web/install_autostart.sh
git commit -m "feat(web): add systemd service + Chromium kiosk autostart for Pi"
```

---

## Self-Review Checklist

| Spec requirement | Task ที่ implement |
|------------------|-------------------|
| GPIO pin config ใน config.py | Task 1 |
| `GpioButton` class ไม่ crash บน Windows (SIMULATOR_MODE) | Task 1 |
| `RPi.GPIO` import ใน runtime เท่านั้น (ไม่ใช่ top-level) | Task 1 |
| Debounce 50ms กัน double-trigger | Task 1 |
| `/events` SSE endpoint | Task 2 |
| SSE heartbeat ทุก 15 วินาที กัน proxy timeout | Task 2 |
| `_make_sse_stream` patchable ใน tests | Task 2 |
| screen.js `EventSource` reconnect อัตโนมัติ | Task 3 |
| กัน trigger ซ้อน (`!listening && !state-thinking`) | Task 3 |
| systemd service เริ่ม Flask ทุกบูท | Task 4 |
| Chromium kiosk fullscreen | Task 4 |
| `sleep 5` รอ Flask ก่อน Chromium | Task 4 |
| `install_autostart.sh` ติดตั้งทุกอย่างครั้งเดียว | Task 4 |
| pytest 18 passed ทุก task | Task 1–4 |
