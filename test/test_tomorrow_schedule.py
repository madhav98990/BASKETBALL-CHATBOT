"""Test tomorrow schedule with fallback to next available games"""
from chatbot import BasketballChatbot

chatbot = BasketballChatbot()

query = "nba schedule for tomorrow"
print(f"Query: {query}\n")
print("="*70)

response = chatbot.process_question(query)
print(f"\nResponse:\n{response}\n")
print("="*70)
