"""Test specific queries"""
from agents.schedule_agent import ScheduleAgent
from agents.stats_agent import StatsAgent
from datetime import date, timedelta

print("Testing Queries...")
print("=" * 60)

# Test Schedule Agent
print("\n1. Testing 'NBA schedule' query:")
schedule_agent = ScheduleAgent()
result = schedule_agent.process_query("NBA schedule")
print(f"   Type: {result.get('type')}")
print(f"   Data count: {len(result.get('data', []))}")
data = result.get('data', [])
if data:
    print(f"   First match: {data[0].get('team1_name')} vs {data[0].get('team2_name')} on {data[0].get('match_date')}")
else:
    print("   No data returned!")

# Test Stats Agent - Yesterday
print("\n2. Testing 'Result of yesterday games' query:")
stats_agent = StatsAgent()
yesterday = date.today() - timedelta(days=1)
print(f"   Yesterday date: {yesterday}")
result = stats_agent.process_query("Result of yesterday games")
print(f"   Type: {result.get('type')}")
print(f"   Data count: {len(result.get('data', []))}")
print(f"   Date extracted: {result.get('date')}")
data = result.get('data', [])
if data:
    print(f"   First match: {data[0].get('team1_name')} vs {data[0].get('team2_name')} on {data[0].get('match_date')}")
else:
    print("   No data returned!")
    # Check if there are any matches in the database
    all_matches = stats_agent.get_recent_matches(limit=5)
    print(f"   Recent matches in DB: {len(all_matches)}")
    if all_matches:
        print(f"   Most recent match date: {all_matches[0].get('match_date')}")

print("\n" + "=" * 60)

