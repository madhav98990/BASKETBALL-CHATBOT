"""Test getting current season stats"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.nba_api_library import NBAAPILibrary
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 70)
print("Testing Current Season Stats (2025-26)")
print("=" * 70 + "\n")

api = NBAAPILibrary()
print(f"Current season detected: {api.current_season}")
print(f"Today's date: {datetime.now().strftime('%Y-%m-%d')}\n")

print("Fetching top 5 players by points for CURRENT season...")
print("-" * 70)

try:
    # Force current season by not passing season parameter
    players = api.get_top_players_by_stat('points', limit=5)
    
    if players and len(players) > 0:
        print(f"\n✅ SUCCESS! Retrieved {len(players)} players from {api.current_season} season:\n")
        for i, player in enumerate(players, 1):
            print(f"{i}. {player.get('player_name')} ({player.get('team')}): {player.get('stat_value'):.1f} PPG")
            print(f"   Games: {player.get('games_played')}, PTS: {player.get('points'):.1f}, REB: {player.get('rebounds'):.1f}, AST: {player.get('assists'):.1f}")
        print("\n✅ These are CURRENT SEASON (2025-26) stats!")
    else:
        print("\n❌ No players returned")
        print("The current season may not have enough data yet.")
        print("Trying previous season as fallback...")
        
        # Try previous season explicitly
        prev_season = "2024-25"
        players_prev = api.get_top_players_by_stat('points', limit=5, season=prev_season)
        if players_prev:
            print(f"\n⚠️  Fallback: Retrieved {len(players_prev)} players from {prev_season} season")
            for i, player in enumerate(players_prev, 1):
                print(f"{i}. {player.get('player_name')} ({player.get('team')}): {player.get('stat_value'):.1f} PPG")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

