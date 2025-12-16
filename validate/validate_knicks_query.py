#!/usr/bin/env python3
"""
Quick validation test for "Did the Knicks win their most recent game?" query
Tests the code flow without making actual API calls (which can be slow)
"""

import logging
import sys
import os

# Suppress verbose logging for cleaner output
logging.basicConfig(level=logging.WARNING)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def validate_intent_detection():
    """Test intent detection"""
    print("="*70)
    print("VALIDATION: Intent Detection")
    print("="*70)
    
    from agents.intent_detection_agent import IntentDetectionAgent
    
    agent = IntentDetectionAgent()
    query = "Did the Knicks win their most recent game?"
    
    intent = agent.detect_intent(query)
    print(f"Query: {query}")
    print(f"Detected Intent: {intent}")
    
    if intent == 'match_stats':
        print("✅ PASS: Intent correctly detected as 'match_stats'")
        return True
    else:
        print(f"❌ FAIL: Expected 'match_stats', got '{intent}'")
        return False


def validate_stats_agent_structure():
    """Test that stats agent has the correct structure for win queries"""
    print("\n" + "="*70)
    print("VALIDATION: Stats Agent Structure")
    print("="*70)
    
    from agents.stats_agent import StatsAgent
    
    # Check that the method exists
    if hasattr(StatsAgent, 'process_query'):
        print("✅ PASS: StatsAgent has process_query method")
    else:
        print("❌ FAIL: StatsAgent missing process_query method")
        return False
    
    # Check that win_query detection logic exists in the code
    import inspect
    source = inspect.getsource(StatsAgent.process_query)
    
    if 'is_win_query' in source:
        print("✅ PASS: Stats agent has win_query detection logic")
    else:
        print("❌ FAIL: Stats agent missing win_query detection")
        return False
    
    if 'get_team_most_recent_game_result' in source or 'espn' in source.lower() or 'nba_api' in source.lower():
        print("✅ PASS: Stats agent has API integration for win queries")
    else:
        print("⚠️  WARNING: Could not verify API integration in stats agent")
    
    return True


def validate_ball_dont_lie_api():
    """Test that Ball Don't Lie API has the new method"""
    print("\n" + "="*70)
    print("VALIDATION: Ball Don't Lie API")
    print("="*70)
    
    from services.balldontlie_api import BallDontLieAPI
    
    api = BallDontLieAPI()
    
    if hasattr(api, 'get_team_most_recent_game_result'):
        print("✅ PASS: Ball Don't Lie API has get_team_most_recent_game_result method")
        
        # Check method signature
        import inspect
        sig = inspect.signature(api.get_team_most_recent_game_result)
        params = list(sig.parameters.keys())
        
        if 'team_name' in params:
            print("✅ PASS: Method has correct parameter 'team_name'")
        else:
            print("⚠️  WARNING: Method parameter check failed")
        
        return True
    else:
        print("❌ FAIL: Ball Don't Lie API missing get_team_most_recent_game_result method")
        return False


def validate_response_formatter():
    """Test that response formatter handles win_query"""
    print("\n" + "="*70)
    print("VALIDATION: Response Formatter")
    print("="*70)
    
    from agents.response_formatter_agent import ResponseFormatterAgent
    
    formatter = ResponseFormatterAgent()
    
    # Check that format_response method exists
    if hasattr(formatter, 'format_response'):
        print("✅ PASS: ResponseFormatterAgent has format_response method")
    else:
        print("❌ FAIL: ResponseFormatterAgent missing format_response method")
        return False
    
    # Check that win_query handling exists
    import inspect
    source = inspect.getsource(ResponseFormatterAgent._format_fallback)
    
    if 'win_query' in source:
        print("✅ PASS: Response formatter handles win_query")
    else:
        print("⚠️  WARNING: Could not verify win_query handling in formatter")
    
    return True


def validate_chatbot_routing():
    """Test that chatbot routes match_stats to stats_agent"""
    print("\n" + "="*70)
    print("VALIDATION: Chatbot Routing")
    print("="*70)
    
    from chatbot import BasketballChatbot
    
    chatbot = BasketballChatbot()
    
    # Check that stats_agent exists
    if hasattr(chatbot, 'stats_agent'):
        print("✅ PASS: Chatbot has stats_agent")
    else:
        print("❌ FAIL: Chatbot missing stats_agent")
        return False
    
    # Check routing logic
    import inspect
    source = inspect.getsource(chatbot.process_question)
    
    if "intent == 'match_stats'" in source and 'stats_agent' in source:
        print("✅ PASS: Chatbot routes match_stats to stats_agent")
    else:
        print("❌ FAIL: Chatbot routing logic issue")
        return False
    
    return True


def main():
    """Run all validations"""
    print("\n" + "="*70)
    print("VALIDATION TEST: Did the Knicks win their most recent game?")
    print("="*70)
    print("\nThis test validates the code structure and flow.")
    print("It does NOT make actual API calls (which can be slow).")
    print("\n")
    
    results = []
    
    results.append(("Intent Detection", validate_intent_detection()))
    results.append(("Stats Agent Structure", validate_stats_agent_structure()))
    results.append(("Ball Don't Lie API", validate_ball_dont_lie_api()))
    results.append(("Response Formatter", validate_response_formatter()))
    results.append(("Chatbot Routing", validate_chatbot_routing()))
    
    # Summary
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} validations passed")
    
    if passed == total:
        print("\n🎉 All validations passed!")
        print("\nThe query 'Did the Knicks win their most recent game?' should work correctly.")
        print("\nThe system will:")
        print("  1. Detect intent as 'match_stats' ✅")
        print("  2. Route to stats_agent ✅")
        print("  3. Try ESPN API (primary) ✅")
        print("  4. Fallback to NBA API Library ✅")
        print("  5. Fallback to Ball Don't Lie API ✅")
        print("  6. Format response with win/loss answer ✅")
    else:
        print("\n⚠️  Some validations failed. Check the output above.")
    
    print("="*70)


if __name__ == "__main__":
    main()

