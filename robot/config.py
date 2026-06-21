import os
from dotenv import load_dotenv

load_dotenv()

# --- สวิตช์หลัก: True = จำลองบนคอม, False = ฮาร์ดแวร์จริงบน Pi ---
SIMULATOR_MODE = True

# --- API Keys (เก็บใน .env ไม่ hardcode) ---
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")

# --- ตั้งค่า AI ---
# เลือกเจ้าผู้ให้บริการ AI: "gemini" (ฟรี) หรือ "claude" (ต้องเติมเครดิต)
# สลับกลับไปใช้ Claude ได้โดยแก้บรรทัดเดียวนี้
AI_PROVIDER = "gemini"
AI_MAX_TOKENS = 800

# โมเดลของแต่ละเจ้า
CLAUDE_MODEL = "claude-sonnet-4-6"
GEMINI_MODEL = "gemini-2.5-flash"

# --- ตั้งค่าเสียง (เฟส 2) ---
RECORD_SECONDS = 5
SAMPLE_RATE = 16000
AUDIO_IN = "question.wav"
AUDIO_OUT = "answer.wav"

# --- ไฟล์ฐานข้อมูล ---
COLLEGE_DATA_PATH = "college_data.json"

# --- ตั้งค่าเว็บ (เฟสกล่องพูดได้) ---
WEB_HOST = "127.0.0.1"     # เปิดเฉพาะเครื่องตัวเอง
WEB_PORT = 5000
SPEECH_LANG = "th-TH"      # ภาษาเสียงฟัง/พูดในเบราว์เซอร์

# --- ตั้งค่า GPIO (เฟส 2) ---
GPIO_BUTTON_PIN = 18  # BCM pin สำหรับปุ่มกายภาพ (เปลี่ยนได้)
