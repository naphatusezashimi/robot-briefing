"""
จุดเริ่มต้นของระบบ — เลือกโหมดจาก config.py แล้วรัน
รัน: python main.py
"""

from config import SIMULATOR_MODE


def main():
    if SIMULATOR_MODE:
        from simulator import run
        run()
        return

    # โหมดฮาร์ดแวร์จริง (เฟส 3)
    from database import load_college_data
    from stt import record_audio, speech_to_text
    from ai import ask_ai
    from tts import text_to_speech
    from output import set_led, show_on_screen, play_audio

    college_data = load_college_data()
    print("=== หุ่นยนต์วิทยาลัยเทคนิคท่าหลวง พร้อมทำงาน ===")

    while True:
        try:
            set_led("ฟัง")
            record_audio()
            question = speech_to_text()

            set_led("คิด")
            answer = ask_ai(question, college_data)

            set_led("ตอบ")
            show_on_screen(answer)
            text_to_speech(answer)
            play_audio()

        except KeyboardInterrupt:
            print("\nปิดระบบ")
            break
        except Exception as e:
            set_led("ผิดพลาด")
            print(f"[ผิดพลาด] {e}")


if __name__ == "__main__":
    main()
