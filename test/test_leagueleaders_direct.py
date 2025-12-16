"""Direct test of LeagueLeaders endpoint"""
from nba_api.stats.endpoints import leagueleaders
import time

print("Testing LeagueLeaders endpoint directly...")
print("=" * 70)

# Test with 2024-25 season
try:
    print("\n1. Creating LeagueLeaders object for 2024-25 season, PTS stat...")
    leaders = leagueleaders.LeagueLeaders(
        season='2024-25',
        season_type_all_star='Regular Season',
        stat_category_abbreviation='PTS'
    )
    
    print("2. Waiting for API response...")
    time.sleep(2)
    
    print("3. Getting DataFrame...")
    df = leaders.get_data_frames()[0]
    
    print(f"4. Got {len(df)} players total")
    
    if len(df) > 0:
        print("\n5. Sorting by PTS and getting top 5...")
        # Sort by PTS descending (should already be sorted, but ensure it)
        top5 = df.nlargest(5, 'PTS')
        
        print("\n" + "=" * 70)
        print("TOP 5 PLAYERS BY POINTS PER GAME:")
        print("=" * 70)
        for i, (idx, row) in enumerate(top5.iterrows(), 1):
            name = row.get('PLAYER', 'Unknown')
            team = row.get('TEAM', '')
            pts = row.get('PTS', 0)
            gp = row.get('GP', 0)
            print(f"{i}. {name} ({team}): {pts:.1f} PPG ({gp} games)")
        
        print("\n✓ SUCCESS! LeagueLeaders endpoint is working.")
    else:
        print("\n✗ FAILED: No players in DataFrame")
        
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

