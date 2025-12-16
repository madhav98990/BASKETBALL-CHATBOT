@echo off
REM Docker setup script for Basketball AI Chatbot (Windows)

echo 🐳 Setting up PostgreSQL with Docker...
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed!
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker compose version >nul 2>&1
if errorlevel 1 (
    docker-compose --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Docker Compose is not available!
        pause
        exit /b 1
    )
    set COMPOSE_CMD=docker-compose
) else (
    set COMPOSE_CMD=docker compose
)

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file...
    (
        echo # Database Configuration (Docker)
        echo DB_HOST=localhost
        echo DB_PORT=5433
        echo DB_NAME=nba_chatbot
        echo DB_USER=postgres
        echo DB_PASSWORD=postgres
        echo.
        echo # Pinecone Configuration (Optional - for article search)
        echo PINECONE_API_KEY=
        echo PINECONE_ENVIRONMENT=us-east-1
        echo PINECONE_INDEX_NAME=basketball-articles
        echo.
        echo # Ollama Configuration
        echo OLLAMA_BASE_URL=http://localhost:11434
        echo OLLAMA_MODEL=llama3
    ) > .env
    echo ✅ .env file created with Docker defaults
)

REM Stop and remove existing containers
echo 🛑 Stopping existing containers (if any)...
%COMPOSE_CMD% down 2>nul

REM Start PostgreSQL container
echo 🚀 Starting PostgreSQL container...
%COMPOSE_CMD% up -d

REM Wait for PostgreSQL to be ready
echo ⏳ Waiting for PostgreSQL to be ready...
timeout /t 5 /nobreak >nul

REM Check if container is running
docker ps | findstr nba_chatbot_db >nul
if errorlevel 1 (
    echo ❌ Failed to start PostgreSQL container
    echo Check logs with: %COMPOSE_CMD% logs
    pause
    exit /b 1
) else (
    echo ✅ PostgreSQL container is running!
    echo.
    echo Database connection details:
    echo   Host: localhost
    echo   Port: 5433
    echo   Database: nba_chatbot
    echo   User: postgres
    echo   Password: postgres
    echo.
    echo The database schema and seed data will be automatically loaded.
    echo.
    echo To stop the database: %COMPOSE_CMD% down
    echo To view logs: %COMPOSE_CMD% logs -f
    echo.
)

pause

