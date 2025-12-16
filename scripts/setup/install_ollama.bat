@echo off
REM Install Ollama and pull llama3 model

echo 🚀 Installing Ollama...
winget install Ollama.Ollama

echo.
echo ⏳ Waiting for installation to complete...
timeout /t 5 /nobreak

echo.
echo 📦 Pulling llama3 model (this may take a few minutes, ~4.7 GB)...
ollama pull llama3

echo.
echo ✅ Setup complete!
echo.
echo To test Ollama, run: ollama run llama3 "Hello"
pause

