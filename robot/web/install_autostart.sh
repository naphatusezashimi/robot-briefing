#!/bin/bash
# รันบน Pi ครั้งเดียว:  bash robot/web/install_autostart.sh
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "[1/4] ติดตั้ง systemd service..."
sudo cp "$SCRIPT_DIR/robot.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable robot.service
sudo systemctl start robot.service

echo "[2/4] ติดตั้ง Chromium kiosk autostart..."
mkdir -p ~/.config/autostart
cp "$SCRIPT_DIR/robot-kiosk.desktop" ~/.config/autostart/

echo ""
echo "⚠  สำคัญ: แก้ SIMULATOR_MODE ใน robot/config.py ก่อนใช้งานบน Pi"
echo "   เปิดไฟล์: nano /home/pi/robot-briefing/robot/config.py"
echo "   เปลี่ยน: SIMULATOR_MODE = True"
echo "   เป็น:    SIMULATOR_MODE = False"
echo ""

echo "[3/4] ติดตั้ง RPi.GPIO (ถ้ายังไม่มี)..."
sudo apt-get install -y python3-rpi.gpio 2>/dev/null || pip install RPi.GPIO --quiet --break-system-packages

echo "[4/4] เปิด I2C + ติดตั้งไลบรารีเซอร์โว (แขนโบก ผ่านบอร์ด PCA9685)..."
sudo raspi-config nonint do_i2c 0
pip install adafruit-circuitpython-servokit --quiet --break-system-packages
chmod +x "$SCRIPT_DIR/kiosk.sh"

echo "Done. รัน 'sudo reboot' เพื่อทดสอบ autostart เต็มรูปแบบ"
