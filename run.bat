@echo off
setlocal enabledelayedexpansion

REM Colors and formatting
cls
echo.
echo ============================================================
echo     BD Top Companies - Django Development Server
echo ============================================================
echo.

REM Get the script directory
set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%SCRIPT_DIR%
set VENV_DIR=%SCRIPT_DIR%..\venv

REM Check if virtual environment exists
if not exist "%VENV_DIR%" (
    echo ERROR: Virtual environment not found at: %VENV_DIR%
    echo Please create it first:
    echo    cd %PROJECT_DIR% ^&^& python -m venv ..\venv
    pause
    exit /b 1
)

REM Activate virtual environment
echo [*] Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

REM Check if Django is installed
python -c "import django" >nul 2>&1
if errorlevel 1 (
    echo [*] Installing Django...
    pip install django==6.0.4 -q
)

REM Navigate to project directory
cd /d "%PROJECT_DIR%"

REM Run migrations if needed
echo [*] Running migrations...
python manage.py migrate --run-syncdb -q >nul 2>&1

REM Display server info
echo.
echo ============================================================
echo Mobile Information:
echo    URL: http://localhost:8000
echo    Admin: http://localhost:8000/admin
echo    Credentials: admin / admin123
echo ============================================================
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start server
python manage.py runserver 0.0.0.0:8000

pause
