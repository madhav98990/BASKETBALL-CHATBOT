"""Full test of Thunder query through chatbot pipeline"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test through the full chatbot pipeline
from agents.intent_detection_agent import IntentDetectionAgent
from agents.standings_agent import StandingsAgent
from agents.response_formatter_agent import ResponseFormatterAgent

query = "Are the Oklahoma City Thunder still in the top 3 of the West?"
print("="*80)
print(f"Testing Query: {query}")
print("="*80)

# Step 1: Intent Detection
print("\n1. Intent Detection:")
intent_agent = IntentDetectionAgent()
intent_result = intent_agent.detect_intent(query)
print(f"   Intent: {intent_result.get('intent')}")
print(f"   Confidence: {intent_result.get('confidence')}")

# Step 2: Standings Agent
print("\n2. Standings Agent:")
if intent_result.get('intent') == 'standings':
    standings_agent = StandingsAgent()
    standings_result = standings_agent.process_query(query)
    
    if standings_result:
        print(f"   Type: {standings_result.get('type')}")
        print(f"   Team Position Query: {standings_result.get('team_position_query')}")
        print(f"   Data: {standings_result.get('data')}")
        print(f"   Error: {standings_result.get('error')}")
        
        if standings_result.get('team_position_query'):
            print(f"   ✓ Successfully processed")
            print(f"   Team: {standings_result.get('team')}")
            print(f"   Rank: {standings_result.get('actual_rank')}")
            print(f"   In Top 3: {standings_result.get('is_in_top')}")
            
            # Step 3: Response Formatter
            print("\n3. Response Formatter:")
            formatter = ResponseFormatterAgent()
            response = formatter.format_response(standings_result)
            print(f"   Response: {response}")
        else:
            print(f"   ✗ Not processed as team_position_query")
    else:
        print(f"   ✗ No result returned")
else:
    print(f"   ✗ Intent not detected as 'standings'")

