# Quick Ollama Installation

## Option 1: Manual Installation (Recommended)

1. **Download Ollama:**
   - Go to: https://ollama.ai/download/windows
   - Download and run the installer
   - Follow the installation wizard

2. **After installation, restart your terminal/PowerShell**

3. **Pull the llama3 model:**
   ```bash
   ollama pull llama3
   ```
   This downloads ~4.7 GB and may take a few minutes.

4. **Test it:**
   ```bash
   ollama run llama3 "Hello, how are you?"
   ```

## Option 2: Using Winget (If Available)

```bash
winget install Ollama.Ollama
```

Then restart terminal and run:
```bash
ollama pull llama3
```

## ✅ Verify Installation

After installation, check:
```bash
ollama --version
ollama list
```

You should see `llama3` in the list.

## 🎯 Next Steps

Once Ollama is installed and llama3 is pulled:

1. ✅ Database is ready (Docker on port 5433)
2. ✅ Ollama will be ready
3. Start the API: `python api/main.py`
4. Open `frontend/index.html` in browser

## ⚠️ Important Notes

- **Ollama must be running** for the chatbot to work
- The Ollama service usually starts automatically
- If it doesn't, start it manually or run: `ollama serve`
- The chatbot is configured to use `http://localhost:11434` (default Ollama port)

