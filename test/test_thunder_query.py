"""Test the Thunder query directly"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.standings_agent import StandingsAgent

query = "Are the Oklahoma City Thunder still in the top 3 of the West?"
print(f"Testing query: {query}\n")

agent = StandingsAgent()

# Test extraction
team_position_info = agent._extract_team_position_query(query)
print(f"Extracted info: {team_position_info}\n")

# Test full processing
result = agent.process_query(query)
print(f"Result: {result}")

if result:
    if result.get('team_position_query'):
        print(f"\n✓ Processed as team_position_query")
        print(f"Team: {result.get('team')}")
        print(f"Actual Rank: {result.get('actual_rank')}")
        print(f"Target Position: {result.get('target_position')}")
        print(f"Is in Top 3: {result.get('is_in_top')}")
        print(f"Conference: {result.get('conference')}")
        print(f"Source: {result.get('source')}")
    else:
        print(f"\n✗ Not processed as team_position_query")
        print(f"Type: {result.get('type')}")
        print(f"Error: {result.get('error')}")

