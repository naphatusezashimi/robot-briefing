# Phase 2: Web Interface Production Mode — Design Spec

**วันที่:** 2026-06-21
**เป้าหมาย:** ทำให้ web interface ทำงานได้จริงบน Raspberry Pi 5 สำหรับการใช้งานและการแข่งขัน โดยไม่ใช้ Google Cloud STT/TTS (ใช้ browser Web Speech API แทน ซึ่งฟรีและไม่ต้องจัดการ credentials)

---

## บริบทและเหตุผล

ระบบปัจจุบันมี web interface (Flask + screen.html + screen.js) ที่ทำงานได้บน localhost แล้ว รวมถึง STT/TTS ผ่าน browser Web Speech API ที่ทำงานได้โดยไม่ต้องมี Google Cloud credentials

Phase 2 จึงเน้นที่ **production readiness** บน Pi:
1. Pi บูทแล้วระบบ start อัตโนมัติ (ไม่ต้อง login / พิมพ์คำสั่ง)
2. ปุ่ม GPIO กายภาพบนตัวหุ่น trigger STT ได้ (นอกจาก touchscreen)
3. Chromium เปิด fullscreen kiosk mode ไม่มี address bar

---

## สถาปัตยกรรม

```
[ปุ่ม GPIO] ──press──▶ gpio_btn.py (background thread)
                              │
                              ▼ queue.Queue
                        server.py /events  ──SSE──▶ screen.js EventSource
                                                         │
                                                    mic.click() → STT เริ่ม

[Pi บูท] ──▶ systemd: robot.service (Flask) ──▶ LXDE autostart: Chromium kiosk
                                                  http://localhost:5000/screen
```

---

## File Map

| ไฟล์ | สถานะ | บทบาท |
|------|-------|-------|
| `robot/config.py` | แก้ | เพิ่ม `GPIO_BUTTON_PIN = 18` |
| `robot/web/gpio_btn.py` | ใหม่ | `GpioButton` class: thread + debounce + queue |
| `robot/web/server.py` | แก้ | import gpio_btn, เพิ่ม `/events` SSE endpoint |
| `robot/web/static/screen.js` | แก้ | `EventSource('/events')` listener → `mic.click()` |
| `robot/web/robot.service` | ใหม่ | systemd unit สำหรับ Flask |
| `robot/web/robot-kiosk.desktop` | ใหม่ | LXDE autostart สำหรับ Chromium kiosk |
| `robot/web/install_autostart.sh` | ใหม่ | script ติดตั้ง autostart บน Pi ครั้งเดียว |
| `robot/web/test_server.py` | แก้ | test `/events` endpoint |

---

## รายละเอียดแต่ละชิ้น

### 1. config.py — เพิ่ม GPIO_BUTTON_PIN

```python
GPIO_BUTTON_PIN = 18  # BCM pin สำหรับปุ่มกายภาพ (เปลี่ยนได้)
```

GPIO ใช้เฉพาะตอน `SIMULATOR_MODE = False`

---

### 2. gpio_btn.py — GpioButton

```python
import queue
import threading
from config import SIMULATOR_MODE, GPIO_BUTTON_PIN

class GpioButton:
    def __init__(self, event_queue: queue.Queue, debounce_ms: int = 50):
        self._q = event_queue
        if SIMULATOR_MODE:
            return  # ไม่ start thread ในโหมดจำลอง
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(GPIO_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            GPIO_BUTTON_PIN, GPIO.FALLING,
            callback=self._on_press,
            bouncetime=debounce_ms,
        )

    def _on_press(self, channel):
        self._q.put("mic-start")
```

- `RPi.GPIO` import ใน runtime เท่านั้น (ไม่ crash บน Windows/Mac)
- `SIMULATOR_MODE = True` → ไม่ start thread เลย, ปุ่มบนจอ touchscreen ยังใช้ได้ปกติ
- Debounce 50ms กัน double-trigger จากปุ่มกระดอน

---

### 3. server.py — /events SSE endpoint

```python
import queue
from gpio_btn import GpioButton

button_queue = queue.Queue()
_gpio = GpioButton(button_queue)

@app.route("/events")
def events():
    def stream():
        yield "data: connected\n\n"
        while True:
            try:
                evt = button_queue.get(timeout=15)
                yield f"data: {evt}\n\n"
            except queue.Empty:
                yield ": heartbeat\n\n"  # กัน proxy/nginx ตัดการเชื่อมต่อ
    return Response(stream(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
```

- Heartbeat comment (`: heartbeat`) ทุก 15 วินาที — ไม่ trigger `onmessage` ในบราวเซอร์
- `X-Accel-Buffering: no` กัน nginx buffer SSE

---

### 4. screen.js — EventSource listener

เพิ่มท้ายไฟล์ (หลัง lightbox block):

```js
// ---- GPIO button via SSE ----
const evtSrc = new EventSource("/events");
evtSrc.onmessage = (e) => {
  if (e.data === "mic-start" && !listening && !document.body.classList.contains("state-thinking")) {
    mic.click();
  }
};
```

- `EventSource` reconnect อัตโนมัติถ้าหลุด — ไม่ต้องเขียน retry
- เช็ค `!listening` และ `!state-thinking` กัน trigger ซ้อน

---

### 5. robot.service — systemd unit

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

---

### 6. robot-kiosk.desktop — Chromium kiosk autostart

```ini
[Desktop Entry]
Type=Application
Name=Robot Kiosk
Exec=bash -c "sleep 5 && chromium-browser --kiosk --noerrdialogs --disable-infobars --disable-session-crashed-bubble http://localhost:5000/screen"
```

- `sleep 5` รอให้ Flask start ก่อน Chromium เปิด

---

### 7. install_autostart.sh — ติดตั้งบน Pi

```bash
#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# systemd service
sudo cp "$SCRIPT_DIR/robot.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable robot.service
sudo systemctl start robot.service

# Chromium kiosk autostart
mkdir -p ~/.config/autostart
cp "$SCRIPT_DIR/robot-kiosk.desktop" ~/.config/autostart/

echo "Done. Reboot to test full autostart."
```

---

### 8. test_server.py — เพิ่ม test สำหรับ /events

```python
def test_events_endpoint_returns_stream():
    c = make_client()
    r = c.get("/events")
    assert r.status_code == 200
    assert "text/event-stream" in r.content_type
```

---

## Dependencies ใหม่

| Package | ใช้ทำอะไร | ติดตั้งเฉพาะ |
|---------|----------|-------------|
| `RPi.GPIO` | อ่าน GPIO pin | Pi เท่านั้น |

ไม่ต้องเพิ่มใน `requirements.txt` หลัก — เพิ่มใน comment ว่า "install on Pi: `pip install RPi.GPIO`"

---

## Self-Review Checklist

| ข้อ | ผ่าน? |
|-----|-------|
| SIMULATOR_MODE = True → ไม่ crash เพราะ RPi.GPIO ไม่มี | ✓ (import ใน runtime) |
| EventSource reconnect อัตโนมัติถ้า Flask restart | ✓ (native behavior) |
| GPIO double-trigger ถูกกัน | ✓ (debounce 50ms) |
| Chromium เปิดหลัง Flask ready | ✓ (sleep 5) |
| ไม่แตะ ai.py / face.html / face.js / wayfinding.py | ✓ |
| pytest ผ่านทั้งหมด | ต้องยืนยันใน implementation |
