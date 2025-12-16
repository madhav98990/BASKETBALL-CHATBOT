"""Test top 5 players in NBA by points per game query"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.player_stats_agent import PlayerStatsAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 70)
print("Testing: Top 5 Players in NBA by Points Per Game")
print("=" * 70 + "\n")

agent = PlayerStatsAgent()

# Test the exact query
query = "top 5 players in nba by points per game"

try:
    result = agent._handle_top_players_query(query)
    
    print(f"Query: {query}")
    print(f"Source: {result.get('source', 'unknown')}")
    print(f"Stat Type: {result.get('stat', 'unknown')}")
    print(f"Limit: {result.get('limit', 'unknown')}")
    
    if result.get('error'):
        print(f"\n✗ ERROR: {result.get('error')}")
        print("\nThis indicates the NBA API and fallbacks failed.")
    else:
        players = result.get('data', [])
        if players and len(players) > 0:
            print(f"\n✓ SUCCESS! Retrieved {len(players)} players from {result.get('source')}\n")
            print("Top 5 Players by Points Per Game:")
            print("-" * 70)
            for i, player in enumerate(players, 1):
                print(f"{i}. {player.get('player_name')} ({player.get('team')})")
                print(f"   Points Per Game: {player.get('stat_value'):.1f} PPG")
                print(f"   Games Played: {player.get('games_played')}")
                print(f"   Additional Stats: {player.get('points'):.1f} PTS, {player.get('rebounds'):.1f} REB, {player.get('assists'):.1f} AST")
                print()
            print("✓ Test PASSED!")
        else:
            print("\n✗ FAILED: No players returned")
            print("All APIs may have failed or returned empty results.")
    
except Exception as e:
    print(f"\n✗ EXCEPTION: {e}")
    import traceback
    traceback.print_exc()

