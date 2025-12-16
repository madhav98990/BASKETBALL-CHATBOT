#!/usr/bin/env python3
"""
Test script to answer "Did the Knicks win their most recent game?" using ESPN API
and validate the answer
"""

import logging
import sys
import os
from datetime import date, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_espn_api():
    """Test ESPN API directly"""
    print("="*70)
    print("TEST: ESPN API - Knicks Most Recent Game")
    print("="*70)
    
    try:
        from services.direct_espn_fetcher import DirectESPNFetcher
        
        api = DirectESPNFetcher()
        team_name = "knicks"
        
        print(f"\nFetching most recent game result for: {team_name}")
        print("Using ESPN API (most reliable for recent games)...")
        
        result = api.get_team_most_recent_game_result(team_name, days_back=30)
        
        if result:
            print("\n" + "="*70)
            print("✅ SUCCESS: Game result retrieved from ESPN API")
            print("="*70)
            print(f"\nTeam: {result.get('team_name', 'N/A')}")
            print(f"Opponent: {result.get('opponent_name', 'N/A')}")
            print(f"Game Date: {result.get('game_date', 'N/A')}")
            print(f"Team Score: {result.get('team_score', 'N/A')}")
            print(f"Opponent Score: {result.get('opponent_score', 'N/A')}")
            print(f"Did Win: {result.get('did_win', 'N/A')}")
            print(f"Matchup: {result.get('matchup', 'N/A')}")
            
            # Answer the question
            did_win = result.get('did_win', False)
            team_score = result.get('team_score', 0)
            opponent_score = result.get('opponent_score', 0)
            opponent_name = result.get('opponent_name', 'Unknown')
            game_date = result.get('game_date', 'Unknown date')
            
            print("\n" + "="*70)
            print("ANSWER TO: Did the Knicks win their most recent game?")
            print("="*70)
            
            if did_win:
                answer = f"✅ YES, the Knicks won their most recent game on {game_date}. They defeated the {opponent_name} {team_score}-{opponent_score}."
            else:
                answer = f"❌ NO, the Knicks lost their most recent game on {game_date}. They were defeated by the {opponent_name} {opponent_score}-{team_score}."
            
            print(f"\n{answer}\n")
            
            return result, answer
        else:
            print("\n❌ FAILED: ESPN API returned None")
            print("Possible reasons:")
            print("  - No recent games found in last 30 days")
            print("  - API rate limiting")
            print("  - Network issues")
            return None, None
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def test_nba_api_with_fallback():
    """Test NBA API with season fallback"""
    print("\n" + "="*70)
    print("TEST: NBA API Library - Knicks Most Recent Game (with season fallback)")
    print("="*70)
    
    try:
        from services.nba_api_library import NBAAPILibrary
        from nba_api.stats.endpoints import teamgamelog
        from nba_api.stats.static import teams
        
        # Find team
        team_dict = teams.get_teams()
        team_id = None
        team_abbrev = None
        team_full_name = None
        
        for team in team_dict:
            if 'knicks' in team['full_name'].lower() or team['abbreviation'] == 'NYK':
                team_id = team['id']
                team_abbrev = team['abbreviation']
                team_full_name = team['full_name']
                break
        
        if not team_id:
            print("❌ Could not find Knicks team ID")
            return None
        
        print(f"Found team: {team_full_name} (ID: {team_id})")
        
        # Try multiple seasons
        seasons_to_try = ['2024-25', '2023-24', '2025-26']
        
        for season in seasons_to_try:
            print(f"\nTrying season: {season}")
            try:
                game_log = teamgamelog.TeamGameLog(
                    team_id=team_id,
                    season=season
                )
                
                import time
                time.sleep(0.6)  # Rate limit
                
                data_dict = game_log.get_dict()
                result_sets = data_dict.get('resultSets', [])
                
                if result_sets:
                    result_set = result_sets[0]
                    headers = result_set.get('headers', [])
                    row_set = result_set.get('rowSet', [])
                    
                    if row_set:
                        latest_game = dict(zip(headers, row_set[0]))
                        game_date = latest_game.get('GAME_DATE', '')
                        matchup = latest_game.get('MATCHUP', '')
                        wl = latest_game.get('WL', '')
                        team_score = int(latest_game.get('PTS', 0) or 0)
                        
                        print(f"✅ Found game in season {season}:")
                        print(f"  Date: {game_date}")
                        print(f"  Matchup: {matchup}")
                        print(f"  Result: {wl}")
                        print(f"  Score: {team_score}")
                        
                        # Parse opponent and get opponent score
                        opponent_abbrev = matchup.split()[-1] if '@' in matchup or 'vs' in matchup else ''
                        
                        return {
                            'team_name': 'Knicks',
                            'opponent_name': opponent_abbrev,
                            'game_date': game_date,
                            'team_score': team_score,
                            'did_win': wl == 'W',
                            'season': season
                        }
            except Exception as e:
                print(f"  ⚠️  Season {season} failed: {e}")
                continue
        
        print("\n❌ No games found in any season")
        return None
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_full_chatbot():
    """Test the full chatbot query"""
    print("\n" + "="*70)
    print("TEST: Full Chatbot Query")
    print("="*70)
    
    try:
        from chatbot import BasketballChatbot
        
        chatbot = BasketballChatbot()
        query = "Did the Knicks win their most recent game?"
        
        print(f"\nQuery: {query}")
        print("Processing through full chatbot...")
        
        response = chatbot.process_question(query)
        
        print("\n" + "="*70)
        print("CHATBOT RESPONSE:")
        print("="*70)
        print(f"\n{response}\n")
        
        return response
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("COMPREHENSIVE TEST: Did the Knicks win their most recent game?")
    print("="*70)
    print("\nThis test will:")
    print("  1. Query ESPN API (primary - most reliable)")
    print("  2. Query NBA API Library with season fallback")
    print("  3. Test full chatbot response")
    print("\n")
    
    # Test 1: ESPN API (PRIMARY - Most Reliable)
    espn_result, espn_answer = test_espn_api()
    
    # Test 2: NBA API with fallback
    nba_result = test_nba_api_with_fallback()
    
    # Validate
    if espn_result and nba_result:
        print("\n" + "="*70)
        print("VALIDATION: Comparing API Results")
        print("="*70)
        
        espn_win = espn_result.get('did_win')
        nba_win = nba_result.get('did_win')
        
        print(f"\nESPN API Result:")
        print(f"  Did Win: {espn_win}")
        print(f"  Date: {espn_result.get('game_date')}")
        
        print(f"\nNBA API Result:")
        print(f"  Did Win: {nba_win}")
        print(f"  Date: {nba_result.get('game_date')}")
        print(f"  Season: {nba_result.get('season')}")
        
        if espn_win == nba_win:
            print("\n✅ VALIDATION PASSED: Both APIs agree on win/loss result")
        else:
            print("\n⚠️  WARNING: APIs disagree on win/loss result")
            print("Using ESPN API result as primary source (most reliable for recent games)")
    
    # Test 3: Full chatbot
    print("\n" + "="*70)
    print("Run full chatbot test?")
    print("="*70)
    response = input("Continue with full chatbot test? (y/n): ").strip().lower()
    
    chatbot_response = None
    if response == 'y':
        chatbot_response = test_full_chatbot()
    
    # Final Summary
    print("\n" + "="*70)
    print("FINAL ANSWER SUMMARY")
    print("="*70)
    
    if espn_result:
        did_win = espn_result.get('did_win', False)
        team_score = espn_result.get('team_score', 0)
        opponent_score = espn_result.get('opponent_score', 0)
        opponent_name = espn_result.get('opponent_name', 'Unknown')
        game_date = espn_result.get('game_date', 'Unknown date')
        
        print(f"\nQuestion: Did the Knicks win their most recent game?")
        print(f"\nAnswer: {'YES' if did_win else 'NO'}")
        print(f"\nDetails:")
        print(f"  - Game Date: {game_date}")
        print(f"  - Opponent: {opponent_name}")
        print(f"  - Score: Knicks {team_score} - {opponent_name} {opponent_score}")
        print(f"  - Result: {'WIN' if did_win else 'LOSS'}")
        print(f"\nSource: ESPN API (Most Reliable for Recent Games)")
        
        if nba_result:
            print(f"\nNBA API Validation:")
            print(f"  - Season: {nba_result.get('season')}")
            print(f"  - Result: {'WIN' if nba_result.get('did_win') else 'LOSS'}")
            print(f"  - Date: {nba_result.get('game_date')}")
        
        if chatbot_response:
            print(f"\nFull Chatbot Response:")
            print(f"  {chatbot_response}")
    else:
        print("\n❌ Could not retrieve answer from ESPN API")
        if nba_result:
            print("\nNBA API Result (fallback):")
            print(f"  Did Win: {nba_result.get('did_win')}")
            print(f"  Date: {nba_result.get('game_date')}")
        else:
            print("Please check:")
            print("  - Internet connection")
            print("  - API availability")
            print("  - Rate limiting")
    
    print("="*70)


if __name__ == "__main__":
    main()

