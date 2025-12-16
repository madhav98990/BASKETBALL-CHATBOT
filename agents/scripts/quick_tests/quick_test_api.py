"""Quick test to verify API is working"""
import requests
import json

try:
    print("Testing API server...")
    response = requests.get('http://localhost:8000/', timeout=5)
    print(f"✓ Server is running (Status: {response.status_code})")
    print(f"Response: {response.json()}\n")
    
    print("Testing chat endpoint with 'top 5 player points per game'...")
    chat_response = requests.post(
        'http://localhost:8000/chat/message',
        json={'question': 'top 5 player points per game', 'conversation_id': None},
        timeout=30
    )
    
    if chat_response.status_code == 200:
        data = chat_response.json()
        answer = data.get('answer', '')
        print(f"✓ API responded successfully!")
        print(f"\nAnswer preview (first 200 chars):")
        print("-" * 70)
        print(answer[:200])
        print("-" * 70)
        
        if 'Shai' in answer or 'Giannis' in answer or '32.7' in answer:
            print("\n✅ SUCCESS! API is returning player data correctly!")
        elif 'Unable' in answer or 'error' in answer.lower():
            print("\n❌ WARNING: API returned an error message")
            print("The server may need to be restarted to load latest code")
        else:
            print("\n⚠️  Response received but content unclear")
    else:
        print(f"❌ Error: HTTP {chat_response.status_code}")
        print(chat_response.text)
        
except requests.exceptions.ConnectionError:
    print("❌ ERROR: Could not connect to server")
    print("Make sure the server is running on http://localhost:8000")
except Exception as e:
    print(f"❌ ERROR: {e}")

