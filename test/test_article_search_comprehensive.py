"""Comprehensive test for article search with different question types"""
from chatbot import BasketballChatbot

def test_article_search():
    """Test article search with various question types"""
    print("=" * 70)
    print("COMPREHENSIVE ARTICLE SEARCH TEST")
    print("=" * 70)
    
    chatbot = BasketballChatbot()
    
    # Different types of questions based on article content
    test_queries = [
        # Game results/losses
        "what does the articles say about the thunder loss?",
        "what do the articles say about the lakers losing?",
        "what does the articles say about the celtics win?",
        
        # Player performance
        "what does the articles say about jalen brunson performance?",
        "what do the articles say about jalen brunson in the nba cup?",
        "what does the articles say about brunson mvp?",
        
        # Injuries
        "what does the articles say about trae young injury?",
        "what do the articles say about mobley injury?",
        
        # Team performance
        "what does the articles say about the knicks?",
        "what do the articles say about okc thunder?",
        
        # Trades/transactions
        "what does the articles say about giannis trade?",
        "what do the articles say about paul george trade?",
    ]
    
    results_summary = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}/{len(test_queries)}: {query}")
        print(f"{'='*70}")
        
        try:
            # Test intent detection
            intent = chatbot.intent_agent.detect_intent(query)
            print(f"Intent: {intent}")
            
            if intent != 'articles':
                print(f"⚠️  WARNING: Expected 'articles', got '{intent}'")
                results_summary.append((query, intent, "WRONG_INTENT", None))
                continue
            
            # Test article search
            article_result = chatbot.article_agent.process_query(query)
            print(f"Articles found: {len(article_result.get('data', []))}")
            print(f"Combined text length: {len(article_result.get('combined_text', ''))}")
            
            if not article_result.get('data') and not article_result.get('combined_text'):
                print(f"❌ No articles found")
                results_summary.append((query, intent, "NO_ARTICLES", None))
                continue
            
            # Test full response
            response = chatbot.process_question(query)
            print(f"\nResponse ({len(response)} chars):")
            print("-" * 70)
            print(response[:800] if len(response) > 800 else response)
            print("-" * 70)
            
            # Evaluate response quality
            if "couldn't find" in response.lower() or "no articles" in response.lower() or "don't mention" in response.lower():
                status = "NO_INFO"
            elif len(response) < 50:
                status = "TOO_SHORT"
            else:
                status = "SUCCESS"
            
            results_summary.append((query, intent, status, len(response)))
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            results_summary.append((query, "ERROR", "EXCEPTION", None))
    
    # Summary
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}")
    success_count = sum(1 for _, _, status, _ in results_summary if status == "SUCCESS")
    print(f"Success: {success_count}/{len(test_queries)}")
    print(f"\nDetailed Results:")
    for query, intent, status, length in results_summary:
        status_icon = "✓" if status == "SUCCESS" else "✗"
        print(f"  {status_icon} {status:15} | {intent:12} | {query[:50]}")

if __name__ == "__main__":
    test_article_search()

