#!/usr/bin/env python3
"""Test the full flow without heavy API calls"""

import logging
logging.basicConfig(level=logging.INFO)

from chatbot import BasketballChatbot

# Test with a simpler query first
bot = BasketballChatbot()

query = "Give me Nikola Jokic's triple-double count for this season"
print(f"\nQuery: {query}")
print("Getting response...")

try:
    # Use shorter timeout via keyboard interrupt approach
    import signal
    
    def timeout_handler(signum, frame):
        print("\nTimeout: Request took too long")
        raise TimeoutError("Request timeout")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(5)  # 5 second timeout
    
    response = bot.process_question(query)
    signal.alarm(0)  # Cancel alarm
    
    print(f"\nResponse: {response}")
except TimeoutError:
    print("The request is taking too long - likely waiting on API")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
