@echo off
echo ========================================
echo Starting Basketball Chatbot API Server
echo ========================================
echo.
echo Server will be available at: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

