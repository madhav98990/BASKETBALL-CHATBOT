import sys
import os
# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from services.nba_api_library import NBAAPILibrary

api = NBAAPILibrary()
print(f"Current season: {api.current_season}")
print("\nTesting top 5 players in points...")

players = api.get_top_players_by_stat('points', limit=5)

if players:
    print(f"\n✓ Retrieved {len(players)} players:\n")
    for i, p in enumerate(players, 1):
        print(f"{i}. {p['player_name']} ({p['team']}): {p['stat_value']} PPG")
else:
    print("\n✗ No players returned")

