"""Test article search improvements with different question types"""
from chatbot import BasketballChatbot

chatbot = BasketballChatbot()

test_queries = [
    ("what does the articles say about the thunder loss?", "loss"),
    ("what do the articles say about jalen brunson performance?", "performance"),
    ("what does the articles say about brunson mvp?", "award"),
    ("what do the articles say about trae young injury?", "injury"),
]

print("=" * 70)
print("TESTING ARTICLE SEARCH IMPROVEMENTS")
print("=" * 70)

for query, expected_type in test_queries:
    print(f"\n{'='*70}")
    print(f"Query: {query}")
    print(f"Expected type: {expected_type}")
    print(f"{'-'*70}")
    
    try:
        response = chatbot.process_question(query)
        
        # Check response quality
        if len(response) < 50:
            print(f"❌ Response too short: {len(response)} chars")
        elif "couldn't find" in response.lower() or "no articles" in response.lower():
            print(f"❌ No information found")
        elif "< >" in response or "EmailPrint" in response:
            print(f"⚠️  Response contains navigation junk")
        else:
            print(f"✓ Response length: {len(response)} chars")
            print(f"\nResponse preview (first 300 chars):")
            print(response[:300] + "..." if len(response) > 300 else response)
    except Exception as e:
        print(f"❌ Error: {e}")

print(f"\n{'='*70}")
print("Testing complete!")

