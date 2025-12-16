# Project Structure

Complete file structure of the Basketball AI Chatbot system.

```
chatbot-basketball-24/
│
├── agents/                          # Agent modules
│   ├── __init__.py
│   ├── intent_detection_agent.py   # Detects query intent
│   ├── stats_agent.py              # Handles match statistics
│   ├── player_stats_agent.py       # Handles player statistics
│   ├── schedule_agent.py            # Handles schedule queries
│   ├── article_search_agent.py     # Searches Pinecone for articles
│   └── response_formatter_agent.py # Formats responses using Ollama
│
├── api/                             # FastAPI backend
│   └── main.py                     # Main API server with /chat endpoint
│
├── database/                        # PostgreSQL database
│   ├── __init__.py
│   ├── schema.sql                  # Database schema (tables, indexes)
│   ├── seed_data.sql               # Seed data (teams, players, matches, stats)
│   └── db_connection.py            # Database connection utilities
│
├── embeddings/                      # Vector embeddings
│   ├── __init__.py
│   └── vector_store.py             # Pinecone integration & embeddings
│
├── scraper/                         # Article scraper
│   ├── __init__.py
│   └── article_scraper.py         # RSS feed scraper for articles
│
├── frontend/                        # Frontend UI
│   └── index.html                  # Chat interface (HTML + JS)
│
├── data/                            # Generated data (not in repo)
│   └── articles/                   # Scraped articles (article_0.txt ...)
│
├── config.py                        # Configuration file
├── chatbot.py                       # Main chatbot orchestration engine
├── setup_database.py                # Database setup script
├── test_chatbot.py                  # Test suite
├── requirements.txt                 # Python dependencies
├── README.md                        # Main documentation
├── QUICKSTART.md                    # Quick start guide
├── PROJECT_STRUCTURE.md             # This file
├── .gitignore                      # Git ignore rules
├── .env                            # Environment variables (not in repo)
├── run.sh                          # Quick start script (Linux/Mac)
└── run.bat                         # Quick start script (Windows)
```

## Module Descriptions

### Agents (`agents/`)
- **IntentDetectionAgent**: Classifies user queries into categories
- **StatsAgent**: Queries match results and scores from PostgreSQL
- **PlayerStatsAgent**: Queries player performance data
- **ScheduleAgent**: Queries upcoming game schedules
- **ArticleSearchAgent**: Searches Pinecone vector database for articles
- **ResponseFormatterAgent**: Uses Ollama LLM to format natural responses

### Database (`database/`)
- **schema.sql**: Creates all tables (teams, players, matches, player_stats, schedule)
- **seed_data.sql**: Populates database with fictional NBA data
  - 30 NBA teams
  - 120+ players (4 per team)
  - 33+ past matches with scores
  - Player stats for each match
  - 100+ upcoming scheduled games
- **db_connection.py**: PostgreSQL connection management

### Embeddings (`embeddings/`)
- **vector_store.py**: 
  - Generates embeddings using sentence-transformers
  - Chunks articles into 200-300 word segments
  - Uploads to Pinecone vector database
  - Searches for relevant articles

### Scraper (`scraper/`)
- **article_scraper.py**:
  - Fetches articles from RSS feeds
  - Cleans content (removes ads, garbage text)
  - Saves as individual .txt files
  - Handles rate limiting and errors

### API (`api/`)
- **main.py**: FastAPI server with:
  - POST /chat endpoint
  - CORS middleware
  - Error handling

### Frontend (`frontend/`)
- **index.html**: 
  - Modern chat UI
  - Connects to FastAPI backend
  - Real-time messaging
  - Suggestion chips

## Data Flow

1. **User Question** → Frontend (index.html)
2. **API Request** → FastAPI (api/main.py)
3. **Intent Detection** → IntentDetectionAgent
4. **Route Query** → Appropriate Agent(s)
   - StatsAgent → PostgreSQL
   - PlayerStatsAgent → PostgreSQL
   - ScheduleAgent → PostgreSQL
   - ArticleSearchAgent → Pinecone
5. **Format Response** → ResponseFormatterAgent (Ollama LLM)
6. **Return Answer** → Frontend

## Key Files

- **chatbot.py**: Main orchestration logic
- **config.py**: All configuration (DB, Pinecone, Ollama)
- **setup_database.py**: One-command database setup
- **test_chatbot.py**: Test suite for verification

## Generated Files (Not in Repo)

- `data/articles/*.txt`: Scraped articles
- `.env`: Environment variables
- `__pycache__/`: Python cache files

