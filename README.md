<div align="center">

# 🏀 Basketball AI Chatbot  

**A production-style NBA AI assistant for real-time scores, stats, schedules, standings, injuries, trends, news, and article-based analysis — powered entirely by free & open-source tools.**  

<br>

<img src="https://img.shields.io/badge/League-NBA_Style-1D428A?logo=nba&logoColor=FFFFFF" />
<img src="https://img.shields.io/badge/Backend-FastAPI-006BB6?logo=fastapi&logoColor=white" />
<img src="https://img.shields.io/badge/Database-PostgreSQL-1D428A?logo=postgresql&logoColor=white" />
<img src="https://img.shields.io/badge/VectorDB-Pinecone-C8102E" />
<img src="https://img.shields.io/badge/LLM-Ollama_(Llama3/Mistral)-000000?logo=ollama&logoColor=white" />
<img src="https://img.shields.io/badge/Status-Open_Source-007A33" />

</div>

---

## ✨ Overview

This project uses an intent-based orchestration engine to route each user query to the correct specialist agent (stats, schedule, standings, injuries, trends, news, or articles) and then formats a natural-language answer with a local LLM via Ollama.  
It is designed as an end-to-end reference for building multi-agent sports chatbots over both structured (PostgreSQL) and unstructured (articles + vector search) data.

---

## 🧠 Architecture

User Question → IntentDetectionAgent
├── Fact-Based Query → NBA Stats / Schedule / Standings / Injuries Agents (PostgreSQL)
└── Article-Based Query → Pinecone Vector Search (scraped articles)
↓
ResponseFormatterAgent (Ollama LLM)
↓
Final Natural Answer

text

- `IntentDetectionAgent` classifies the question (match stats, player stats, schedule, live game, standings, injuries, player trends, season averages, team news, articles, or mixed).  
- `BasketballChatbot` in `chatbot.py` orchestrates all agents and validates the data before formatting.  
- `ResponseFormatterAgent` uses a local Ollama LLM to turn raw data and article context into a conversational answer.  

---

## 🧩 Features

- 📊 **Fact-based NBA queries** – match scores, player stats, team stats, schedules, season averages, trends.  
- 📺 **Live-style queries** – live games, standings, injury reports, and team news where data is available.  
- 📰 **Article-based answers** – analysis, opinions, narrative breakdowns using a Pinecone index over scraped basketball articles.  
- 🧬 **Mixed Q&A** – combine stats + article-style context in one answer (e.g., “stats + what analysts say”).  
- 💻 **Local-only LLM** – uses Ollama (Llama 3 / Mistral), no paid LLM APIs required.  
- 🆓 **Free stack** – FastAPI, PostgreSQL, Pinecone free tier, sentence-transformers, and standard Python tooling.  

---

## 🛠 Tech Stack

- 🧾 **Backend**: FastAPI (Python) for the HTTP API.  
- 🔀 **Orchestration**: `BasketballChatbot` managing all agents in `chatbot.py`.  
- 🗄 **Database**: PostgreSQL with tables for teams, players, matches, player_stats, and schedule.  
- 📚 **Vector DB**: Pinecone (free tier) for article embeddings and semantic search.  
- 🧠 **Embeddings**: `sentence-transformers` (e.g., `all-MiniLM-L6-v2`).  
- 🤖 **LLM**: Ollama serving Llama 3 or Mistral over HTTP.  
- 🕸 **Scraping**: `requests`, `feedparser`, `beautifulsoup4`, `lxml` for RSS and article ingestion.  
- 🌐 **Frontend**: HTML + JavaScript client in `frontend/index.html` calling `/chat`.  

---

## 📂 Project Structure

chatbot-basketball-24/
├── agents/ # Intent + stats/schedule/news/article agents
│ ├── intent_detection_agent.py
│ ├── stats_agent.py
│ ├── player_stats_agent.py
│ ├── schedule_agent.py
│ ├── article_search_agent.py
│ ├── response_formatter_agent.py
│ ├── live_game_agent.py
│ ├── standings_agent.py
│ ├── injury_report_agent.py
│ ├── player_trend_agent.py
│ ├── season_averages_agent.py
│ └── team_news_agent.py
├── services/ # External NBA/ESPN/Balldontlie integrations
├── database/ # Schema, seed data, DB connection helpers
├── embeddings/ # Pinecone vector store builder
├── scraper/ # Article scraper utilities
├── api/ # FastAPI app (main.py)
├── frontend/ # Static web UI
├── scripts/ # Setup, debug, quick tests
├── validate/ # Validation scripts
├── tools/ # Extra utilities
├── docs/ # Extended documentation
├── data/
│ └── articles/ # Scraped article .txt files (generated)
├── logs/ # Application logs
├── config.py # Global configuration
├── chatbot.py # Main chatbot orchestration engine
├── requirements.txt # Dependencies
├── docker-compose.yml # Docker services (PostgreSQL, etc.)
└── README.md # Project documentation

text

---

## 🚀 Quick Start

### ✅ Prerequisites

