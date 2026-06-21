import queue
from config import SIMULATOR_MODE, GPIO_BUTTON_PIN


class GpioButton:
    """ตรวจปุ่ม GPIO และ push "mic-start" เข้า queue เมื่อกด
    SIMULATOR_MODE=True: ไม่ทำอะไร (ใช้ปุ่มบน touchscreen แทน)
    """

    def __init__(self, event_queue: queue.Queue, debounce_ms: int = 50):
        self._q = event_queue
        if SIMULATOR_MODE:
            return
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(GPIO_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            GPIO_BUTTON_PIN,
            GPIO.FALLING,
            callback=self._on_press,
            bouncetime=debounce_ms,
        )

    def _on_press(self, channel):
        self._q.put("mic-start")
