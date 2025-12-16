"""Simple test for top 5 players by PPG"""
from nba_api.stats.endpoints import leaguedashplayerstats
import time

print("Testing simple approach...")
try:
    # Try 2024-25 season
    stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season='2024-25',
        season_type_all_star='Regular Season',
        per_mode_detailed='PerGame'
    )
    time.sleep(1)
    
    df = stats.get_data_frames()[0]
    print(f"Got {len(df)} players")
    
    # Sort by PTS and get top 5
    top5 = df.nlargest(5, 'PTS')
    
    print("\nTop 5 by PPG:")
    for idx, row in top5.iterrows():
        print(f"{row['PLAYER_NAME']} ({row['TEAM_ABBREVIATION']}): {row['PTS']:.1f} PPG")
except Exception as e:
    print(f"Error: {e}")

