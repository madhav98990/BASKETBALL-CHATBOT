# Docker Setup Guide

This guide explains how to set up the Basketball AI Chatbot using Docker for PostgreSQL.

## 🐳 Why Docker?

- **Easy Setup**: No need to install PostgreSQL manually
- **Isolated**: Doesn't affect your system PostgreSQL
- **Portable**: Works the same on Windows, Mac, and Linux
- **Automatic**: Database schema and data are loaded automatically

## 📋 Prerequisites

1. **Docker Desktop** installed
   - Windows/Mac: Download from https://www.docker.com/products/docker-desktop
   - Linux: Install Docker Engine and Docker Compose

2. Verify Docker is running:
   ```bash
   docker --version
   docker compose version
   ```

## 🚀 Quick Start

### Windows

1. Run the setup script:
   ```cmd
   setup_docker.bat
   ```

2. The script will:
   - Create `.env` file with default credentials
   - Start PostgreSQL container
   - Automatically load schema and seed data

### Linux/Mac

1. Make script executable:
   ```bash
   chmod +x setup_docker.sh
   ```

2. Run the setup script:
   ```bash
   ./setup_docker.sh
   ```

### Manual Setup

If you prefer to do it manually:

1. **Start the database:**
   ```bash
   docker-compose up -d
   ```

2. **Check if it's running:**
   ```bash
   docker ps
   ```
   You should see `nba_chatbot_db` container running.

3. **Verify database is ready:**
   ```bash
   docker-compose exec postgres psql -U postgres -d nba_chatbot -c "SELECT COUNT(*) FROM teams;"
   ```
   Should return `30` (number of teams).

## 📊 Database Details

- **Host**: `localhost`
- **Port**: `5433` (changed from 5432 to avoid conflicts)
- **Database**: `nba_chatbot`
- **Username**: `postgres`
- **Password**: `postgres`

These are set in `.env` file (auto-created by setup script).

## 🔧 Common Commands

### Start Database
```bash
docker-compose up -d
```

### Stop Database
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f
```

### Access PostgreSQL Shell
```bash
docker-compose exec postgres psql -U postgres -d nba_chatbot
```

### Restart Database
```bash
docker-compose restart
```

### Remove Database (keeps data)
```bash
docker-compose down
```

### Remove Database and Data
```bash
docker-compose down -v
```

## 🗄️ Data Persistence

Data is stored in a Docker volume named `postgres_data`. This means:
- Data persists even if you stop the container
- Data is removed only if you use `docker-compose down -v`

## 🔍 Troubleshooting

### Container won't start

1. Check if port 5432 is already in use:
   ```bash
   # Windows
   netstat -ano | findstr :5432
   
   # Linux/Mac
   lsof -i :5432
   ```

2. If port is in use, either:
   - Stop the other PostgreSQL service
   - The default port is already set to 5433 in `docker-compose.yml` to avoid conflicts
   - If you need a different port, change it in `docker-compose.yml` and update `.env`

### Database connection errors

1. Make sure container is running:
   ```bash
   docker ps
   ```

2. Check container logs:
   ```bash
   docker-compose logs postgres
   ```

3. Verify `.env` file exists and has correct values

### Schema not loaded

The schema and seed data are automatically loaded on first startup. If they're missing:

1. Stop and remove container:
   ```bash
   docker-compose down -v
   ```

2. Start again:
   ```bash
   docker-compose up -d
   ```

Or manually run:
```bash
docker-compose exec postgres psql -U postgres -d nba_chatbot -f /docker-entrypoint-initdb.d/01-schema.sql
docker-compose exec postgres psql -U postgres -d nba_chatbot -f /docker-entrypoint-initdb.d/02-seed_data.sql
```

## 🔐 Security Note

The default credentials (`postgres/postgres`) are fine for local development. For production:
1. Change the password in `docker-compose.yml`
2. Update `.env` file accordingly
3. Use Docker secrets or environment variables for sensitive data

## 📝 Next Steps

After Docker setup:
1. ✅ Database is ready
2. Install Ollama: https://ollama.ai
3. (Optional) Setup Pinecone for article search
4. Start the API: `python api/main.py`
5. Open `frontend/index.html` in browser

## 🆘 Need Help?

- Check Docker logs: `docker-compose logs -f`
- Verify container status: `docker ps`
- Test connection: `python -c "from database.db_connection import db; db.connect()"`

