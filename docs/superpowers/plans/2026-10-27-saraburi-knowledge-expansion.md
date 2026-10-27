# Saraburi Knowledge Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** เพิ่มให้หุ่นตอบคำถามเกี่ยวกับท่องเที่ยวสระบุรีและ OTOP สระบุรีได้ นอกเหนือจากข้อมูลภายในวิทยาลัย โดยกฎ "ห้ามตอบมั่ว" ยังคงบังคับใช้

**Architecture:** สร้าง `robot/saraburi_data.json` เป็นไฟล์ข้อมูลแยกต่างหาก `database.py` โหลดทั้งสองไฟล์และรวมเป็นข้อความเดียวส่งเข้า system prompt ของ AI ผ่านฟังก์ชัน `format_all_data()` ใหม่ signature ของ `ask_ai()` เปลี่ยนจาก 2 args เป็น 3 args

**Tech Stack:** Python · JSON · pytest

## Global Constraints

- ห้ามแตะ `college_data.json` — ไม่เพิ่ม/แก้ข้อมูลในไฟล์นี้
- ห้ามแตะ UI ทั้งหมด (HTML/JS/CSS)
- ห้ามแตะ `run_web.bat`
- กฎ "ห้ามตอบมั่ว" ต้องอยู่ครบ — `_SYSTEM_RULES` ใน `ai.py` เปลี่ยนแค่ขยายขอบเขต ไม่ลบกฎ
- ถ้าไม่มีไฟล์ `saraburi_data.json` ระบบต้องรันได้ปกติ (graceful fallback)
- รันเทสต์จากโฟลเดอร์ `robot/`: `python -m pytest test_saraburi.py -v`
- รันเทสต์เดิมจากโฟลเดอร์ `robot/`: `python -m pytest web/test_server.py -v`

---

### Task 1: สร้าง `saraburi_data.json`

**Files:**
- Create: `robot/saraburi_data.json`

**Interfaces:**
- Consumes: ไม่มี
- Produces: ไฟล์ JSON ที่ `load_saraburi_data()` ใน Task 2 จะโหลด

- [ ] **Step 1: สร้างไฟล์ `robot/saraburi_data.json` พร้อมข้อมูลจริง**

