"""Debug NBA API to see what's happening"""
import sys
import os
# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from nba_api.stats.endpoints import leagueleaders
import time
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

print("=" * 70)
print("Debugging NBA API LeagueLeaders")
print("=" * 70)

seasons_to_test = ['2025-26', '2024-25', '2023-24']

for season in seasons_to_test:
    print(f"\n{'='*70}")
    print(f"Testing season: {season}")
    print(f"{'='*70}")
    
    try:
        print(f"Creating LeagueLeaders object...")
        leaders = leagueleaders.LeagueLeaders(
            season=season,
            season_type_all_star='Regular Season',
            stat_category_abbreviation='PTS'
        )
        
        print(f"Waiting for rate limit...")
        time.sleep(1)
        
        print(f"Getting data dictionary...")
        data_dict = leaders.get_dict()
        
        print(f"Checking result sets...")
        result_sets = data_dict.get('resultSets', [])
        print(f"  Number of result sets: {len(result_sets)}")
        
        if result_sets:
            result_set = result_sets[0]
            headers = result_set.get('headers', [])
            row_set = result_set.get('rowSet', [])
            
            print(f"  Headers: {len(headers)} columns")
            print(f"  Rows: {len(row_set)} players")
            
            if row_set:
                print(f"\n✓ SUCCESS! Season {season} has data")
                print(f"\nFirst 3 players:")
                for i, row in enumerate(row_set[:3], 1):
                    player_dict = dict(zip(headers, row))
                    name = player_dict.get('PLAYER', 'Unknown')
                    team = player_dict.get('TEAM', '')
                    pts = player_dict.get('PTS', 0)
                    reb = player_dict.get('REB', 0)
                    ast = player_dict.get('AST', 0)
                    fg_pct = player_dict.get('FG_PCT', 0)
                    print(f"  {i}. {name} ({team}): {pts} PPG, {reb} RPG, {ast} APG, {fg_pct*100:.1f}% FG")
                break
            else:
                print(f"  ✗ No rows in result set")
        else:
            print(f"  ✗ No result sets returned")
            
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        continue

print(f"\n{'='*70}")
print("Debug complete")
print(f"{'='*70}")

