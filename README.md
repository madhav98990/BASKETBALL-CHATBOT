# Basketball AI Chatbot

A comprehensive, end-to-end Basketball AI Chatbot system that answers both fact-based questions (scores, stats, schedules) and article-based questions (analysis, opinions, news) using only free, open-source tools.

## 🏗️ Architecture

```
User Question → Intent Detection Agent
        ├── Fact-Based Query → PostgreSQL Fictional NBA Database Agents
        └── Article-Based Query → Pinecone Vector Search Agent
                                   ↓
                         Response Formatter Agent (Ollama LLM)
                                   ↓
                           Final Natural Answer
```

## 📋 Features

- **Fact-Based Queries**: Match scores, player statistics, upcoming schedules
- **Article-Based Queries**: Analysis, opinions, news breakdowns
- **Hybrid Workflow**: Intelligent routing between database and vector search
- **Local LLM**: Uses Ollama with Llama3/Mistral for natural responses
- **Free Tools Only**: No paid APIs or services

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (fictional NBA data)
- **Vector DB**: Pinecone (free tier)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **LLM**: Ollama (Llama3 or Mistral)
- **Frontend**: HTML + JavaScript
- **Scraping**: requests, feedparser, newspaper3k, BeautifulSoup

## 📁 Project Structure

```
chatbot-basketball-24/
├── agents/                 # Agent modules for different query types
│   ├── intent_detection_agent.py
│   ├── stats_agent.py
│   ├── player_stats_agent.py
│   ├── schedule_agent.py
│   ├── article_search_agent.py
│   ├── response_formatter_agent.py
│   └── ... (other agents)
├── services/              # External API service integrations
│   ├── nba_api.py
│   ├── espn_api.py
│   ├── balldontlie_api.py
│   └── ... (other services)
├── database/              # Database schema and connection
│   ├── schema.sql
│   ├── seed_data.sql
│   └── db_connection.py
├── embeddings/           # Vector store for article search
│   └── vector_store.py
├── scraper/              # Article scraping utilities
│   └── article_scraper.py
├── api/                  # FastAPI server
│   └── main.py
├── frontend/             # Web frontend
│   └── index.html
├── test/                 # Test files
│   └── ... (test scripts)
├── scripts/              # Utility scripts
│   ├── debug/           # Debug and troubleshooting scripts
│   ├── setup/           # Setup and installation scripts
│   └── quick_tests/     # Quick test scripts
├── validate/             # Validation scripts
│   └── ... (validation scripts)
├── tools/                # Utility tools
│   └── ... (tool scripts)
├── docs/                 # Documentation files
│   └── ... (markdown documentation)
├── data/                 # Data files
│   └── articles/        # Scraped articles (generated)
├── logs/                 # Log files
├── config.py            # Configuration file
├── chatbot.py           # Main chatbot entry point
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Docker configuration
└── README.md           # This file
```

## 🚀 Setup Instructions

### Prerequisites

1. **Python 3.8+**
2. **Docker & Docker Compose** (recommended) OR **PostgreSQL** (installed and running)
3. **Ollama** (installed with Llama3 or Mistral model)
4. **Pinecone Account** (free tier, optional for article search)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Setup PostgreSQL Database

#### Option A: Using Docker (Recommended) 🐳

1. **Start PostgreSQL with Docker:**
   ```bash
   # Windows
   scripts\setup\setup_docker.bat
   
   # Linux/Mac
   chmod +x scripts/setup/setup_docker.sh
   ./scripts/setup/setup_docker.sh
   ```
   
   Or manually:
   ```bash
   docker-compose up -d
   ```

   This will:
   - Start PostgreSQL container
   - Automatically create the database
   - Load schema and seed data
   - Create `.env` file with default credentials

2. **Verify it's running:**
   ```bash
   docker ps
   ```

3. **View logs (if needed):**
   ```bash
   docker-compose logs -f
   ```

#### Option B: Manual PostgreSQL Setup

1. Create a new database:
```sql
CREATE DATABASE nba_chatbot;
```

2. Run the schema:
```bash
psql -U postgres -d nba_chatbot -f database/schema.sql
```

3. Seed the data:
```bash
psql -U postgres -d nba_chatbot -f database/seed_data.sql
```

### Step 3: Configure Environment Variables

**If using Docker**, the `.env` file is automatically created. Otherwise, create a `.env` file in the project root:

