@echo off
echo ========================================
echo Restarting Basketball Chatbot Server
echo ========================================
echo.

REM Stop Python processes
echo Stopping existing Python processes...
taskkill /F /IM python.exe >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✓ Python processes stopped
) else (
    echo ✓ No Python processes found
)

echo.
echo Waiting 2 seconds...
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo Starting Server
echo ========================================
echo.
echo Server will be available at: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to start server
    echo.
    echo Please make sure:
    echo   1. Python is installed and in PATH
    echo   2. Virtual environment is activated (if using one)
    echo   3. Dependencies are installed (pip install -r requirements.txt)
    pause
)

