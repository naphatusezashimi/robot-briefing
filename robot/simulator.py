"""
โหมดจำลอง — รันบนคอมธรรมดา ไม่ต้องมีไมค์/ลำโพง/จอจริง
รัน: python simulator.py
"""

from database import load_college_data
from ai import ask_ai
from output import set_led, show_on_screen


def run():
    print("=" * 55)
    print("  หุ่นยนต์วิทยาลัยเทคนิคท่าหลวง — โหมดจำลอง")
    print("=" * 55)
    print("พิมพ์คำถามเกี่ยวกับวิทยาลัย หรือพิมพ์ q เพื่อออก\n")

    college_data = load_college_data()

    while True:
        try:
            set_led("รอ")
            question = input("คุณ: ").strip()

            if not question:
                continue
            if question.lower() in ("q", "quit", "exit", "ออก"):
                print("ปิดระบบ")
                break

            set_led("คิด")
            answer = ask_ai(question, college_data)

            set_led("ตอบ")
            show_on_screen(answer)

        except KeyboardInterrupt:
            print("\nปิดระบบ")
            break
        except Exception as e:
            set_led("ผิดพลาด")
            print(f"[ผิดพลาด] {e}")


if __name__ == "__main__":
    run()
