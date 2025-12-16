"""Test full chatbot pipeline"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot import BasketballChatbot

query = "Are the Oklahoma City Thunder still in the top 3 of the West?"
print("="*80)
print(f"Query: {query}")
print("="*80)

chatbot = BasketballChatbot()
response = chatbot.process_question(query)

print(f"\nResponse: {response}")
print("="*80)