```env
# Database (Docker defaults shown)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nba_chatbot
DB_USER=postgres
DB_PASSWORD=postgres

# Pinecone
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=basketball-articles

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

### Step 4: Install and Setup Ollama

1. Install Ollama from https://ollama.ai
2. Pull the model:
```bash
ollama pull llama3
# OR
ollama pull mistral
```

### Step 5: Scrape Articles (Optional but Recommended)

Run the article scraper to collect ~1400 basketball articles:

```bash
python scraper/article_scraper.py
```

This will:
- Fetch articles from RSS feeds
- Clean and save them to `data/articles/`
- Create files: `article_0.txt` through `article_1399.txt`

**Note**: If RSS feeds are unavailable, you may need to configure additional feeds in `config.py` or manually add article URLs.

### Step 6: Build Vector Store

Generate embeddings and upload to Pinecone:

```bash
python embeddings/vector_store.py
```

This will:
- Load all articles from `data/articles/`
- Chunk them into 200-300 word segments
- Generate embeddings using sentence-transformers
- Upload to Pinecone index

### Step 7: Start the API Server

```bash
python api/main.py
```

Or using uvicorn directly:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### Step 8: Open Frontend

Open `frontend/index.html` in your web browser, or serve it with a simple HTTP server:

```bash
cd frontend
python -m http.server 8080
```

Then open `http://localhost:8080` in your browser.

## 📝 Usage Examples

### Fact-Based Questions

- "How many points did LeBron James score?"
- "What was the score in the Warriors vs Suns match?"
- "When is the next Lakers game?"
- "Show me Giannis' last game stats."
- "What are the recent Celtics games?"

### Article-Based Questions

- "What's the analysis on the Lakers' recent performance?"
- "Explain the Warriors' strategy this season."
- "What are the opinions on the trade deadline?"
- "Break down the latest NBA news."

### Mixed Questions

- "How did LeBron perform and what do analysts say about it?"
- "What's the score and analysis of the last Lakers game?"

## 🗄️ Database Schema

The PostgreSQL database contains:

- **teams**: All 30 NBA teams
- **players**: Top 3-4 players per team (120+ players)
- **matches**: 30+ past games with scores
- **player_stats**: Detailed stats for each player in each match
- **schedule**: Upcoming games for all teams

## 🔧 Common Errors & Fixes

### Error: "Database connection failed"

**Fix**: 
- Ensure PostgreSQL is running
- Check database credentials in `.env`
- Verify database exists: `psql -U postgres -l`

### Error: "PINECONE_API_KEY not set"

**Fix**:
- Sign up for free Pinecone account at https://www.pinecone.io
- Get your API key from the dashboard
- Add it to `.env` file

### Error: "Ollama connection failed"

**Fix**:
- Ensure Ollama is installed and running: `ollama serve`
- Verify model is downloaded: `ollama list`
- Check `OLLAMA_BASE_URL` in `.env` (default: `http://localhost:11434`)

### Error: "No articles found"

**Fix**:
- Run the scraper first: `python scraper/article_scraper.py`
- If RSS feeds fail, manually add article URLs or configure additional feeds
- Ensure `data/articles/` directory exists and contains `.txt` files

### Error: "Vector store not initialized"

**Fix**:
- Run the vector store builder: `python embeddings/vector_store.py`
- Ensure articles are scraped first
- Check Pinecone API key is valid

**Note**: This project uses Pinecone client v2.2.4. If you're using a newer Pinecone account, you may need to update the code to use Pinecone v3+ API. The current code works with the free tier of Pinecone.

### Error: CORS error in frontend

**Fix**:
- Ensure API server is running on `http://localhost:8000`
- Check browser console for specific error
- Verify `API_URL` in `frontend/index.html` matches your API server

### Error: "Model not found" (Ollama)

**Fix**:
- Pull the model: `ollama pull llama3`
- Or use mistral: `ollama pull mistral`
- Update `OLLAMA_MODEL` in `.env` accordingly

## 🧪 Testing

Test the chatbot directly:

```bash
python chatbot.py
```

This will run test questions and display responses.

## 📊 API Endpoints

### POST /chat

Request:
```json
{
  "question": "How many points did LeBron James score?"
}
```

Response:
```json
{
  "answer": "LeBron James scored 32 points in his last game..."
}
```

### GET /

Health check endpoint.

## 🎯 Agent Architecture

1. **IntentDetectionAgent**: Classifies query type
2. **StatsAgent**: Handles match results and scores
3. **PlayerStatsAgent**: Handles player statistics
4. **ScheduleAgent**: Handles upcoming game schedules
5. **ArticleSearchAgent**: Searches Pinecone for relevant articles
6. **ResponseFormatterAgent**: Formats responses using Ollama LLM

## 🔐 Security Notes

- The `.env` file should not be committed to version control
- Add `.env` to `.gitignore`
- In production, use proper CORS origins instead of `["*"]`
- Use environment variables for all sensitive data

## 📈 Future Enhancements

- Add more RSS feed sources
- Implement conversation history
- Add user authentication
- Support for multiple languages
- Real-time game updates
- Advanced analytics queries

## 📄 License

This project is open-source and free to use.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📞 Support

For issues or questions:
1. Check the "Common Errors & Fixes" section
2. Review the logs for detailed error messages
3. Ensure all prerequisites are installed and configured

---

**Built with ❤️ using only free and open-source tools**

#   N B A - C H A T B O T - 1 
 
 
