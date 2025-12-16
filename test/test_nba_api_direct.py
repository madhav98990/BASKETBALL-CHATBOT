"""STEP 1: Test NBA API directly - NO AGENT"""
from nba_api.stats.endpoints import leagueleaders

print("=" * 70)
print("STEP 1: Testing NBA API LeagueLeaders Directly")
print("=" * 70)

try:
    print("\nCreating LeagueLeaders object...")
    leaders = leagueleaders.LeagueLeaders(
        season="2024-25",
        season_type_all_star="Regular Season",
        stat_category_abbreviation="PTS",
        per_mode48="PerGame",
        scope="S"
    )
    
    print("Getting DataFrame...")
    df = leaders.get_data_frames()[0]
    
    print("\n✓ SUCCESS! DataFrame retrieved")
    print(f"Shape: {df.shape}")
    print(f"\nTop 5 players in Points Per Game:")
    print(df.head(5)[["PLAYER", "PTS"]])
    
except Exception as e:
    print(f"\n✗ FAILED: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
