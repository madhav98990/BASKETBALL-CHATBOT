"""Simple test for article search - one query at a time"""
from chatbot import BasketballChatbot
import sys

chatbot = BasketballChatbot()

# Test one query
query = sys.argv[1] if len(sys.argv) > 1 else "what does the articles say about jalen brunson performance?"

print(f"Query: {query}\n")
print("Processing...\n")

response = chatbot.process_question(query)

print(f"Response ({len(response)} chars):\n")
print(response)
print("\n" + "="*70)
print("Quality checks:")
print(f"  Length: {'✓' if len(response) > 100 else '✗'} {len(response)} chars")
print(f"  No navigation junk: {'✓' if '< >' not in response and 'EmailPrint' not in response else '✗'}")
print(f"  Has content: {'✓' if 'couldn\'t find' not in response.lower() and 'no articles' not in response.lower() else '✗'}")

