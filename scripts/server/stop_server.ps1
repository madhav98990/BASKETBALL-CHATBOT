# Stop Basketball Chatbot Server
# This script stops all Python processes (server instances)

Write-Host "⏹️  Stopping Basketball Chatbot Server..." -ForegroundColor Yellow
Write-Host ""

# Stop all Python processes
$pythonProcesses = Get-Process | Where-Object {$_.ProcessName -eq "python"}
if ($pythonProcesses) {
    $count = 0
    $pythonProcesses | ForEach-Object {
        Write-Host "   Stopping process ID: $($_.Id)" -ForegroundColor Gray
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        $count++
    }
    Write-Host ""
    Write-Host "✓ Stopped $count Python process(es)" -ForegroundColor Green
} else {
    Write-Host "✓ No Python processes found" -ForegroundColor Green
}

# Check if port 8000 is still in use
Write-Host ""
Write-Host "🔍 Checking port 8000..." -ForegroundColor Yellow
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
    Write-Host "✓ Port 8000 freed" -ForegroundColor Green
} else {
    Write-Host "✓ Port 8000 is available" -ForegroundColor Green
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Cyan

