"""
Test script for Basketball Chatbot
Tests all major functionality
"""
import sys
import os
from chatbot import BasketballChatbot
from database.db_connection import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_database_connection():
    """Test database connection"""
    print("Testing database connection...")
    try:
        conn = db.get_connection()
        result = db.execute_query("SELECT COUNT(*) as count FROM teams")
        if result:
            print(f"✅ Database connected. Found {result[0]['count']} teams.")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_agents():
    """Test all agents"""
    print("\nTesting agents...")
    chatbot = BasketballChatbot()
    
    test_cases = [
        ("How many points did LeBron James score?", "player_stats"),
        ("What was the Warriors vs Suns score?", "match_stats"),
        ("When is the next Lakers game?", "schedule"),
        ("What's the analysis on the Lakers?", "articles"),
    ]
    
    for question, expected_type in test_cases:
        print(f"\nQ: {question}")
        try:
            intent = chatbot.intent_agent.detect_intent(question)
            print(f"   Detected intent: {intent}")
            
            if intent == expected_type or intent == 'mixed':
                print(f"   ✅ Intent detection correct")
            else:
                print(f"   ⚠️  Expected {expected_type}, got {intent}")
        except Exception as e:
            print(f"   ❌ Error: {e}")


def test_full_queries():
    """Test full query processing"""
    print("\nTesting full query processing...")
    chatbot = BasketballChatbot()
    
    questions = [
        "How many points did LeBron James score?",
        "When is the next Lakers game?",
        "What was the Warriors vs Suns score?",
    ]
    
    for question in questions:
        print(f"\nQ: {question}")
        try:
            answer = chatbot.process_question(question)
            print(f"A: {answer[:200]}...")
            print("   ✅ Query processed successfully")
        except Exception as e:
            print(f"   ❌ Error: {e}")


def main():
    """Run all tests"""
    print("🧪 Basketball Chatbot Test Suite")
    print("=" * 50)
    
    # Test database
    if not test_database_connection():
        print("\n❌ Database tests failed. Please setup database first.")
        print("   Run: python setup_database.py")
        return
    
    # Test agents
    test_agents()
    
    # Test full queries (may take longer due to LLM)
    print("\n" + "=" * 50)
    print("Testing full queries (this may take a while)...")
    response = input("Continue? (y/n): ")
    if response.lower() == 'y':
        test_full_queries()
    
    print("\n" + "=" * 50)
    print("✅ Tests complete!")


if __name__ == "__main__":
    main()

