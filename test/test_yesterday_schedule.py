"""
Test script to validate NBA schedule for yesterday functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.intent_detection_agent import IntentDetectionAgent
from agents.schedule_agent import ScheduleAgent
from chatbot import BasketballChatbot

def test_yesterday_schedule():
    """Test that queries about yesterday's NBA schedule work correctly"""
    
    print("=" * 60)
    print("Testing NBA Schedule for Yesterday Functionality")
    print("=" * 60)
    
    # Test queries
    test_queries = [
        "nba schedule yesterday",
        "nba schedules for yesterday",
        "what games were on yesterday",
        "show me yesterday's nba games"
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
                for i, game in enumerate(schedule_data.get('data', [])[:10], 1):
                    team1 = game.get('team1_name', game.get('team1_display', 'Unknown'))
                    team2 = game.get('team2_name', game.get('team2_display', 'Unknown'))
                    status = game.get('status', 'unknown')
                    team1_score = game.get('team1_score')
                    team2_score = game.get('team2_score')
                    
                    if status == 'completed' and team1_score is not None and team2_score is not None:
                        print(f"    {i}. {team1} vs {team2}: {team1_score}-{team2_score} (Final)")
                    else:
                        print(f"    {i}. {team1} vs {team2} - {status}")
            else:
                print(f"  ⚠️  No games found for yesterday")
            
            # Test full chatbot response
            response = chatbot.process_question(query)
            print(f"\nFull Response:")
            print(f"  {response[:300]}..." if len(response) > 300 else f"  {response}")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("Test Complete")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_yesterday_schedule()

