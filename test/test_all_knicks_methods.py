#!/usr/bin/env python3
"""
Test all methods to get Knicks most recent game result
"""

import logging
import sys
import os

logging.basicConfig(level=logging.INFO)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_all_methods():
    """Test all available methods"""
    print("="*70)
    print("TESTING ALL METHODS FOR: Did the Knicks win their most recent game?")
    print("="*70)
    
    team_name = "knicks"
    results = []
    
    # Method 1: ESPN API (DirectESPNFetcher)
    print("\n1. Testing ESPN API (DirectESPNFetcher)...")
    try:
        from services.direct_espn_fetcher import DirectESPNFetcher
        api = DirectESPNFetcher()
        result = api.get_team_most_recent_game_result(team_name, days_back=30)
        if result:
            print(f"   ✅ SUCCESS: {result.get('did_win')} - {result.get('team_score')}-{result.get('opponent_score')} vs {result.get('opponent_name')}")
            results.append(("ESPN API", result))
        else:
            print("   ❌ FAILED: Returned None")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Method 2: NBA API Library
    print("\n2. Testing NBA API Library...")
    try:
        from services.nba_api_library import NBAAPILibrary
        api = NBAAPILibrary()
        result = api.get_team_most_recent_game_result(team_name)
        if result:
            print(f"   ✅ SUCCESS: {result.get('did_win')} - {result.get('team_score')}-{result.get('opponent_score')} vs {result.get('opponent_name')}")
            results.append(("NBA API Library", result))
        else:
            print("   ❌ FAILED: Returned None")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Method 3: Ball Don't Lie API
    print("\n3. Testing Ball Don't Lie API...")
    try:
        from services.balldontlie_api import BallDontLieAPI
        api = BallDontLieAPI()
        result = api.get_team_most_recent_game_result(team_name, days_back=30)
        if result:
            print(f"   ✅ SUCCESS: {result.get('did_win')} - {result.get('team_score')}-{result.get('opponent_score')} vs {result.get('opponent_name')}")
            results.append(("Ball Don't Lie API", result))
        else:
            print("   ❌ FAILED: Returned None")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Method 4: NBA API Service get_recent_games
    print("\n4. Testing NBA API Service get_recent_games...")
    try:
        from services.nba_api import NBAApiService
        api = NBAApiService()
        games = api.get_recent_games(days=30, team_name=team_name, limit=50)
        if games:
            for game in games:
                team1 = game.get('team1_name', '').upper()
                team2 = game.get('team2_name', '').upper()
                if 'NYK' in team1 or 'NYK' in team2:
                    team1_score = game.get('team1_score')
                    team2_score = game.get('team2_score')
                    if team1_score is not None and team2_score is not None:
                        is_team1 = 'NYK' in team1
                        team_score = team1_score if is_team1 else team2_score
                        opponent_score = team2_score if is_team1 else team1_score
                        did_win = team_score > opponent_score
                        print(f"   ✅ SUCCESS: {did_win} - {team_score}-{opponent_score}")
                        results.append(("NBA API Service", {'did_win': did_win, 'team_score': team_score, 'opponent_score': opponent_score}))
                        break
        else:
            print("   ❌ FAILED: No games returned")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Method 5: Ball Don't Lie date search
    print("\n5. Testing Ball Don't Lie date search...")
    try:
        from services.balldontlie_api import BallDontLieAPI
        from datetime import date, timedelta
        api = BallDontLieAPI()
        today = date.today()
        found = False
        for days_ago in range(30):
            check_date = today - timedelta(days=days_ago)
            games = api.get_games_for_date(check_date)
            for game in games:
                team1 = game.get('team1_name', '').upper()
                team2 = game.get('team2_name', '').upper()
                if 'NYK' in team1 or 'NYK' in team2:
                    team1_score = game.get('team1_score')
                    team2_score = game.get('team2_score')
                    if team1_score is not None and team2_score is not None:
                        is_team1 = 'NYK' in team1
                        team_score = team1_score if is_team1 else team2_score
                        opponent_score = team2_score if is_team1 else team1_score
                        did_win = team_score > opponent_score
                        print(f"   ✅ SUCCESS: {did_win} - {team_score}-{opponent_score}")
                        results.append(("Ball Don't Lie Date Search", {'did_win': did_win, 'team_score': team_score, 'opponent_score': opponent_score}))
                        found = True
                        break
            if found:
                break
        if not found:
            print("   ❌ FAILED: No games found")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nTotal methods that succeeded: {len(results)}")
    
    if results:
        print("\nWorking methods:")
        for method, result in results:
            did_win = result.get('did_win', False)
            team_score = result.get('team_score', 0)
            opponent_score = result.get('opponent_score', 0)
            print(f"  - {method}: {'WIN' if did_win else 'LOSS'} ({team_score}-{opponent_score})")
        
        # Get the first successful result
        first_result = results[0][1]
        did_win = first_result.get('did_win', False)
        team_score = first_result.get('team_score', 0)
        opponent_score = first_result.get('opponent_score', 0)
        opponent_name = first_result.get('opponent_name', 'Opponent')
        game_date = first_result.get('game_date', 'Unknown date')
        
        print("\n" + "="*70)
        print("ANSWER:")
        print("="*70)
        if did_win:
            print(f"\n✅ YES, the Knicks won their most recent game on {game_date}.")
            print(f"   They defeated the {opponent_name} {team_score}-{opponent_score}.")
        else:
            print(f"\n❌ NO, the Knicks lost their most recent game on {game_date}.")
            print(f"   They were defeated by the {opponent_name} {opponent_score}-{team_score}.")
    else:
        print("\n❌ All methods failed. Please check:")
        print("  - Internet connection")
        print("  - API availability")
        print("  - Rate limiting")
    
    print("="*70)

if __name__ == "__main__":
    test_all_methods()

