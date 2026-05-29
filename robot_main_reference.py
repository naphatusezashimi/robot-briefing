"""
========================================================================
 หุ่นยนต์แนะนำข้อมูลวิทยาลัยเทคนิคท่าหลวง  -  โครงโค้ดตัวอย่าง (Python)
========================================================================
 รันบน  : Raspberry Pi 5
 แนวคิด : รับเสียง -> แปลงเป็นข้อความ -> ถาม AI (พร้อมข้อมูลวิทยาลัย)
          -> แปลงคำตอบเป็นเสียง -> เล่นออกลำโพง + แสดงผล/ไฟ LED

 *** นี่เป็นโครงตัวอย่างเพื่อให้เห็นภาพว่าแต่ละขั้นเชื่อมกันอย่างไร ***
 *** ต้องเติม API key และปรับให้เข้ากับอุปกรณ์จริงก่อนใช้งาน      ***

 ติดตั้งไลบรารีที่ใช้ (รันใน terminal บน Pi):
   pip install sounddevice scipy requests anthropic google-cloud-speech \
               google-cloud-texttospeech
========================================================================
"""

import os
import json
import wave
import requests

# ----------------------------------------------------------------------
# 0) ตั้งค่า  (เก็บ key ไว้ใน Environment Variable ไม่ควร hardcode ในไฟล์)
# ----------------------------------------------------------------------
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")   # สำหรับถาม AI
GOOGLE_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")  # STT/TTS

AUDIO_IN = "question.wav"     # ไฟล์เสียงที่อัดจากผู้ใช้
AUDIO_OUT = "answer.wav"      # ไฟล์เสียงคำตอบ
RECORD_SECONDS = 5            # อัดเสียงนานกี่วินาที


# ----------------------------------------------------------------------
# 1) ฐานข้อมูลวิทยาลัย
#    เริ่มจากไฟล์ JSON ง่าย ๆ ก่อน พอโตค่อยย้ายไป SQLite/ฐานข้อมูลจริง
#    *** ข้อมูลตรงนี้คือหัวใจ ต้องอัปเดตให้ถูกต้องเสมอ ***
# ----------------------------------------------------------------------
def load_college_data():
    """โหลดข้อมูลวิทยาลัยจากไฟล์ college_data.json"""
    try:
        with open("college_data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # ตัวอย่างโครงสร้างข้อมูล - แก้เป็นข้อมูลจริงของวิทยาลัย
        return {
            "ปรับปรุงล่าสุด": "2569-05-01",
            "หลักสูตร": [
                "ปวช. ช่างยนต์", "ปวช. ช่างไฟฟ้า", "ปวช. ช่างอิเล็กทรอนิกส์",
                "ปวส. เทคนิคยานยนต์", "ปวส. ไฟฟ้ากำลัง"
            ],
            "การรับสมัคร": "เปิดรับสมัครรอบปกติ เดือนกุมภาพันธ์ถึงมีนาคม สมัครออนไลน์ผ่านเว็บไซต์วิทยาลัย",
            "ค่าเทอม": "ระดับ ปวช. เรียนฟรีตามนโยบายรัฐ มีค่าบำรุงการศึกษาตามที่วิทยาลัยกำหนด",
            "ติดต่อ": "ฝ่ายทะเบียน โทร 0xx-xxx-xxxx เวลาราชการ",
        }


# ----------------------------------------------------------------------
# 2) อัดเสียงจากไมโครโฟน  (Input)
# ----------------------------------------------------------------------
def record_audio(filename=AUDIO_IN, seconds=RECORD_SECONDS, samplerate=16000):
    """อัดเสียงจากไมค์เป็นไฟล์ wav"""
    import sounddevice as sd
    from scipy.io.wavfile import write

    print(f"[ไมค์] กำลังฟัง... พูดได้เลย ({seconds} วินาที)")
    audio = sd.rec(int(seconds * samplerate), samplerate=samplerate,
                   channels=1, dtype="int16")
    sd.wait()
    write(filename, samplerate, audio)
    print("[ไมค์] อัดเสียงเสร็จแล้ว")
    return filename


# ----------------------------------------------------------------------
# 3) แปลงเสียงเป็นข้อความ  (Speech Recognition / STT)
#    ใช้ Google Cloud Speech-to-Text รองรับภาษาไทยดี
# ----------------------------------------------------------------------
def speech_to_text(filename=AUDIO_IN):
    """ส่งไฟล์เสียงไปแปลงเป็นข้อความภาษาไทย"""
    from google.cloud import speech

    client = speech.SpeechClient()
    with open(filename, "rb") as f:
        content = f.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="th-TH",      # ภาษาไทย
    )
    response = client.recognize(config=config, audio=audio)

    if not response.results:
        return ""   # ฟังไม่ออก
    text = response.results[0].alternatives[0].transcript
    print(f"[STT] ผู้ใช้ถามว่า: {text}")
    return text


