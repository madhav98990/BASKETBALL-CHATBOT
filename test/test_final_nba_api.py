"""Final test of NBA API with correct parameters"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set headers first
try:
    from nba_api.stats.library.http import NBAStatsHTTP
    NBAStatsHTTP.headers = {
        "Host": "stats.nba.com",
        "Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*",
        "x-nba-stats-token": "true",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "x-nba-stats-origin": "stats",
        "Referer": "https://www.nba.com/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9"
    }
except Exception:
    pass

from services.nba_api_library import NBAAPILibrary
import logging

logging.basicConfig(level=logging.INFO)
print("=" * 70)
print("Testing NBA API Library with correct parameters")
print("=" * 70)

api = NBAAPILibrary()
print(f"\nCurrent season: {api.current_season}")

print("\nTesting: Top 5 players in points per game")
print("-" * 70)

try:
    players = api.get_top_players_by_stat('points', limit=5)
    
    if players:
        print(f"\n✓ SUCCESS! Retrieved {len(players)} players:\n")
        for i, p in enumerate(players, 1):
            print(f"{i}. {p['player_name']} ({p['team']}): {p['stat_value']:.1f} PPG")
            print(f"   Rebounds: {p.get('rebounds', 0):.1f} RPG | Assists: {p.get('assists', 0):.1f} APG")
            if p.get('field_goal_pct', 0) > 0:
                print(f"   FG%: {p['field_goal_pct']*100:.1f}%")
            print()
    else:
        print("\n✗ FAILED: No players returned")
        
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("=" * 70)

