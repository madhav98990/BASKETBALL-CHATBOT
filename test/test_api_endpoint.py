"""
Test the API endpoint that the frontend uses
"""
import requests
import json

API_BASE = 'http://localhost:8000'
API_MESSAGE = f'{API_BASE}/chat/message'

print("=" * 70)
print("Testing API Endpoint: /chat/message")
print("=" * 70 + "\n")

query = "top 5 player points per game"

print(f"Query: '{query}'")
print(f"Endpoint: {API_MESSAGE}\n")
print("Sending request...\n")

try:
    response = requests.post(
        API_MESSAGE,
        headers={'Content-Type': 'application/json'},
        json={
            'question': query,
            'conversation_id': None
        },
        timeout=60
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}\n")
    
    if response.status_code == 200:
        data = response.json()
        print("=" * 70)
        print("RESPONSE DATA:")
        print("=" * 70)
        print(json.dumps(data, indent=2))
        print("\n" + "=" * 70)
        
        if 'answer' in data:
            answer = data['answer']
            print(f"\nAnswer length: {len(answer)} characters")
            print(f"\nAnswer content:")
            print("-" * 70)
            print(answer)
            print("-" * 70)
            
            if len(answer) > 0:
                print("\n✅ SUCCESS: API returned answer!")
            else:
                print("\n❌ PROBLEM: Answer is empty!")
        else:
            print("\n❌ PROBLEM: Response doesn't contain 'answer' field")
            print(f"Available fields: {list(data.keys())}")
    else:
        print(f"\n❌ ERROR: HTTP {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Could not connect to API")
    print("Make sure the API server is running:")
    print("  python -m uvicorn api.main:app --reload")
    
except requests.exceptions.Timeout:
    print("\n❌ ERROR: Request timed out")
    print("The API might be taking too long to respond")
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()

