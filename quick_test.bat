@echo off
REM Quick Test Script for Codeplex AI - Windows

color 0A
cls

echo.
echo ==========================================
echo Codeplex AI - Quick Startup Test
echo ==========================================
echo.

REM Check Python
echo [1] Checking Python Installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/
    pause
    exit /b 1
) else (
    python --version
    echo.
)

REM Check Flask
echo [2] Checking Flask Installation...
python -c "import flask; print('Flask version:', flask.__version__)" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Flask not installed. Installing dependencies...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo.
) else (
    echo Flask is installed
    echo.
)

REM Check project structure
echo [3] Checking Project Structure...
if exist "main.py" (
    echo ✓ main.py found
) else (
    echo ERROR: main.py not found
    pause
    exit /b 1
)

if exist "app\routes.py" (
    echo ✓ app\routes.py found
) else (
    echo ERROR: app\routes.py not found
    pause
    exit /b 1
)

if exist "app\ai_services.py" (
    echo ✓ app\ai_services.py found
) else (
    echo ERROR: app\ai_services.py not found
    pause
    exit /b 1
)

echo.

REM Create .env if not exists
echo [4] Checking Configuration...
if not exist ".env" (
    echo Creating .env from .env.example...
    if exist ".env.example" (
        copy .env.example .env >nul
        echo ✓ .env created
    ) else (
        echo WARNING: .env.example not found
    )
) else (
    echo ✓ .env already exists
)
echo.

REM Run verification script
echo [5] Running Verification Script...
python verify_startup.py
if errorlevel 1 (
    echo.
    echo ERROR: Verification failed
    pause
    exit /b 1
)

echo.
echo ==========================================
echo All checks passed!
echo ==========================================
echo.
echo To start the application:
echo   python main.py
echo.
echo The API will be available at:
echo   http://localhost:8000
echo.
echo Test Health Check:
echo   curl http://localhost:8000/health
echo.
echo Press any key to exit...
pause >nul

