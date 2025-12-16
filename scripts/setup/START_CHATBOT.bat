@echo off
REM Start the Basketball AI Chatbot

echo 🏀 Starting Basketball AI Chatbot...
echo ========================================
echo.

REM Check if database is running
docker ps | findstr nba_chatbot_db >nul
if errorlevel 1 (
    echo ⚠️  PostgreSQL container not running. Starting it...
    docker-compose up -d
    timeout /t 5 /nobreak >nul
)

REM Check if Ollama is running
netstat -ano | findstr :11434 >nul
if errorlevel 1 (
    echo ⚠️  Ollama not running. Please start Ollama first.
    echo    You can start it from the Start Menu or run: ollama serve
    pause
    exit /b 1
)

REM Add Ollama to PATH if needed
if not exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
    echo ❌ Ollama not found. Please install Ollama first.
    pause
    exit /b 1
)

set PATH=%PATH%;%LOCALAPPDATA%\Programs\Ollama

echo ✅ All services ready!
echo.
echo 🚀 Starting API server...
echo    API will be available at: http://localhost:8000
echo    Open frontend/index.html in your browser to chat!
echo.
echo    Press Ctrl+C to stop the server
echo.

python api/main.py