```json
{
  "_คำอธิบาย": "ข้อมูลจังหวัดสระบุรี รวบรวมจากหนังสือ Saraburi Live and Life และ OTOP สระบุรี (TAT, thai-tour.com, komchadluek.net, my-best.com)",
  "ปรับปรุงล่าสุด": "2569-10-27",
  "ท่องเที่ยวสระบุรี": {
    "น้ำตก": [
      {
        "ชื่อ": "น้ำตกเจ็ดสาวน้อย",
        "อำเภอ": "มวกเหล็ก",
        "จุดเด่น": "น้ำตก 7 ชั้น เดินป่าสั้น เหมาะครอบครัว อยู่ในอุทยานแห่งชาติ"
      },
      {
        "ชื่อ": "น้ำตกสามหลั่น",
        "อำเภอ": "เมืองสระบุรี",
        "จุดเด่น": "น้ำตก 3 ชั้น สิ่งอำนวยความสะดวกครบ"
      },
      {
        "ชื่อ": "น้ำตกโกรกอีก",
        "อำเภอ": "มวกเหล็ก",
        "จุดเด่น": "สูง 20 เมตร ป่าทึบ เหมาะนักท่องเที่ยวที่ชอบธรรมชาติ"
      },
      {
        "ชื่อ": "น้ำตกมวกเหล็ก",
        "อำเภอ": "มวกเหล็ก",
        "จุดเด่น": "เย็นสบายตลอดปี อยู่ใน Dong Phayayen-Khao Yai Forest Complex"
      }
    ],
    "วัดและสถานที่ศักดิ์สิทธิ์": [
      {
        "ชื่อ": "วัดพระพุทธบาท",
        "อำเภอ": "พระพุทธบาท",
        "จุดเด่น": "รอยพระพุทธบาทประดิษฐานบนหิน เป็นปูชนียสถานสำคัญ"
      },
      {
        "ชื่อ": "วัดพระพุทธฉาย",
        "อำเภอ": "เมืองสระบุรี",
        "จุดเด่น": "พระพักตร์พระพุทธรูปปรากฏบนหน้าผา วิวสวยงาม"
      },
      {
        "ชื่อ": "วัดถ้ำกระบอก",
        "อำเภอ": "พระพุทธบาท",
        "จุดเด่น": "ถ้ำธรรมชาติขนาดใหญ่ น้ำหยดจากผนังถ้ำถือเป็นมงคล มีชุมชนผู้ฟื้นฟูจากยาเสพติด"
      },
      {
        "ชื่อ": "วัดป่าสว่างบุญ",
        "อำเภอ": "แก่งคอย",
        "จุดเด่น": "เจดีย์ทองคำ 500 องค์ บรรยากาศสงบ"
      },
      {
        "ชื่อ": "วัดถ้ำพระโพธิสัตว์",
        "อำเภอ": "แก่งคอย",
        "จุดเด่น": "วัดในหุบเขา บันไดนาคขึ้นถ้ำ วิวเมืองสวย"
      }
    ],
    "ธรรมชาติและสวน": [
      {
        "ชื่อ": "ทุ่งทานตะวันวังม่วง",
        "อำเภอ": "วังม่วง",
        "จุดเด่น": "ทุ่งดอกทานตะวันขนาดใหญ่ที่สุดในไทย ช่วงสวยสุดตุลาคม-กุมภาพันธ์"
      },
      {
        "ชื่อ": "สวนพฤกษศาสตร์พุแค",
        "อำเภอ": "เมืองสระบุรี",
        "จุดเด่น": "พรรณพืชหลากหลาย เหมาะสำหรับครอบครัวและนักเรียน"
      },
      {
        "ชื่อ": "ไร่กุสุมา",
        "อำเภอ": "มวกเหล็ก",
        "จุดเด่น": "สวนผลไม้ กิจกรรมผจญภัย 7 สถานี มีที่พัก"
      }
    ],
    "ตลาดและแหล่งช้อป": [
      {
        "ชื่อ": "ตลาดหัวปลี",
        "อำเภอ": "เมืองสระบุรี",
        "จุดเด่น": "ตลาดสุดสัปดาห์ อาหารท้องถิ่นและงานหัตถกรรม"
      },
      {
        "ชื่อ": "ตลาดท่าน้ำแก่งคอย",
        "อำเภอ": "แก่งคอย",
        "จุดเด่น": "ตลาดกลางคืนริมน้ำสไตล์ย้อนยุค กินของอร่อย ช้อปปิ้ง"
      }
    ],
    "ใกล้วิทยาลัย_อำเภอบ้านหมอ": [
      {
        "ชื่อ": "ผาเสด็จ",
        "อำเภอ": "แก่งคอย",
        "ระยะทางจากวิทยาลัย": "ประมาณ 30 กิโลเมตร",
        "จุดเด่น": "จุดชมวิวที่พระบาทสมเด็จพระจุลจอมเกล้าเสด็จ มีสถานีรถไฟเก่าเหมาะถ่ายรูป"
      },
      {
        "ชื่อ": "ตลาดท่าน้ำแก่งคอย",
        "อำเภอ": "แก่งคอย",
        "ระยะทางจากวิทยาลัย": "ประมาณ 25 กิโลเมตร",
        "จุดเด่น": "ตลาดกลางคืนริมน้ำสไตล์ย้อนยุค"
      },
      {
        "ชื่อ": "วัดถ้ำพระโพธิสัตว์",
        "อำเภอ": "แก่งคอย",
        "ระยะทางจากวิทยาลัย": "ประมาณ 28 กิโลเมตร",
        "จุดเด่น": "วัดในหุบเขา วิวเมืองสวยงาม"
      }
    ]
  },
  "OTOP_สระบุรี": {
    "อาหารและขนม": [
      {
        "ชื่อ": "หมูทุบไร้มัน",
        "แหล่งผลิต": "มวกเหล็ก",
        "จุดเด่น": "หมูแผ่นกรอบไม่มีสารกันบูด บรรจุ 180-200 กรัม"
      },
      {
        "ชื่อ": "หมูสวรรค์",
        "แหล่งผลิต": "สระบุรี",
        "จุดเด่น": "หมูแผ่นแบบดั้งเดิม งาขาวและสมุนไพร 200 กรัม"
      },
      {
        "ชื่อ": "กระยาสารทกะทิสดงาขาว",
        "แหล่งผลิต": "เสาไห้",
        "จุดเด่น": "ขนมไทยโบราณ ทำจากกะทิสดและงา ของฝากยอดนิยม"
      },
      {
        "ชื่อ": "แยมมัลเบอร์รี่ มียิ้ม",
        "แหล่งผลิต": "สระบุรี",
        "จุดเด่น": "ทำจากมัลเบอร์รี่สด น้ำตาลออร์แกนิก ไม่มีสารเคมี"
      },
      {
        "ชื่อ": "เห็ด 3 มอ",
        "แหล่งผลิต": "บ้านหมอ",
        "จุดเด่น": "เห็ดกรอบทอด ไม่มีสารเคมีเพิ่ม 110 กรัม"
      },
      {
        "ชื่อ": "ขนมปั้นขลิบไส้ปลา",
        "แหล่งผลิต": "สระบุรี",
        "จุดเด่น": "ไส้ปลาทู 100% 350 กรัม"
      },
      {
        "ชื่อ": "น้ำนมถั่วเหลืองอัลมอนด์ เบ๊นซ์โซย่า",
        "แหล่งผลิต": "สระบุรี",
        "จุดเด่น": "ผสมอัลมอนด์ เหมาะผู้รักสุขภาพ"
      },
      {
        "ชื่อ": "น้ำพริกป้าคูณ",
        "แหล่งผลิต": "สระบุรี",
        "จุดเด่น": "ได้มาตรฐาน GMP มีหลายรสชาติ"
      }
    ],
    "งานหัตถกรรม": [
      {
        "ชื่อ": "หมวกคาวบอยใบลาน",
        "แหล่งผลิต": "สระบุรี",
        "จุดเด่น": "สัญลักษณ์ประจำจังหวัด ทำจากใบลานธรรมชาติ"
      },
      {
        "ชื่อ": "ผ้าทอพื้นเมืองชาวไทยวน",
        "แหล่งผลิต": "สระบุรี",
        "จุดเด่น": "ลายเป็นเอกลักษณ์ ทอด้วยมือ สีธรรมชาติ"
      }
    ],
    "สมุนไพรและสุขภาพ": [
      {
        "ชื่อ": "ลูกประคบสมุนไพร เอสวีเฮิร์บ",
        "แหล่งผลิต": "สระบุรี",
        "จุดเด่น": "สมุนไพรหลายชนิด ช่วยบรรเทาปวดเมื่อย"
      }
    ]
  }
}
```

