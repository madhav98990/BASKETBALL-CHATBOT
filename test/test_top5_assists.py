"""Test top 5 players by assists per game"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.player_stats_agent import PlayerStatsAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 70)
print("Testing: Top 5 Players by Assists Per Game")
print("=" * 70)

agent = PlayerStatsAgent()

try:
    # Test the query
    result = agent._handle_top_players_query("top 5 players assists per game")
    
    if result and result.get('data') and len(result['data']) > 0:
        print(f"\n✓ SUCCESS! Retrieved {len(result['data'])} players:\n")
        print(f"Stat Type: {result.get('stat', 'assists')}")
        print(f"Source: {result.get('source', 'unknown')}\n")
        
        for i, player in enumerate(result['data'], 1):
            player_name = player.get('player_name', 'Unknown')
            team = player.get('team', '')
            assists = player.get('stat_value', 0)
            games = player.get('games_played', 0)
            points = player.get('points', 0)
            rebounds = player.get('rebounds', 0)
            
            print(f"{i}. {player_name} ({team})")
            print(f"   Assists Per Game: {assists:.1f} APG")
            print(f"   Games: {games}")
            print(f"   Additional Stats: {points:.1f} PPG, {rebounds:.1f} RPG")
            print()
        
        print("✓ Test PASSED!")
    else:
        error = result.get('error', 'No error message')
        print(f"\n✗ FAILED: {error}")
        print("✗ Test FAILED!")
        
except Exception as e:
    print(f"\n✗ EXCEPTION: {e}")
    import traceback
    traceback.print_exc()

