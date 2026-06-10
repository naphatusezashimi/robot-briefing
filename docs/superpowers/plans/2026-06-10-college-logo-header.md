# College Logo on Screen Header — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** เอาโลโก้จริงของวิทยาลัย (`image/1780392362301.jpg`) มาแสดงแทนไอคอนจำลองบนหัวจอเนื้อหาของเว็บ "กล่องพูดได้" ในไทล์ขาวขอบมน

**Architecture:** คัดลอกไฟล์โลโก้เข้า `robot/web/static/` ซึ่ง Flask เสิร์ฟอยู่แล้วที่ `/static/` (ไม่ต้องแก้ server) แล้วแก้ `screen.html` ไฟล์เดียว: CSS ของไทล์ `.logo` (พื้นขาว+ขอบ+เงาจาง) และ HTML ข้างใน (เปลี่ยน SVG เป็น `<img>`)

**Tech Stack:** Flask static files, HTML/CSS, pytest (Flask test client)

**Spec:** `docs/superpowers/specs/2026-06-10-college-logo-header-design.md`

**บริบทที่ต้องรู้ก่อนเริ่ม:**
- ทำงานบน branch `add-college-logo` (มีอยู่แล้ว, มีไฟล์ `image/1780392362301.jpg` commit ไว้แล้ว, push แล้ว → PR #1)
- คำสั่งทั้งหมดรันจากโฟลเดอร์ `robot/` ของ repo (ยกเว้นที่ระบุว่ารันจาก repo root)
- รันเทสต์: `python -m pytest web/test_server.py -v` (pytest หา `server` เจอเพราะ prepend import mode ใส่ `web/` ใน sys.path ให้)
- ห้ามแตะ: `server.py`, `face.html`, ไฟล์ `.js`, `mockups/`

---

## File Structure

| ไฟล์ | ทำอะไร |
|------|--------|
| `robot/web/static/logo.jpg` | **สร้างใหม่** — สำเนาโลโก้จริง (ต้นฉบับ `image/1780392362301.jpg` คงไว้) |
| `robot/web/static/screen.html` | **แก้ 2 จุด** — CSS `.logo` (บรรทัด ~51-53) และ HTML `<div class="logo">` (บรรทัด ~136-138) |
| `robot/web/test_server.py` | **เพิ่ม 2 เทสต์** ต่อท้ายไฟล์ ตามแพทเทิร์น `make_client()` เดิม |

---

### Task 1: เสิร์ฟไฟล์โลโก้จาก static

**Files:**
- Create: `robot/web/static/logo.jpg` (คัดลอกจาก `image/1780392362301.jpg`)
- Test: `robot/web/test_server.py`

- [ ] **Step 1: เขียนเทสต์ที่ fail ก่อน** — เพิ่มต่อท้าย `robot/web/test_server.py`:

```python
def test_logo_asset_served():
    c = make_client()
    r = c.get("/static/logo.jpg")
    assert r.status_code == 200
    assert r.data[:3] == b"\xff\xd8\xff"   # magic bytes ของไฟล์ JPEG
```

- [ ] **Step 2: รันเทสต์ให้เห็นว่า fail**

Run (จาก `robot/`): `python -m pytest web/test_server.py::test_logo_asset_served -v`
Expected: FAIL — `assert 404 == 200` (ไฟล์ยังไม่มี)

- [ ] **Step 3: คัดลอกไฟล์โลโก้**

Run (จาก repo root): `cp image/1780392362301.jpg robot/web/static/logo.jpg`

- [ ] **Step 4: รันเทสต์ให้ผ่าน**

Run (จาก `robot/`): `python -m pytest web/test_server.py::test_logo_asset_served -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add robot/web/static/logo.jpg robot/web/test_server.py
git commit -m "feat(web): serve college logo from static" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 2: หัวจอเนื้อหาใช้โลโก้จริง

**Files:**
- Modify: `robot/web/static/screen.html:51-53` (CSS `.logo`) และ `:136-138` (HTML)
- Test: `robot/web/test_server.py`

- [ ] **Step 1: เขียนเทสต์ที่ fail ก่อน** — เพิ่มต่อท้าย `robot/web/test_server.py`:

```python
def test_screen_header_uses_real_logo():
    c = make_client()
    screen = c.get("/screen")
    assert screen.status_code == 200
    assert b"/static/logo.jpg" in screen.data   # header อ้างโลโก้จริง
```

- [ ] **Step 2: รันเทสต์ให้เห็นว่า fail**

Run (จาก `robot/`): `python -m pytest web/test_server.py::test_screen_header_uses_real_logo -v`
Expected: FAIL — assert ไม่เจอ `/static/logo.jpg` ใน HTML

- [ ] **Step 3: แก้ CSS `.logo`** ใน `robot/web/static/screen.html` (บรรทัด ~51-53)

ของเดิม:
```css
  .logo{width:48px;height:48px;border-radius:14px;flex:none; display:grid;place-items:center;
    background:linear-gradient(145deg,var(--blue),var(--blue-d));
    box-shadow:0 8px 18px -6px rgba(42,157,244,.6)}
```

เปลี่ยนเป็น (พื้นขาว + ขอบโทนเดียวกับเส้นแบ่ง header + เงาจางลง):
```css
  .logo{width:48px;height:48px;border-radius:14px;flex:none; display:grid;place-items:center;
    background:#fff; border:1px solid #e7eefb;
    box-shadow:0 8px 18px -6px rgba(20,60,120,.18)}
```

- [ ] **Step 4: แก้ HTML ใน `<div class="logo">`** (บรรทัด ~136-138)

ของเดิม:
```html
      <div class="logo">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="#fff"><path d="M12 2 1 8l11 6 9-4.9V17h2V8L12 2zM5 13.2V17c0 1.7 3.1 3 7 3s7-1.3 7-3v-3.8l-7 3.8-7-3.6z"/></svg>
      </div>
```

เปลี่ยนเป็น:
```html
      <div class="logo">
        <img src="/static/logo.jpg" alt="ตราวิทยาลัยเทคนิคท่าหลวงซิเมนต์ไทยอนุสรณ์" width="40" height="40" style="object-fit:contain">
      </div>
```

- [ ] **Step 5: รันเทสต์ใหม่ให้ผ่าน**

Run (จาก `robot/`): `python -m pytest web/test_server.py::test_screen_header_uses_real_logo -v`
Expected: PASS

- [ ] **Step 6: รันเทสต์ทั้งไฟล์ กันของเดิมพัง**

Run (จาก `robot/`): `python -m pytest web/test_server.py -v`
Expected: PASS ทั้งหมด 7 เทสต์ (5 เดิม + 2 ใหม่) — โดยเฉพาะ `test_pages_are_served` ต้องยังผ่าน (มาร์กเกอร์ `id="mic"` ยังอยู่)

- [ ] **Step 7: Commit**

```bash
git add robot/web/static/screen.html robot/web/test_server.py
git commit -m "feat(web): show real college logo on screen header" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 3: ตรวจรับด้วยตาจริง + push ขึ้น PR

**Files:** ไม่มีไฟล์ใหม่ (ตรวจรับ + push)

- [ ] **Step 1: เปิดเว็บดูของจริง**

Run (จาก `robot/`): `python web/server.py` (หรือดับเบิลคลิก `web/run_web.bat`)
เปิดเบราว์เซอร์: `http://127.0.0.1:5000/screen` แล้วเช็คตาม spec:
- โลโก้จริงแสดงในไทล์ขาวขอบมน คมชัด ไม่ยืด/ไม่บีบ
- ชื่อวิทยาลัย + pill สถานะ ไม่ขยับเพี้ยน
- ลองย่อหน้าต่างแคบ ๆ header ไม่พัง
- เปิด `http://127.0.0.1:5000/face` — จอใบหน้าปกติเหมือนเดิม

- [ ] **Step 2: ปิดเซิร์ฟเวอร์** (Ctrl+C)

- [ ] **Step 3: Push ขึ้น PR**

```bash
git push
```
Expected: branch `add-college-logo` อัปเดต → commit ใหม่ขึ้นไปโผล่ใน PR #1 อัตโนมัติ
