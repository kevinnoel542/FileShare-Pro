@echo off
color 0A
title FileShare Pro - Dependency Installer by Hacker Joe

:: === Constants ===
set "APP_NAME=FileShare Pro"
set "AUTHOR=Hacker Joe"

:: === Welcome Message ===
echo.
echo =============================================================
echo               Welcome to %APP_NAME% Dependency Installer
echo                    Created by: %AUTHOR%
echo =============================================================
echo.
echo This script installs the required Python packages:
echo   Flask, pystray, Pillow, psutil, qrcode
echo.
echo NOTE: Python must already be installed and available in PATH.
echo.

:: === Check Python ===
echo [INFO] Checking for Python...
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python manually first.
    pause
    exit /b
)

:: === Install Dependencies ===
echo [INFO] Installing required packages...
python -m pip install --upgrade pip
python -m pip install flask pystray pillow psutil qrcode

echo.
echo ✅ Dependencies installed successfully!
pause
exit /b
