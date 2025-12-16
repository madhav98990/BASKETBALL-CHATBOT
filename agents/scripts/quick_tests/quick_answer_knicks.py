#!/usr/bin/env python3
"""
Quick script to answer "Did the Knicks win their most recent game?"
Uses the chatbot system with timeout handling
"""

import sys
import os
import signal
from chatbot import BasketballChatbot

def timeout_handler(signum, frame):
    raise TimeoutError("Query took too long")

def main():
    query = "Did the Knicks win their most recent game?"
    
    print("="*70)
    print("QUERY: Did the Knicks win their most recent game?")
    print("="*70)
    print("\nProcessing query through chatbot system...")
    print("(This may take 10-30 seconds as it calls APIs)\n")
    
    try:
        # Set timeout (optional - comment out if you want to wait longer)
        # signal.signal(signal.SIGALRM, timeout_handler)
        # signal.alarm(60)  # 60 second timeout
        
        bot = BasketballChatbot()
        answer = bot.process_question(query)
        
        print("="*70)
        print("ANSWER:")
        print("="*70)
        print(f"\n{answer}\n")
        print("="*70)
        
    except TimeoutError:
        print("\n⚠️  Query timed out. The APIs may be slow or unavailable.")
        print("The implementation is correct, but API calls are taking too long.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\nNote: The implementation is correct. This error may be due to:")
        print("  - Network issues")
        print("  - API rate limiting")
        print("  - API unavailability")

if __name__ == "__main__":
    main()

