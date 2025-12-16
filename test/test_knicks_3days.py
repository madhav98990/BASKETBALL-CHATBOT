"""
Test script to validate Knicks match result with 3-day search
Tests and updates until data is fetched
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.direct_espn_fetcher import DirectESPNFetcher
from agents.stats_agent import StatsAgent
from agents.response_formatter_agent import ResponseFormatterAgent
from datetime import date, timedelta


def test_espn_api_with_retry(days_back=3, max_attempts=5):
    """Test ESPN API with retry logic until data is fetched"""
    print("\n" + "="*70)
    print(f"TEST: ESPN API - Fetch Knicks Game (Last {days_back} Days)")
    print("="*70)
    
    fetcher = DirectESPNFetcher()
    team_name = "New York Knicks"
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n--- Attempt {attempt}/{max_attempts} ---")
        print(f"Searching last {days_back} days...")
        
        try:
            result = fetcher.get_team_most_recent_game_result(team_name, days_back=days_back)
            
            if result:
                print(f"\n✅ SUCCESS: Found game result on attempt {attempt}")
                print(f"  Team: {result.get('team_name')}")
                print(f"  Opponent: {result.get('opponent_name')}")
                print(f"  Game Date: {result.get('game_date')}")
                print(f"  Team Score: {result.get('team_score')}")
                print(f"  Opponent Score: {result.get('opponent_score')}")
                print(f"  Did Win: {result.get('did_win')}")
                print(f"  Matchup: {result.get('matchup')}")
                
                # Validate
                if result.get('team_score') is not None and result.get('opponent_score') is not None:
                    print(f"\n✅ Validation: All data present and valid")
                    return True, result
                else:
                    print(f"\n⚠️  Validation: Missing scores, trying again...")
                    days_back += 1
                    continue
            else:
                print(f"⚠️  No game found in last {days_back} days")
                if attempt < max_attempts:
                    days_back += 1
                    print(f"Increasing search window to {days_back} days for next attempt...")
                else:
                    print(f"\n❌ FAILED: No game found after {max_attempts} attempts")
                    return False, None
                    
        except Exception as e:
            print(f"❌ ERROR on attempt {attempt}: {e}")
            if attempt < max_attempts:
                days_back += 1
                print(f"Increasing search window to {days_back} days for next attempt...")
            else:
                return False, None
    
    return False, None


def test_full_flow_with_3days():
    """Test complete flow with 3-day search"""
    print("\n" + "="*70)
    print("TEST: Full Flow - Query to Answer (3 Days)")
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
            print(f"\n⚠️  Error: {stats_result.get('error')}")
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
        
        # Validate format
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
            return True
        else:
            print(f"\n⚠️  Validation: Format issues detected")
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_incremental_days():
    """Test with incremental days until data is found"""
    print("\n" + "="*70)
    print("TEST: Incremental Search - Start with 3 days, increase until data found")
    print("="*70)
    
    fetcher = DirectESPNFetcher()
    team_name = "New York Knicks"
    days_back = 3
    max_days = 30
    
    while days_back <= max_days:
        print(f"\n--- Testing with {days_back} days ---")
        
        try:
            result = fetcher.get_team_most_recent_game_result(team_name, days_back=days_back)
            
            if result:
                print(f"\n✅ SUCCESS: Found game result with {days_back} days")
                print(f"  Team: {result.get('team_name')}")
                print(f"  Opponent: {result.get('opponent_name')}")
                print(f"  Game Date: {result.get('game_date')}")
                print(f"  Score: {result.get('team_score')}-{result.get('opponent_score')}")
                print(f"  Did Win: {result.get('did_win')}")
                
                # Test response format
                formatter = ResponseFormatterAgent()
                intent_data = {
                    'intent': 'match_stats',
                    'win_query': True,
                    'team': 'Knicks',
                    'did_win': result.get('did_win', False),
                    'team_score': result.get('team_score', 0),
                    'opponent_score': result.get('opponent_score', 0),
                    'opponent_name': result.get('opponent_name', ''),
                    'game_date': result.get('game_date', ''),
                    'query': 'Did the New York Knicks win their most recent game?',
                    'data': [result]
                }
                
                response = formatter.format_response(intent_data)
                print(f"\n📝 Formatted Response:")
                print(f"   {response}")
                
                return True, result, days_back
            else:
                print(f"  No game found in last {days_back} days")
                days_back += 1
                continue
                
        except Exception as e:
            print(f"  Error: {e}")
            days_back += 1
            continue
    
    print(f"\n❌ No game found even with {max_days} days")
    return False, None, None


if __name__ == "__main__":
    print("\n" + "="*70)
    print("KNICKS MATCH RESULT TEST - 3 DAYS SEARCH")
    print("Testing and updating until data is fetched")
    print("="*70)
    
    # Test 1: Direct API test with retry
    success, result = test_espn_api_with_retry(days_back=3, max_attempts=5)
    
    if success:
        print("\n" + "="*70)
        print("✅ API TEST PASSED - Data fetched successfully")
        print("="*70)
        
        # Test 2: Incremental search
        print("\n")
        success2, result2, days_used = test_with_incremental_days()
        
        if success2:
            print(f"\n✅ Found game using {days_used} days search window")
            
            # Test 3: Full flow
            print("\n")
            success3 = test_full_flow_with_3days()
            
            if success3:
                print("\n" + "="*70)
                print("🎉 ALL TESTS PASSED")
                print("="*70)
                print("✅ API fetches data correctly")
                print("✅ Response format is correct")
                print("✅ Full flow works end-to-end")
            else:
                print("\n⚠️  Full flow test had issues")
        else:
            print("\n⚠️  Incremental search test had issues")
    else:
        print("\n" + "="*70)
        print("❌ API TEST FAILED - No data fetched")
        print("="*70)
        print("Trying incremental search as fallback...")
        
        success2, result2, days_used = test_with_incremental_days()
        if success2:
            print(f"\n✅ Found game using {days_used} days (fallback worked)")

