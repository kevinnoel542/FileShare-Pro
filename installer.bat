@echo off
color 0A
title FileShare Pro - Installer by Hacker Joe

:: === Constants ===
set "APP_NAME=FileShare Pro"
set "AUTHOR=Hacker Joe"
set "PYTHON_INSTALLER=python-3.11.4-amd64.exe"

:: === Welcome Message ===
echo.
echo =============================================================
echo               Welcome to %APP_NAME% Setup
echo                   Created by: %AUTHOR%
echo =============================================================
echo.
echo This installer will set up everything you need to run %APP_NAME%.
echo It does NOT collect or transmit any personal data.
echo It will:
echo   - Install Python (if needed) system-wide
echo   - Add Python to PATH
echo   - Install required packages:
echo       Flask, pystray, Pillow, psutil, qrcode
echo.
echo Options:
echo [1] I ALREADY have Python installed
echo [2] I DO NOT have Python (install it now)
echo [3] Exit the Installer
echo.

set /p choice="Enter your choice (1/2/3): "

if "%choice%"=="1" goto has_python
if "%choice%"=="2" goto install_python
if "%choice%"=="3" goto exit_installer

echo [ERROR] Invalid choice. Please restart the installer.
pause
exit /b

:: === Check Existing Python ===
:has_python
echo.
echo [INFO] Checking for Python...
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python was not found in your system PATH.
    echo Please rerun the installer and choose option [2] to install Python.
    pause
    exit /b
)
goto install_deps

:: === Install Python ===
:install_python
echo.
echo [INFO] Preparing to install Python...

if not exist "%PYTHON_INSTALLER%" (
    echo [ERROR] Missing file: %PYTHON_INSTALLER%
    echo Please place the official Python installer in this folder:
    echo %~dp0
    echo.
    echo You can download it from:
    echo https://www.python.org/downloads/release/python-3114/
    pause
    exit /b
)

echo [INFO] Installing Python system-wide...
start /wait "" "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1

echo.
echo [INFO] Verifying installation...
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python did not install correctly.
    echo Please restart your system or check environment variables.
    pause
    exit /b
)

echo [OK] Python installed and added to PATH.
goto install_deps

:: === Install Dependencies ===
:install_deps
echo.
echo [INFO] Upgrading pip and installing required packages...
python -m pip install --upgrade pip
python -m pip install flask pystray pillow psutil qrcode

echo.
echo ✅ %APP_NAME% is now fully installed and ready to use!
echo Launching your application...
start pythonw app\launcher.pyw
exit /b

:: === Exit ===
:exit_installer
echo.
echo Installer closed. No changes were made.
pause
exit /b
:: === End of Script ===
:: This script is designed to be run in a Windows environment.