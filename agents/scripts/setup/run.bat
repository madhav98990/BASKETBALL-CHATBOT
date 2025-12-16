@echo off
REM Quick start script for Basketball AI Chatbot (Windows)

echo 🏀 Basketball AI Chatbot - Quick Start
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo ❌ .env file not found!
    echo Please create .env file with your configuration.
    echo See README.md for details.
    pause
    exit /b 1
)

REM Check if database is set up
echo 📊 Checking database...
python -c "from database.db_connection import db; db.connect()" 2>nul
if errorlevel 1 (
    echo ⚠️  Database not set up. Running setup...
    python setup_database.py
)

REM Check if Ollama is running
echo 🤖 Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Ollama not running. Please start it with: ollama serve
    echo    (Run this in a separate terminal)
)

REM Start the API server
echo 🚀 Starting API server...
echo    API will be available at http://localhost:8000
echo    Open frontend/index.html in your browser
echo.
python api/main.py
pause

