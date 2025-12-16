"""Simple test for LeagueLeaders"""
from nba_api.stats.endpoints import leagueleaders
import time

print("Testing LeagueLeaders for 2024-25 season...")
try:
    leaders = leagueleaders.LeagueLeaders(
        season='2024-25',
        season_type_all_star='Regular Season',
        stat_category_abbreviation='PTS'
    )
    print("Created LeagueLeaders object, waiting...")
    time.sleep(2)
    
    print("Getting data...")
    df = leaders.get_data_frames()[0]
    print(f"Got {len(df)} players")
    
    # Top 5 by PTS
    top5 = df.head(5)
    print("\nTop 5 by PTS:")
    for idx, row in top5.iterrows():
        print(f"{row['PLAYER']} ({row['TEAM']}): {row['PTS']:.1f} PPG")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

