"""Test NBA API with specific season"""
from services.nba_api_library import NBAAPILibrary

api = NBAAPILibrary()
print("Testing with 2024-25 season directly...")
players = api.get_top_players_by_stat('points', limit=3, season='2024-25')

if players:
    print(f"\n✓ Got {len(players)} players:\n")
    for i, p in enumerate(players, 1):
        print(f"{i}. {p['player_name']} ({p['team']})")
        print(f"   Points: {p['stat_value']:.1f} PPG")
        print(f"   Rebounds: {p.get('rebounds', 0):.1f} RPG")
        print(f"   Assists: {p.get('assists', 0):.1f} APG")
        if p.get('field_goal_pct', 0) > 0:
            print(f"   FG%: {p['field_goal_pct']*100:.1f}%")
        print()
else:
    print("\n✗ No players returned")

