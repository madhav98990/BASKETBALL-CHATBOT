"""Test assists detection in top players query"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.player_stats_agent import PlayerStatsAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 70)
print("Testing: Assists Detection in Top Players Query")
print("=" * 70)

agent = PlayerStatsAgent()

# Test queries
test_queries = [
    "top 5 players assists per game",
    "top 5 players in assists per game",
    "top 5 players by assists",
    "top 5 assists per game",
    "top 5 players points per game",  # Should detect points
]

for query in test_queries:
    print(f"\n{'='*70}")
    print(f"Testing query: '{query}'")
    print(f"{'='*70}")
    
    try:
        result = agent._handle_top_players_query(query)
        
        detected_stat = result.get('stat', 'unknown')
        print(f"Detected stat type: {detected_stat}")
        print(f"Source: {result.get('source', 'unknown')}")
        
        if result.get('data') and len(result['data']) > 0:
            print(f"Retrieved {len(result['data'])} players")
            # Show first player's stat_value to verify
            first_player = result['data'][0]
            stat_value = first_player.get('stat_value', 0)
            player_name = first_player.get('player_name', 'Unknown')
            print(f"First player: {player_name} - {stat_value} {detected_stat}")
        else:
            error = result.get('error', 'No error message')
            print(f"Error: {error}")
            
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()

