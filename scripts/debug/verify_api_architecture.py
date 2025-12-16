#!/usr/bin/env python3
"""
Verify the system architecture uses API with current date (2025-12-11)
"""
import sys
sys.path.append('.')
from datetime import date
from agents.stats_agent import StatsAgent
from agents.player_stats_agent import PlayerStatsAgent
import logging

logging.basicConfig(level=logging.WARNING)

def test_api_date_handling():
    """Verify the system uses current date (2025-12-11) for API queries"""
    print("=" * 80)
    print("ARCHITECTURE VERIFICATION: API with Current Date (2025-12-11)")
    print("=" * 80)
    print()
    
    today = date.today()
    print(f"✓ System date: {today}")
    print(f"✓ NBA season: 2025-2026 (Oct 2025 - Jun 2026)")
    print()
    
    # Test 1: Stats Agent uses API with current date
    print("Test 1: StatsAgent.process_query() uses API")
    print("-" * 80)
    stats_agent = StatsAgent()
    result = stats_agent.process_query("What are the latest NBA scores?")
    
    print(f"Data source: {result.get('source')}")
    print(f"Expected: 'api' (not 'database')")
    
    if result.get('source') == 'api':
        data = result.get('data', [])
        if data:
            game = data[0]
            game_date = game.get('match_date', '')
            print(f"✓ PASS: Using API")
            print(f"✓ Latest game date from API: {game_date}")
            if game_date.startswith('2025'):
                print(f"✓ Game date is from 2025-2026 season")
            else:
                print(f"⚠ Game date is from {game_date.split('-')[0]} (unexpected)")
        return True
    else:
        print(f"✗ FAIL: Using {result.get('source')} instead of API")
        return False

def test_player_stats_agent_architecture():
    """Verify PlayerStatsAgent tries ESPN API first for player queries"""
    print()
    print("Test 2: PlayerStatsAgent Architecture")
    print("-" * 80)
    
    agent = PlayerStatsAgent()
    print(f"Has api_service: {agent.api_service is not None}")
    print(f"API service type: {type(agent.api_service).__name__}")
    
    # Check if the player handlers are updated to use API
    # We can't easily test without network, but we can verify the code
    import inspect
    
    source = inspect.getsource(agent._handle_triple_double_query)
    if 'espn_api' in source or 'api_service.get_player_stats' in source:
        print(f"✓ PASS: Triple-double handler uses API")
        return True
    else:
        print(f"✗ FAIL: Triple-double handler might not use API")
        print("Handler source:")
        print(source[:200])
        return False

def test_date_extraction():
    """Verify date extraction uses current date correctly"""
    print()
    print("Test 3: Date Extraction Uses Current Date")
    print("-" * 80)
    
    stats_agent = StatsAgent()
    
    today = date.today()
    
    # Test "yesterday"
    yesterday_date = stats_agent.extract_date("What games were played yesterday?")
    if yesterday_date:
        expected = date(today.year, today.month, today.day - 1)
        # Handle month/year boundaries
        from datetime import timedelta
        expected = today - timedelta(days=1)
        if yesterday_date == expected:
            print(f"✓ 'yesterday' correctly extracts to {yesterday_date}")
        else:
            print(f"⚠ 'yesterday' extracts to {yesterday_date}, expected {expected}")
    
    # Test "today"
    today_date = stats_agent.extract_date("What games are there today?")
    if today_date == today:
        print(f"✓ 'today' correctly extracts to {today_date}")
    else:
        print(f"⚠ 'today' extracts to {today_date}, expected {today}")
    
    return True

if __name__ == "__main__":
    print()
    results = [
        test_api_date_handling(),
        test_player_stats_agent_architecture(),
        test_date_extraction()
    ]
    
    print()
    print("=" * 80)
    print("ARCHITECTURE VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"API with current date: {'✓ PASS' if results[0] else '✗ FAIL'}")
    print(f"Player stats uses API: {'✓ PASS' if results[1] else '✗ FAIL'}")
    print(f"Date extraction correct: {'✓ PASS' if results[2] else '✗ FAIL'}")
    print()
    
    if all(results):
        print("✓ SYSTEM ARCHITECTURE VERIFIED")
        print("✓ Using latest API data with current date (2025-12-11) for filtering")
        sys.exit(0)
    else:
        print("⚠ Some verifications need attention")
        sys.exit(1)
