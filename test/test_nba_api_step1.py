"""
STEP 1: Verify NBA API works
Run this exact code to test if NBA API is working
"""
from nba_api.stats.endpoints import leagueleaders

# Set headers (MOST COMMON FIX)
from nba_api.stats.library.http import NBAStatsHTTP

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

print("Testing NBA API LeagueLeaders endpoint...")
print("=" * 50)

try:
    leaders = leagueleaders.LeagueLeaders(
        season="2024-25",
        season_type_all_star="Regular Season",
        stat_category_abbreviation="PTS",
        per_mode48="PerGame",
        scope="S"
    )
    
    df = leaders.get_data_frames()[0]
    print("\n✅ SUCCESS! NBA API is working!")
    print("\nTop 5 players in Points Per Game:")
    print("-" * 50)
    top5 = df.head(5)
    for idx, (_, row) in enumerate(top5.iterrows(), 1):
        player = row.get("PLAYER", "Unknown")
        pts = row.get("PTS", 0)
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
    raise

