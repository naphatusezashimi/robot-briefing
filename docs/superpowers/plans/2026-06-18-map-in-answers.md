# Map-in-Answers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** เพิ่มฟีเจอร์ให้หุ่นแนบแผนผังวิทยาลัยในคำตอบเมื่อตรวจพบคำถามเรื่องตำแหน่ง/อาคาร พร้อมแก้หัวข้อจอแชทตัดคำเสียรูป (P1)

**Architecture:** ตรวจคีย์เวิร์ด deterministic ฝั่งเซิร์ฟเวอร์ใน `wayfinding.py` → `/ask` แนบ `image` ใน JSON response → `screen.js` render thumbnail + lightbox; ชิป "แผนผังวิทยาลัย" โทร `showMap()` ตรงโดยไม่ผ่าน AI

**Tech Stack:** Python 3.14, Flask, pytest, vanilla JS/CSS (ไม่มี framework เพิ่ม)

---

## File Map

| ไฟล์ | สถานะ | บทบาท |
|------|-------|-------|
| `robot/college_data.json` | แก้ | เพิ่ม section `"แผนผังและที่ตั้งอาคาร"` (legend รหัสอาคาร) |
| `robot/web/wayfinding.py` | ใหม่ | `wants_map(text) -> bool` — ตรวจคีย์เวิร์ดตำแหน่ง |
| `robot/web/static/map.jpg` | ใหม่ | รูปแผนผัง (download จาก www.tl.ac.th) |
| `robot/web/server.py` | แก้ | `/ask` เรียก `wants_map` → แนบ `image` ใน JSON |
| `robot/web/static/screen.html` | แก้ | แก้ header CSS (P1) + ชิปแผนผัง + lightbox markup/CSS |
| `robot/web/static/screen.js` | แก้ | `addMsg` รองรับ image, `ask()` ส่ง image, `showMap()`, lightbox JS |
| `robot/web/test_server.py` | แก้ | เทสต์ `wants_map`, `/ask`+image, `/static/map.jpg`, ชิปแผนผัง |

---

### Task 1: เพิ่ม building legend ใน college_data.json

**Files:**
- Modify: `robot/college_data.json`

- [ ] **Step 1: เพิ่ม section แผนผังและที่ตั้งอาคาร**

เพิ่ม key ใหม่ต่อจาก `"งานบริการและกิจกรรม"` (ก่อน `}` ปิดสุดท้าย):

```json
  "แผนผังและที่ตั้งอาคาร": {
    "_หมายเหตุ": "รหัส (ตัวเลข/ตัวอักษร) ตรงกับที่ปรากฏบนรูปแผนผังวิทยาลัย ใช้บอกตำแหน่ง/ทางให้ผู้มาติดต่อ ถ้าถูกถามว่าอะไรอยู่อาคารไหน ให้ตอบตามนี้",
    "รูปแผนผัง": "/static/map.jpg",
    "รหัสอาคาร": {
      "1": "อาคาร 1 — ห้องเรียนวิชาสามัญสัมพันธ์, คณะวิชาสามัญสัมพันธ์, งานพยาบาล",
      "2": "อาคาร 2 — ห้องเรียนวิชาสามัญสัมพันธ์, งานพัสดุ",
      "3": "อาคาร 3 — สาขาวิชาเมคคาทรอนิกส์และหุ่นยนต์, สาขาวิชาเทคนิคพื้นฐาน",
      "4": "อาคารเอนกประสงค์ — โรงอาหาร, หอประชุมอดิเรกสาร",
      "5": "อาคารช่างอุตสาหกรรม — สาขาวิชาไฟฟ้ากำลัง, สาขาวิชาเทคนิคการผลิต, สาขาวิชาเทคนิคอุตสาหกรรม",
      "6": "อาคารจอดรถส่วนกลาง — งานอาคารสถานที่, อาคารจอดรถส่วนกลาง",
      "7": "อาคาร 7 — ฝ่ายแผนงานและความร่วมมือ, ฝ่ายพัฒนากิจการนักเรียนนักศึกษา, สาขาวิชาอิเล็กทรอนิกส์, สาขาวิชาเทคโนโลยีคอมพิวเตอร์, สาขาวิชาเทคโนโลยีสารสนเทศ",
      "8": "อาคาร 8 (อาคารอำนวยการ) — สาขาวิชาการบัญชี, สาขาวิชาคอมพิวเตอร์ธุรกิจ, สาขาวิชาการตลาด",
      "9": "อาคาร 9 — สาขาวิชายานยนต์ไฟฟ้า",
      "A": "บ้านพักครู (บ้านเดียว)",
      "B": "บ้านพักครู (ตึกแถว)",
      "C": "บ้านพักครู (แฟล็ต)",
      "D": "บ้านพักเจ้าหน้าที่ พนักงานขับรถ นักการ",
      "E": "สนามบาสเกตบอล",
      "F": "สนามเทนนิส",
      "G": "ป้อมยาม",
      "H": "องค์พระวิษณุกรรม",
      "I": "เสาธง",
      "J": "ป้ายประชาสัมพันธ์",
      "K": "ที่จอดรถยนต์",
      "L": "อาคารงานการค้า",
      "M": "สหการวิทยาลัย",
      "N": "สาขาวิชาโลหะการ",
      "O": "โดมเอนกประสงค์ วีระพล อดิเรกสาร",
      "P": "อาคารศูนย์วิทยบริการ, งานเอกสารการพิมพ์",
      "Q": "ร้านค้าศูนย์บ่มเพาะวิสาหกิจเพื่อการศึกษา, งานแนะแนวอาชีพและการจัดหางาน, งานอาชีวศึกษาระบบทวิภาคี, ศูนย์บ่มเพาะวิสาหกิจเพื่อการศึกษา, ธนาคารโรงเรียน",
      "R": "อาคารปฏิบัติงานสาขาวิชาเทคนิคอุตสาหกรรม"
    }
  }
```

