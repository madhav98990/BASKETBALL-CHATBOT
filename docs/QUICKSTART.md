# Quick Start Guide

## 🚀 Fast Setup (5 minutes)

### 1. Install Prerequisites

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install PostgreSQL (if not already installed)
# Windows: Download from https://www.postgresql.org/download/windows/
# Mac: brew install postgresql
# Linux: sudo apt-get install postgresql

# Install Ollama
# Download from https://ollama.ai and install
ollama pull llama3
```

### 2. Setup Database

```bash
# Option A: Use the setup script
python setup_database.py

# Option B: Manual setup
psql -U postgres
CREATE DATABASE nba_chatbot;
\q
psql -U postgres -d nba_chatbot -f database/schema.sql
psql -U postgres -d nba_chatbot -f database/seed_data.sql
```

### 3. Configure Environment

Create `.env` file:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nba_chatbot
DB_USER=postgres
DB_PASSWORD=postgres

PINECONE_API_KEY=your_key_here
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=basketball-articles

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

### 4. Scrape Articles (Optional)

```bash
python scraper/article_scraper.py
```

**Note**: If RSS feeds fail, the system will still work for fact-based queries. You can skip this step for testing.

### 5. Build Vector Store (If articles scraped)

```bash
python embeddings/vector_store.py
```

### 6. Start the Server

```bash
python api/main.py
```

### 7. Open Frontend

Open `frontend/index.html` in your browser, or:

```bash
cd frontend
python -m http.server 8080
```

Then visit: `http://localhost:8080`

## ✅ Test It!

Try these questions:
- "How many points did LeBron James score?"
- "When is the next Lakers game?"
- "What was the Warriors vs Suns score?"

## 🔧 Troubleshooting

### Database Connection Error
- Check PostgreSQL is running: `pg_isready`
- Verify credentials in `.env`
- Test connection: `psql -U postgres -d nba_chatbot`

### Ollama Not Working
- Start Ollama: `ollama serve` (in separate terminal)
- Check model: `ollama list`
- Pull model: `ollama pull llama3`

### Pinecone Error
- Sign up at https://www.pinecone.io (free tier)
- Get API key from dashboard
- Add to `.env` file

### No Articles Found
- Run scraper: `python scraper/article_scraper.py`
- Or skip articles - fact-based queries will still work!

## 📝 Next Steps

1. Customize RSS feeds in `config.py`
2. Add more players/stats to database
3. Adjust chunk size in `config.py` (CHUNK_SIZE)
4. Try different LLM models: `ollama pull mistral`

