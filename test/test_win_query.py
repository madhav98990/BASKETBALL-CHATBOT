"""
Test script to validate "Did the Knicks win their most recent game?" query
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot import BasketballChatbot

def test_win_query():
    """Test that 'did team win' queries work correctly"""
    
    print("=" * 60)
    print("Testing 'Did the Knicks win their most recent game?' Query")
    print("=" * 60)
    
    # Test queries
    test_queries = [
        "Did the Knicks win their most recent game?",
        "Did the Knicks win their last game?",
        "Did the Lakers win their most recent game?",
        "Did the Warriors win their last game?"
    ]
    
    chatbot = BasketballChatbot()
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        
        try:
            # Test intent detection
            intent = chatbot.intent_agent.detect_intent(query)
            print(f"Detected Intent: {intent}")
            
            # Test stats agent
            stats_data = chatbot.stats_agent.process_query(query)
            print(f"\nStats Data:")
            print(f"  Type: {stats_data.get('type')}")
            print(f"  Source: {stats_data.get('source')}")
            print(f"  Team: {stats_data.get('team')}")
            print(f"  Did Win: {stats_data.get('did_win')}")
            print(f"  Team Score: {stats_data.get('team_score')}")
            print(f"  Opponent Score: {stats_data.get('opponent_score')}")
            print(f"  Opponent: {stats_data.get('opponent_name')}")
            print(f"  Game Date: {stats_data.get('game_date')}")
            
            # Test full chatbot response
            response = chatbot.process_question(query)
            print(f"\nFull Response:")
            print(f"  {response}")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("Test Complete")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_win_query()


