#!/usr/bin/env python3
"""Quick test for triple-double counting"""

import sys
import logging
import timeout_decorator

# Setup logging
logging.basicConfig(level=logging.INFO)

from chatbot import BasketballChatbot

# Create chatbot instance
bot = BasketballChatbot()

# Test triple-double query
query = "Give me Nikola Jokic's triple-double count for this season"
print(f"\n{'='*60}")
print(f"Query: {query}")
print(f"{'='*60}")

# Get response with timeout
try:
    response = bot.get_response(query)
    print(f"\nResponse: {response}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
