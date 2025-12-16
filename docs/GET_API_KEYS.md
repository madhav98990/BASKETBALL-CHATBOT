# How to Get API Keys for NBA Chatbot

## Overview
Your chatbot currently works **without any API keys** using free ESPN API. However, if you want to enable additional features, you'll need to get API keys from these services.

---

## 1. RapidAPI Key (Optional - for alternative NBA data)

### Purpose
- Provides alternative NBA data source through API-Basketball
- Can be used as a fallback if ESPN API fails

### How to Get:
1. **Sign up**: Go to https://rapidapi.com/
2. **Create account**: Sign up for free (credit card may be required for some APIs)
3. **Find API**: Search for "API-Basketball" or "NBA API"
4. **Subscribe**: Choose the free tier (usually 100 requests/day)
5. **Get Key**: 
   - Go to your Dashboard
   - Navigate to "My Apps" or "Default Application"
   - Copy your `X-RapidAPI-Key`

### Free Tier Limits:
- Usually 100 requests per day
- Perfect for personal/testing use

### Cost:
- **Free tier available** with limited requests
- Paid plans start around $5-10/month for more requests

---

## 2. Pinecone API Key (Optional - for article search feature)

### Purpose
- Enables semantic search through scraped NBA articles
- Powers article-based queries like "what do articles say about LeBron James?"

### How to Get:
1. **Sign up**: Go to https://www.pinecone.io/
2. **Create account**: Sign up with email or Google account
3. **Create index**: 
   - Go to "Indexes" section
   - Click "Create Index"
   - Name: `basketball-articles`
   - Dimensions: `384` (for all-MiniLM-L6-v2 model)
   - Metric: `cosine`
4. **Get API Key**:
   - Go to "API Keys" section in dashboard
   - Click "Create API Key"
   - Copy the key (starts with something like `pcsk_...`)

### Free Tier Limits:
- **Free tier**: 1 index, ~100K vectors
- Perfect for development/testing

### Cost:
- **Free tier available** for personal projects
- Paid plans start around $70/month for production use

---

## 3. Ball Don't Lie API (Currently Not Working)

**Note**: This API is currently returning 404 errors. It was a free API that didn't require keys, but appears to be down or changed. You can skip this for now since ESPN API is working.

---

## How to Add API Keys to Your Project

### Step 1: Create `.env` file (if it doesn't exist)
```bash
# Copy from template
cp env_template.txt .env
```

### Step 2: Edit `.env` file
Open `.env` file and add your keys:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nba_chatbot
DB_USER=postgres
DB_PASSWORD=your_postgres_password_here

# Pinecone Configuration (Optional - for article search)
PINECONE_API_KEY=pcsk_your_pinecone_key_here
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=basketball-articles

# RapidAPI Configuration (Optional - for alternative NBA data)
RAPIDAPI_KEY=your_rapidapi_key_here

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

### Step 3: Restart the Server
After adding keys, restart your server:
```bash
# Stop current server (Ctrl+C)
# Then restart
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Quick Decision Guide

### Do I Need API Keys?

**❌ You DON'T need API keys if:**
- ✅ You only want player stats, game results, standings
- ✅ ESPN API is working (which it is!)
- ✅ You don't need article search feature

**✅ You DO need API keys if:**
- You want article-based queries ("what do articles say about...")
  → Need: **Pinecone API Key**
- You want an alternative data source as backup
  → Need: **RapidAPI Key**

---

## Current Status (Without Keys)

✅ **Working Features (No Keys Needed):**
- Player statistics
- Game results
- Standings
- Schedules
- All ESPN API features

❌ **Not Working (Requires Keys):**
- Article search (needs Pinecone)
- RapidAPI fallback (needs RapidAPI key)

---

## Cost Summary

| Service | Free Tier | Paid Plans |
|---------|-----------|------------|
| **ESPN API** | ✅ Unlimited | N/A (Free) |
| **RapidAPI** | ✅ 100 req/day | $5-10/month |
| **Pinecone** | ✅ 100K vectors | $70+/month |

**Recommendation**: Start with free tiers - they're usually enough for testing and personal use!

---

## Troubleshooting

### Key Not Working?
1. Make sure you copied the entire key (no spaces)
2. Check if key has expired (regenerate if needed)
3. Verify you're on the correct service tier
4. Check `.env` file is in project root directory
5. Restart server after adding keys

### Still Having Issues?
- Check server logs for specific error messages
- Verify `.env` file format (no quotes around values)
- Make sure `python-dotenv` is installed: `pip install python-dotenv`

---

## Next Steps

1. **For Article Search**: Get Pinecone key → Add to `.env` → Restart server
2. **For Backup Data**: Get RapidAPI key → Add to `.env` → Restart server
3. **For Current Use**: You're all set! ESPN API works without keys.

