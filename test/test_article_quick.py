"""Quick test for article search improvements"""
from chatbot import BasketballChatbot

chatbot = BasketballChatbot()

test_query = "what does the articles say about the thunder loss?"
print(f"Testing: {test_query}\n")

response = chatbot.process_question(test_query)
print(f"Response ({len(response)} chars):\n{response}\n")

