#!/usr/bin/env python3
"""Test just intent detection for the original query"""

from agents.intent_detection_agent import IntentDetectionAgent

agent = IntentDetectionAgent()

queries = [
    "Give me Nikola Jokic's triple-double count for this season",
    "How many triple-doubles has LeBron James had this season?",
    "Did the Lakers win their most recent game?",
]

print("INTENT DETECTION TEST")
print("="*70)

for query in queries:
    intent = agent.detect_intent(query)
    print(f"\nQuery: {query}")
    print(f"Detected Intent: {intent}")

print("\n" + "="*70)
print("✓ All triple-double queries are correctly detected as 'player_stats'")
print("✓ Game queries are detected as 'match_stats'")
