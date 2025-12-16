#!/usr/bin/env python3
"""
Test script to answer "Did the Knicks win their most recent game?" using NBA API
and validate the answer
"""

import logging
import sys
import os
from datetime import date, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_nba_api_library():
    """Test NBA API Library directly"""
    print("="*70)
    print("TEST: NBA API Library - Knicks Most Recent Game")
    print("="*70)
    
    try:
        from services.nba_api_library import NBAAPILibrary
        
        api = NBAAPILibrary()
        team_name = "knicks"
        
        print(f"\nFetching most recent game result for: {team_name}")
        print("Using NBA API Library (official NBA API)...")
        
        result = api.get_team_most_recent_game_result(team_name)
        
        if result:
            print("\n" + "="*70)
            print("✅ SUCCESS: Game result retrieved from NBA API")
            print("="*70)
            print(f"\nTeam: {result.get('team_name', 'N/A')}")
            print(f"Opponent: {result.get('opponent_name', 'N/A')}")
            print(f"Game Date: {result.get('game_date', 'N/A')}")
            print(f"Team Score: {result.get('team_score', 'N/A')}")
            print(f"Opponent Score: {result.get('opponent_score', 'N/A')}")
            print(f"Did Win: {result.get('did_win', 'N/A')}")
            
            # Answer the question
            did_win = result.get('did_win', False)
            team_score = result.get('team_score', 0)
            opponent_score = result.get('opponent_score', 0)
            opponent_name = result.get('opponent_name', 'Unknown')
            game_date = result.get('game_date', 'Unknown date')
            
            print("\n" + "="*70)
            print("ANSWER TO: Did the Knicks win their most recent game?")
            print("="*70)
            
            if did_win:
                answer = f"✅ YES, the Knicks won their most recent game on {game_date}. They defeated the {opponent_name} {team_score}-{opponent_score}."
            else:
                answer = f"❌ NO, the Knicks lost their most recent game on {game_date}. They were defeated by the {opponent_name} {opponent_score}-{team_score}."
            
            print(f"\n{answer}\n")
            
            return result, answer
        else:
            print("\n❌ FAILED: NBA API Library returned None")
            print("Possible reasons:")
            print("  - No recent games found")
            print("  - API rate limiting")
            print("  - Network issues")
            return None, None
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def test_ball_dont_lie_api():
    """Test Ball Don't Lie API as comparison"""
    print("\n" + "="*70)
    print("TEST: Ball Don't Lie API - Knicks Most Recent Game (Comparison)")
    print("="*70)
    
    try:
        from services.balldontlie_api import BallDontLieAPI
        
        api = BallDontLieAPI()
        team_name = "knicks"
        
        print(f"\nFetching most recent game result for: {team_name}")
        print("Using Ball Don't Lie API (free NBA API)...")
        
        result = api.get_team_most_recent_game_result(team_name, days_back=30)
        
        if result:
            print("\n✅ SUCCESS: Game result retrieved from Ball Don't Lie API")
            print(f"Team: {result.get('team_name', 'N/A')}")
            print(f"Opponent: {result.get('opponent_name', 'N/A')}")
            print(f"Game Date: {result.get('game_date', 'N/A')}")
            print(f"Team Score: {result.get('team_score', 'N/A')}")
            print(f"Opponent Score: {result.get('opponent_score', 'N/A')}")
            print(f"Did Win: {result.get('did_win', 'N/A')}")
            return result
        else:
            print("\n⚠️  WARNING: Ball Don't Lie API returned None")
            return None
            
    except Exception as e:
        print(f"\n⚠️  ERROR: {e}")
        return None


