@echo off
setlocal
title KCC Chatbot Assistant
cd /d "%~dp0"

set "VENV_PY=%~dp0.venv\Scripts\python.exe"

if not exist "%VENV_PY%" (
    echo [*] No .venv found - creating one...
    where python >nul 2>&1
    if errorlevel 1 (
        echo [X] Python is not on PATH. Install Python 3.13+ first.
        goto :fail
    )
    python -m venv .venv
    if errorlevel 1 goto :fail
    echo [*] Installing requirements...
    "%VENV_PY%" -m pip install --upgrade pip >nul 2>&1
    "%VENV_PY%" -m pip install -r requirements.txt
    if errorlevel 1 goto :fail
)

echo [*] Applying database migrations...
"%VENV_PY%" manage.py migrate --noinput
if errorlevel 1 goto :fail

echo [*] Starting KCC Chatbot Assistant at http://127.0.0.1:8000/
echo [*] Press CTRL+C to stop the server.
start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 3; Start-Process 'http://127.0.0.1:8000/'"
"%VENV_PY%" manage.py runserver 127.0.0.1:8000

echo.
echo [!] Server stopped.
pause
exit /b 0

:fail
echo.
echo [X] Startup failed - read the error above.
pause
exit /b 1
