from config import SIMULATOR_MODE

_LED_LABELS = {
    "ฟัง":      "[LED] สีฟ้า     = กำลังฟัง",
    "คิด":      "[LED] สีเหลือง  = กำลังคิด",
    "ตอบ":      "[LED] สีเขียว   = กำลังตอบ",
    "รอ":       "[LED] สีขาว     = รอคำถาม",
    "ผิดพลาด":  "[LED] สีแดง     = เกิดข้อผิดพลาด",
}


def set_led(state: str):
    label = _LED_LABELS.get(state, f"[LED] {state}")
    if SIMULATOR_MODE:
        print(label)
    else:
        # เฟส 3: ใช้ rpi_ws281x ควบคุม WS2812B
        pass


def show_on_screen(text: str):
    if SIMULATOR_MODE:
        print(f"\n{'─' * 50}")
        print(f"  {text}")
        print(f"{'─' * 50}\n")
    else:
        # เฟส 3: Tkinter / PyQt / หน้าเว็บ
        pass


def play_audio(audio_file: str):
    if SIMULATOR_MODE:
        pass  # เฟส 1 ไม่เล่นเสียง
    else:
        import os
        os.system(f"aplay {audio_file}")
