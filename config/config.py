"""
Configuration file for Basketball AI Chatbot
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'nba_chatbot'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

# Pinecone Configuration
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY', '')
PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT', 'us-east-1')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'basketball-articles')
PINECONE_DIMENSION = 384  # all-MiniLM-L6-v2 dimension

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3')

# Scraper Configuration
ARTICLES_DIR = 'data/articles'
CHUNK_SIZE = 250  # words per chunk
CHUNK_OVERLAP = 50  # words overlap

# Scraper Performance Settings
MAX_CONCURRENT_REQUESTS = 15  # Number of concurrent downloads
REQUEST_TIMEOUT = 10  # Request timeout in seconds
RATE_LIMIT_DELAY = 0.2  # Delay between requests (seconds)
MAX_RETRIES = 2  # Maximum retry attempts
MIN_ARTICLE_LENGTH = 200  # Minimum article length (characters)

# RSS Feed Sources - NBA-specific feeds only
# Removed general news feeds to ensure only NBA content
RSS_FEEDS = [
    # Primary NBA sources
    'https://www.cbssports.com/rss/headlines/nba',
    'https://www.espn.com/espn/rss/nba/news',
    'https://www.espn.com/espn/rss/nba',
    'https://www.nba.com/.rss/nba/rss.xml',
    'https://basketball.realgm.com/rss/wiretap/0/0.xml',
    'https://www.hoopsrumors.com/feed',
    'https://www.clutchpoints.com/nba/feed/',
    'https://www.rotoworld.com/rss/feed.aspx?sport=nba',
    
    # RealGM pagination (working pages)
    'https://basketball.realgm.com/rss/wiretap/0/2.xml',
    'https://basketball.realgm.com/rss/wiretap/0/4.xml',
    'https://basketball.realgm.com/rss/wiretap/0/6.xml',
    'https://basketball.realgm.com/rss/wiretap/0/8.xml',
    
    # Additional NBA-specific sources
    'https://www.talkbasket.net/feed',
    'https://feeds.feedburner.com/nba/rss',
    'https://www.si.com/nba/feed',
    'https://www.thescore.com/nba/news.rss',
    'https://www.bleacherreport.com/nba/feed',
]

