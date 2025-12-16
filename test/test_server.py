#!/usr/bin/env python3
"""Quick test of the backend server"""
import requests
import sys

try:
    print("Testing backend server at http://localhost:8000/")
    response = requests.get('http://localhost:8000/', timeout=5)
    print(f"✓ Status Code: {response.status_code}")
    print(f"✓ Response: {response.json()}")
    
    print("\nTesting /chat endpoint...")
    chat_response = requests.post(
        'http://localhost:8000/chat',
        json={'question': 'test'},
        timeout=10
    )
    print(f"✓ Status Code: {chat_response.status_code}")
    if chat_response.status_code == 200:
        print(f"✓ Response: {chat_response.json()}")
    else:
        print(f"✗ Error: {chat_response.text}")
    
except requests.exceptions.ConnectionError:
    print("✗ ERROR: Cannot connect to server. Is it running?")
    sys.exit(1)
except Exception as e:
    print(f"✗ ERROR: {e}")
    sys.exit(1)

