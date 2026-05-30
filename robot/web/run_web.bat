@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0\.."
"%LOCALAPPDATA%\Programs\Python\Python314\python.exe" web\server.py
pause
