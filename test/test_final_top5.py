"""
Final test for "top 5 player points per game"
This simulates exactly what happens when a user asks the question
"""
import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("FINAL TEST: 'top 5 player points per game'")
print("=" * 70 + "\n")

from chatbot import BasketballChatbot

chatbot = BasketballChatbot()
query = "top 5 player points per game"

print(f"Query: '{query}'\n")
print("Processing through chatbot...\n")
print("-" * 70)

try:
    response = chatbot.process_question(query)
    
    print("\n" + "=" * 70)
    print("FINAL RESPONSE:")
    print("=" * 70)
    print(response)
    print("=" * 70)
    
    # Detailed validation
    print("\n" + "=" * 70)
    print("VALIDATION:")
    print("=" * 70)
    
    checks = {
        "Response is not empty": len(response) > 0,
        "Response contains numbers (PPG values)": any(char.isdigit() for char in response),
        "Response contains 'points' or 'PPG'": "points" in response.lower() or "ppg" in response.lower(),
        "Response contains player names": any(name in response for name in ["Shai", "Giannis", "Jokić", "Edwards", "Tatum", "Gilgeous"]),
        "Response length is reasonable": len(response) > 100,
    }
    
    all_passed = True
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}: {passed}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL CHECKS PASSED - Response looks correct!")
    else:
        print("❌ SOME CHECKS FAILED - Response may be incomplete")
    print("=" * 70)
    
    # If response is empty or too short, show what might be wrong
    if len(response) < 50:
        print("\n⚠️  WARNING: Response is very short. Possible issues:")
        print("   1. Response formatter may not be working")
        print("   2. LLM may be returning empty response")
        print("   3. Error may be occurring silently")
    
except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")
    import traceback
    traceback.print_exc()

