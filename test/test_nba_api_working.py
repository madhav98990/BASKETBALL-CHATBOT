"""
STEP 1: Verify NBA API works (using dictionary method to avoid pandas issues)
"""
from nba_api.stats.endpoints import leagueleaders
from nba_api.stats.library.http import NBAStatsHTTP

# Set headers (MANDATORY)
NBAStatsHTTP.headers = {
    "Host": "stats.nba.com",
    "Connection": "keep-alive",
    "Accept": "application/json, text/plain, */*",
    "x-nba-stats-token": "true",
    "User-Agent": "Mozilla/5.0",
    "x-nba-stats-origin": "stats",
    "Referer": "https://www.nba.com/",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9"
}

import sys
import time

print("Testing NBA API LeagueLeaders endpoint...", flush=True)
sys.stdout.flush()
print("=" * 50, flush=True)

try:
    print("Creating LeagueLeaders object...", flush=True)
    leaders = leagueleaders.LeagueLeaders(
        season="2024-25",
        season_type_all_star="Regular Season",
        stat_category_abbreviation="PTS",
        per_mode48="PerGame",
        scope="S"
    )
    
    print("API call made, waiting for response...", flush=True)
    time.sleep(1)
    
    # Use dictionary method instead of DataFrame (avoids pandas conversion issues)
    print("Getting dictionary data...", flush=True)
    data_dict = leaders.get_dict()
    print("Got dictionary data!", flush=True)
    result_sets = data_dict.get('resultSets', [])
    
    if not result_sets or not result_sets[0].get('rowSet'):
        print("❌ FAILED: Empty response from API")
        exit(1)
    
    result_set = result_sets[0]
    headers = result_set.get('headers', [])
    row_set = result_set.get('rowSet', [])
    
    print(f"\n✅ SUCCESS! NBA API is working!")
    print(f"Found {len(row_set)} players")
    print("\nTop 5 players in Points Per Game:")
    print("-" * 50)
    
    # Get top 5 by PTS (already sorted by API)
    top5_data = []
    for row in row_set[:5]:
        player_dict = dict(zip(headers, row))
        player = player_dict.get('PLAYER', 'Unknown')
        pts = player_dict.get('PTS', 0)
        top5_data.append((player, pts))
    
    for idx, (player, pts) in enumerate(top5_data, 1):
        print(f"{idx}. {player} – {pts} PPG")
    
    print("\n" + "=" * 50)
    print("✅ API test PASSED - Your chatbot can use NBA API!")
    
except Exception as e:
    print(f"\n❌ FAILED! Error: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    print("\n" + "=" * 50)
    print("❌ API test FAILED - Check the error above")
    print("\nCommon issues:")
    print("1. Timeout? → Network/API issue")
    print("2. JSONDecodeError? → API returned invalid data")
    print("3. Empty dataframe? → No data for this season")
    print("4. 403/429? → Rate limiting or blocking")
    import traceback
    traceback.print_exc()
    exit(1)
