"""
Diagnostic script to check Python environment and module availability
"""
import sys
import os

print("=" * 60)
print("Python Environment Diagnostic")
print("=" * 60)

# Check Python version and path
print(f"\n1. Python Version: {sys.version}")
print(f"   Python Executable: {sys.executable}")
print(f"   Python Path: {sys.path[:3]}...")

# Check if we're in a virtual environment
venv = os.environ.get('VIRTUAL_ENV')
if venv:
    print(f"\n2. Virtual Environment: {venv}")
else:
    print("\n2. Virtual Environment: Not detected (using system Python)")

# Test critical imports
print("\n3. Testing Module Imports:")
modules_to_test = [
    'aiohttp',
    'aiofiles', 
    'bs4',
    'feedparser',
    'tqdm',
    'asyncio'
]

for module in modules_to_test:
    try:
        if module == 'bs4':
            __import__('bs4')
            print(f"   ✓ {module} (beautifulsoup4)")
        else:
            __import__(module)
            print(f"   ✓ {module}")
    except ImportError as e:
        print(f"   ✗ {module}: {e}")

# Check if we can import the scraper
print("\n4. Testing Scraper Import:")
try:
    # Add project root to path
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, project_root)
    from scraper.article_scraper import ArticleScraper
    print("   ✓ ArticleScraper imported successfully")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Diagnostic Complete!")
print("\nIf aiohttp shows ✗, run: pip install aiohttp")
print("If using a virtual environment, make sure it's activated")

