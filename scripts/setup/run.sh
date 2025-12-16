#!/bin/bash
# Quick start script for Basketball AI Chatbot

echo "🏀 Basketball AI Chatbot - Quick Start"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file with your configuration."
    echo "See README.md for details."
    exit 1
fi

# Check if database is set up
echo "📊 Checking database..."
python -c "from database.db_connection import db; db.connect()" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Database not set up. Running setup..."
    python setup_database.py
fi

# Check if Ollama is running
echo "🤖 Checking Ollama..."
curl -s http://localhost:11434/api/tags > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️  Ollama not running. Please start it with: ollama serve"
    echo "   (Run this in a separate terminal)"
fi

# Start the API server
echo "🚀 Starting API server..."
echo "   API will be available at http://localhost:8000"
echo "   Open frontend/index.html in your browser"
echo ""
python api/main.py

