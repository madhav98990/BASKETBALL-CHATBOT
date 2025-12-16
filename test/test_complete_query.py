"""Complete test of top 5 players query with full flow"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.player_stats_agent import PlayerStatsAgent
import logging

# Reduce logging noise
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

print("=" * 70)
print("COMPLETE TEST: Top 5 Players in NBA by Points Per Game")
print("=" * 70 + "\n")

agent = PlayerStatsAgent()

# Test the exact query
query = "top 5 players in nba by points per game"

print(f"Query: {query}\n")
print("Processing query through PlayerStatsAgent...\n")

try:
    result = agent._handle_top_players_query(query)
    
    print("=" * 70)
    print("RESULTS:")
    print("=" * 70)
    print(f"Source: {result.get('source', 'unknown')}")
    print(f"Stat Type: {result.get('stat', 'unknown')}")
    print(f"Limit: {result.get('limit', 'unknown')}")
    
    if result.get('error'):
        print(f"\n✗ ERROR: {result.get('error')}")
        print("\nThis means:")
        print("1. NBA API Library failed")
        print("2. ESPN API fallback failed") 
        print("3. Ball Don't Lie API fallback failed")
    else:
        players = result.get('data', [])
        if players and len(players) > 0:
            print(f"\n✓ SUCCESS! Retrieved {len(players)} players from {result.get('source')}\n")
            print("TOP 5 PLAYERS BY POINTS PER GAME:")
            print("-" * 70)
            for i, player in enumerate(players, 1):
                print(f"{i}. {player.get('player_name')} ({player.get('team')})")
                print(f"   Points Per Game: {player.get('stat_value'):.2f} PPG")
                print(f"   Games Played: {player.get('games_played')}")
                if player.get('rebounds', 0) > 0 or player.get('assists', 0) > 0:
                    print(f"   Additional: {player.get('rebounds', 0):.1f} REB, {player.get('assists', 0):.1f} AST")
                print()
            print("=" * 70)
            print("✓ TEST PASSED - Query working correctly!")
            print("=" * 70)
        else:
            print("\n✗ FAILED: No players returned")
            print("All APIs returned empty results.")
    
except Exception as e:
    print(f"\n✗ EXCEPTION: {e}")
    import traceback
    traceback.print_exc()

