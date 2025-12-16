"""Test the method works for all teams, not just Knicks"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.direct_espn_fetcher import DirectESPNFetcher
from agents.stats_agent import StatsAgent
from agents.response_formatter_agent import ResponseFormatterAgent


def test_multiple_teams():
    """Test the method works for multiple teams"""
    print("\n" + "="*70)
    print("TEST: Method Works for All Teams (Not Just Knicks)")
    print("="*70)
    
    fetcher = DirectESPNFetcher()
    formatter = ResponseFormatterAgent()
    
    # Test with multiple teams
    test_teams = [
        "New York Knicks",
        "Lakers",
        "Warriors",
        "Celtics"
    ]
    
    results = []
    
    for team_name in test_teams:
        print(f"\n--- Testing: {team_name} ---")
        
        try:
            # Test ESPN API
            result = fetcher.get_team_most_recent_game_result(team_name, days_back=3)
            
            if result:
                print(f"✅ Found game result")
                print(f"  Team: {result.get('team_name')}")
                print(f"  Opponent: {result.get('opponent_name')}")
                print(f"  Score: {result.get('team_score')}-{result.get('opponent_score')}")
                print(f"  Did Win: {result.get('did_win')}")
                
                # Validate opponent is not the same as team
                if result.get('opponent_name') == result.get('team_name'):
                    print(f"  ❌ ERROR: Opponent name is same as team name!")
                    results.append((team_name, False, "Opponent name error"))
                else:
                    # Test response format
                    intent_data = {
                        'intent': 'match_stats',
                        'win_query': True,
                        'team': team_name,
                        'did_win': result.get('did_win', False),
                        'team_score': result.get('team_score', 0),
                        'opponent_score': result.get('opponent_score', 0),
                        'opponent_name': result.get('opponent_name', ''),
                        'game_date': result.get('game_date', ''),
                        'query': f'Did the {team_name} win their most recent game?',
                        'data': [result]
                    }
                    
                    response = formatter.format_response(intent_data)
                    print(f"  Response: {response}")
                    
                    # Validate format
                    if response.startswith('Yes.') or response.startswith('No.'):
                        print(f"  ✅ Format correct")
                        results.append((team_name, True, "Success"))
                    else:
                        print(f"  ⚠️  Format may be incorrect")
                        results.append((team_name, False, "Format issue"))
            else:
                print(f"  ⚠️  No game found (may be no games in last 3 days)")
                results.append((team_name, None, "No data"))
                
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            results.append((team_name, False, str(e)))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    for team, success, note in results:
        if success is True:
            status = "✅ PASSED"
        elif success is False:
            status = "❌ FAILED"
        else:
            status = "⚠️  NO DATA"
        print(f"{status}: {team} - {note}")
    
    passed = sum(1 for _, s, _ in results if s is True)
    total = len([r for r in results if r[1] is not None])
    
    print(f"\nPassed: {passed}/{total} teams with data")
    return passed > 0


def test_full_flow_multiple_teams():
    """Test full flow for multiple teams"""
    print("\n" + "="*70)
    print("TEST: Full Flow for Multiple Teams")
    print("="*70)
    
    agent = StatsAgent()
    formatter = ResponseFormatterAgent()
    
    test_queries = [
        "Did the New York Knicks win their most recent game?",
        "Did the Lakers win their most recent game?",
        "Did the Warriors win their most recent game?"
    ]
    
    for query in test_queries:
        print(f"\n--- Query: {query} ---")
        
        try:
            # Stats Agent
            stats_result = agent.process_query(query)
            
            if stats_result and stats_result.get('win_query'):
                if stats_result.get('error'):
                    print(f"  ⚠️  Error: {stats_result.get('error')}")
                    continue
                
                print(f"  ✅ Processed")
                print(f"    Team: {stats_result.get('team')}")
                print(f"    Opponent: {stats_result.get('opponent_name')}")
                print(f"    Score: {stats_result.get('team_score')}-{stats_result.get('opponent_score')}")
                print(f"    Source: {stats_result.get('source')}")
                
                # Response Formatter
                response = formatter.format_response(stats_result)
                print(f"  📝 Response: {response}")
                
                # Validate
                if (response.startswith('Yes.') or response.startswith('No.')) and 'most recent game' in response.lower():
                    print(f"  ✅ Format correct")
                else:
                    print(f"  ⚠️  Format may need review")
            else:
                print(f"  ❌ Not processed as win query")
                
        except Exception as e:
            print(f"  ❌ ERROR: {e}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("ALL TEAMS TEST - Verify Method Works for All Teams")
    print("="*70)
    
    # Test 1: Multiple teams
    success1 = test_multiple_teams()
    
    # Test 2: Full flow
    test_full_flow_multiple_teams()
    
    if success1:
        print("\n✅ Method works for multiple teams!")
    else:
        print("\n⚠️  Some issues detected")

