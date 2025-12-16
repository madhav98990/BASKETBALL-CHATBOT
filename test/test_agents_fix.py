"""Test script to verify agents are returning correct data"""
from agents.stats_agent import StatsAgent
from agents.schedule_agent import ScheduleAgent
from agents.player_stats_agent import PlayerStatsAgent
from agents.response_formatter_agent import ResponseFormatterAgent

print("Testing Agents...")
print("=" * 60)

# Test Stats Agent
print("\n1. Testing Stats Agent:")
stats_agent = StatsAgent()
result = stats_agent.process_query("What was the score in the Lakers vs Warriors match?")
print(f"   Type: {result.get('type')}")
print(f"   Data count: {len(result.get('data', []))}")
data = result.get('data', [])
if data:
    match = data[0]
    print(f"   Sample: {match.get('team1_name')} vs {match.get('team2_name')}: {match.get('team1_score')}-{match.get('team2_score')} on {match.get('match_date')}")

# Test Schedule Agent
print("\n2. Testing Schedule Agent:")
schedule_agent = ScheduleAgent()
result = schedule_agent.process_query("When is the next Lakers game?")
print(f"   Type: {result.get('type')}")
print(f"   Data count: {len(result.get('data', []))}")
data = result.get('data', [])
if data:
    match = data[0]
    print(f"   Sample: {match.get('team1_name')} vs {match.get('team2_name')} on {match.get('match_date')} at {match.get('venue')}")

# Test Response Formatter
print("\n3. Testing Response Formatter:")
formatter = ResponseFormatterAgent()
stats_result = stats_agent.process_query("What was the score in the Lakers vs Warriors match?")
response = formatter.format_response(stats_result)
print(f"   Response: {response}")

schedule_result = schedule_agent.process_query("When is the next Lakers game?")
response = formatter.format_response(schedule_result)
print(f"   Response: {response}")

print("\n" + "=" * 60)
print("Test complete!")

