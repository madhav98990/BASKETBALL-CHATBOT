# Restart Basketball Chatbot Server
# This script stops all Python processes and restarts the server cleanly

Write-Host "🔄 Restarting Basketball Chatbot Server..." -ForegroundColor Cyan
Write-Host ""

# Step 1: Stop all Python processes
Write-Host "⏹️  Stopping existing Python processes..." -ForegroundColor Yellow
$pythonProcesses = Get-Process | Where-Object {$_.ProcessName -eq "python"}
if ($pythonProcesses) {
    $pythonProcesses | ForEach-Object {
        Write-Host "   Stopping process ID: $($_.Id)" -ForegroundColor Gray
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "✓ All Python processes stopped" -ForegroundColor Green
} else {
    Write-Host "✓ No Python processes found" -ForegroundColor Green
}

# Wait a moment for processes to fully terminate
Write-Host ""
Write-Host "⏳ Waiting 2 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

# Step 2: Check if port 8000 is still in use
Write-Host ""
Write-Host "🔍 Checking if port 8000 is available..." -ForegroundColor Yellow
$portInUse = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "⚠️  Port 8000 is still in use. Attempting to free it..." -ForegroundColor Yellow
    $portInUse | ForEach-Object {
        $process = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "   Stopping process $($process.ProcessName) (ID: $($process.Id))" -ForegroundColor Gray
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        }
    }
    Start-Sleep -Seconds 1
}

# Step 3: Start the server
Write-Host ""
Write-Host "🚀 Starting server..." -ForegroundColor Green
Write-Host "   Server will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   Press Ctrl+C to stop the server" -ForegroundColor Cyan
Write-Host ""

# Change to the project directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Start the server
try {
    python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
} catch {
    Write-Host ""
    Write-Host "❌ Error starting server: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please make sure:" -ForegroundColor Yellow
    Write-Host "  1. Python is installed and in PATH" -ForegroundColor Yellow
    Write-Host "  2. Virtual environment is activated (if using one)" -ForegroundColor Yellow
    Write-Host "  3. Dependencies are installed (pip install -r requirements.txt)" -ForegroundColor Yellow
    exit 1
}

