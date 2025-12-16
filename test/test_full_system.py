"""
Test the complete chatbot system
"""
import sys
import os

print("🧪 Testing Basketball AI Chatbot System")
print("=" * 50)

# Test 1: Database Connection
print("\n1️⃣ Testing Database Connection...")
try:
    from database.db_connection import db
    db.connect()
    result = db.execute_query('SELECT COUNT(*) as count FROM teams')
    print(f"   ✅ Database connected: {result[0]['count']} teams found")
except Exception as e:
    print(f"   ❌ Database error: {e}")
    sys.exit(1)

# Test 2: Ollama Connection
print("\n2️⃣ Testing Ollama Connection...")
try:
    import requests
    from config import OLLAMA_BASE_URL, OLLAMA_MODEL
    
    response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
    if response.status_code == 200:
        models = response.json().get('models', [])
        model_names = [m.get('name', '') for m in models]
        if any(OLLAMA_MODEL in name for name in model_names):
            print(f"   ✅ Ollama connected: {OLLAMA_MODEL} model available")
        else:
            print(f"   ⚠️  Ollama connected but {OLLAMA_MODEL} not found")
            print(f"   Available models: {model_names}")
    else:
        print(f"   ❌ Ollama returned status {response.status_code}")
except Exception as e:
    print(f"   ❌ Ollama error: {e}")
    print(f"   Make sure Ollama is running on {OLLAMA_BASE_URL}")

# Test 3: Chatbot Agents
print("\n3️⃣ Testing Chatbot Agents...")
try:
    from agents.intent_detection_agent import IntentDetectionAgent
    from agents.stats_agent import StatsAgent
    from agents.player_stats_agent import PlayerStatsAgent
    from agents.schedule_agent import ScheduleAgent
    
    intent_agent = IntentDetectionAgent()
    intent = intent_agent.detect_intent("How many points did LeBron score?")
    print(f"   ✅ Intent detection working: detected '{intent}'")
    
    stats_agent = StatsAgent()
    results = stats_agent.get_recent_matches(limit=1)
    print(f"   ✅ Stats agent working: found {len(results)} matches")
    
    schedule_agent = ScheduleAgent()
    upcoming = schedule_agent.get_upcoming_matches(limit=1)
    print(f"   ✅ Schedule agent working: found {len(upcoming)} upcoming matches")
    
except Exception as e:
    print(f"   ❌ Agent error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Full Chatbot Query
print("\n4️⃣ Testing Full Chatbot Query...")
try:
    from chatbot import BasketballChatbot
    
    chatbot = BasketballChatbot()
    test_question = "How many points did LeBron James score?"
    print(f"   Question: {test_question}")
    
    answer = chatbot.process_question(test_question)
    print(f"   ✅ Chatbot response generated:")
    print(f"   {answer[:200]}...")
    
except Exception as e:
    print(f"   ❌ Chatbot error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("✅ System test complete!")
print("\nNext steps:")
print("1. Start the API: python api/main.py")
print("2. Open frontend/index.html in your browser")
print("3. Start chatting!")

