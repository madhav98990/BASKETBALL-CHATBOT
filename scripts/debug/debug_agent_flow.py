"""
Debug the full agent flow for "top 5 player points per game"
"""
import sys
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

print("=" * 70)
print("DEBUGGING: 'top 5 player points per game'")
print("=" * 70 + "\n")

# Step 1: Test Intent Detection
print("STEP 1: Testing Intent Detection...")
from agents.intent_detection_agent import IntentDetectionAgent

intent_agent = IntentDetectionAgent()
query = "top 5 player points per game"
intent = intent_agent.detect_intent(query)
print(f"Query: '{query}'")
print(f"Detected Intent: {intent}\n")

if intent != 'player_stats':
    print(f"❌ PROBLEM: Intent should be 'player_stats' but got '{intent}'")
    print("This means the query won't route to PlayerStatsAgent\n")
else:
    print("✅ Intent detection OK\n")

# Step 2: Test PlayerStatsAgent directly
print("STEP 2: Testing PlayerStatsAgent._handle_top_players_query()...")
from agents.player_stats_agent import PlayerStatsAgent

player_agent = PlayerStatsAgent()
result = player_agent._handle_top_players_query(query)

print(f"Result type: {type(result)}")
print(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
print(f"Has data: {bool(result.get('data') if isinstance(result, dict) else False)}")
print(f"Data length: {len(result.get('data', [])) if isinstance(result, dict) else 0}")
print(f"Has error: {bool(result.get('error') if isinstance(result, dict) else False)}")
if result.get('error'):
    print(f"Error message: {result.get('error')}")

if result.get('data'):
    print(f"\n✅ Got {len(result['data'])} players:")
    for i, player in enumerate(result['data'][:5], 1):
        print(f"  {i}. {player.get('player_name', 'Unknown')} - {player.get('stat_value', 0):.1f} PPG")
else:
    print("\n❌ PROBLEM: No data returned from _handle_top_players_query()")

print("\n" + "=" * 70)

# Step 3: Test full process_query
print("\nSTEP 3: Testing PlayerStatsAgent.process_query()...")
result2 = player_agent.process_query(query)
print(f"Result type: {type(result2)}")
print(f"Result keys: {result2.keys() if isinstance(result2, dict) else 'Not a dict'}")
print(f"Has data: {bool(result2.get('data') if isinstance(result2, dict) else False)}")
if result2.get('data'):
    print(f"Data length: {len(result2.get('data', []))}")
    print(f"First player: {result2['data'][0] if result2['data'] else 'None'}")

print("\n" + "=" * 70)

# Step 4: Test full chatbot flow
print("\nSTEP 4: Testing full BasketballChatbot.process_question()...")
from chatbot import BasketballChatbot

chatbot = BasketballChatbot()
response = chatbot.process_question(query)

print(f"\nResponse type: {type(response)}")
print(f"Response length: {len(response) if isinstance(response, str) else 'N/A'}")
print(f"\nResponse content:")
print("-" * 70)
print(response)
print("-" * 70)

if not response or len(response) < 50:
    print("\n❌ PROBLEM: Response is too short or empty")
elif "couldn't" in response.lower() or "unable" in response.lower() or "error" in response.lower():
    print("\n❌ PROBLEM: Response contains error message")
elif any(char.isdigit() for char in response) and any(name in response for name in ["Shai", "Giannis", "Jokić", "Edwards", "Tatum"]):
    print("\n✅ SUCCESS: Response contains player names and numbers!")
else:
    print("\n⚠️  WARNING: Response doesn't look like it has player data")

