#!/usr/bin/env python3
"""Check what recent games are available in ESPN API"""

from services.espn_api import ESPNNBAApi

espn = ESPNNBAApi()

# Get recent games
games = espn.get_recent_games(days=7, limit=20)
print(f"Found {len(games)} games in the last 7 days\n")

# Look for Nuggets games
for game in games:
    team1 = game.get('team1_name', '').upper()
    team2 = game.get('team2_name', '').upper()
    if 'DEN' in team1 or 'DEN' in team2 or 'NUGGETS' in team1 or 'NUGGETS' in team2:
        print(f"✓ NUGGETS GAME: {game.get('team1_name')} vs {game.get('team2_name')} - {game.get('match_date')}")

print("\nFirst 10 games:")
for game in games[:10]:
    print(f"{game.get('team1_name')} vs {game.get('team2_name')} - {game.get('match_date')}")
