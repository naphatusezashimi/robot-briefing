#!/bin/bash
# เปิดหุ่น 2 จอบน Pi: หน้าแชท (/screen) บนจอสัมผัส 10.1" + หน้าหุ่น (/face) บนจอ HDMI 7"
# ถูกเรียกจาก robot-kiosk.desktop ตอนเปิดเครื่อง
#
# จอวางต่อกันแนวนอน: จอแรกเริ่มที่ x=0, จอที่สองเริ่มที่ x = ความกว้างจอแรก
# ถ้าหน้าไปโผล่ผิดจอ → สลับค่า SCREEN_X กับ FACE_X
# ถ้าทั้งสองหน้าซ้อนกันอยู่จอเดียว → Pi OS ใช้ Wayland ที่ไม่ยอมให้กำหนดตำแหน่งหน้าต่าง
#   แก้: sudo raspi-config → Advanced Options → Wayland → เลือก X11 แล้วรีบูต
SCREEN_X="${SCREEN_X:-0}"      # จอสัมผัส 10.1" (จอแรก)
FACE_X="${FACE_X:-1280}"       # จอหน้าหุ่น 7" (= ความกว้างพิกเซลของจอแรก)
URL="http://localhost:5000"

BROWSER="$(command -v chromium-browser || command -v chromium)"
FLAGS="--kiosk --noerrdialogs --disable-infobars --disable-session-crashed-bubble \
  --autoplay-policy=no-user-gesture-required --use-fake-ui-for-media-stream"

# รอเซิร์ฟเวอร์พร้อม (สูงสุด ~30 วินาที)
for _ in $(seq 1 30); do
  curl -s -o /dev/null "$URL/state" && break
  sleep 1
done

# แต่ละหน้าต้องใช้โปรไฟล์แยก ไม่งั้น Chromium รวมเป็นหน้าต่างเดียว
"$BROWSER" $FLAGS --user-data-dir="$HOME/.robot-kiosk/screen" \
  --window-position="$SCREEN_X,0" "$URL/screen" &
"$BROWSER" $FLAGS --user-data-dir="$HOME/.robot-kiosk/face" \
  --window-position="$FACE_X,0" "$URL/face" &
wait
