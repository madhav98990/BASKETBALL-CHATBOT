"""
Test the full agent flow for "top 5 player points per game"
"""
import sys
import os
# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from chatbot import BasketballChatbot
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 70)
print("Testing: 'top 5 player points per game'")
print("=" * 70 + "\n")

chatbot = BasketballChatbot()

# Test the exact query
query = "top 5 player points per game"

try:
    print(f"Query: {query}\n")
    print("Processing through chatbot...\n")
    
    response = chatbot.process_question(query)
    
    print("=" * 70)
    print("RESPONSE:")
    print("=" * 70)
    print(response)
    print("=" * 70)
    
    # Check if response contains player names and PPG
    if any(keyword in response.lower() for keyword in ['ppg', 'points per game', 'points']):
        if any(char.isdigit() for char in response):  # Has numbers (PPG values)
            print("\n✅ SUCCESS! Response contains player data with PPG")
        else:
            print("\n⚠️  WARNING: Response mentions PPG but no numbers found")
    else:
        print("\n❌ FAILED: Response doesn't contain expected player/PPG information")
        print("Agent may not be executing the tool correctly")
    
except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")
    import traceback
    traceback.print_exc()