- [ ] **Step 2: Commit**

```bash
git add robot/college_data.json
git commit -m "feat(data): add building legend to college_data.json"
```

---

### Task 2: สร้าง wayfinding.py + tests

**Files:**
- Create: `robot/web/wayfinding.py`
- Modify: `robot/web/test_server.py`

- [ ] **Step 1: เขียน failing tests สำหรับ wants_map**

เพิ่มท้าย `robot/web/test_server.py`:

```python
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
```

- [ ] **Step 2: รันเทสต์เพื่อดูว่า fail**

```
cd robot
python -m pytest web/test_server.py::test_wants_map_true_for_location_keywords -v
```

Expected: `FAILED` with `ModuleNotFoundError: No module named 'wayfinding'`

- [ ] **Step 3: สร้าง robot/web/wayfinding.py**

```python
_KEYWORDS = [
    "อยู่ที่ไหน", "อยู่ไหน", "ตรงไหน", "ที่ไหน",
    "ไปยังไง", "ไปทางไหน", "ไปยัง", "เดินไป",
    "ทางไป", "เส้นทาง", "แผนผัง", "แผนที่",
    "อาคาร", "ตึก", "ห้อง", "สนาม",
    "จุด", "โรงอาหาร", "หอประชุม", "ป้อมยาม",
    "เสาธง", "ที่จอดรถ", "บ้านพัก",
]


def wants_map(text: str) -> bool:
    """คืน True ถ้าข้อความมีคีย์เวิร์ดที่บ่งบอกว่าถามเรื่องตำแหน่ง/ทาง"""
    for kw in _KEYWORDS:
        if kw in text:
            return True
    return False
```

- [ ] **Step 4: รันเทสต์เพื่อดูว่า pass**

```
cd robot
python -m pytest web/test_server.py::test_wants_map_true_for_location_keywords web/test_server.py::test_wants_map_false_for_non_location -v
```

Expected: `2 passed`

- [ ] **Step 5: Commit**

```bash
git add robot/web/wayfinding.py robot/web/test_server.py
git commit -m "feat(web): add wayfinding.py wants_map keyword detector + tests"
```

---

### Task 3: ดาวน์โหลด map.jpg + test asset

**Files:**
- Create: `robot/web/static/map.jpg`
- Modify: `robot/web/test_server.py`

- [ ] **Step 1: เขียน failing test สำหรับ map asset**

เพิ่มต่อจาก `test_logo_asset_served` ใน `robot/web/test_server.py`:

```python
def test_map_asset_served():
    c = make_client()
    r = c.get("/static/map.jpg")
    assert r.status_code == 200
    assert r.data[:3] == b"\xff\xd8\xff"  # JPEG magic bytes
```

- [ ] **Step 2: รันเพื่อดูว่า fail**

