#!/usr/bin/env python3
"""Test Ball Don't Lie API player search"""

from services.balldontlie_api import BallDontLieAPI

api = BallDontLieAPI()

# Try searching for Jokic
print("Searching for 'Nikola Jokic'...")
result = api.search_player("Nikola Jokic")
if result:
    print(f"✓ Found: {result}")
else:
    print("✗ Not found")

print("\nSearching for 'Jokic'...")
result = api.search_player("Jokic")
if result:
    print(f"✓ Found: {result}")
else:
    print("✗ Not found")

print("\nSearching for 'LeBron James'...")
result = api.search_player("LeBron James")
if result:
    print(f"✓ Found: {result}")
else:
    print("✗ Not found")
