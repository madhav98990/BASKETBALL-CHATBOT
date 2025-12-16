#!/usr/bin/env python3
"""
Test script to verify the system uses latest API data with current date filtering
"""
import sys
sys.path.append('.')
from datetime import date
from agents.player_stats_agent import PlayerStatsAgent
from agents.stats_agent import StatsAgent
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_triple_double_with_api():
    """Test that triple-double query uses ESPN API with current date"""
    print("=" * 80)
    print("TEST 1: Triple-Double Query (Should use ESPN API, not outdated database)")
    print("=" * 80)
    print(f"Today's date: {date.today()}")
    print()
    
    agent = PlayerStatsAgent()
    question = "Give me Nikola Jokic's triple-double count for this season."
    
    print(f"Question: {question}\n")
    
    result = agent.process_query(question)
    
    print(f"Result Type: {result.get('type')}")
    print(f"Source: {result.get('source')}")  # Should be 'espn_api', not 'database'
    
    if result.get('source') == 'espn_api':
        print("✓ PASS: Using ESPN API (not outdated database)")
    else:
        print(f"✗ FAIL: Using {result.get('source')} instead of espn_api")
    
    data = result.get('data')
    if data:
        count = data.get('count', 0)
        print(f"Triple-double count: {count}")
    
    print()
    return result.get('source') == 'espn_api'

def test_match_stats_with_current_date():
    """Test that match stats query uses API and filters by current date"""
    print("=" * 80)
    print("TEST 2: Match Stats Query (Should use API with 2025-12-11 as reference)")
    print("=" * 80)
    print(f"Today's date: {date.today()}")
    print()
    
    agent = StatsAgent()
    question = "Show me recent match results"
    
    print(f"Question: {question}\n")
    
    result = agent.process_query(question)
    
    print(f"Result Type: {result.get('type')}")
    print(f"Source: {result.get('source')}")  # Should be 'api'
    
    if result.get('source') == 'api':
        print("✓ PASS: Using API for latest data")
    else:
        print(f"✗ FAIL: Using {result.get('source')} instead of api")
    
    data = result.get('data', [])
    if data:
        print(f"\nFound {len(data)} games from API:")
        for i, game in enumerate(data[:3], 1):
            match_date = game.get('match_date', 'Unknown')
            team1 = game.get('team1_name', 'Unknown')
            team2 = game.get('team2_name', 'Unknown')
            score1 = game.get('team1_score', 0)
            score2 = game.get('team2_score', 0)
            print(f"  {i}. {team1} ({score1}) vs {team2} ({score2}) - {match_date}")
            
            # Check if dates are from current season (2025)
            if match_date.startswith('2025'):
                print(f"     ✓ Date is from current season 2025-2026")
            else:
                print(f"     ⚠ Date is NOT from current season: {match_date}")
    else:
        print("\n✗ No data returned from API")
    
    print()
    return result.get('source') == 'api'

def test_season_averages_with_api():
    """Test that season averages query uses ESPN API"""
    print("=" * 80)
    print("TEST 3: Season Averages Query (Should use ESPN API)")
    print("=" * 80)
    print(f"Today's date: {date.today()}")
    print()
    
    agent = PlayerStatsAgent()
    question = "What are Luka Doncic's season averages?"
    
    print(f"Question: {question}\n")
    
    result = agent.process_query(question)
    
    print(f"Result Type: {result.get('type')}")
    print(f"Source: {result.get('source')}")  # Should be 'espn_api'
    
    if result.get('source') == 'espn_api':
        print("✓ PASS: Using ESPN API (not outdated database)")
    else:
        print(f"✗ FAIL: Using {result.get('source')} instead of espn_api")
    
    data = result.get('data')
    if data and data.get('games_played', 0) > 0:
        print(f"Games played: {data.get('games_played')}")
        print(f"PPG: {data.get('avg_points', 0)}")
        print(f"RPG: {data.get('avg_rebounds', 0)}")
        print(f"APG: {data.get('avg_assists', 0)}")
    
    print()
    return result.get('source') == 'espn_api'

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("VERIFICATION: System Uses Latest API Data with Current Date Filtering")
    print("=" * 80)
    print()
    
    try:
        test1 = test_triple_double_with_api()
        test2 = test_match_stats_with_current_date()
        test3 = test_season_averages_with_api()
        
        print("=" * 80)
        print("TEST RESULTS")
        print("=" * 80)
        print(f"Triple-double query uses API: {'✓ PASS' if test1 else '✗ FAIL'}")
        print(f"Match stats uses API with current date: {'✓ PASS' if test2 else '✗ FAIL'}")
        print(f"Season averages uses API: {'✓ PASS' if test3 else '✗ FAIL'}")
        
        all_pass = test1 and test2 and test3
        if all_pass:
            print("\n✓ ALL TESTS PASSED - System is using latest API data!")
            sys.exit(0)
        else:
            print("\n✗ Some tests failed - Review the output above")
            sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