```
cd robot
python -m pytest web/test_server.py::test_map_asset_served -v
```

Expected: `FAILED` with `AssertionError` (status 404)

- [ ] **Step 3: ดาวน์โหลด map.jpg**

```python
# รันจาก shell หรือ Python prompt
import urllib.request
urllib.request.urlretrieve(
    "http://www.tl.ac.th/pictures/plan2568.jpg",
    "robot/web/static/map.jpg"
)
```

หรือใช้ curl/wget:
```bash
curl -o robot/web/static/map.jpg http://www.tl.ac.th/pictures/plan2568.jpg
```

- [ ] **Step 4: ตรวจสอบไฟล์**

```bash
ls -lh robot/web/static/map.jpg   # ต้องมีไฟล์ขนาด ~200KB
```

- [ ] **Step 5: รันเทสต์เพื่อดูว่า pass**

```
cd robot
python -m pytest web/test_server.py::test_map_asset_served -v
```

Expected: `1 passed`

- [ ] **Step 6: Commit**

```bash
git add robot/web/static/map.jpg robot/web/test_server.py
git commit -m "feat(web): add college map image asset + asset test"
```

---

### Task 4: แก้ server.py ให้แนบ image ใน /ask

**Files:**
- Modify: `robot/web/server.py`
- Modify: `robot/web/test_server.py`

- [ ] **Step 1: เขียน failing tests สำหรับ image ใน /ask**

เพิ่มใน `robot/web/test_server.py`:

```python
def test_ask_location_question_includes_image(monkeypatch):
    c = make_client()
    set_valid_key(monkeypatch)
    monkeypatch.setattr(server, "ask_ai", lambda q, d: "อาคาร 7 ครับ")
    monkeypatch.setattr(server, "wants_map", lambda q: True)
    r = c.post("/ask", json={"question": "สาขาอิเล็กทรอนิกส์อยู่ตึกไหน"})
    assert r.status_code == 200
    d = r.get_json()
    assert d["answer"] == "อาคาร 7 ครับ"
    assert d.get("image") == "/static/map.jpg"


def test_ask_non_location_question_no_image(monkeypatch):
    c = make_client()
    set_valid_key(monkeypatch)
    monkeypatch.setattr(server, "ask_ai", lambda q, d: "ตอบ: ค่าเทอม")
    monkeypatch.setattr(server, "wants_map", lambda q: False)
    r = c.post("/ask", json={"question": "ค่าเทอมเท่าไหร่"})
    assert r.status_code == 200
    d = r.get_json()
    assert d["answer"] == "ตอบ: ค่าเทอม"
    assert "image" not in d
```

- [ ] **Step 2: รันเพื่อดูว่า fail**

```
cd robot
python -m pytest web/test_server.py::test_ask_location_question_includes_image web/test_server.py::test_ask_non_location_question_no_image -v
```

Expected: `FAILED` — `AttributeError: module 'server' has no attribute 'wants_map'`

- [ ] **Step 3: แก้ robot/web/server.py**

เพิ่ม import (หลัง `from ai import ask_ai`):
```python
from wayfinding import wants_map                               # noqa: E402
```

แก้ฟังก์ชัน `ask()` — เปลี่ยน `return jsonify(answer=answer)` เป็น:
```python
        answer = ask_ai(question, college_data)
        state["value"] = "answering"
        result = {"answer": answer}
        if wants_map(question):
            result["image"] = "/static/map.jpg"
        return jsonify(**result)
```

- [ ] **Step 4: รัน tests ทั้งหมดเพื่อดูว่า pass**

```
cd robot
python -m pytest web/test_server.py -v
```

Expected: ทุก test ผ่าน (รวม 10 เดิม + 4 ใหม่ = 14 tests)

- [ ] **Step 5: Commit**

```bash
git add robot/web/server.py robot/web/test_server.py
git commit -m "feat(web): /ask attaches map image for location questions"
```

---

### Task 5: แก้ screen.html — header P1 + map chip + lightbox

**Files:**
- Modify: `robot/web/static/screen.html`
- Modify: `robot/web/test_server.py`

- [ ] **Step 1: เขียน failing test สำหรับ map chip**

เพิ่มใน `robot/web/test_server.py`:

```python
def test_screen_has_map_chip():
    c = make_client()
    screen = c.get("/screen")
    assert screen.status_code == 200
    html = screen.data.decode("utf-8")
    assert "แผนผังวิทยาลัย" in html
    assert 'data-action="showMap"' in html
```

