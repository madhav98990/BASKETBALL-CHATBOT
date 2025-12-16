"""Test season averages for LeBron James and other players"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.nba_api_library import NBAAPILibrary
from agents.player_stats_agent import PlayerStatsAgent
from agents.response_formatter_agent import ResponseFormatterAgent
from chatbot import BasketballChatbot

def test_lebron_season_averages():
    """Test LeBron James season averages"""
    print("="*80)
    print("Testing Season Averages: LeBron James")
    print("="*80)
    
    # Test 1: NBA API Library directly
    print("\n1. Testing NBA API Library directly:")
    try:
        nba_api = NBAAPILibrary()
        result = nba_api.get_player_season_averages("LeBron James")
        
        if result:
            print(f"   ✓ Success!")
            print(f"   Player: {result.get('player_name')}")
            print(f"   Games: {result.get('games_played')}")
            print(f"   Points: {result.get('points_per_game')} PPG")
            print(f"   Rebounds: {result.get('rebounds_per_game')} RPG")
            print(f"   Assists: {result.get('assists_per_game')} APG")
            print(f"   Steals: {result.get('steals_per_game')} SPG")
            print(f"   Blocks: {result.get('blocks_per_game')} BPG")
            print(f"   FG%: {result.get('field_goal_percentage', 0):.3f}")
            print(f"   3P%: {result.get('three_point_percentage', 0):.3f}")
            print(f"   FT%: {result.get('free_throw_percentage', 0):.3f}")
            print(f"   Minutes: {result.get('minutes_per_game')} MPG")
            print(f"   Season: {result.get('season')}")
            print(f"   Source: {result.get('source')}")
            
            # Validate
            if result.get('games_played', 0) <= 0:
                print(f"   ⚠️  WARNING: Invalid games played")
            if result.get('points_per_game', 0) < 0 or result.get('points_per_game', 0) > 50:
                print(f"   ⚠️  WARNING: Unusual points per game")
        else:
            print(f"   ✗ Failed to get season averages")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Player Stats Agent
    print("\n2. Testing Player Stats Agent:")
    try:
        agent = PlayerStatsAgent()
        query = "What are LeBron James' season averages right now?"
        result = agent.process_query(query)
        
        if result and result.get('type') == 'season_averages':
            data = result.get('data', {})
            print(f"   ✓ Processed successfully")
            print(f"   Player: {data.get('player_name')}")
            print(f"   Games: {data.get('games_played')}")
            print(f"   Points: {data.get('points_per_game')} PPG")
            print(f"   Source: {result.get('source')}")
        else:
            print(f"   ✗ Failed: {result}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Full Chatbot Pipeline
    print("\n3. Testing Full Chatbot Pipeline:")
    try:
        chatbot = BasketballChatbot()
        query = "What are LeBron James' season averages right now?"
        response = chatbot.process_question(query)
        print(f"   Query: {query}")
        print(f"   Response: {response}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Multiple players
    print("\n4. Testing Multiple Players:")
    test_players = ["Stephen Curry", "Kevin Durant", "Nikola Jokic"]
    for player in test_players:
        try:
            nba_api = NBAAPILibrary()
            result = nba_api.get_player_season_averages(player)
            if result:
                print(f"   ✓ {player}: {result.get('points_per_game')} PPG, {result.get('rebounds_per_game')} RPG, {result.get('assists_per_game')} APG ({result.get('games_played')} games)")
            else:
                print(f"   ✗ {player}: Failed")
        except Exception as e:
            print(f"   ✗ {player}: Error - {e}")
    
    print("\n" + "="*80)
    print("Testing Complete")
    print("="*80)


if __name__ == "__main__":
    test_lebron_season_averages()

