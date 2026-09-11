@echo off
title Study Sphere

cd /d "%~dp0"

if not exist "run.py" (
    echo run.py not found.
    pause
    exit /b 1
)

start "" cmd /c "python run.py"

timeout /t 3 /nobreak >nul

start "" "http://127.0.0.1:5000/student/tutor"