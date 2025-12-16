"""Direct test of the query"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.standings_agent import StandingsAgent
from agents.response_formatter_agent import ResponseFormatterAgent

query = "Are the Oklahoma City Thunder still in the top 3 of the West?"
print("="*70)
print(f"Query: {query}")
print("="*70)

agent = StandingsAgent()
formatter = ResponseFormatterAgent()

# Test extraction first
print("\n1. Testing team extraction:")
team_info = agent._extract_team_position_query(query)
print(f"   Extracted: {team_info}")

if team_info:
    print(f"\n2. Processing query:")
    result = agent.process_query(query)
    
    if result and result.get('team_position_query'):
        print(f"   ✓ Processed successfully")
        print(f"   Team: {result.get('team')}")
        print(f"   Actual Rank: {result.get('actual_rank')}")
        print(f"   Target Position: Top {result.get('target_position')}")
        print(f"   Is in Top 3: {result.get('is_in_top')}")
        print(f"   Conference: {result.get('conference')}")
        print(f"   Record: {result.get('wins')}-{result.get('losses')}")
        print(f"   Source: {result.get('source')}")
        
        print(f"\n3. Formatting response:")
        response = formatter.format_response(result)
        print(f"   {response}")
    else:
        print(f"   ✗ Failed to process")
        print(f"   Type: {result.get('type') if result else 'None'}")
        print(f"   Error: {result.get('error') if result else 'No result'}")
else:
    print("   ✗ Failed to extract team info")

