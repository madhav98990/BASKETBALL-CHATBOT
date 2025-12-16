#!/usr/bin/env python3
"""
Comprehensive test with timeout handling
"""

import logging
import sys
from multiprocessing import Process, Queue

logging.basicConfig(level=logging.WARNING)

def run_test(queue):
    """Run the test and put results in queue"""
    from chatbot import BasketballChatbot
    
    bot = BasketballChatbot()
    
    test_queries = [
        "Give me Nikola Jokic's triple-double count for this season",
        "How many triple-doubles has LeBron James had this season?",
        "Did the Lakers win their most recent game?",
    ]
    
    results = []
    for query in test_queries:
        try:
            response = bot.process_question(query)
            results.append((query, response))
        except Exception as e:
            results.append((query, f"ERROR: {e}"))
    
    queue.put(results)

if __name__ == '__main__':
    # Run with timeout
    queue = Queue()
    process = Process(target=run_test, args=(queue,))
    process.start()
    process.join(timeout=30)  # 30 second timeout
    
    if process.is_alive():
        # Process timed out
        process.terminate()
        process.join()
        print("ERROR: Test timed out after 30 seconds")
        sys.exit(1)
    
    # Get results
    if not queue.empty():
        results = queue.get()
        
        print("="*70)
        print("CHATBOT SYSTEM TEST RESULTS")
        print("="*70)
        
        for query, response in results:
            print(f"\nQuery: {query}")
            print(f"Response: {response[:100]}..." if len(str(response)) > 100 else f"Response: {response}")
        
        print("\n" + "="*70)
        print("TEST COMPLETE")
        print("="*70)
    else:
        print("ERROR: No results from test process")
        sys.exit(1)
