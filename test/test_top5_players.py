"""Quick test for top 5 players query"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.nba_api_library import NBAAPILibrary
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_top5_points():
    """Test getting top 5 players in points per game"""
    nba_api = NBAAPILibrary()
    
    print("\n" + "=" * 70)
    print("Testing: Top 5 Players in Points Per Game")
    print("=" * 70 + "\n")
    
    try:
        players = nba_api.get_top_players_by_stat('points', limit=5)
        if players and len(players) > 0:
            print(f"✓ Successfully retrieved {len(players)} players\n")
            for i, player in enumerate(players, 1):
                print(f"{i}. {player.get('player_name')} ({player.get('team')}): {player.get('stat_value'):.1f} PPG")
            print("\n✓ Test PASSED!")
            return True
        else:
            print("✗ No players returned")
            print("✗ Test FAILED!")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_top5_points()

