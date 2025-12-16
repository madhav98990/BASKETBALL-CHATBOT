@echo off
echo ========================================
echo Stopping Basketball Chatbot Server
echo ========================================
echo.

REM Stop Python processes
echo Stopping Python processes...
taskkill /F /IM python.exe >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✓ Python processes stopped
) else (
    echo ✓ No Python processes found
)

echo.
echo Done!
pause

