"""
แขนโบกมือของหุ่น — เซอร์โว MG996R ต่อบอร์ด PCA9685 (I2C) บน Raspberry Pi
SIMULATOR_MODE=True: ไม่แตะฮาร์ดแวร์ แค่พิมพ์บอกในหน้าต่างเซิร์ฟเวอร์ (ทดสอบบนคอมได้)
องศา/ช่องเซอร์โวทั้งหมดตั้งใน config.py

⚠ ไฟเลี้ยงเซอร์โวต้องมาจากตัวแปลงไฟแยก ห้ามดึงจากขา 5V ของ Pi (Pi จะรีสตาร์ทตอนแขนยก)
"""
import threading
import time

import config


def wave_steps():
    """ลำดับท่าโบก 1 รอบ: [(ช่อง, องศาเป้าหมาย, พักหลังถึง (วินาที)), ...]"""
    sh, el = config.ARM_SHOULDER_CH, config.ARM_ELBOW_CH
    steps = [(sh, config.ARM_SHOULDER_UP, 0.2)]
    for _ in range(config.ARM_WAVE_TIMES):
        steps.append((el, config.ARM_ELBOW_WAVE_A, 0.05))
        steps.append((el, config.ARM_ELBOW_WAVE_B, 0.05))
    steps.append((el, config.ARM_ELBOW_REST, 0.1))
    steps.append((sh, config.ARM_SHOULDER_REST, 0.0))
    return steps


class _ServoKitDriver:
    """ไดรเวอร์จริง: ใช้ไลบรารี adafruit-circuitpython-servokit"""

    def __init__(self):
        from adafruit_servokit import ServoKit   # มีเฉพาะบน Pi
        self._kit = ServoKit(channels=16, address=config.ARM_I2C_ADDRESS)
        for ch in (config.ARM_SHOULDER_CH, config.ARM_ELBOW_CH, config.ARM_NECK_CH):
            self._kit.servo[ch].set_pulse_width_range(500, 2500)   # ช่วงพัลส์ของ MG996R

    def set_angle(self, channel, angle):
        self._kit.servo[channel].angle = angle


class _PrintDriver:
    """โหมดจำลอง: ไม่ขยับอะไร"""

    def set_angle(self, channel, angle):
        pass


class Arm:
    def __init__(self, driver=None, simulator=None, sleep=time.sleep, background=True):
        if simulator is None:
            simulator = config.SIMULATOR_MODE
        self._sim = simulator and driver is None
        if driver is None and not simulator:
            try:
                driver = _ServoKitDriver()
            except Exception as e:   # ยังไม่ได้เสียบ PCA9685 / ยังไม่เปิด I2C / ยังไม่ลงไลบรารี
                print(f"[arm] ⚠ หาบอร์ด PCA9685 ไม่เจอ ({e}) — ทำงานต่อแบบไม่ขยับแขน")
                self._sim = True
        if driver is None:
            driver = _PrintDriver()
        self._drv = driver
        self._sleep = sleep
        self._background = background
        self._lock = threading.Lock()
        self._thread = None
        self._pos = {}
        self.busy = False
        # ท่าเริ่มต้นตอนเปิดเครื่อง (ตั้งตรงๆ ครั้งเดียว ยังไม่รู้ว่าเซอร์โวค้างอยู่ที่ไหน)
        for ch, angle in ((config.ARM_SHOULDER_CH, config.ARM_SHOULDER_REST),
                          (config.ARM_ELBOW_CH, config.ARM_ELBOW_REST),
                          (config.ARM_NECK_CH, config.ARM_NECK_CENTER)):
            self._set(ch, angle)

    def _set(self, ch, angle):
        self._drv.set_angle(ch, angle)
        self._pos[ch] = angle

    def _move(self, ch, target):
        """ค่อยๆ ขยับทีละ ARM_STEP_DEG จนถึงเป้า"""
        cur = self._pos.get(ch, target)
        step = config.ARM_STEP_DEG
        while cur != target:
            cur = min(cur + step, target) if target > cur else max(cur - step, target)
            self._set(ch, cur)
            self._sleep(config.ARM_STEP_SECONDS)

    def _run(self):
        try:
            for ch, target, pause in wave_steps():
                self._move(ch, target)
                if pause:
                    self._sleep(pause)
        except Exception as e:   # เซอร์โว/I2C มีปัญหา — ไม่ให้เซิร์ฟเวอร์ล่ม
            print(f"[arm] ขยับแขนไม่ได้: {e}")
        finally:
            self.busy = False

    def wave(self):
        """สั่งโบกมือ 1 รอบ คืน True ถ้าเริ่มโบก / False ถ้ายังโบกรอบเก่าไม่เสร็จ"""
        with self._lock:
            if self.busy:
                return False
            self.busy = True
        if self._sim:
            print("[arm] 👋 โบกมือ (โหมดจำลอง)")
        if self._background:
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
        else:
            self._run()
        return True

    def join(self, timeout=None):
        if self._thread:
            self._thread.join(timeout)
