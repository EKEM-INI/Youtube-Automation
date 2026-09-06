@echo off
title AutoShorts AI - 1-Click YouTube Shorts Automation
echo ===================================================
echo     ⚡ AutoShorts AI - YouTube Automation Web App
echo ===================================================
echo.
echo Starting web server on http://localhost:8000 ...
echo.

C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload

pause