1. Python 3.8+.  
2. Docker & Docker Compose (recommended) **or** local PostgreSQL.  
3. Ollama installed (`ollama` CLI available) with at least one model (e.g., `llama3` or `mistral`).  
4. (Optional) Pinecone free-tier account for article search.  

### 1️⃣ Install dependencies

pip install -r requirements.txt

text

### 2️⃣ Set up PostgreSQL

**Option A – Docker (recommended)**  

Windows
scripts\setup\setup_docker.bat

Linux / macOS
chmod +x scripts/setup/setup_docker.sh
./scripts/setup/setup_docker.sh

or
docker-compose up -d

text

This starts PostgreSQL, creates the DB, loads schema + seed data, and creates `.env` with defaults.  

**Option B – Manual**  

CREATE DATABASE nba_chatbot;

text
undefined
psql -U postgres -d nba_chatbot -f database/schema.sql
psql -U postgres -d nba_chatbot -f database/seed_data.sql

text

### 3️⃣ Configure environment

Create `.env` in project root if it does not exist:  

Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nba_chatbot
DB_USER=postgres
DB_PASSWORD=postgres

Pinecone
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=basketball-articles

Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

text

### 4️⃣ Prepare Ollama

ollama pull llama3

or
ollama pull mistral

text

### 5️⃣ (Optional) Scrape articles

python scraper/article_scraper.py

text

Creates `article_0.txt` … `article_1399.txt` in `data/articles/` from RSS feeds.  

### 6️⃣ Build vector store

python embeddings/vector_store.py

text

Loads article text, chunks it, embeds with `sentence-transformers`, and upserts to Pinecone.  

### 7️⃣ Run API

python api/main.py

or
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

text

API available at `http://localhost:8000`.  

### 8️⃣ Open the web UI

cd frontend
python -m http.server 8080

text

Then open `http://localhost:8080` in your browser to chat.  

---

## 💬 Usage

### 🔹 Example stat questions

- “How many points did LeBron James score?”  
- “What was the score in the Warriors vs Suns match?”  
- “When is the next Lakers game?”  
- “Show me Giannis' last game stats.”  

These go through `IntentDetectionAgent`, then `StatsAgent` / `PlayerStatsAgent`, and get formatted into natural language.  

### 🔹 Example article / mixed questions

- “What's the analysis on the Lakers’ recent performance?”  
- “Explain the Warriors' strategy this season.”  
- “How did LeBron perform and what do analysts say about it?”  

These combine structured stats agents with `ArticleSearchAgent` and `ResponseFormatterAgent` for richer answers.  

### 🔹 CLI quick test

python chatbot.py

text

Runs `BasketballChatbot` with a few test questions and prints responses to the console.  

---

## 🌐 API

- `POST /chat` – main chat endpoint.  

**Request**  

{
"question": "How many points did LeBron James score?"
}

text

**Response**  

{
"answer": "LeBron James scored 32 points in his last game..."
}

text

- `GET /` – health check.  

---

## 🧱 Agents

Core agents and roles:  

- 🧭 `IntentDetectionAgent` – classify query type (stats, schedule, live, standings, injuries, trends, news, articles, mixed).  
- 📊 `StatsAgent` – game results, final scores, match stats.  
- 🧍 `PlayerStatsAgent` – player box-score style stats and performance lines.  
- 🗓 `ScheduleAgent` – upcoming games, date-based schedules.  
- 📺 `LiveGameAgent` – live or in-progress game context (where supported).  
- 🏆 `StandingsAgent` – conference standings and rankings.  
- 🚑 `InjuryReportAgent` – injury status queries.  
- 📈 `PlayerTrendAgent` – recent form and performance trends.  
- 📅 `SeasonAveragesAgent` – season averages for players.  
- 📰 `TeamNewsAgent` – latest team news.  
- 🔍 `ArticleSearchAgent` – semantic article search via Pinecone.  
- 🗣 `ResponseFormatterAgent` – composes final answers using Ollama.  

---

## 🧰 Common Issues

- ❌ **“Database connection failed”** – ensure PostgreSQL is running, `.env` credentials are correct, and `nba_chatbot` exists.  
- ❌ **“PINECONE_API_KEY not set”** – add key + environment to `.env` and restart.  
- ❌ **“Ollama connection failed”** – run `ollama serve`, verify model with `ollama list`, check `OLLAMA_BASE_URL`.  
- ❌ **“No articles found”** – run `python scraper/article_scraper.py` and confirm `data/articles/` has `.txt` files.  
- ❌ **“Vector store not initialized”** – run `python embeddings/vector_store.py` after scraping and confirm Pinecone config.  

---

## 🔒 Security

- Never commit `.env`; ensure it is in `.gitignore`.  
- Use restrictive CORS settings for production (do not leave as `*`).  
- Keep all secrets (DB passwords, API keys) in environment variables.  

---

## 🤝 Contributing

Issues and PRs are welcome. Please follow the existing agent pattern and update documentation when adding new capabilities.  

---

## 📄 License

Open-source and free for educational and personal use.  

---

<div align="center">

**Built with ❤️ for NBA fans and AI builders.**  

</div>