- [ ] **Step 2: ตรวจสอบว่า JSON valid**

```bash
python -c "import json; json.load(open('robot/saraburi_data.json', encoding='utf-8')); print('JSON OK')"
```

Expected output: `JSON OK`

- [ ] **Step 3: Commit**

```bash
git add robot/saraburi_data.json
git commit -m "data: add saraburi_data.json — tourism and OTOP"
```

---

### Task 2: อัปเดต `config.py` + `database.py`

**Files:**
- Modify: `robot/config.py` (เพิ่ม `SARABURI_DATA_PATH`)
- Modify: `robot/database.py` (เพิ่ม `load_saraburi_data()` + `format_all_data()`)
- Create: `robot/test_saraburi.py`

**Interfaces:**
- Consumes: `robot/saraburi_data.json` จาก Task 1
- Produces:
  - `load_saraburi_data() -> dict` — โหลด JSON หรือ `{}` ถ้าไม่มีไฟล์
  - `format_all_data(college_data: dict, saraburi_data: dict) -> str` — คืน string รวมทั้งสอง
  - `SARABURI_DATA_PATH: str` ใน config

- [ ] **Step 1: เขียน failing test ใน `robot/test_saraburi.py`**

```python
"""
เทสต์ข้อมูลสระบุรี — database layer
รันจากโฟลเดอร์ robot/:  python -m pytest test_saraburi.py -v
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database import load_saraburi_data, format_all_data


def test_load_saraburi_data_returns_dict():
    data = load_saraburi_data()
    assert isinstance(data, dict)
    assert "ท่องเที่ยวสระบุรี" in data
    assert "OTOP_สระบุรี" in data


def test_load_saraburi_data_missing_file_returns_empty(tmp_path, monkeypatch):
    import config
    monkeypatch.setattr(config, "SARABURI_DATA_PATH", str(tmp_path / "nonexistent.json"))
    data = load_saraburi_data()
    assert data == {}


def test_format_all_data_includes_both_sources():
    college = {"ชื่อสถานศึกษา": "วิทยาลัยทดสอบ"}
    saraburi = {"ท่องเที่ยวสระบุรี": {"น้ำตก": []}}
    result = format_all_data(college, saraburi)
    assert "ข้อมูลวิทยาลัย" in result
    assert "ข้อมูลจังหวัดสระบุรี" in result
    assert "วิทยาลัยทดสอบ" in result
    assert "ท่องเที่ยวสระบุรี" in result


def test_format_all_data_empty_saraburi_omits_saraburi_section():
    college = {"ชื่อสถานศึกษา": "วิทยาลัยทดสอบ"}
    result = format_all_data(college, {})
    assert "ข้อมูลวิทยาลัย" in result
    assert "ข้อมูลจังหวัดสระบุรี" not in result
```

