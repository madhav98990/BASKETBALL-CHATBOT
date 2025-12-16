"""
Quick validation script for team game results - tests key teams
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.direct_espn_fetcher import DirectESPNFetcher
from agents.stats_agent import StatsAgent

def quick_validate():
    """Quick validation of key teams"""
    print("\n" + "="*70)
    print("QUICK VALIDATION - Key Teams")
    print("="*70)
    
    # Test key teams with different name formats
    test_cases = [
        ("warriors", "Warriors"),
        ("lakers", "Lakers"),
        ("knicks", "Knicks"),
        ("golden state warriors", "Golden State Warriors"),
        ("GSW", "GSW"),
        ("76ers", "76ers"),
        ("trail blazers", "Trail Blazers"),
    ]
    
    fetcher = DirectESPNFetcher()
    agent = StatsAgent()
    
    print("\nTesting ESPN API directly...")
    for team_input, team_display in test_cases:
        print(f"\n  Testing: {team_input}")
        try:
            result = fetcher.get_team_most_recent_game_result(team_input, days_back=30)
            if result:
                # Quick validation
                valid = True
                errors = []
                
                if result.get('team_score', 0) <= 0:
                    errors.append("Invalid team score")
                    valid = False
                if result.get('opponent_score', 0) <= 0:
                    errors.append("Invalid opponent score")
                    valid = False
                if result.get('opponent_name', '').upper() == result.get('team_name', '').upper():
                    errors.append("Opponent same as team")
                    valid = False
                if result.get('did_win') != (result.get('team_score', 0) > result.get('opponent_score', 0)):
                    errors.append("Win/loss mismatch")
                    valid = False
                
                if valid:
                    win_loss = "WON" if result.get('did_win') else "LOST"
                    print(f"    ✅ {result.get('team_name')} {win_loss} {result.get('team_score')}-{result.get('opponent_score')} vs {result.get('opponent_name')} on {result.get('game_date')}")
                else:
                    print(f"    ❌ Validation errors: {', '.join(errors)}")
                    print(f"       Result: {result.get('team_name')} {result.get('team_score')}-{result.get('opponent_score')} vs {result.get('opponent_name')}")
            else:
                print(f"    ⚠️  No result found")
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
    
    print("\n" + "="*70)
    print("Testing Stats Agent integration...")
    print("="*70)
    
    test_queries = [
        "Did the warriors win their most recent game?",
        "Did the lakers win their most recent game?",
        "Did the knicks win their most recent game?"
    ]
    
    for query in test_queries:
        print(f"\n  Query: {query}")
        try:
            result = agent.process_query(query)
            if result and result.get('win_query') and not result.get('error'):
                win_loss = "WON" if result.get('did_win') else "LOST"
                print(f"    ✅ {result.get('team')} {win_loss} {result.get('team_score')}-{result.get('opponent_score')} vs {result.get('opponent_name')} on {result.get('game_date')}")
            elif result and result.get('error'):
                print(f"    ❌ Error: {result.get('error')}")
            else:
                print(f"    ⚠️  No valid result")
        except Exception as e:
            print(f"    ❌ Exception: {str(e)}")
    
    print("\n" + "="*70)
    print("Validation complete!")
    print("="*70)


if __name__ == "__main__":
    quick_validate()

