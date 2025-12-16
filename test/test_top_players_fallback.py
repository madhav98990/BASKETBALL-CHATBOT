"""Test top players query with fallback chain"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.player_stats_agent import PlayerStatsAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_top_players_fallback():
    """Test getting top 5 players with fallback chain"""
    agent = PlayerStatsAgent()
    
    print("\n" + "=" * 70)
    print("Testing: Top 5 Players in NBA by Points Per Game (with Fallbacks)")
    print("=" * 70 + "\n")
    
    # Test query
    query = "top 5 players in nba by points per game"
    
    try:
        result = agent._handle_top_players_query(query)
        
        print(f"Query: {query}")
        print(f"Source: {result.get('source', 'unknown')}")
        print(f"Stat Type: {result.get('stat', 'unknown')}")
        print(f"Limit: {result.get('limit', 'unknown')}")
        
        if result.get('error'):
            print(f"\n✗ Error: {result.get('error')}")
            print("\n✗ Test FAILED - All APIs failed!")
            return False
        
        players = result.get('data', [])
        if players and len(players) > 0:
            print(f"\n✓ Successfully retrieved {len(players)} players from {result.get('source')}\n")
            for i, player in enumerate(players, 1):
                print(f"{i}. {player.get('player_name')} ({player.get('team')}): {player.get('stat_value'):.1f} PPG")
                print(f"   Games: {player.get('games_played')}, PTS: {player.get('points'):.1f}, REB: {player.get('rebounds'):.1f}, AST: {player.get('assists'):.1f}")
            print("\n✓ Test PASSED!")
            return True
        else:
            print("\n✗ No players returned")
            print("✗ Test FAILED!")
            return False
    
    except Exception as e:
        print(f"\n✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_different_stats():
    """Test different stat types"""
    agent = PlayerStatsAgent()
    
    stats_to_test = ['points', 'assists', 'rebounds']
    
    print("\n" + "=" * 70)
    print("Testing Different Stat Types")
    print("=" * 70 + "\n")
    
    for stat in stats_to_test:
        query = f"top 5 players in nba by {stat}"
        print(f"\nTesting: {query}")
        
        try:
            result = agent._handle_top_players_query(query)
            players = result.get('data', [])
            
            if players and len(players) > 0:
                print(f"  ✓ Got {len(players)} players from {result.get('source')}")
                print(f"  Top player: {players[0].get('player_name')} ({players[0].get('team')}): {players[0].get('stat_value'):.1f}")
            else:
                print(f"  ✗ Failed: {result.get('error', 'No data returned')}")
        except Exception as e:
            print(f"  ✗ Exception: {e}")

if __name__ == "__main__":
    success = test_top_players_fallback()
    test_different_stats()
    
    if success:
        print("\n" + "=" * 70)
        print("Overall: Test PASSED - Fallback chain is working!")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("Overall: Test FAILED - Check API availability")
        print("=" * 70)

