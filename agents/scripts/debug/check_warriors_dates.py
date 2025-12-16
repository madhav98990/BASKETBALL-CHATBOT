import requests

url = 'http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard'
resp = requests.get(url, params={'dates': '20251208,20251209,20251210,20251211'}, timeout=10)

if resp.status_code == 200:
    data = resp.json()
    events = data.get('events', [])
    
    print(f'Total events: {len(events)}')
    
    warriors_games = []
    for event in events:
        comp = event.get('competitions', [{}])[0]
        competitors = comp.get('competitors', [])
        
        if len(competitors) >= 2:
            team1 = competitors[0].get('team', {}).get('displayName', '')
            team2 = competitors[1].get('team', {}).get('displayName', '')
            
            if 'Warriors' in team1 or 'Warriors' in team2:
                date = event.get('date', '')
                warriors_games.append({
                    'date': date,
                    'teams': f"{team1} vs {team2}",
                    'id': event.get('id')
                })
    
    print('\nWarriors games (in order):')
    for i, game in enumerate(warriors_games):
        print(f"{i+1}. {game['date']} - {game['teams']}")
        print(f"   ID: {game['id']}")
