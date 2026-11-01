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
SARABURI_DATA_PATH = "saraburi_data.json"

# --- ตั้งค่าเว็บ (เฟสกล่องพูดได้) ---
WEB_HOST = "127.0.0.1"     # เปิดเฉพาะเครื่องตัวเอง
WEB_PORT = 5000
SPEECH_LANG = "th-TH"      # ภาษาเสียงฟัง/พูดในเบราว์เซอร์

# --- ตั้งค่า GPIO (เฟส 2) ---
GPIO_BUTTON_PIN = 18  # BCM pin สำหรับปุ่มกายภาพ (เปลี่ยนได้)

# --- ทักทาย ---
GREET_IDLE_SECONDS = 60   # ไม่มีใครใช้นานเท่านี้ (วินาที) แล้วมีคนแตะจอ → หุ่นโบกมือทักก่อน 1 ครั้ง

# --- แขนโบกมือ: เซอร์โว MG996R ต่อบอร์ด PCA9685 (I2C) ---
# ประกอบจริงแล้วแขนเอียงผิดมุม → แก้ตัวเลของศาตรงนี้ที่เดียว (0–180)
ARM_I2C_ADDRESS = 0x40    # ค่าเริ่มต้นของ PCA9685
ARM_SHOULDER_CH = 0       # ช่องบน PCA9685 ที่เสียบเซอร์โวหัวไหล่
ARM_ELBOW_CH = 1          # ช่องของเซอร์โวข้อศอก
ARM_NECK_CH = 2           # ช่องของเซอร์โวคอ (ยังไม่ใช้ในรอบนี้ ตั้งให้หันตรงตอนเปิดเครื่อง)
ARM_SHOULDER_REST = 10    # แขนห้อยลง
ARM_SHOULDER_UP = 160     # แขนยกขึ้น
ARM_ELBOW_REST = 90
ARM_ELBOW_WAVE_A = 60     # โบกไปทางหนึ่ง
ARM_ELBOW_WAVE_B = 120    # โบกกลับอีกทาง
ARM_NECK_CENTER = 90
ARM_WAVE_TIMES = 3        # โบกไป-กลับกี่ครั้ง
ARM_STEP_DEG = 5          # ขยับทีละกี่องศา (น้อย = นุ่มนวล ไม่กระชากไฟ)
ARM_STEP_SECONDS = 0.015  # เว้นระหว่างแต่ละก้าว (มาก = ช้าลง)
