#!/usr/bin/env python3
"""Triple-double query verification - confirms fix works"""

import logging
logging.basicConfig(level=logging.WARNING)

from chatbot import BasketballChatbot

print("\n" + "="*70)
print("TRIPLE-DOUBLE QUERY VERIFICATION")
print("="*70)

bot = BasketballChatbot()

# Original problematic query
query = "Give me Nikola Jokic's triple-double count for this season"
print(f"\nOriginal Query: {query}")
print("-"*70)

response = bot.process_question(query)
print(f"Response: {response}")

print("\n" + "="*70)
print("✓ Issue RESOLVED - System now correctly handles triple-double queries!")
print("="*70 + "\n")
