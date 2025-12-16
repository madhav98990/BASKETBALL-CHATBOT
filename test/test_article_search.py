"""Test script to verify article search works correctly"""
from chatbot import BasketballChatbot

def test_article_search():
    """Test article search queries"""
    print("Testing Article Search Functionality")
    print("=" * 60)
    
    chatbot = BasketballChatbot()
    
    test_queries = [
        "what does the articles say about the thunder loss?",
        "what do the articles say about the lakers?",
        "what does the articles say about the celtics win?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)
        
        try:
            # Test intent detection
            intent = chatbot.intent_agent.detect_intent(query)
            print(f"Detected Intent: {intent}")
            
            if intent != 'articles':
                print(f"⚠️  WARNING: Intent should be 'articles', got '{intent}'")
            else:
                print(f"✓ Intent detection correct")
            
            # Test full chatbot response
            response = chatbot.process_question(query)
            print(f"\nResponse:")
            print(response[:500] if len(response) > 500 else response)
            
            if "couldn't find" in response.lower() or "no articles" in response.lower():
                print(f"⚠️  WARNING: No articles found or error in response")
            else:
                print(f"✓ Article search working")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_article_search()

