@echo off
echo ============================================
echo   StockSage - Starting...
echo ============================================

REM Check if venv exists, create if not
IF NOT EXIST "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet

REM Check if .env exists
IF NOT EXIST ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Copying .env.example to .env...
    copy .env.example .env
    echo Please edit .env and set your SECRET_KEY, then run this script again.
    pause
    exit
)

REM Launch the app
echo.
echo ============================================
echo   StockSage is running!
echo   Open your browser: http://localhost:5000
echo   Press CTRL+C to stop
echo ============================================
echo.
python run.py

pause