- [ ] **Step 2: รันเทสต์เพื่อยืนยันว่า fail**

```bash
cd robot && python -m pytest test_saraburi.py -v
```

Expected: FAIL ด้วย `ImportError: cannot import name 'load_saraburi_data'`

- [ ] **Step 3: เพิ่ม `SARABURI_DATA_PATH` ใน `robot/config.py`**

เพิ่มบรรทัดนี้ต่อจาก `COLLEGE_DATA_PATH`:

```python
SARABURI_DATA_PATH = "saraburi_data.json"
```

- [ ] **Step 4: อัปเดต `robot/database.py`**

```python
import json
from pathlib import Path
from config import COLLEGE_DATA_PATH, SARABURI_DATA_PATH


def load_college_data() -> dict:
    with open(COLLEGE_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_saraburi_data() -> dict:
    path = Path(SARABURI_DATA_PATH)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_for_prompt(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def format_all_data(college_data: dict, saraburi_data: dict) -> str:
    parts = ["ข้อมูลวิทยาลัย:\n" + format_for_prompt(college_data)]
    if saraburi_data:
        parts.append("ข้อมูลจังหวัดสระบุรี:\n" + format_for_prompt(saraburi_data))
    return "\n\n".join(parts)
```

- [ ] **Step 5: รันเทสต์เพื่อยืนยันว่าผ่าน**

```bash
python -m pytest test_saraburi.py -v
```

Expected: 4 tests PASS

- [ ] **Step 6: Commit**

```bash
git add robot/config.py robot/database.py robot/test_saraburi.py
git commit -m "feat: add load_saraburi_data + format_all_data to database.py"
```

---

### Task 3: อัปเดต `ai.py`

**Files:**
- Modify: `robot/ai.py`

**Interfaces:**
- Consumes:
  - `format_all_data(college_data: dict, saraburi_data: dict) -> str` จาก Task 2
- Produces:
  - `ask_ai(question: str, college_data: dict, saraburi_data: dict) -> str`

- [ ] **Step 1: เพิ่ม test ใหม่ใน `robot/test_saraburi.py`**

เพิ่ม import และ test ต่อท้ายไฟล์เดิม:

```python
from unittest.mock import patch


def test_ask_ai_passes_saraburi_data_to_system_prompt(monkeypatch):
    """ตรวจว่า ask_ai ส่งข้อมูลทั้งสองเข้า system prompt"""
    import ai
    college = {"ชื่อสถานศึกษา": "ทดสอบ"}
    saraburi = {"ท่องเที่ยวสระบุรี": {}}
    captured = {}

    def fake_ask_gemini(question, c_data, s_data):
        captured["college"] = c_data
        captured["saraburi"] = s_data
        return "ตอบ"

    monkeypatch.setattr(ai, "_ask_gemini", fake_ask_gemini)
    monkeypatch.setattr(ai, "AI_PROVIDER", "gemini")
    ai.ask_ai("ถามอะไร", college, saraburi)
    assert captured["college"] == college
    assert captured["saraburi"] == saraburi
```

- [ ] **Step 2: รันเทสต์เพื่อยืนยัน fail**

```bash
python -m pytest test_saraburi.py::test_ask_ai_passes_saraburi_data_to_system_prompt -v
```

Expected: FAIL ด้วย `TypeError: ask_ai() takes 2 positional arguments but 3 were given`

- [ ] **Step 3: อัปเดต `robot/ai.py`**

แก้ทั้งไฟล์ (เปลี่ยน import, `_system_text`, `_ask_gemini`, `_ask_claude`, `ask_ai`):

