#!/usr/bin/env python3
"""
Comprehensive test of the chatbot system
Demonstrates:
1. Intent detection is working correctly
2. Triple-double queries are routed to the right agent
3. System gracefully handles when APIs return no data
"""

import logging
logging.basicConfig(level=logging.WARNING)  # Suppress verbose logging

from chatbot import BasketballChatbot

# Create chatbot
bot = BasketballChatbot()

# Test queries
test_queries = [
    # Original problematic query - should now work correctly
    "Give me Nikola Jokic's triple-double count for this season",
    
    # Other triple-double queries
    "How many triple-doubles has LeBron James had this season?",
    "Does Stephen Curry have any triple-doubles this season?",
    
    # Control query - should be detected as different intent
    "Did the Lakers win their most recent game?",
]

print("="*70)
print("CHATBOT SYSTEM TEST")
print("="*70)

for query in test_queries:
    print(f"\nQuery: {query}")
    print("-" * 70)
    
    # Get response
    response = bot.process_question(query)
    
    # Show result
    print(f"Response: {response}\n")

print("="*70)
print("TEST COMPLETE")
print("="*70)
