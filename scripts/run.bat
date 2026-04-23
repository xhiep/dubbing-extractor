@echo off
chcp 65001 >nul
title Dubbing Extractor
color 0B
set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%.."
if not exist ".cache" mkdir ".cache"
if not exist ".tmp" mkdir ".tmp"
set "XDG_CACHE_HOME=%CD%\.cache"
set "HF_HOME=%CD%\.cache\huggingface"
set "HUGGINGFACE_HUB_CACHE=%CD%\.cache\huggingface\hub"
set "TRANSFORMERS_CACHE=%CD%\.cache\huggingface\transformers"
set "TORCH_HOME=%CD%\.cache\torch"
set "PIP_CACHE_DIR=%CD%\.cache\pip"
set "UV_CACHE_DIR=%CD%\.cache\uv"
set "TEMP=%CD%\.tmp"
set "TMP=%CD%\.tmp"

if not exist "venv\Scripts\python.exe" (
    echo.
    echo [LOI] Chua cai dat! Hay chay scripts\install.bat truoc.
    echo.
    pause
    popd
    exit /b 1
)

venv\Scripts\python.exe main.py
if errorlevel 1 (
    echo.
    echo [LOI] Script thoat voi loi. Neu thieu thu vien, hay chay lai scripts\install.bat
    pause
)
popd
