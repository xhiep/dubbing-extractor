@echo off
chcp 65001 >nul
title Dubbing Extractor - Cai dat moi truong
color 0A
set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%.."

echo.
echo ================================================================
echo   DUBBING EXTRACTOR -- CAI DAT TU DONG
echo.
echo   Yeu cau he thong:
echo     - Windows 10/11 (64-bit)
echo     - Python 3.11+  (https://www.python.org/downloads/)
echo     - NVIDIA GPU co CUDA (RTX series khuyen nghi)
echo     - Internet de tai FFmpeg + PyTorch CUDA (~3 GB)
echo.
echo   Se cai:
echo     [0] Virtual environment (venv\)
echo     [1] FFmpeg static (bin\ffmpeg\)
echo     [2] Python packages: yt-dlp, openai-whisper, deep-translator, vieneu
echo     [3] PyTorch Nightly CUDA 12.8 (ho tro RTX 5060 / Blackwell)
echo ================================================================
echo.

:: ── Kiem tra Python ────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [LOI] Khong tim thay Python!
    echo.
    echo   Hay tai Python 3.11+ tai: https://www.python.org/downloads/
    echo   Nho tick "Add Python to PATH" khi cai.
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo [OK] %PYVER%
echo.

:: ── Chay installer.py ──────────────────────────────────────────────
echo [1/2] Chay bo cai dat chinh (installer.py)...
echo.
python "%SCRIPT_DIR%installer.py"

if errorlevel 1 (
    echo.
    echo ================================================================
    echo   [LOI] Cai dat that bai. Xem log ben tren de biet chi tiet.
    echo ================================================================
    pause
    popd
    exit /b 1
)

:: ── Chay system_check.py ───────────────────────────────────────────
echo.
echo [2/2] Kiem tra lai toan bo moi truong...
echo.
venv\Scripts\python.exe "%SCRIPT_DIR%system_check.py"

echo.
echo ================================================================
echo   CAI DAT HOAN TAT!
echo.
echo   Cac buoc tiep theo:
echo     1. (Neu can) Copy cookies.txt vao thu muc goc (cho Bilibili)
echo     2. Double-click  run.bat  de khoi dong ung dung
echo ================================================================
echo.
pause
popd
