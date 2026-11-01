"""
เทสต์แขนโบก — ใช้ไดรเวอร์ปลอม (ไม่ต้องมี PCA9685/เซอร์โวจริง)
รันจากโฟลเดอร์ robot/:  python -m pytest web/test_arm.py -v
"""
import threading

import config
from arm import Arm, wave_steps


class FakeDriver:
    """จำว่าสั่งเซอร์โวช่องไหนไปกี่องศา"""

    def __init__(self):
        self.moves = []
        self.angles = {}

    def set_angle(self, channel, angle):
        self.moves.append((channel, angle))
        self.angles[channel] = angle


def no_sleep(_):
    pass


def test_wave_steps_raise_wave_then_return_to_rest():
    steps = wave_steps()
    sh, el = config.ARM_SHOULDER_CH, config.ARM_ELBOW_CH
    # ท่าแรกคือยกหัวไหล่ ท่าสุดท้ายคือหัวไหล่กลับท่าพัก
    assert steps[0][:2] == (sh, config.ARM_SHOULDER_UP)
    assert steps[-1][:2] == (sh, config.ARM_SHOULDER_REST)
    # ข้อศอกโบกไป-กลับครบตามจำนวนครั้งที่ตั้งไว้
    elbow_targets = [a for ch, a, _ in steps if ch == el]
    assert elbow_targets.count(config.ARM_ELBOW_WAVE_A) == config.ARM_WAVE_TIMES
    assert elbow_targets.count(config.ARM_ELBOW_WAVE_B) == config.ARM_WAVE_TIMES
    assert elbow_targets[-1] == config.ARM_ELBOW_REST


def test_wave_moves_servos_and_ends_at_rest():
    drv = FakeDriver()
    arm = Arm(driver=drv, sleep=no_sleep, background=False)
    assert arm.wave() is True
    assert drv.angles[config.ARM_SHOULDER_CH] == config.ARM_SHOULDER_REST
    assert drv.angles[config.ARM_ELBOW_CH] == config.ARM_ELBOW_REST
    assert len(drv.moves) > 4
    assert arm.busy is False


def test_moves_are_smooth_not_jumps():
    """เซอร์โวต้องค่อยๆ ขยับ (ทีละไม่เกิน ARM_STEP_DEG) ไม่กระชากทีเดียว — กันไฟกระชาก"""
    drv = FakeDriver()
    arm = Arm(driver=drv, sleep=no_sleep, background=False)
    arm.wave()
    last = {}
    for ch, angle in drv.moves:
        if ch in last:
            assert abs(angle - last[ch]) <= config.ARM_STEP_DEG
        last[ch] = angle


def test_wave_while_busy_is_ignored():
    drv = FakeDriver()
    gate = threading.Event()
    arm = Arm(driver=drv, sleep=lambda _: gate.wait(2), background=True)
    assert arm.wave() is True       # เริ่มโบก (ค้างรอ gate)
    assert arm.wave() is False      # สั่งซ้อนตอนกำลังโบก → ไม่รับ
    gate.set()
    arm.join(timeout=5)
    assert arm.busy is False
    assert arm.wave() is True       # โบกเสร็จแล้วสั่งใหม่ได้
    arm.join(timeout=5)


def test_simulator_arm_needs_no_hardware(capsys):
    arm = Arm(simulator=True, sleep=no_sleep, background=False)
    assert arm.wave() is True
    assert "โบก" in capsys.readouterr().out


def test_wave_angles_stay_in_servo_range():
    for _, angle, _ in wave_steps():
        assert 0 <= angle <= 180


def test_missing_hardware_falls_back_to_simulator(monkeypatch, capsys):
    """บน Pi ที่ยังไม่ได้เสียบ PCA9685 → เซิร์ฟเวอร์ต้องไม่ล่ม แค่เตือนแล้วทำงานต่อแบบไม่มีแขน"""
    import arm as arm_mod

    def broken():
        raise ValueError("No I2C device at address: 0x40")

    monkeypatch.setattr(arm_mod, "_ServoKitDriver", broken)
    a = Arm(simulator=False, sleep=no_sleep, background=False)
    assert "PCA9685" in capsys.readouterr().out
    assert a.wave() is True
