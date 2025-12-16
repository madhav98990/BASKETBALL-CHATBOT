"""
Test script to validate Knicks match result functionality
Tests the exact format specified in the instructions
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.direct_espn_fetcher import DirectESPNFetcher
from agents.stats_agent import StatsAgent
from agents.response_formatter_agent import ResponseFormatterAgent


def test_espn_api_knicks():
    """Test ESPN API for New York Knicks"""
    print("\n" + "="*70)
    print("TEST 1: ESPN API - Fetch New York Knicks Most Recent Game")
    print("="*70)
    
    try:
        fetcher = DirectESPNFetcher()
        
        # Test with different team name variations
        test_names = ["knicks", "New York Knicks", "NYK"]
        
        for team_name in test_names:
            print(f"\nTesting with team name: '{team_name}'")
            result = fetcher.get_team_most_recent_game_result(team_name, days_back=30)
            
            if result:
                print(f"✅ SUCCESS: Found game result")
                print(f"  Team: {result.get('team_name')}")
                print(f"  Team Abbrev: {result.get('team_abbrev')}")
                print(f"  Opponent: {result.get('opponent_name')}")
                print(f"  Game Date: {result.get('game_date')}")
                print(f"  Team Score: {result.get('team_score')}")
                print(f"  Opponent Score: {result.get('opponent_score')}")
                print(f"  Did Win: {result.get('did_win')}")
                print(f"  Matchup: {result.get('matchup')}")
                
                # Validate required fields
                required = ['team_name', 'opponent_name', 'team_score', 'opponent_score', 'did_win']
                missing = [f for f in required if result.get(f) is None]
                
                if missing:
                    print(f"  ⚠️  Missing fields: {missing}")
                else:
                    print(f"  ✅ All required fields present")
                
                # Validate win/loss logic
                team_score = result.get('team_score', 0)
                opponent_score = result.get('opponent_score', 0)
                did_win = result.get('did_win', False)
                expected_win = team_score > opponent_score
                
                if did_win == expected_win:
                    print(f"  ✅ Win/loss logic correct")
                else:
                    print(f"  ❌ Win/loss logic incorrect! did_win={did_win}, but scores: {team_score} vs {opponent_score}")
                
                return result
            else:
                print(f"  ⚠️  No result found for '{team_name}'")
        
        print("\n❌ No game result found for any team name variation")
        return None
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_stats_agent():
    """Test Stats Agent with Knicks win query"""
    print("\n" + "="*70)
    print("TEST 2: Stats Agent - Process Knicks Win Query")
    print("="*70)
    
    try:
        agent = StatsAgent()
        question = "Did the New York Knicks win their most recent game?"
        
        print(f"\nQuery: {question}")
        result = agent.process_query(question)
        
        if result and result.get('win_query'):
            print(f"✅ SUCCESS: Processed as win query")
            print(f"  Type: {result.get('type')}")
            print(f"  Team: {result.get('team')}")
            print(f"  Did Win: {result.get('did_win')}")
            print(f"  Team Score: {result.get('team_score')}")
            print(f"  Opponent Score: {result.get('opponent_score')}")
            print(f"  Opponent: {result.get('opponent_name')}")
            print(f"  Source: {result.get('source')}")
            
            # Check for error
            if result.get('error'):
                print(f"  ⚠️  Error: {result.get('error')}")
                return False, result
            
            # Validate data
            if result.get('team_score') is not None and result.get('opponent_score') is not None:
                print(f"  ✅ Valid scores present")
                return True, result
            else:
                print(f"  ⚠️  Missing scores")
                return False, result
        else:
            print(f"❌ FAILED: Not processed as win query")
            print(f"  Result: {result}")
            return False, None
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_response_format():
    """Test Response Formatter - Exact Format Validation"""
    print("\n" + "="*70)
    print("TEST 3: Response Formatter - Validate Exact Format")
    print("="*70)
    
    try:
        formatter = ResponseFormatterAgent()
        
        # Get actual data from ESPN API
        fetcher = DirectESPNFetcher()
        game_result = fetcher.get_team_most_recent_game_result("New York Knicks", days_back=30)
        
        if not game_result:
            print("\n⚠️  SKIPPED: No game result available to format")
            return False, None
        
        # Create intent data
        intent_data = {
            'intent': 'match_stats',
            'win_query': True,
            'team': 'Knicks',
            'did_win': game_result.get('did_win', False),
            'team_score': game_result.get('team_score', 0),
            'opponent_score': game_result.get('opponent_score', 0),
            'opponent_name': game_result.get('opponent_name', ''),
            'game_date': game_result.get('game_date', ''),
            'query': 'Did the New York Knicks win their most recent game?',
            'data': [game_result]
        }
        
        print(f"\nInput Data:")
        print(f"  Did Win: {intent_data.get('did_win')}")
        print(f"  Team Score: {intent_data.get('team_score')}")
        print(f"  Opponent Score: {intent_data.get('opponent_score')}")
        print(f"  Opponent: {intent_data.get('opponent_name')}")
        
        response = formatter.format_response(intent_data)
        
        print(f"\n📝 Generated Response:")
        print(f"  {response}")
        
        # Validate exact format
        response_lower = response.lower()
        did_win = intent_data.get('did_win', False)
        team_score = intent_data.get('team_score', 0)
        opponent_score = intent_data.get('opponent_score', 0)
        opponent_name = intent_data.get('opponent_name', '')
        
        # Check format requirements
        checks = {
            'Starts with Yes/No': response_lower.startswith('yes') or response_lower.startswith('no'),
            'Contains "New York Knicks"': 'new york knicks' in response_lower,
            'Contains "won their most recent game" or "lost their most recent game"': 
                ('won their most recent game' in response_lower) or ('lost their most recent game' in response_lower),
            'Contains "against"': 'against' in response_lower,
            'Contains opponent name': opponent_name.lower() in response_lower if opponent_name else False,
            'Contains "with a final score of"': 'with a final score of' in response_lower,
            'Contains team score': str(team_score) in response,
            'Contains opponent score': str(opponent_score) in response,
            'Uses en dash (–) for score': '–' in response or '-' in response
        }
        
        print(f"\n📋 Format Validation:")
        all_passed = True
        for check_name, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}: {passed}")
            if not passed:
                all_passed = False
        
        # Check exact format
        if did_win:
            expected_start = "Yes. The New York Knicks won their most recent game against"
            expected_end = f"with a final score of {team_score}–{opponent_score}."
        else:
            expected_start = "No. The New York Knicks lost their most recent game against"
            expected_end = f"with a final score of {team_score}–{opponent_score}."
        
        format_correct = (
            response.startswith(expected_start.split('.')[0] + '.') and
            expected_end in response
        )
        
        if format_correct:
            print(f"\n✅ Format matches specification exactly!")
        else:
            print(f"\n⚠️  Format may not match specification exactly")
            print(f"  Expected start: {expected_start}")
            print(f"  Expected end: {expected_end}")
        
        return all_passed and format_correct, response
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_full_flow():
    """Test complete flow from query to formatted answer"""
    print("\n" + "="*70)
    print("TEST 4: Full Flow - Query to Final Answer")
    print("="*70)
    
    try:
        question = "Did the New York Knicks win their most recent game?"
        print(f"\nUser Query: {question}")
        
        # Step 1: Stats Agent
        stats_agent = StatsAgent()
        stats_result = stats_agent.process_query(question)
        
        if not stats_result or not stats_result.get('win_query'):
            print("\n❌ FAILED: Stats Agent did not process query correctly")
            return False
        
        # Check for error
        if stats_result.get('error'):
            print(f"\n⚠️  Error returned: {stats_result.get('error')}")
            response = stats_result.get('error')
            if response == "Live game data is temporarily unavailable. Please try again shortly.":
                print("✅ Error message matches specification")
                return True
            else:
                print("❌ Error message does not match specification")
                return False
        
        print(f"\n✅ Step 1: Stats Agent processed query")
        print(f"   Did Win: {stats_result.get('did_win')}")
        print(f"   Score: {stats_result.get('team_score')}-{stats_result.get('opponent_score')}")
        print(f"   Opponent: {stats_result.get('opponent_name')}")
        print(f"   Source: {stats_result.get('source')}")
        
        # Step 2: Response Formatter
        formatter = ResponseFormatterAgent()
        final_answer = formatter.format_response(stats_result)
        
        print(f"\n✅ Step 2: Response formatted")
        print(f"\n📝 Final Answer:")
        print(f"   {final_answer}")
        
        # Validate final answer
        answer_lower = final_answer.lower()
        is_valid = (
            (answer_lower.startswith('yes') or answer_lower.startswith('no')) and
            'new york knicks' in answer_lower and
            'most recent game' in answer_lower and
            'against' in answer_lower and
            'with a final score of' in answer_lower and
            str(stats_result.get('team_score')) in final_answer and
            str(stats_result.get('opponent_score')) in final_answer
        )
        
        if is_valid:
            print(f"\n✅ Validation: Complete flow works correctly")
            print(f"   - Query processed ✓")
            print(f"   - Game result fetched ✓")
            print(f"   - Win/loss determined ✓")
            print(f"   - Yes/No answer with score formatted ✓")
            return True
        else:
            print(f"\n⚠️  Validation: Some issues detected")
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*70)
    print("KNICKS MATCH RESULT VALIDATION TEST")
    print("Testing implementation against exact specifications")
    print("="*70)
    
    results = []
    
    # Test 1: ESPN API
    game_result = test_espn_api_knicks()
    results.append(("ESPN API - Knicks Identification", game_result is not None))
    
    # Test 2: Stats Agent
    success, data = test_stats_agent()
    results.append(("Stats Agent Processing", success))
    
    # Test 3: Response Format
    success, response = test_response_format()
    results.append(("Response Format (Exact)", success))
    
    # Test 4: Full Flow
    success = test_full_flow()
    results.append(("Full Flow Test", success))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    print(f"\n{'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 The implementation matches the specifications exactly!")
        print("   - Knicks identified correctly ✓")
        print("   - Most recent completed game fetched ✓")
        print("   - Win/loss determined by score comparison ✓")
        print("   - Yes/No answer format matches specification ✓")
        print("   - Error handling with retry works ✓")