- [ ] **Step 2: รันเพื่อดูว่า fail**

```
cd robot
python -m pytest web/test_server.py::test_screen_has_map_chip -v
```

Expected: `FAILED` — assertion error (ยังไม่มีใน HTML)

- [ ] **Step 3: แก้ CSS ใน screen.html — header P1 fix**

แทนที่ block CSS `.brand h1` และเพิ่ม `.brand`:

เปลี่ยนจาก:
```css
  .brand h1{font-family:"Mitr";font-weight:500;font-size:1.04rem;line-height:1.15;color:#13243b}
  .brand p{font-size:.74rem;color:var(--muted);margin-top:2px}
```

เป็น:
```css
  .brand{flex:1;min-width:0}
  .brand h1{font-family:"Mitr";font-weight:500;font-size:.9rem;line-height:1.2;color:#13243b;text-wrap:balance}
  .brand p{font-size:.72rem;color:var(--muted);margin-top:2px}
```

และลด padding/font ของ `.led span`:
```css
  .led{margin-left:auto; display:flex;align-items:center;gap:6px; padding:5px 9px;
    background:#f1f6fe;border-radius:999px;border:1px solid #e2ecfb;white-space:nowrap}
  .led .d{width:9px;height:9px;border-radius:50%;background:var(--led);transition:background .4s;
    box-shadow:0 0 0 3px color-mix(in srgb,var(--led) 25%,transparent)}
  .led .d.live{animation:lpulse 1.4s infinite}
  .led span{font-size:.68rem;color:#46618a;font-weight:500}
```

- [ ] **Step 4: เพิ่ม CSS สำหรับ .map-thumb และ lightbox**

เพิ่มหลัง `.chip:active{transform:none}`:
```css
  /* ---------- map thumbnail & lightbox ---------- */
  .map-thumb{display:block;width:100%;max-width:320px;border-radius:10px;margin-top:8px;
    cursor:zoom-in;border:1px solid #e0eaf6;box-shadow:0 4px 14px -6px rgba(20,60,120,.3)}
  #lightbox{display:none;position:fixed;inset:0;z-index:200;background:rgba(0,0,0,.88);
    align-items:center;justify-content:center;cursor:zoom-out}
  #lightbox.open{display:flex}
  #lightbox img{max-width:95vw;max-height:90vh;border-radius:8px;object-fit:contain;
    box-shadow:0 20px 60px -10px rgba(0,0,0,.7)}
```

- [ ] **Step 5: เพิ่มชิป "แผนผังวิทยาลัย" เป็นชิปแรกใน .chips**

เปลี่ยนจาก:
```html
        <div class="chips">
          <button type="button" class="chip">เปิดสอนสาขาอะไรบ้าง</button>
```

เป็น:
```html
        <div class="chips">
          <button type="button" class="chip" data-action="showMap">🗺️ แผนผังวิทยาลัย</button>
          <button type="button" class="chip">เปิดสอนสาขาอะไรบ้าง</button>
```

- [ ] **Step 6: เพิ่ม lightbox overlay div ก่อน `</body>`**

เพิ่มก่อน `<script src="/static/screen.js"></script>`:
```html
<div id="lightbox"><img src="" alt="แผนผังวิทยาลัยขยาย"></div>
```

- [ ] **Step 7: รัน tests เพื่อดูว่า pass**

```
cd robot
python -m pytest web/test_server.py -v
```

Expected: ทุก test ผ่าน (15 tests)

- [ ] **Step 8: Commit**

```bash
git add robot/web/static/screen.html robot/web/test_server.py
git commit -m "feat(web): fix header word-wrap (P1), add map chip, lightbox markup + CSS"
```

---

### Task 6: แก้ screen.js — addMsg image, showMap, lightbox JS

**Files:**
- Modify: `robot/web/static/screen.js`

- [ ] **Step 1: อัปเดต addMsg ให้รองรับ opts.image**

เปลี่ยนจาก:
```js
function addMsg(role, text, opts = {}) {
  const m = document.createElement("div");
  m.className = "msg " + role;
  const tag = opts.voice ? '<span class="mic-tag">🎤 พูด</span>' : "";
  const ava = role === "bot" ? '<div class="ava"><i></i><i></i></div>' : "";
  m.innerHTML = ava + '<div class="bubble' + (opts.warn ? " warn" : "") + '">' + tag + escapeHtml(text) + "</div>";
  chat.appendChild(m); chat.scrollTop = chat.scrollHeight;
}
```

