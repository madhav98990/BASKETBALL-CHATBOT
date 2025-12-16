"""Debug Thunder standings query"""
import sys
import os
# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from services.nba_api_library import NBAAPILibrary
from services.direct_espn_fetcher import DirectESPNFetcher
from agents.standings_agent import StandingsAgent
from agents.response_formatter_agent import ResponseFormatterAgent

query = "Are the Oklahoma City Thunder still in the top 3 of the West?"
print(f"Query: {query}\n")

# Test NBA API Library
print("="*70)
print("Testing NBA API Library")
print("="*70)
try:
    nba_api = NBAAPILibrary()
    west_standings = nba_api.get_standings('West')
    print(f"Got {len(west_standings)} teams from NBA API Library\n")
    
    # Find Thunder
    for standing in west_standings:
        team_name = standing.get('team_name', '').lower()
        if 'thunder' in team_name or 'okc' in team_name or 'oklahoma' in team_name:
            print(f"Found Thunder:")
            print(f"  Team Name: {standing.get('team_name')}")
            print(f"  Conference Rank: {standing.get('conference_rank')}")
            print(f"  Wins: {standing.get('wins')}")
            print(f"  Losses: {standing.get('losses')}")
            print(f"  Win %: {standing.get('win_percentage')}")
            print(f"  Conference: {standing.get('conference')}")
            break
    else:
        print("Thunder not found in standings")
        print("\nAll teams in West:")
        for i, s in enumerate(west_standings[:5], 1):
            print(f"  {i}. {s.get('team_name')} - Rank {s.get('conference_rank')}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# Test ESPN API
print("\n" + "="*70)
print("Testing ESPN API")
print("="*70)
try:
    espn_fetcher = DirectESPNFetcher()
    espn_standings = espn_fetcher.get_standings('West')
    print(f"Got {len(espn_standings)} teams from ESPN API\n")
    
    if espn_standings:
        # Find Thunder
        for standing in espn_standings:
            team_name = standing.get('team_name', '').lower()
            if 'thunder' in team_name or 'okc' in team_name or 'oklahoma' in team_name:
                print(f"Found Thunder:")
                print(f"  Team Name: {standing.get('team_name')}")
                print(f"  Conference Rank: {standing.get('conference_rank')}")
                print(f"  Wins: {standing.get('wins')}")
                print(f"  Losses: {standing.get('losses')}")
                print(f"  Win %: {standing.get('win_percentage')}")
                break
        else:
            print("Thunder not found in ESPN standings")
            print("\nAll teams in West:")
            for i, s in enumerate(espn_standings[:5], 1):
                print(f"  {i}. {s.get('team_name')} - Rank {s.get('conference_rank')}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# Test Standings Agent
print("\n" + "="*70)
print("Testing Standings Agent")
print("="*70)
try:
    agent = StandingsAgent()
    result = agent.process_query(query)
    
    if result:
        print(f"Result type: {result.get('type')}")
        print(f"Team position query: {result.get('team_position_query')}")
        if result.get('team_position_query'):
            print(f"\nTeam: {result.get('team')}")
            print(f"Actual Rank: {result.get('actual_rank')}")
            print(f"Target Position: Top {result.get('target_position')}")
            print(f"Is in Top 3: {result.get('is_in_top')}")
            print(f"Conference: {result.get('conference')}")
            print(f"Wins: {result.get('wins')}")
            print(f"Losses: {result.get('losses')}")
            print(f"Source: {result.get('source')}")
            
            # Test response formatter
            print("\n" + "="*70)
            print("Testing Response Formatter")
            print("="*70)
            formatter = ResponseFormatterAgent()
            response = formatter.format_response(result)
            print(f"Response: {response}")
        else:
            print(f"Error: {result.get('error')}")
    else:
        print("No result returned")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

