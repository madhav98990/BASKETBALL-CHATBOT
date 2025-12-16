# Ollama Setup Guide

Ollama is required for the LLM (Large Language Model) that generates natural responses.

## 🚀 Installation

### Windows

1. **Download Ollama:**
   - Visit: https://ollama.ai/download
   - Download the Windows installer
   - Run the installer and follow the prompts

2. **Verify Installation:**
   ```bash
   ollama --version
   ```

3. **Pull the Llama3 Model:**
   ```bash
   ollama pull llama3
   ```
   
   This will download the model (approximately 4.7 GB). It may take a few minutes.

### Alternative: Using Winget (Windows Package Manager)

If you have winget installed:
```bash
winget install Ollama.Ollama
```

Then restart your terminal and run:
```bash
ollama pull llama3
```

## ✅ Verify Setup

After installation, test Ollama:

```bash
ollama run llama3 "Hello, how are you?"
```

You should see a response from the model.

## 🔧 Configuration

The chatbot is configured to use Ollama with these defaults (in `.env`):
- **Base URL**: `http://localhost:11434`
- **Model**: `llama3`

If you want to use a different model (like Mistral), update `.env`:
```env
OLLAMA_MODEL=mistral
```

And pull that model:
```bash
ollama pull mistral
```

## 🐛 Troubleshooting

### Ollama not found after installation

1. **Restart your terminal/PowerShell**
2. **Check if Ollama service is running:**
   - Look for "Ollama" in Windows Services
   - Or check if port 11434 is listening:
     ```bash
     netstat -ano | findstr :11434
     ```

3. **Manually start Ollama:**
   - Open Ollama from Start Menu
   - Or run: `ollama serve`

### Model download fails

- Check your internet connection
- Ensure you have enough disk space (models are large)
- Try again: `ollama pull llama3`

### Port 11434 already in use

- Stop other services using that port
- Or change the port in `.env`:
  ```env
  OLLAMA_BASE_URL=http://localhost:11435
  ```

## 📝 Next Steps

Once Ollama is installed and llama3 is pulled:

1. ✅ Database is ready (Docker)
2. ✅ Ollama is ready
3. (Optional) Setup Pinecone for article search
4. Start the API: `python api/main.py`
5. Open `frontend/index.html` in browser

## 🔗 Resources

- Ollama Website: https://ollama.ai
- Available Models: https://ollama.ai/library
- Documentation: https://github.com/ollama/ollama

