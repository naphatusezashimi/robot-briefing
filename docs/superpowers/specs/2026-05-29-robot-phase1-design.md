# Design Spec: หุ่นยนต์แนะนำข้อมูลวิทยาลัยเทคนิคท่าหลวง — เฟส 1

**วันที่:** 2026-05-29  
**สถานะ:** อนุมัติแล้ว  
**ขอบเขต:** เฟส 1 — โครงและโหมดจำลอง (ไม่ต้องมีอุปกรณ์)

---

## ภาพรวม

ระบบหุ่นยนต์ตอบคำถามผู้มาติดต่อวิทยาลัยโดยใช้ Claude API เป็น AI หลัก  
เฟส 1 สร้างโครงไฟล์ครบทุกตัว และทำให้วนลูปหลักทำงานได้ผ่านการพิมพ์แทนเสียง

**เป้าหมายเฟส 1:** พิมพ์คำถามเรื่องวิทยาลัย → ได้คำตอบจาก AI บนหน้าจอคอม

---

## โครงสร้างไฟล์

```
robot-briefing/
├── BRIEF.md
├── college_data.example.json
├── robot_main_reference.py
├── docs/superpowers/specs/
│   └── 2026-05-29-robot-phase1-design.md   ← ไฟล์นี้
└── robot/
    ├── main.py              วนลูปหลัก — เลือกโหมดจาก config แล้วรัน
    ├── config.py            สวิตช์ SIMULATOR_MODE + env var ทั้งหมด
    ├── database.py          โหลด college_data.json + แปลงเป็น string
    ├── ai.py                Anthropic SDK + prompt caching + กันตอบมั่ว
    ├── stt.py               stub เฟส 1 / Google STT จริงเฟส 2
    ├── tts.py               stub เฟส 1 / Google TTS จริงเฟส 2
    ├── output.py            print/LED simulator เฟส 1 / ฮาร์ดแวร์จริงเฟส 3
    ├── simulator.py         loop: input() → ai → show_on_screen
    ├── college_data.json    ฐานข้อมูลวิทยาลัย (copy จาก example แล้วเติมข้อมูลจริง)
    ├── requirements.txt
    ├── .env.example
    ├── .gitignore
    └── README.md
```

---

## config.py — จุดควบคุมโหมด

```python
SIMULATOR_MODE = True   # False = ฮาร์ดแวร์จริง
```

ทุกโมดูลอ่าน flag นี้เพื่อตัดสินใจพฤติกรรม  
เปลี่ยนโหมดทั้งระบบโดยแก้บรรทัดเดียว

---

## ai.py — หัวใจของระบบ

### กันตอบมั่ว (สำคัญที่สุด)

System prompt บังคับ 3 ข้อ:
1. ตอบจากข้อมูลวิทยาลัยที่ให้ไว้เท่านั้น
2. ห้ามแต่งหรือคาดเดาข้อมูลที่ไม่มีในฐานข้อมูล
3. ถ้าไม่มีข้อมูล → ตอบว่ายังไม่มี และแนะนำติดต่อเจ้าหน้าที่

### Prompt Caching

`college_data.json` ถูกส่งใน system prompt พร้อม `cache_control: ephemeral`  
→ Anthropic cache ข้อมูลนี้ไว้ที่ server 5 นาที  
→ ประหยัด input token ในการทดสอบซ้ำ (college_data มักไม่เปลี่ยน)

### Model

`claude-sonnet-4-6` — รองรับ prompt caching, max_tokens 500 เพียงพอสำหรับคำตอบสั้น

---

## output.py — สถานะ LED และหน้าจอ

| สถานะ | LED จริง (เฟส 3) | โหมดจำลอง (เฟส 1) |
|-------|----------------|------------------|
| รอ    | ขาว            | print `[LED] สีขาว` |
| ฟัง   | ฟ้า            | print `[LED] สีฟ้า` |
| คิด   | เหลือง         | print `[LED] สีเหลือง` |
| ตอบ   | เขียว          | print `[LED] สีเขียว` |
| ผิดพลาด | แดง          | print `[LED] สีแดง` |

---

## simulator.py — flow เฟส 1

```
รัน python simulator.py
  ↓
โหลด college_data.json
  ↓
[loop]
  LED: รอ → รับ input() จากคีย์บอร์ด
  LED: คิด → ส่งคำถาม + college_data → Claude API
  LED: ตอบ → print คำตอบบนหน้าจอ
  ↓ วนซ้ำ (พิมพ์ q เพื่อออก)
```

---

## stub ที่รอเฟสถัดไป

| ไฟล์  | เฟส 1 | เฟส 2 | เฟส 3 |
|-------|-------|-------|-------|
| stt.py | raise RuntimeError | Google STT th-TH | — |
| tts.py | return ทันที | Google TTS th-TH | — |
| output.py | print | print | Tkinter + rpi_ws281x |

---

## ความปลอดภัย

- API key เก็บใน `.env` (โหลดผ่าน `python-dotenv`)
- `.gitignore` ครอบ `.env` และไฟล์ credentials ทุกชนิด
- ห้าม hardcode key ในโค้ดทุกไฟล์

---

## เฟสถัดไป

- **เฟส 2:** ต่อ Google STT + TTS ทดสอบด้วยไฟล์เสียง ยังไม่ต้องมีไมค์จริง
- **เฟส 3:** เปิด `SIMULATOR_MODE = False` ต่อฮาร์ดแวร์จริงบน Raspberry Pi 5
- **เฟส 4:** เพิ่ม log คำถาม-คำตอบ + ปุ่มพิมพ์สำรอง
