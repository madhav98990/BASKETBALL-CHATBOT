#!/usr/bin/env python3
import sys
sys.path.append('.')
import requests

# Get Lakers game boxscore directly
url = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary"
params = {'event': '401810191'}  # TOR vs LAL game

resp = requests.get(url, params=params, timeout=5)
if resp.status_code == 200:
    data = resp.json()
    boxscore = data.get('boxscore', {})
    comps = boxscore.get('competitions', [])
    if comps:
        comp = comps[0]
        competitors = comp.get('competitors', [])
        
        for c in competitors:
            team = c.get('team', {})
            team_name = team.get('displayName', 'Unknown')
            print(f"\n{team_name} players:")
            
            roster = c.get('roster', {})
            entries = roster.get('entries', [])
            
            # Check all players in this team
            found_lebron = False
            for entry in entries:
                athlete = entry.get('athlete', {})
                name = athlete.get('displayName', 'Unknown')
                
                # Check if this is LeBron
                if 'LeBron' in name or name == 'LeBron James':
                    print(f"  ✓✓✓ {name} FOUND!")
                    found_lebron = True
                else:
                    print(f"  - {name}")
            
            if not found_lebron and 'Lakers' in team_name:
                print("  (LeBron James NOT in Lakers roster)")
else:
    print(f"Error: {resp.status_code}")
