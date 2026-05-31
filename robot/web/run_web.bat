@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0\.."

REM หา Python: ลอง path เฉพาะของเครื่องนี้ก่อน ถ้าไม่เจอ (เช่นบนโน้ตบุ๊ก) ใช้ python ใน PATH
set "PYEXE=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
if not exist "%PYEXE%" set "PYEXE=python"

"%PYEXE%" web\server.py
pause
