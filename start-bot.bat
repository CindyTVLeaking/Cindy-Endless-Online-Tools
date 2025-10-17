@echo off
title Project Cindy - Launcher
color 0A

echo ================================================
echo           PROJECT CINDY LAUNCHER
echo ================================================
echo.
echo Starting Project Cindy...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

REM Launch splash screen which will then launch the bot
python cindy_splash.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start Project Cindy
    echo Check the error messages above
    pause
)

exit
