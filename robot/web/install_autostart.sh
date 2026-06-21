#!/bin/bash
# รันบน Pi ครั้งเดียว:  bash robot/web/install_autostart.sh
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "[1/3] ติดตั้ง systemd service..."
sudo cp "$SCRIPT_DIR/robot.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable robot.service
sudo systemctl start robot.service

echo "[2/3] ติดตั้ง Chromium kiosk autostart..."
mkdir -p ~/.config/autostart
cp "$SCRIPT_DIR/robot-kiosk.desktop" ~/.config/autostart/

echo "[3/3] ติดตั้ง RPi.GPIO (ถ้ายังไม่มี)..."
pip install RPi.GPIO --quiet

echo "Done. รัน 'sudo reboot' เพื่อทดสอบ autostart เต็มรูปแบบ"
