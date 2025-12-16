"""Test script for real-time agents"""
from agents.live_game_agent import LiveGameAgent
from agents.standings_agent import StandingsAgent
from agents.injury_report_agent import InjuryReportAgent
from agents.intent_detection_agent import IntentDetectionAgent

print("Testing Real-Time Agents...")
print("=" * 60)

# Test Intent Detection
print("\n1. Testing Intent Detection:")
intent_agent = IntentDetectionAgent()
test_questions = [
    "What games are live right now?",
    "Show me the Eastern Conference standings",
    "Who's injured on the Lakers?",
    "What are LeBron James' season averages?"
]

for q in test_questions:
    intent = intent_agent.detect_intent(q)
    print(f"   Q: {q}")
    print(f"   Intent: {intent}")

# Test Live Game Agent
print("\n2. Testing Live Game Agent:")
live_agent = LiveGameAgent()
live_games = live_agent.get_live_games()
print(f"   Live games found: {len(live_games)}")
for game in live_games[:3]:
    print(f"   {game.get('team1_name')} vs {game.get('team2_name')} - {game.get('game_status')}")

# Test Standings Agent
print("\n3. Testing Standings Agent:")
standings_agent = StandingsAgent()
east_standings = standings_agent.get_conference_standings('East')
print(f"   Eastern Conference standings: {len(east_standings)}")
for standing in east_standings[:5]:
    print(f"   {standing.get('team_name')}: {standing.get('wins')}-{standing.get('losses')} (Rank: {standing.get('conference_rank')})")

# Test Injury Agent
print("\n4. Testing Injury Agent:")
injury_agent = InjuryReportAgent()
lakers_injuries = injury_agent.get_team_injuries('Lakers')
print(f"   Lakers injuries: {len(lakers_injuries)}")
for injury in lakers_injuries[:3]:
    print(f"   {injury.get('player_name')}: {injury.get('injury_type')} - {injury.get('status')}")

# Test process_query methods
print("\n5. Testing process_query methods:")
print("\n   Standings query:")
standings_result = standings_agent.process_query("Show me the Eastern Conference standings")
print(f"   Type: {standings_result.get('type')}")
print(f"   Data count: {len(standings_result.get('data', []))}")
print(f"   Conference: {standings_result.get('conference')}")

print("\n   Injury query:")
injury_result = injury_agent.process_query("Who's injured on the Lakers?")
print(f"   Type: {injury_result.get('type')}")
print(f"   Data count: {len(injury_result.get('data', []))}")
print(f"   Team: {injury_result.get('team')}")

print("\n   Live game query:")
live_result = live_agent.process_query("What games are live right now?")
print(f"   Type: {live_result.get('type')}")
print(f"   Data count: {len(live_result.get('data', []))}")

print("\n" + "=" * 60)
print("Test complete!")

