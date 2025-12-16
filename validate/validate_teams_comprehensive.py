"""
Comprehensive validation script for team game results across all NBA teams
Tests ESPN API and validates results for accuracy
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.direct_espn_fetcher import DirectESPNFetcher
from agents.stats_agent import StatsAgent
from datetime import datetime

def validate_team_result(team_name: str, fetcher: DirectESPNFetcher) -> dict:
    """Validate a single team's result and return validation report"""
    result = {
        'team': team_name,
        'success': False,
        'has_result': False,
        'errors': [],
        'warnings': [],
        'data': None
    }
    
    try:
        # Test the API
        api_result = fetcher.get_team_most_recent_game_result(team_name, days_back=30)
        
        if not api_result:
            result['errors'].append(f"No result returned from API for {team_name}")
            return result
        
        result['has_result'] = True
        result['data'] = api_result
        
        # Validate required fields
        required_fields = ['team_name', 'team_abbrev', 'opponent_name', 'team_score', 'opponent_score', 'did_win', 'game_date', 'matchup']
        for field in required_fields:
            if field not in api_result or api_result[field] is None:
                result['errors'].append(f"Missing required field: {field}")
        
        # Validate scores
        team_score = api_result.get('team_score', 0)
        opponent_score = api_result.get('opponent_score', 0)
        
        if team_score <= 0:
            result['errors'].append(f"Invalid team score: {team_score}")
        if opponent_score <= 0:
            result['errors'].append(f"Invalid opponent score: {opponent_score}")
        
        # Validate scores are reasonable (NBA games typically 80-150 points)
        if team_score < 50 or team_score > 200:
            result['warnings'].append(f"Unusual team score: {team_score}")
        if opponent_score < 50 or opponent_score > 200:
            result['warnings'].append(f"Unusual opponent score: {opponent_score}")
        
        # Validate win/loss logic
        did_win = api_result.get('did_win', False)
        expected_win = team_score > opponent_score
        if did_win != expected_win:
            result['errors'].append(f"Win/loss mismatch: did_win={did_win} but scores {team_score}-{opponent_score} (expected win={expected_win})")
        
        # Validate opponent name is different from team name
        team_name_val = api_result.get('team_name', '').upper()
        opponent_name = api_result.get('opponent_name', '').upper()
        if not opponent_name:
            result['errors'].append("Opponent name is empty")
        elif opponent_name == team_name_val:
            result['errors'].append(f"Opponent name '{opponent_name}' is same as team name")
        
        # Validate game date
        game_date = api_result.get('game_date', '')
        if not game_date:
            result['errors'].append("Game date is missing")
        else:
            # Check date is recent (within last 30 days)
            try:
                # Try to parse date (could be various formats)
                if '-' in game_date:
                    date_parts = game_date.split('-')
                    if len(date_parts) >= 3:
                        date_obj = datetime(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
                        from datetime import date, timedelta
                        days_ago = (date.today() - date_obj.date()).days
                        if days_ago > 30:
                            result['warnings'].append(f"Game date is {days_ago} days ago (older than expected)")
            except:
                result['warnings'].append(f"Could not parse game date: {game_date}")
        
        # If no errors, mark as success
        if not result['errors']:
            result['success'] = True
            
    except Exception as e:
        result['errors'].append(f"Exception occurred: {str(e)}")
        import traceback
        result['errors'].append(f"Traceback: {traceback.format_exc()}")
    
    return result


def validate_multiple_teams():
    """Validate results for multiple teams"""
    print("\n" + "="*80)
    print("COMPREHENSIVE TEAM VALIDATION")
    print("="*80)
    
    # Test with various team name formats
    test_teams = [
        # Standard names
        'warriors', 'lakers', 'celtics', 'bucks', 'nuggets', 'suns', 'heat',
        'knicks', 'hawks', 'thunder', 'kings', 'pelicans', 'grizzlies', 'raptors',
        # Full names
        'golden state warriors', 'los angeles lakers', 'boston celtics',
        'new york knicks', 'oklahoma city thunder',
        # Variations
        'gsw', '76ers', 'sixers', 'trail blazers', 'blazers'
    ]
    
    fetcher = DirectESPNFetcher()
    results = []
    
    print(f"\nTesting {len(test_teams)} team name variations...\n")
    
    for team_name in test_teams:
        print(f"Testing: {team_name:30s} ", end='', flush=True)
        result = validate_team_result(team_name, fetcher)
        results.append(result)
        
        if result['success']:
            print(f"✅ PASS - {result['data'].get('team_name')} {'WON' if result['data'].get('did_win') else 'LOST'} {result['data'].get('team_score')}-{result['data'].get('opponent_score')} vs {result['data'].get('opponent_name')} on {result['data'].get('game_date')}")
        elif result['has_result']:
            status = "⚠️  WARNINGS" if result['warnings'] and not result['errors'] else "❌ ERRORS"
            print(f"{status}")
            for error in result['errors']:
                print(f"    ERROR: {error}")
            for warning in result['warnings']:
                print(f"    WARNING: {warning}")
        else:
            print(f"❌ NO RESULT")
    
    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    successful = [r for r in results if r['success']]
    with_warnings = [r for r in results if r['has_result'] and r['warnings'] and not r['errors']]
    with_errors = [r for r in results if r['errors']]
    no_result = [r for r in results if not r['has_result']]
    
    print(f"\n✅ Successful validations: {len(successful)}/{len(results)}")
    print(f"⚠️  With warnings only: {len(with_warnings)}/{len(results)}")
    print(f"❌ With errors: {len(with_errors)}/{len(results)}")
    print(f"❌ No result: {len(no_result)}/{len(results)}")
    
    # Show errors
    if with_errors:
        print("\n--- Teams with Errors ---")
        for result in with_errors:
            print(f"\n{result['team']}:")
            for error in result['errors']:
                print(f"  - {error}")
    
    # Show warnings
    if with_warnings:
        print("\n--- Teams with Warnings ---")
        for result in with_warnings:
            print(f"\n{result['team']}:")
            for warning in result['warnings']:
                print(f"  - {warning}")
    
    # Test with Stats Agent
    print("\n" + "="*80)
    print("TESTING STATS AGENT INTEGRATION")
    print("="*80)
    
    agent = StatsAgent()
    test_queries = [
        "Did the warriors win their most recent game?",
        "Did the lakers win their most recent game?",
        "Did the knicks win their most recent game?",
        "Did the celtics win their most recent game?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            agent_result = agent.process_query(query)
            if agent_result and agent_result.get('win_query'):
                if agent_result.get('error'):
                    print(f"  ❌ Error: {agent_result.get('error')}")
                else:
                    did_win = agent_result.get('did_win', False)
                    team = agent_result.get('team', '')
                    score = f"{agent_result.get('team_score', 0)}-{agent_result.get('opponent_score', 0)}"
                    opponent = agent_result.get('opponent_name', '')
                    game_date = agent_result.get('game_date', '')
                    print(f"  ✅ Result: {team} {'WON' if did_win else 'LOST'} {score} vs {opponent} on {game_date}")
            else:
                print(f"  ⚠️  Not processed as win query")
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
    
    print("\n" + "="*80)
    print("VALIDATION COMPLETE")
    print("="*80)
    
    return results


if __name__ == "__main__":
    validate_multiple_teams()

