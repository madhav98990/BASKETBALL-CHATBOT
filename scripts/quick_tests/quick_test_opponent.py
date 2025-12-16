"""Quick test to verify opponent name"""
from services.direct_espn_fetcher import DirectESPNFetcher

fetcher = DirectESPNFetcher()
result = fetcher.get_team_most_recent_game_result("New York Knicks", days_back=3)

if result:
    print(f"\n✅ Result found:")
    print(f"  Team: {result.get('team_name')}")
    print(f"  Opponent: {result.get('opponent_name')}")
    print(f"  Matchup: {result.get('matchup')}")
    print(f"  Score: {result.get('team_score')}-{result.get('opponent_score')}")
    print(f"  Did Win: {result.get('did_win')}")
    
    # Check if opponent is correct
    matchup = result.get('matchup', '')
    opponent = result.get('opponent_name', '')
    
    if 'Orlando' in matchup and 'Orlando' in opponent:
        print(f"\n✅ Opponent name is CORRECT: {opponent}")
    elif 'Orlando' in matchup and 'Orlando' not in opponent:
        print(f"\n❌ Opponent name is WRONG: Expected Orlando Magic, got {opponent}")
    else:
        print(f"\n⚠️  Could not verify opponent name")
else:
    print("❌ No result found")

