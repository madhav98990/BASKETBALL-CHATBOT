"""
Test script to validate NBA schedule for today functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.intent_detection_agent import IntentDetectionAgent
from agents.schedule_agent import ScheduleAgent
from agents.response_formatter_agent import ResponseFormatterAgent
from chatbot import BasketballChatbot

def test_today_schedule():
    """Test that queries about today's NBA schedule work correctly"""
    
    print("=" * 60)
    print("Testing NBA Schedule for Today Functionality")
    print("=" * 60)
    
    # Test queries
    test_queries = [
        "nba schedule today",
        "nba schedules for today",
        "what games are on today",
        "show me today's nba games"
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
            
            if intent not in ['schedule', 'date_schedule']:
                print(f"⚠️  WARNING: Intent should be 'schedule' or 'date_schedule', got '{intent}'")
            else:
                print(f"✓ Intent detection correct")
            
            # Test schedule agent
            schedule_data = chatbot.schedule_agent.process_query(query)
            print(f"\nSchedule Data:")
            print(f"  Type: {schedule_data.get('type')}")
            print(f"  Source: {schedule_data.get('source')}")
            print(f"  Date: {schedule_data.get('date')}")
            print(f"  Games Found: {len(schedule_data.get('data', []))}")
            
            if schedule_data.get('data'):
                print(f"\n  Games:")
                for i, game in enumerate(schedule_data.get('data', [])[:5], 1):
                    team1 = game.get('team1_name', game.get('team1_display', 'Unknown'))
                    team2 = game.get('team2_name', game.get('team2_display', 'Unknown'))
                    status = game.get('status', 'unknown')
                    time = game.get('game_time', '')
                    print(f"    {i}. {team1} vs {team2} - {status}" + (f" at {time}" if time else ""))
            else:
                print(f"  ⚠️  No games found for today")
            
            # Test full chatbot response
            response = chatbot.process_question(query)
            print(f"\nFull Response:")
            print(f"  {response[:200]}..." if len(response) > 200 else f"  {response}")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("Test Complete")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_today_schedule()