เป็น:
```js
function addMsg(role, text, opts = {}) {
  const m = document.createElement("div");
  m.className = "msg " + role;
  const tag = opts.voice ? '<span class="mic-tag">🎤 พูด</span>' : "";
  const ava = role === "bot" ? '<div class="ava"><i></i><i></i></div>' : "";
  const img = opts.image ? `<img class="map-thumb" src="${opts.image}" alt="แผนผังวิทยาลัย">` : "";
  m.innerHTML = ava + '<div class="bubble' + (opts.warn ? " warn" : "") + '">' + tag + escapeHtml(text) + img + "</div>";
  chat.appendChild(m); chat.scrollTop = chat.scrollHeight;
}
```

- [ ] **Step 2: อัปเดต ask() ให้ส่ง d.image ต่อให้ addMsg**

เปลี่ยนจาก:
```js
    const answer = d.answer || "";
    addMsg("bot", answer);
```

เป็น:
```js
    const answer = d.answer || "";
    addMsg("bot", answer, { image: d.image || null });
```

- [ ] **Step 3: เพิ่ม showMap() ก่อน setState**

เพิ่มหลัง `function typing(on) { ... }`:
```js
// ---- โชว์แผนผังทันที (ไม่เรียก /ask) ----
function showMap() {
  addMsg("bot", "นี่คือแผนผังวิทยาลัยค่ะ แตะที่รูปเพื่อขยายดูได้เลย", { image: "/static/map.jpg" });
}
```

- [ ] **Step 4: เพิ่ม lightbox event handlers**

เพิ่มหลัง `setState("idle");` บรรทัดสุดท้าย:
```js
// ---- lightbox ----
const lightbox = document.getElementById("lightbox");
if (lightbox) {
  lightbox.addEventListener("click", () => lightbox.classList.remove("open"));
  chat.addEventListener("click", (e) => {
    if (e.target.classList.contains("map-thumb")) {
      lightbox.querySelector("img").src = e.target.src;
      lightbox.classList.add("open");
    }
  });
}
```

- [ ] **Step 5: อัปเดต chip click handler ให้ showMap ชิปแผนผัง**

เปลี่ยนจาก:
```js
document.querySelectorAll("#quickQs .chip").forEach((b) => {
  b.addEventListener("click", () => {
    if (document.body.classList.contains("state-thinking")) return;
    ask(b.textContent.trim(), { voice: false });
  });
});
```

เป็น:
```js
document.querySelectorAll("#quickQs .chip").forEach((b) => {
  b.addEventListener("click", () => {
    if (document.body.classList.contains("state-thinking")) return;
    if (b.dataset.action === "showMap") { showMap(); return; }
    ask(b.textContent.trim(), { voice: false });
  });
});
```

- [ ] **Step 6: รัน tests ครั้งสุดท้ายเพื่อยืนยันทุก test ผ่าน**

```
cd robot
python -m pytest web/test_server.py -v
```

Expected: `15 passed, 0 failed`

- [ ] **Step 7: Commit**

```bash
git add robot/web/static/screen.js
git commit -m "feat(web): screen.js map thumbnail, lightbox, showMap chip"
```

---

## Self-Review Checklist

| Spec requirement | Task ที่ implement |
|------------------|-------------------|
| `wants_map` deterministic keyword check | Task 2 |
| `wayfinding.py` แยกออกมา unit test ง่าย | Task 2 |
| Download `map.jpg` → `robot/web/static/map.jpg` | Task 3 |
| `/ask` แนบ `image` เมื่อ `wants_map` = True | Task 4 |
| `/ask` ไม่แนบ `image` เมื่อ `wants_map` = False | Task 4 |
| Building legend ใน `college_data.json` | Task 1 |
| แก้หัวข้อ P1 (ตัดคำเสียรูป) | Task 5 |
| ชิป "แผนผังวิทยาลัย" เป็นชิปแรก | Task 5 |
| thumbnail ในฟอง + lightbox แตะขยาย | Task 5+6 |
| `showMap()` ไม่เรียก `/ask` | Task 6 |
| ไม่แตะ `ai.py` / `face.html` / `face.js` | ไม่มีในแผน |
| pytest ผ่านทั้งหมด | Task 2–6 |