# ----------------------------------------------------------------------
# 4) ถาม AI พร้อมแนบข้อมูลวิทยาลัย  (AI Processing + ค้นฐานข้อมูล)
#    เคล็ดลับสำคัญ: ใส่ข้อมูลวิทยาลัยลงใน prompt และสั่งห้ามมั่ว
#    ถ้าไม่มีข้อมูล ให้ตอบว่าไม่ทราบ + แนะนำให้ติดต่อเจ้าหน้าที่
# ----------------------------------------------------------------------
def ask_ai(question, college_data):
    """ส่งคำถาม + ข้อมูลวิทยาลัยไปให้ AI ตอบ"""
    if not question.strip():
        return "ขออภัยค่ะ ไม่ได้ยินคำถาม กรุณาพูดอีกครั้งนะคะ"

    system_prompt = (
        "คุณเป็นหุ่นยนต์ผู้ช่วยแนะนำข้อมูลของวิทยาลัยเทคนิคท่าหลวง "
        "ตอบเป็นภาษาไทยสุภาพ สั้น กระชับ เข้าใจง่าย "
        "ให้ตอบโดยอ้างอิงจากข้อมูลวิทยาลัยที่ให้ไว้เท่านั้น "
        "ห้ามแต่งข้อมูลเอง หากไม่มีข้อมูลในที่ให้มา ให้บอกว่ายังไม่มีข้อมูล "
        "และแนะนำให้ติดต่อเจ้าหน้าที่ของวิทยาลัยโดยตรง\n\n"
        "ข้อมูลวิทยาลัย:\n" + json.dumps(college_data, ensure_ascii=False, indent=2)
    )

    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 500,
            "system": system_prompt,
            "messages": [{"role": "user", "content": question}],
        },
        timeout=30,
    )
    data = resp.json()
    answer = data["content"][0]["text"]
    print(f"[AI] ตอบว่า: {answer}")
    return answer


# ----------------------------------------------------------------------
# 5) แปลงข้อความเป็นเสียง  (Text to Speech / TTS)
# ----------------------------------------------------------------------
def text_to_speech(text, filename=AUDIO_OUT):
    """แปลงคำตอบเป็นเสียงภาษาไทย แล้วบันทึกเป็น wav"""
    from google.cloud import texttospeech

    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="th-TH",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    with open(filename, "wb") as out:
        out.write(response.audio_content)
    print("[TTS] สร้างเสียงคำตอบเสร็จแล้ว")
    return filename


# ----------------------------------------------------------------------
# 6) เล่นเสียง + แสดงผล/ไฟ LED  (Output)
# ----------------------------------------------------------------------
def play_audio(filename=AUDIO_OUT):
    """เล่นไฟล์เสียงออกลำโพง"""
    os.system(f"aplay {filename}")   # คำสั่งเล่นเสียงบน Linux/Pi

def show_on_screen(text):
    """แสดงข้อความบนหน้าจอ (ตัวอย่าง: print เฉย ๆ ก่อน)
       ของจริงทำเป็นหน้าจอด้วย Tkinter / PyQt / เว็บ"""
    print(f"[จอ] แสดง: {text}")

def set_led(state):
    """ควบคุมไฟ LED ตามสถานะ เช่น ฟัง=ฟ้า / คิด=เหลือง / ตอบ=เขียว"""
    print(f"[LED] เปลี่ยนเป็นสถานะ: {state}")
    # ของจริงใช้ไลบรารี เช่น rpi_ws281x ควบคุม WS2812B


# ----------------------------------------------------------------------
# 7) วนลูปการทำงานหลัก  (ตรงกับ Flow ในแผนภาพ + Feedback loop)
# ----------------------------------------------------------------------
def main():
    college_data = load_college_data()
    print("=== หุ่นยนต์แนะนำข้อมูลวิทยาลัยเทคนิคท่าหลวง พร้อมทำงาน ===")

    while True:
        try:
            set_led("ฟัง")                       # ไฟฟ้า = กำลังฟัง
            record_audio()                        # 1. รับเสียง
            question = speech_to_text()           # 2. แปลงเสียงเป็นข้อความ

            set_led("คิด")                        # ไฟเหลือง = กำลังคิด
            answer = ask_ai(question, college_data)  # 3+4. AI + ค้นข้อมูล

            set_led("ตอบ")                        # ไฟเขียว = กำลังตอบ
            show_on_screen(answer)                # 5. แสดงบนจอ
            text_to_speech(answer)                # 5. แปลงเป็นเสียง
            play_audio()                          # 6. เล่นออกลำโพง

            # ---- Feedback loop: ถามต่อได้เรื่อย ๆ ----
            cont = input("ถามต่อไหม? (กด Enter เพื่อถามต่อ / พิมพ์ q เพื่อออก): ")
            if cont.strip().lower() == "q":
                break

        except KeyboardInterrupt:
            print("\nปิดระบบ")
            break
        except Exception as e:
            # ไม่ให้โปรแกรมล่ม ถ้าพังขั้นไหนให้แจ้งแล้วไปต่อ
            print(f"[ผิดพลาด] {e}")
            set_led("ฟัง")


if __name__ == "__main__":
    main()
