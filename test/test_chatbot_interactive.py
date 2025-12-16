"""
Interactive test script for chatbot with questions from articles
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot import BasketballChatbot

# Questions directly from or based on the articles
test_questions = [
    # From article headline: "'MVP' Brunson drops 40 as Knicks make Cup final"
    "What did Jalen Brunson do in the NBA Cup?",
    "How many points did Brunson score in the NBA Cup?",
    "Did the Knicks make it to the Cup final?",
    
    # From article content about the game
    "What was the score when the Knicks beat Orlando Magic?",
    "Where was the NBA Cup semifinal played?",
    "Who did Jalen Brunson play against in the NBA Cup?",
    
    # About Brunson's performance
    "What were Jalen Brunson's stats in the NBA Cup semifinal?",
    "How did Jalen Brunson shoot in the NBA Cup game?",
    "Was this Brunson's first 40-point game?",
    
    # About MVP discussion
    "Did Brunson receive MVP chants?",
    "What did the coach say about Brunson being an MVP candidate?",
    "Is Jalen Brunson an MVP candidate?",
    
    # About the tournament
    "What round of the NBA Cup was the game against Orlando?",
    "Did the Knicks advance to the NBA Cup final?",
    "Who will the Knicks face in the NBA Cup final?",
]

def test_chatbot():
    print("="*80)
    print("TESTING CHATBOT WITH QUESTIONS FROM ARTICLES")
    print("="*80)
    print("\nInitializing chatbot...\n")
    
    try:
        chatbot = BasketballChatbot()
        print("Chatbot initialized successfully!\n")
    except Exception as e:
        print(f"Error initializing chatbot: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"Testing {len(test_questions)} questions...\n")
    print("="*80)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*80}")
        print(f"QUESTION {i}/{len(test_questions)}")
        print(f"{'='*80}")
        print(f"Q: {question}")
        print(f"{'-'*80}")
        
        try:
            response = chatbot.process_question(question)
            print(f"A: {response}")
            
            # Quick validation
            response_lower = response.lower()
            checks = []
            
            if 'brunson' in response_lower or 'jalen' in response_lower:
                checks.append("✓ Mentions Brunson")
            else:
                checks.append("✗ Missing Brunson")
            
            if 'cup' in response_lower or 'nba cup' in response_lower:
                checks.append("✓ Mentions NBA Cup")
            else:
                checks.append("⚠ Missing NBA Cup context")
            
            if '40' in response or 'forty' in response_lower:
                checks.append("✓ Mentions 40 points")
            elif 'points' in question.lower():
                checks.append("⚠ Missing points info")
            
            if 'orlando' in response_lower or 'magic' in response_lower:
                checks.append("✓ Mentions opponent")
            elif 'orlando' in question.lower() or 'magic' in question.lower():
                checks.append("⚠ Missing opponent")
            
            if len(response.strip()) > 50:
                checks.append("✓ Response has content")
            else:
                checks.append("⚠ Response too short")
            
            if "couldn't find" in response_lower or "don't have" in response_lower:
                checks.append("✗ No information found")
            
            print(f"\nValidation: {' | '.join(checks)}")
            
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print("="*80)
    print("TESTING COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_chatbot()