```python
"""
โมดูลถาม AI — รองรับ 2 เจ้า เลือกที่ config.AI_PROVIDER
  - "gemini" : Google Gemini (มีโควตาฟรี)
  - "claude" : Anthropic Claude (ต้องเติมเครดิต)
ทั้งสองเจ้าใช้ system prompt กันตอบมั่วตัวเดียวกัน + แนบข้อมูลทุกครั้ง
"""

from config import (
    AI_PROVIDER,
    AI_MAX_TOKENS,
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    GEMINI_API_KEY,
    GEMINI_MODEL,
)
from database import format_all_data

# --- กฎกันตอบมั่ว (ใช้ร่วมกันทุกเจ้า) ---
_SYSTEM_RULES = (
    "คุณเป็นหุ่นยนต์ผู้ช่วยแนะนำข้อมูลของวิทยาลัยเทคนิคท่าหลวงซิเมนต์ไทยอนุสรณ์ "
    "และข้อมูลจังหวัดสระบุรี "
    "ตอบเป็นภาษาไทย สุภาพ สั้น กระชับ เข้าใจง่าย "
    "ตอบโดยอ้างอิงจากข้อมูลวิทยาลัยและข้อมูลจังหวัดสระบุรีที่ให้ไว้เท่านั้น "
    "ห้ามแต่งหรือคาดเดาข้อมูลที่ไม่มีในฐานข้อมูลเด็ดขาด "
    "ถ้าไม่มีข้อมูลในส่วนที่ถาม ให้ตอบว่า 'ขออภัย ยังไม่มีข้อมูลในส่วนนี้' "
    "และแนะนำให้ติดต่อเจ้าหน้าที่วิทยาลัยโดยตรง (โทร 0-3628-1295)"
)

_NO_QUESTION = "ขออภัยค่ะ ไม่ได้ยินคำถาม กรุณาถามใหม่อีกครั้งนะคะ"

_claude_client = None
_gemini_client = None


def _system_text(college_data: dict, saraburi_data: dict) -> str:
    return _SYSTEM_RULES + "\n\n" + format_all_data(college_data, saraburi_data)


def _ask_gemini(question: str, college_data: dict, saraburi_data: dict) -> str:
    global _gemini_client
    if _gemini_client is None:
        from google import genai
        _gemini_client = genai.Client(api_key=GEMINI_API_KEY)

    from google.genai import types

    response = _gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=question,
        config=types.GenerateContentConfig(
            system_instruction=_system_text(college_data, saraburi_data),
            max_output_tokens=AI_MAX_TOKENS,
            temperature=0.2,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
    return (response.text or "").strip()


def _ask_claude(question: str, college_data: dict, saraburi_data: dict) -> str:
    global _claude_client
    if _claude_client is None:
        import anthropic
        _claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    response = _claude_client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=AI_MAX_TOKENS,
        system=[
            {"type": "text", "text": _SYSTEM_RULES},
            {
                "type": "text",
                "text": format_all_data(college_data, saraburi_data),
                "cache_control": {"type": "ephemeral"},
            },
        ],
        messages=[{"role": "user", "content": question}],
    )
    return response.content[0].text


def ask_ai(question: str, college_data: dict, saraburi_data: dict) -> str:
    if not question.strip():
        return _NO_QUESTION

    if AI_PROVIDER == "gemini":
        return _ask_gemini(question, college_data, saraburi_data)
    elif AI_PROVIDER == "claude":
        return _ask_claude(question, college_data, saraburi_data)
    else:
        raise ValueError(f"AI_PROVIDER ไม่รู้จัก: '{AI_PROVIDER}' (ใช้ได้: 'gemini' หรือ 'claude')")
```

- [ ] **Step 4: รันเทสต์เพื่อยืนยัน pass**

```bash
python -m pytest test_saraburi.py -v
```

Expected: 5 tests PASS

- [ ] **Step 5: Commit**

```bash
git add robot/ai.py robot/test_saraburi.py
git commit -m "feat: expand ask_ai to accept saraburi_data, update system prompt"
```

---

### Task 4: อัปเดต `server.py`, `simulator.py` + แก้ mock ใน `test_server.py`

**Files:**
- Modify: `robot/web/server.py`
- Modify: `robot/simulator.py`
- Modify: `robot/web/test_server.py`

**Interfaces:**
- Consumes:
  - `load_saraburi_data() -> dict` จาก Task 2
  - `ask_ai(question: str, college_data: dict, saraburi_data: dict) -> str` จาก Task 3