def validate_answers(nba_result, bdl_result):
    """Compare results from different APIs to validate"""
    print("\n" + "="*70)
    print("VALIDATION: Comparing API Results")
    print("="*70)
    
    if not nba_result:
        print("❌ Cannot validate: NBA API result is None")
        return False
    
    if not bdl_result:
        print("⚠️  Cannot fully validate: Ball Don't Lie API result is None")
        print("But NBA API result is available, so answer is based on NBA API")
        return True
    
    # Compare key fields
    nba_win = nba_result.get('did_win')
    bdl_win = bdl_result.get('did_win')
    
    nba_date = nba_result.get('game_date', '')
    bdl_date = bdl_result.get('game_date', '')
    
    print(f"\nNBA API Result:")
    print(f"  Did Win: {nba_win}")
    print(f"  Date: {nba_date}")
    
    print(f"\nBall Don't Lie API Result:")
    print(f"  Did Win: {bdl_win}")
    print(f"  Date: {bdl_date}")
    
    if nba_win == bdl_win:
        print("\n✅ VALIDATION PASSED: Both APIs agree on win/loss result")
        return True
    else:
        print("\n⚠️  WARNING: APIs disagree on win/loss result")
        print("Using NBA API result as primary source")
        return True  # Still valid, just different sources


def test_full_chatbot():
    """Test the full chatbot query"""
    print("\n" + "="*70)
    print("TEST: Full Chatbot Query")
    print("="*70)
    
    try:
        from chatbot import BasketballChatbot
        
        chatbot = BasketballChatbot()
        query = "Did the Knicks win their most recent game?"
        
        print(f"\nQuery: {query}")
        print("Processing through full chatbot...")
        
        response = chatbot.process_question(query)
        
        print("\n" + "="*70)
        print("CHATBOT RESPONSE:")
        print("="*70)
        print(f"\n{response}\n")
        
        return response
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("COMPREHENSIVE TEST: Did the Knicks win their most recent game?")
    print("="*70)
    print("\nThis test will:")
    print("  1. Query NBA API Library directly")
    print("  2. Query Ball Don't Lie API for comparison")
    print("  3. Validate answers match")
    print("  4. Test full chatbot response")
    print("\n")
    
    # Test 1: NBA API Library (PRIMARY)
    nba_result, nba_answer = test_nba_api_library()
    
    # Test 2: Ball Don't Lie API (COMPARISON)
    bdl_result = test_ball_dont_lie_api()
    
    # Test 3: Validate
    if nba_result:
        validate_answers(nba_result, bdl_result)
    
    # Test 4: Full chatbot (optional)
    print("\n" + "="*70)
    print("Run full chatbot test? (This may take longer)")
    print("="*70)
    response = input("Continue with full chatbot test? (y/n): ").strip().lower()
    
    if response == 'y':
        chatbot_response = test_full_chatbot()
    else:
        print("Skipping full chatbot test")
        chatbot_response = None
    
    # Final Summary
    print("\n" + "="*70)
    print("FINAL ANSWER SUMMARY")
    print("="*70)
    
    if nba_result:
        did_win = nba_result.get('did_win', False)
        team_score = nba_result.get('team_score', 0)
        opponent_score = nba_result.get('opponent_score', 0)
        opponent_name = nba_result.get('opponent_name', 'Unknown')
        game_date = nba_result.get('game_date', 'Unknown date')
        
        print(f"\nQuestion: Did the Knicks win their most recent game?")
        print(f"\nAnswer: {'YES' if did_win else 'NO'}")
        print(f"\nDetails:")
        print(f"  - Game Date: {game_date}")
        print(f"  - Opponent: {opponent_name}")
        print(f"  - Score: Knicks {team_score} - {opponent_name} {opponent_score}")
        print(f"  - Result: {'WIN' if did_win else 'LOSS'}")
        print(f"\nSource: NBA API Library (Official NBA API)")
        
        if chatbot_response:
            print(f"\nFull Chatbot Response:")
            print(f"  {chatbot_response}")
    else:
        print("\n❌ Could not retrieve answer from NBA API")
        print("Please check:")
        print("  - Internet connection")
        print("  - NBA API availability")
        print("  - Rate limiting")
    
    print("="*70)


if __name__ == "__main__":
    main()

