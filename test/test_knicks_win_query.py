#!/usr/bin/env python3
"""
Test script to validate "Did the Knicks win their most recent game?" query
Tests the complete flow: intent detection -> stats agent -> API calls -> response formatting
"""

import logging
import sys
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_intent_detection():
    """Test that intent detection correctly identifies the query"""
    print("\n" + "="*70)
    print("TEST 1: Intent Detection")
    print("="*70)
    
    try:
        from agents.intent_detection_agent import IntentDetectionAgent
        
        intent_agent = IntentDetectionAgent()
        query = "Did the Knicks win their most recent game?"
        
        intent = intent_agent.detect_intent(query)
        print(f"Query: {query}")
        print(f"Detected Intent: {intent}")
        
        if intent == 'match_stats':
            print("✅ PASS: Intent correctly detected as 'match_stats'")
            return True
        else:
            print(f"❌ FAIL: Expected 'match_stats', got '{intent}'")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_stats_agent_win_query():
    """Test that stats agent correctly processes the win query"""
    print("\n" + "="*70)
    print("TEST 2: Stats Agent - Win Query Processing")
    print("="*70)
    
    try:
        from agents.stats_agent import StatsAgent
        
        stats_agent = StatsAgent()
        query = "Did the Knicks win their most recent game?"
        
        print(f"Query: {query}")
        print("Processing query through stats agent...")
        
        result = stats_agent.process_query(query)
        
        print(f"\nResult type: {result.get('type')}")
        print(f"Win query flag: {result.get('win_query')}")
        print(f"Team: {result.get('team')}")
        print(f"Source: {result.get('source')}")
        
        if result.get('type') == 'match_stats' and result.get('win_query'):
            print("✅ PASS: Stats agent correctly identified as win_query")
            
            if result.get('data') and len(result.get('data', [])) > 0:
                game_result = result['data'][0]
                print(f"\nGame Result Data:")
                print(f"  - Team: {game_result.get('team_name', 'N/A')}")
                print(f"  - Did Win: {game_result.get('did_win', 'N/A')}")
                print(f"  - Team Score: {game_result.get('team_score', 'N/A')}")
                print(f"  - Opponent Score: {game_result.get('opponent_score', 'N/A')}")
                print(f"  - Opponent: {game_result.get('opponent_name', 'N/A')}")
                print(f"  - Game Date: {game_result.get('game_date', 'N/A')}")
                print("✅ PASS: Game result data retrieved successfully")
                return True
            else:
                print("⚠️  WARNING: No game data returned (API may be unavailable)")
                if result.get('error'):
                    print(f"  Error: {result.get('error')}")
                return False
        else:
            print(f"❌ FAIL: Expected win_query=True, got {result}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ball_dont_lie_api():
    """Test Ball Don't Lie API directly"""
    print("\n" + "="*70)
    print("TEST 3: Ball Don't Lie API - Direct Test")
    print("="*70)
    
    try:
        from services.balldontlie_api import BallDontLieAPI
        
        api = BallDontLieAPI()
        team_name = "knicks"
        
        print(f"Testing get_team_most_recent_game_result for: {team_name}")
        result = api.get_team_most_recent_game_result(team_name, days_back=30)
        
        if result:
            print("✅ PASS: Ball Don't Lie API returned game result")
            print(f"  - Team: {result.get('team_name')}")
            print(f"  - Did Win: {result.get('did_win')}")
            print(f"  - Score: {result.get('team_score')} - {result.get('opponent_score')}")
            print(f"  - Opponent: {result.get('opponent_name')}")
            print(f"  - Date: {result.get('game_date')}")
            return True
        else:
            print("⚠️  WARNING: Ball Don't Lie API returned None (may be no recent games)")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_chatbot_query():
    """Test the complete chatbot flow"""
    print("\n" + "="*70)
    print("TEST 4: Full Chatbot Query Processing")
    print("="*70)
    
    try:
        from chatbot import BasketballChatbot
        
        chatbot = BasketballChatbot()
        query = "Did the Knicks win their most recent game?"
        
        print(f"Query: {query}")
        print("Processing through full chatbot pipeline...")
        print("(This may take a moment as it calls APIs and LLM)")
        
        response = chatbot.process_question(query)
        
        print(f"\nResponse: {response}")
        
        # Validate response contains expected information
        response_lower = response.lower()
        has_knicks = 'knicks' in response_lower or 'new york' in response_lower
        has_win_info = any(word in response_lower for word in ['yes', 'no', 'won', 'lost', 'defeated', 'beat'])
        has_score = any(char.isdigit() for char in response)
        
        print(f"\nResponse Validation:")
        print(f"  - Mentions Knicks: {has_knicks}")
        print(f"  - Has win/loss info: {has_win_info}")
        print(f"  - Has score/numbers: {has_score}")
        
        if has_knicks and has_win_info:
            print("✅ PASS: Response contains expected information")
            return True
        else:
            print("⚠️  WARNING: Response may be incomplete")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all validation tests"""
    print("\n" + "="*70)
    print("VALIDATION TEST: Did the Knicks win their most recent game?")
    print("="*70)
    
    results = []
    
    # Test 1: Intent Detection
    results.append(("Intent Detection", test_intent_detection()))
    
    # Test 2: Stats Agent
    results.append(("Stats Agent", test_stats_agent_win_query()))
    
    # Test 3: Ball Don't Lie API
    results.append(("Ball Don't Lie API", test_ball_dont_lie_api()))
    
    # Test 4: Full Chatbot (optional - may take longer)
    print("\n" + "="*70)
    print("Run full chatbot test? (This will call APIs and may take time)")
    print("="*70)
    response = input("Continue with full chatbot test? (y/n): ").strip().lower()
    
    if response == 'y':
        results.append(("Full Chatbot", test_full_chatbot_query()))
    else:
        print("Skipping full chatbot test")
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The query should work correctly.")
    else:
        print("\n⚠️  Some tests failed or returned warnings. Check the output above.")
    
    print("="*70)


if __name__ == "__main__":
    main()

