"""
Comprehensive validation test - validates and fixes until correct answer
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.direct_espn_fetcher import DirectESPNFetcher
from agents.stats_agent import StatsAgent
from agents.response_formatter_agent import ResponseFormatterAgent


def validate_knicks_result():
    """Validate Knicks result end-to-end"""
    print("\n" + "="*70)
    print("VALIDATION: New York Knicks - End-to-End Test")
    print("="*70)
    
    question = "Did the New York Knicks win their most recent game?"
    print(f"\nQuery: {question}")
    
    # Step 1: Test ESPN API directly
    print("\n--- Step 1: ESPN API Direct Test ---")
    fetcher = DirectESPNFetcher()
    api_result = fetcher.get_team_most_recent_game_result("New York Knicks", days_back=3)
    
    if not api_result:
        print("❌ ESPN API returned None")
        return False, None
    
    print(f"✅ ESPN API returned result:")
    print(f"   Team: {api_result.get('team_name')}")
    print(f"   Opponent: {api_result.get('opponent_name')}")
    print(f"   Score: {api_result.get('team_score')}-{api_result.get('opponent_score')}")
    print(f"   Did Win: {api_result.get('did_win')}")
    print(f"   Game Date: {api_result.get('game_date')}")
    
    # Validate opponent is not same as team
    if api_result.get('opponent_name') == api_result.get('team_name'):
        print(f"❌ ERROR: Opponent name is same as team name!")
        return False, api_result
    
    # Step 2: Test Stats Agent
    print("\n--- Step 2: Stats Agent Test ---")
    agent = StatsAgent()
    stats_result = agent.process_query(question)
    
    if not stats_result or not stats_result.get('win_query'):
        print("❌ Stats Agent did not process as win query")
        return False, api_result
    
    if stats_result.get('error'):
        print(f"❌ Stats Agent returned error: {stats_result.get('error')}")
        return False, api_result
    
    print(f"✅ Stats Agent processed correctly:")
    print(f"   Team: {stats_result.get('team')}")
    print(f"   Opponent: {stats_result.get('opponent_name')}")
    print(f"   Score: {stats_result.get('team_score')}-{stats_result.get('opponent_score')}")
    print(f"   Did Win: {stats_result.get('did_win')}")
    print(f"   Source: {stats_result.get('source')}")
    
    # Validate data matches
    if (stats_result.get('team_score') != api_result.get('team_score') or
        stats_result.get('opponent_score') != api_result.get('opponent_score') or
        stats_result.get('did_win') != api_result.get('did_win')):
        print("❌ ERROR: Stats Agent data doesn't match API result!")
        return False, api_result
    
    # Step 3: Test Response Formatter
    print("\n--- Step 3: Response Formatter Test ---")
    formatter = ResponseFormatterAgent()
    final_response = formatter.format_response(stats_result)
    
    print(f"✅ Response formatted:")
    print(f"   {final_response}")
    
    # Validate response format
    response_lower = final_response.lower()
    did_win = stats_result.get('did_win', False)
    team_score = stats_result.get('team_score', 0)
    opponent_score = stats_result.get('opponent_score', 0)
    opponent_name = stats_result.get('opponent_name', '')
    
    checks = {
        'Starts with Yes/No': (response_lower.startswith('yes') or response_lower.startswith('no')),
        'Contains "most recent game"': 'most recent game' in response_lower,
        'Contains "against"': 'against' in response_lower,
        'Contains "with a final score of"': 'with a final score of' in response_lower,
        'Contains team score': str(team_score) in final_response,
        'Contains opponent score': str(opponent_score) in final_response,
        'Contains opponent name': opponent_name.lower() in response_lower if opponent_name else False,
        'Correct Yes/No': (response_lower.startswith('yes') if did_win else response_lower.startswith('no'))
    }
    
    print(f"\n--- Format Validation ---")
    all_passed = True
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check_name}: {passed}")
        if not passed:
            all_passed = False
    
    if not all_passed:
        print("\n❌ Format validation failed")
        return False, api_result
    
    # Step 4: Validate answer correctness
    print("\n--- Step 4: Answer Correctness Validation ---")
    
    # Check if answer matches the actual result
    if did_win:
        expected_start = "Yes."
        expected_win_text = "won"
    else:
        expected_start = "No."
        expected_win_text = "lost"
    
    if not final_response.startswith(expected_start):
        print(f"❌ ERROR: Answer should start with '{expected_start}' but starts with '{final_response[:10]}'")
        return False, api_result
    
    if expected_win_text not in response_lower:
        print(f"❌ ERROR: Answer should contain '{expected_win_text}' but doesn't")
        return False, api_result
    
    print(f"✅ Answer correctness validated")
    print(f"   Expected: {expected_start} ... {expected_win_text} ...")
    print(f"   Got: {final_response[:50]}...")
    
    print("\n" + "="*70)
    print("✅ ALL VALIDATIONS PASSED")
    print("="*70)
    print(f"Final Answer: {final_response}")
    
    return True, api_result


def test_multiple_teams_validation():
    """Test multiple teams to ensure method works for all"""
    print("\n" + "="*70)
    print("VALIDATION: Multiple Teams Test")
    print("="*70)
    
    test_teams = ["knicks", "Lakers", "Warriors"]
    results = []
    
    for team in test_teams:
        print(f"\n--- Testing: {team} ---")
        question = f"Did the {team} win their most recent game?"
        
        try:
            agent = StatsAgent()
            stats_result = agent.process_query(question)
            
            if stats_result and stats_result.get('win_query') and not stats_result.get('error'):
                formatter = ResponseFormatterAgent()
                response = formatter.format_response(stats_result)
                
                # Quick validation
                if (response.startswith('Yes.') or response.startswith('No.')) and 'most recent game' in response.lower():
                    print(f"✅ {team}: Valid response")
                    print(f"   {response[:80]}...")
                    results.append((team, True))
                else:
                    print(f"⚠️  {team}: Format issue")
                    results.append((team, False))
            else:
                print(f"⚠️  {team}: No data or error")
                results.append((team, None))
        except Exception as e:
            print(f"❌ {team}: Error - {e}")
            results.append((team, False))
    
    print(f"\n--- Summary ---")
    for team, result in results:
        if result is True:
            print(f"✅ {team}: PASSED")
        elif result is False:
            print(f"❌ {team}: FAILED")
        else:
            print(f"⚠️  {team}: NO DATA")
    
    return results


if __name__ == "__main__":
    print("\n" + "="*70)
    print("COMPREHENSIVE VALIDATION AND FIX")
    print("="*70)
    
    # Main validation
    success, result = validate_knicks_result()
    
    if success:
        print("\n✅ PRIMARY VALIDATION PASSED")
        
        # Test multiple teams
        team_results = test_multiple_teams_validation()
        
        all_teams_ok = all(r[1] is True or r[1] is None for r in team_results)
        if all_teams_ok:
            print("\n🎉 ALL VALIDATIONS PASSED - Implementation is correct!")
        else:
            print("\n⚠️  Some teams had issues, but primary validation passed")
    else:
        print("\n❌ VALIDATION FAILED - Need to fix issues")
        print("Checking what needs to be fixed...")
        
        # Diagnostic information
        if result:
            print(f"\nAPI Result Details:")
            print(f"  Team: {result.get('team_name')}")
            print(f"  Opponent: {result.get('opponent_name')}")
            print(f"  Score: {result.get('team_score')}-{result.get('opponent_score')}")
            print(f"  Did Win: {result.get('did_win')}")

