# How to Start Server and Frontend

## ✅ Server Status

The API server has been restarted with the latest code changes.

## 🚀 Starting the Server

### Option 1: Using the batch file (Easiest)
```bash
start_server.bat
```

### Option 2: Using PowerShell
```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Using Python directly
```bash
python api/main.py
```

The server will be available at: **http://localhost:8000**

## 🌐 Starting the Frontend

### Option 1: Open directly in browser
1. Navigate to the `frontend` folder
2. Double-click `index.html`
3. It will open in your default browser

### Option 2: Using a local web server (Recommended)
```bash
# Using Python's built-in server
cd frontend
python -m http.server 8080
```
Then open: **http://localhost:8080**

### Option 3: Using VS Code Live Server
1. Install "Live Server" extension in VS Code
2. Right-click on `frontend/index.html`
3. Select "Open with Live Server"

## ✅ Verification

### Test the API:
```bash
python test_api_endpoint.py
```

You should see player data, not an error message.

### Test in Frontend:
1. Open the frontend in your browser
2. Ask: **"top 5 player points per game"**
3. You should see:
   - Shai Gilgeous-Alexander (OKC): 32.7 points per game
   - Giannis Antetokounmpo (MIL): 30.4 points per game
   - Nikola Jokić (DEN): 29.6 points per game
   - Anthony Edwards (MIN): 27.6 points per game
   - Jayson Tatum (BOS): 26.8 points per game

## 🛑 Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

Or use PowerShell:
```powershell
Get-Process | Where-Object {$_.ProcessName -eq "python" -and $_.Path -like "*python*"} | Stop-Process -Force
```

## 📝 Notes

- The server uses `--reload` flag, so it will automatically restart when you make code changes
- The frontend connects to `http://localhost:8000` - make sure the server is running
- If you see CORS errors, check that CORS is enabled in `api/main.py` (it is by default)

