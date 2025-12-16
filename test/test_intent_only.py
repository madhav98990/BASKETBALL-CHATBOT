#!/usr/bin/env python3
"""Test just the intent detection"""

from agents.intent_detection_agent import IntentDetectionAgent

agent = IntentDetectionAgent()

# Test query
query = "Give me Nikola Jokic's triple-double count for this season"
intent = agent.detect_intent(query)

print(f"Query: {query}")
print(f"Detected intent: {intent}")
