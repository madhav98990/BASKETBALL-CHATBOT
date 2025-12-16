"""Test enhanced top players with all stats"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.nba_api_library import NBAAPILibrary
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_enhanced_top_players():
    """Test getting top players with all stats"""
    nba_api = NBAAPILibrary()
    
    print("=" * 70)
    print("Testing Enhanced Top Players - All Stats Included")
    print("=" * 70)
    
    # Test points with all stats
    print("\n1. Top 5 Players in Points Per Game (with all stats):")
    try:
        players = nba_api.get_top_players_by_stat('points', limit=5)
        if players:
            print(f"✓ Successfully retrieved {len(players)} players\n")
            for i, p in enumerate(players, 1):
                print(f"{i}. {p['player_name']} ({p['team']})")
                print(f"   Points: {p['stat_value']:.1f} PPG")
                print(f"   Rebounds: {p.get('rebounds', 0):.1f} RPG")
                print(f"   Assists: {p.get('assists', 0):.1f} APG")
                print(f"   Steals: {p.get('steals', 0):.1f} SPG")
                print(f"   Blocks: {p.get('blocks', 0):.1f} BPG")
                if p.get('field_goal_pct', 0) > 0:
                    print(f"   FG%: {p['field_goal_pct']*100:.1f}%")
                print()
        else:
            print("✗ No players returned")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_top_players()

