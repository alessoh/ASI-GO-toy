@echo off
REM Start script for Toy ASI-ARCH on Windows

echo Starting Toy ASI-ARCH...
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then run: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Run the main program
python main.py

REM Keep window open on error
if errorlevel 1 (
    echo.
    echo An error occurred. Check the logs for details.
    pause
)