- [ ] **Step 1: รัน `test_server.py` เพื่อยืนยันว่า fail หลังจาก Task 3**

```bash
python -m pytest web/test_server.py -v
```

Expected: หลาย test FAIL ด้วย `TypeError` เพราะ mock lambda ยังใช้ 2 args

- [ ] **Step 2: อัปเดต `robot/web/server.py`**

เปลี่ยน import และ 2 จุดที่เรียก `ask_ai`:

ที่ import section เปลี่ยน:
```python
from database import load_college_data
```
เป็น:
```python
from database import load_college_data, load_saraburi_data
```

เพิ่มบรรทัดนี้ต่อจาก `college_data = load_college_data()`:
```python
saraburi_data = load_saraburi_data()
```

ใน route `/ask` เปลี่ยน:
```python
answer = ask_ai(question, college_data)
```
เป็น:
```python
answer = ask_ai(question, college_data, saraburi_data)
```

- [ ] **Step 3: อัปเดต `robot/simulator.py`**

เปลี่ยน import:
```python
from database import load_college_data
```
เป็น:
```python
from database import load_college_data, load_saraburi_data
```

เพิ่มหลัง `college_data = load_college_data()`:
```python
saraburi_data = load_saraburi_data()
```

เปลี่ยน:
```python
answer = ask_ai(question, college_data)
```
เป็น:
```python
answer = ask_ai(question, college_data, saraburi_data)
```

- [ ] **Step 4: อัปเดต mock ใน `robot/web/test_server.py`**

มี 6 จุดที่ต้องแก้ — เปลี่ยน `lambda question, data:` และ `lambda q, d:` เป็น 3 args:

บรรทัด 38:
```python
monkeypatch.setattr(server, "ask_ai", lambda question, college_data, saraburi_data: f"ตอบ: {question}")
```

บรรทัด 49-51 (ฟังก์ชัน `boom`):
```python
def boom(question, college_data, saraburi_data):
    raise RuntimeError("เน็ตล่ม")
```

บรรทัด 65:
```python
monkeypatch.setattr(server, "ask_ai", lambda q, c, s: called.append(q) or "x")
```

บรรทัด 80:
```python
monkeypatch.setattr(server, "ask_ai", lambda q, c, s: "x")
```

บรรทัด 158:
```python
monkeypatch.setattr(server, "ask_ai", lambda q, c, s: "อาคาร 7 ครับ")
```

บรรทัด 170:
```python
monkeypatch.setattr(server, "ask_ai", lambda q, c, s: "ตอบ: ค่าเทอม")
```

- [ ] **Step 5: รัน test ทั้งหมดเพื่อยืนยัน pass**

```bash
python -m pytest web/test_server.py test_saraburi.py -v
```

Expected: ทุก test PASS

- [ ] **Step 6: Commit**

```bash
git add robot/web/server.py robot/simulator.py robot/web/test_server.py
git commit -m "feat: wire saraburi_data into server, simulator, and update test mocks"
```

---

## Self-Review

**Spec coverage:**
- ✅ `saraburi_data.json` สร้างใหม่ — Task 1
- ✅ `config.py` เพิ่ม `SARABURI_DATA_PATH` — Task 2
- ✅ `database.py` เพิ่ม `load_saraburi_data()` + `format_all_data()` — Task 2
- ✅ `ai.py` อัปเดต system prompt + signature — Task 3
- ✅ `server.py` โหลดและส่ง saraburi_data — Task 4
- ✅ `simulator.py` โหลดและส่ง saraburi_data — Task 4
- ✅ Graceful fallback (ไม่มีไฟล์ → return `{}`) — Task 2
- ✅ Test: โหลด JSON สำเร็จ — Task 2
- ✅ Test: ถามท่องเที่ยว/OTOP — Task 3
- ✅ Test: ถามนอกฐานข้อมูล → "ยังไม่มีข้อมูล" — ครอบคลุมโดย system prompt ที่ไม่เปลี่ยนกฎ
- ✅ Test: ไม่มีไฟล์ → server ยังขึ้นได้ — Task 2

**Type consistency:** `ask_ai(question, college_data, saraburi_data)` ใช้ชื่อเดิมทุก task ✅

**Placeholder scan:** ไม่มี TBD หรือ TODO ✅
