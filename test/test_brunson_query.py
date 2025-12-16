"""Test the specific Brunson query to verify improvements"""
from chatbot import BasketballChatbot

chatbot = BasketballChatbot()

query = "What did the articles say about Jalen Brunson's performance in the NBA Cup?"
print(f"Query: {query}\n")
print("="*70)

response = chatbot.process_question(query)
print(f"\nResponse:\n{response}\n")
print("="*70)
print(f"Response length: {len(response)} chars")
print(f"Contains navigation junk: {'Yes' if '< >' in response or 'EmailPrint' in response else 'No'}")
print(f"Has meaningful content: {'Yes' if len(response) > 100 and 'Brunson' in response else 'No'}")

