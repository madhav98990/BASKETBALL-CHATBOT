"""STEP 2: Test NBA API with headers"""
from nba_api.stats.endpoints import leagueleaders

# Set headers (MOST COMMON FIX)
try:
    from nba_api.stats.library.http import NBAStatsHTTP
    NBAStatsHTTP.headers = {
        "Host": "stats.nba.com",
        "Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*",
        "x-nba-stats-token": "true",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "x-nba-stats-origin": "stats",
        "Referer": "https://www.nba.com/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9"
    }
    print("✓ Headers set")
except Exception as e:
    print(f"Warning: Could not set headers: {e}")

print("\n" + "=" * 70)
print("Testing NBA API with headers")
print("=" * 70)

try:
    leaders = leagueleaders.LeagueLeaders(
        season="2024-25",
        season_type_all_star="Regular Season",
        stat_category_abbreviation="PTS",
        per_mode48="PerGame",
        scope="S"
    )
    
    import time
    time.sleep(1)  # Rate limit
    
    df = leaders.get_data_frames()[0]
    
    print(f"\n✓ SUCCESS! Retrieved {len(df)} players")
    print(f"\nTop 5 players in Points Per Game:")
    print(df.head(5)[["PLAYER", "TEAM", "PTS", "GP"]])
    
except Exception as e:
    print(f"\n✗ FAILED: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()

