"""Test intent detection for Thunder query"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.intent_detection_agent import IntentDetectionAgent
from agents.standings_agent import StandingsAgent
from agents.response_formatter_agent import ResponseFormatterAgent

query = "Are the Oklahoma City Thunder still in the top 3 of the West?"
print("="*80)
print(f"Query: {query}")
print("="*80)

# Test intent detection
print("\n1. Intent Detection:")
intent_agent = IntentDetectionAgent()
intent = intent_agent.detect_intent(query)
print(f"   Detected Intent: {intent}")

if intent == 'standings':
    print("   ✓ Correctly detected as 'standings'")
    
    print("\n2. Standings Agent:")
    standings_agent = StandingsAgent()
    result = standings_agent.process_query(query)
    
    if result and result.get('team_position_query'):
        print(f"   ✓ Processed successfully")
        print(f"   Team: {result.get('team')}")
        print(f"   Rank: {result.get('actual_rank')}")
        print(f"   In Top 3: {result.get('is_in_top')}")
        print(f"   Record: {result.get('wins')}-{result.get('losses')}")
        
        print("\n3. Response Formatter:")
        formatter = ResponseFormatterAgent()
        response = formatter.format_response(result)
        print(f"   Response: {response}")
    else:
        print(f"   ✗ Failed to process")
        print(f"   Result: {result}")
else:
    print(f"   ✗ Incorrectly detected as '{intent}' instead of 'standings'")

