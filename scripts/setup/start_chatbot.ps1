# Start the Basketball Chatbot Server
Write-Host "🏀 Starting Basketball AI Chatbot..." -ForegroundColor Green
Write-Host ""
Write-Host "Server starting on http://localhost:8000" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

