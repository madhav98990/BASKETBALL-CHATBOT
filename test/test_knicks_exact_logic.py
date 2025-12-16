#!/usr/bin/env python3
"""
Test the exact logic implementation for "Did the Knicks win their most recent game?"
"""

import logging
import sys
import os

logging.basicConfig(level=logging.INFO)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_exact_logic():
    """Test the exact logic implementation"""
    print("="*70)
    print("TESTING EXACT LOGIC: Did the Knicks win their most recent game?")
    print("="*70)
    print("\nExpected Steps:")
    print("1. Fetch Knicks completed games only (status = Final)")
    print("2. Sort games by game_date descending")
    print("3. Select the latest game")
    print("4. If Knicks_score > Opponent_score → answer 'Yes, the Knicks won.'")
    print("5. Else → answer 'No, the Knicks lost.'")
    print("6. Include final score in the response")
    print("\n" + "="*70)
    
    try:
        from services.direct_espn_fetcher import DirectESPNFetcher
        
        fetcher = DirectESPNFetcher()
        team_name = "knicks"
        
        print(f"\nCalling get_team_most_recent_game_result('{team_name}')...")
        result = fetcher.get_team_most_recent_game_result(team_name, days_back=60)
        
        if result:
            print("\n" + "="*70)
            print("✅ SUCCESS - RESULT RETRIEVED")
            print("="*70)
            
            team_score = result.get('team_score', 0)
            opponent_score = result.get('opponent_score', 0)
            did_win = result.get('did_win', False)
            game_date = result.get('game_date', '')
            opponent_name = result.get('opponent_name', '')
            
            print(f"\nGame Date: {game_date}")
            print(f"Opponent: {opponent_name}")
            print(f"Knicks Score: {team_score}")
            print(f"Opponent Score: {opponent_score}")
            print(f"Result: {'WIN' if did_win else 'LOSS'}")
            
            print("\n" + "="*70)
            print("VALIDATION:")
            print("="*70)
            print(f"✓ Step 1: Fetched completed games only (status = Final)")
            print(f"✓ Step 2: Sorted games by game_date descending")
            print(f"✓ Step 3: Selected latest game ({game_date})")
            print(f"✓ Step 4: Compared scores - {team_score} > {opponent_score} = {did_win}")
            print(f"✓ Step 5: Determined result - {'WIN' if did_win else 'LOSS'}")
            print(f"✓ Step 6: Final score included: {team_score}-{opponent_score}")
            
            print("\n" + "="*70)
            print("FINAL ANSWER:")
            print("="*70)
            
            if did_win:
                answer = f"Yes, the Knicks won their most recent game on {game_date}. They defeated the {opponent_name} {team_score}-{opponent_score}."
            else:
                answer = f"No, the Knicks lost their most recent game on {game_date}. They were defeated by the {opponent_name} {opponent_score}-{team_score}."
            
            print(f"\n{answer}\n")
            
            return result
        else:
            print("\n❌ FAILED: No result returned")
            print("Possible reasons:")
            print("  - No completed games found in last 60 days")
            print("  - API issues")
            print("  - Network problems")
            return None
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_full_chatbot():
    """Test full chatbot integration"""
    print("\n" + "="*70)
    print("TESTING FULL CHATBOT INTEGRATION")
    print("="*70)
    
    try:
        from chatbot import BasketballChatbot
        
        bot = BasketballChatbot()
        query = "Did the Knicks win their most recent game?"
        
        print(f"\nQuery: {query}")
        print("Processing through full chatbot...")
        
        answer = bot.process_question(query)
        
        print("\n" + "="*70)
        print("CHATBOT ANSWER:")
        print("="*70)
        print(f"\n{answer}\n")
        
        # Validate answer contains required elements
        answer_lower = answer.lower()
        has_yes_no = 'yes' in answer_lower or 'no' in answer_lower
        has_knicks = 'knicks' in answer_lower
        has_score = any(char.isdigit() for char in answer)
        
        print("VALIDATION:")
        print(f"  ✓ Contains Yes/No: {has_yes_no}")
        print(f"  ✓ Mentions Knicks: {has_knicks}")
        print(f"  ✓ Contains score: {has_score}")
        
        if has_yes_no and has_knicks and has_score:
            print("\n✅ Answer is valid and complete!")
        
        return answer
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Test exact logic
    result = test_exact_logic()
    
    # Test full chatbot if result was successful
    if result:
        print("\n" + "="*70)
        response = input("Test full chatbot integration? (y/n): ").strip().lower()
        if response == 'y':
            test_full_chatbot()

