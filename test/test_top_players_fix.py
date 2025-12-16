"""Test top players query with current data"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.nba_api_library import NBAAPILibrary
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_top_players():
    """Test getting top players - should return current data"""
    nba_api = NBAAPILibrary()
    
    print("=" * 60)
    print("Testing Top Players - Current Data")
    print("=" * 60)
    
    # Test points
    print("\n1. Top 5 Players in Points:")
    try:
        players = nba_api.get_top_players_by_stat('points', limit=5)
        if players:
            print(f"✓ Successfully retrieved {len(players)} players")
            for i, player in enumerate(players, 1):
                print(f"  {i}. {player.get('player_name')} ({player.get('team')}): {player.get('stat_value')} PPG")
        else:
            print("✗ No players returned")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test assists
    print("\n2. Top 5 Players in Assists:")
    try:
        players = nba_api.get_top_players_by_stat('assists', limit=5)
        if players:
            print(f"✓ Successfully retrieved {len(players)} players")
            for i, player in enumerate(players, 1):
                print(f"  {i}. {player.get('player_name')} ({player.get('team')}): {player.get('stat_value')} APG")
        else:
            print("✗ No players returned")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_top_players()

