"""Test top 5 players by PPG"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.nba_api_library import NBAAPILibrary
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 70)
print("Testing: Top 5 Players by Points Per Game")
print("=" * 70)

api = NBAAPILibrary()
print(f"\nCurrent season: {api.current_season}")

try:
    result = api.get_top_players_by_stat('points', limit=5)
    
    if result and len(result) > 0:
        print(f"\n✓ SUCCESS! Retrieved {len(result)} players:\n")
        for i, player in enumerate(result, 1):
            print(f"{i}. {player['player_name']} ({player['team']}): {player['stat_value']:.1f} PPG")
            print(f"   Games: {player['games_played']}, PTS: {player['points']:.1f}, REB: {player['rebounds']:.1f}, AST: {player['assists']:.1f}")
    else:
        print("\n✗ FAILED: No players returned")
except Exception as e:
    print(f"\n✗ EXCEPTION: {e}")
    import traceback
    traceback.print_exc()

