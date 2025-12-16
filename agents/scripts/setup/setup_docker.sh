#!/bin/bash
# Docker setup script for Basketball AI Chatbot

echo "🐳 Setting up PostgreSQL with Docker..."
echo "========================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "Please install Docker from: https://www.docker.com/get-started"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed!"
    echo "Please install Docker Compose"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Database Configuration (Docker)
DB_HOST=localhost
DB_PORT=5433
DB_NAME=nba_chatbot
DB_USER=postgres
DB_PASSWORD=postgres

# Pinecone Configuration (Optional - for article search)
PINECONE_API_KEY=
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=basketball-articles

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
EOF
    echo "✅ .env file created with Docker defaults"
fi

# Stop and remove existing containers
echo "🛑 Stopping existing containers (if any)..."
docker-compose down 2>/dev/null || docker compose down 2>/dev/null

# Start PostgreSQL container
echo "🚀 Starting PostgreSQL container..."
docker-compose up -d || docker compose up -d

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

# Check if container is running
if docker ps | grep -q nba_chatbot_db; then
    echo "✅ PostgreSQL container is running!"
    echo ""
    echo "Database connection details:"
    echo "  Host: localhost"
    echo "  Port: 5433"
    echo "  Database: nba_chatbot"
    echo "  User: postgres"
    echo "  Password: postgres"
    echo ""
    echo "The database schema and seed data will be automatically loaded."
    echo ""
    echo "To stop the database: docker-compose down"
    echo "To view logs: docker-compose logs -f"
else
    echo "❌ Failed to start PostgreSQL container"
    echo "Check logs with: docker-compose logs"
    exit 1
fi

