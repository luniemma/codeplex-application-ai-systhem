@echo off
REM Setup script for Codeplex AI on Windows

setlocal enabledelayedexpansion

echo ==========================================
echo Codeplex AI - Setup Script (Windows)
echo ==========================================
echo.

REM Check Python version
echo Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel
echo Pip upgraded
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo Dependencies installed
echo.

REM Create directories
echo Creating application directories...
if not exist "logs" mkdir logs
if not exist "app" mkdir app
if not exist "tests" mkdir tests
if not exist "output" mkdir output
echo Directories created
echo.

REM Copy environment file
if not exist ".env" (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo Please update .env with your API keys
) else (
    echo .env file already exists
)
echo.

echo ==========================================
echo Setup completed successfully!
echo ==========================================
echo.
echo Next steps:
echo 1. Update the .env file with your API keys
echo 2. Run 'venv\Scripts\activate.bat' to activate the virtual environment
echo 3. Run 'make dev' to start the development server
echo 4. Or run 'docker-compose up' to run with Docker
echo.

pause

