@echo off
REM ===== ตัวช่วยรันหุ่นยนต์ (โหมดจำลอง) =====
REM ดับเบิลคลิกไฟล์นี้ หรือพิมพ์ run ในโฟลเดอร์นี้ก็ได้
REM ตั้ง console เป็น UTF-8 เพื่อให้พิมพ์/แสดงภาษาไทยได้ถูกต้อง
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

REM Python ของเครื่องนี้ติดตั้งที่ตำแหน่งนี้ (ไม่ได้อยู่ใน PATH)
set "PYEXE=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
if not exist "%PYEXE%" set "PYEXE=python"

"%PYEXE%" simulator.py
echo.
pause
