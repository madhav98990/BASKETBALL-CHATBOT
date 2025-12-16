"""
Test script to diagnose article scraper issues
"""
import sys
import os

print("Testing article scraper setup...")
print("=" * 50)

# Test 1: Check Python version
print(f"Python version: {sys.version}")

# Test 2: Check imports
print("\n1. Testing imports...")
try:
    import asyncio
    print("   ✓ asyncio")
except ImportError as e:
    print(f"   ✗ asyncio: {e}")

try:
    import aiohttp
    print("   ✓ aiohttp")
except ImportError as e:
    print(f"   ✗ aiohttp: {e}")

try:
    import aiofiles
    print("   ✓ aiofiles")
except ImportError as e:
    print(f"   ✗ aiofiles: {e}")

try:
    from bs4 import BeautifulSoup
    print("   ✓ beautifulsoup4")
except ImportError as e:
    print(f"   ✗ beautifulsoup4: {e}")

try:
    import feedparser
    print("   ✓ feedparser")
except ImportError as e:
    print(f"   ✗ feedparser: {e}")

try:
    from tqdm import tqdm
    print("   ✓ tqdm")
except ImportError as e:
    print(f"   ✗ tqdm: {e}")

# Test 3: Check config
print("\n2. Testing config...")
try:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from config import RSS_FEEDS, ARTICLES_DIR, MAX_CONCURRENT_REQUESTS
    print(f"   ✓ Config loaded")
    print(f"   - RSS_FEEDS: {len(RSS_FEEDS)} feeds")
    print(f"   - ARTICLES_DIR: {ARTICLES_DIR}")
    print(f"   - MAX_CONCURRENT_REQUESTS: {MAX_CONCURRENT_REQUESTS}")
except Exception as e:
    print(f"   ✗ Config error: {e}")

# Test 4: Check article scraper import
print("\n3. Testing article scraper import...")
try:
    from scraper.article_scraper import ArticleScraper
    print("   ✓ ArticleScraper imported")
except Exception as e:
    print(f"   ✗ Import error: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Check if articles directory exists
print("\n4. Testing articles directory...")
articles_dir = os.path.join(os.path.dirname(__file__), 'data', 'articles')
if os.path.exists(articles_dir):
    article_count = len([f for f in os.listdir(articles_dir) if f.endswith('.txt')])
    print(f"   ✓ Articles directory exists: {articles_dir}")
    print(f"   - Current articles: {article_count}")
else:
    print(f"   ⚠ Articles directory doesn't exist: {articles_dir}")
    print("   (Will be created automatically)")

print("\n" + "=" * 50)
print("Test complete!")
print("\nIf all tests passed, try running:")
print("  python scraper/article_scraper.py")

