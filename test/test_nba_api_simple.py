"""Simple NBA API test"""
import sys

print("Starting test...", flush=True)
sys.stdout.flush()

try:
    from nba_api.stats.endpoints import leagueleaders
    from nba_api.stats.library.http import NBAStatsHTTP
    
    print("Imports successful", flush=True)
    
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
    
    print("Headers set", flush=True)
    print("Calling LeagueLeaders...", flush=True)
    
    leaders = leagueleaders.LeagueLeaders(
        season="2024-25",
        season_type_all_star="Regular Season",
        stat_category_abbreviation="PTS",
        per_mode48="PerGame",
        scope="S"
    )
    
    print("API call made, getting data...", flush=True)
    df = leaders.get_data_frames()[0]
    
    print("\nSUCCESS!")
    print(f"DataFrame shape: {df.shape}")
    print("\nTop 5 players:")
    top5 = df.head(5)
    for idx, (_, row) in enumerate(top5.iterrows(), 1):
        player = row.get("PLAYER", "Unknown")
        pts = row.get("PTS", 0)
        print(f"{idx}. {player} - {pts} PPG")
    
except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {str(e)}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

