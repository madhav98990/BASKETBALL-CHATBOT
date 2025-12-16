"""
Validation script for standings queries
Tests: "Are the Oklahoma City Thunder still in the top 3 of the West?"
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.standings_agent import StandingsAgent
from agents.response_formatter_agent import ResponseFormatterAgent
from services.direct_espn_fetcher import DirectESPNFetcher
from services.nba_api_library import NBAAPILibrary

def validate_thunder_top3_query():
    """Validate the query: Are the Oklahoma City Thunder still in the top 3 of the West?"""
    print("\n" + "="*80)
    print("VALIDATION: Oklahoma City Thunder Top 3 Query")
    print("="*80)
    
    query = "Are the Oklahoma City Thunder still in the top 3 of the West?"
    print(f"\nQuery: {query}\n")
    
    # Step 1: Test ESPN API directly
    print("--- Step 1: Testing ESPN API Directly ---")
    try:
        espn_fetcher = DirectESPNFetcher()
        espn_standings = espn_fetcher.get_standings('West')
        
        if espn_standings:
            print(f"✅ ESPN API returned {len(espn_standings)} Western Conference teams")
            
            # Find Thunder
            thunder_standing = None
            for standing in espn_standings:
                team_name = standing.get('team_name', '').lower()
                if 'thunder' in team_name or 'okc' in team_name or 'oklahoma' in team_name:
                    thunder_standing = standing
                    break
            
            if thunder_standing:
                rank = thunder_standing.get('conference_rank', 0)
                wins = thunder_standing.get('wins', 0)
                losses = thunder_standing.get('losses', 0)
                win_pct = thunder_standing.get('win_percentage', 0)
                is_top3 = rank <= 3
                
                print(f"  Team: {thunder_standing.get('team_name')}")
                print(f"  Conference Rank: {rank}")
                print(f"  Record: {wins}-{losses} ({win_pct:.3f})")
                print(f"  In Top 3: {'YES' if is_top3 else 'NO'}")
                
                # Show top 3 teams
                print(f"\n  Top 3 in West:")
                top3 = sorted(espn_standings, key=lambda x: x.get('conference_rank', 0))[:3]
                for i, team in enumerate(top3, 1):
                    print(f"    {i}. {team.get('team_name')} - {team.get('wins')}-{team.get('losses')} (Rank: {team.get('conference_rank')})")
            else:
                print("  ⚠️  Thunder not found in ESPN standings")
        else:
            print("  ⚠️  ESPN API returned no standings")
    except Exception as e:
        print(f"  ❌ ESPN API Error: {e}")
    
    # Step 2: Test NBA API Library
    print("\n--- Step 2: Testing NBA API Library ---")
    try:
        nba_api = NBAAPILibrary()
        nba_standings = nba_api.get_standings('West')
        
        if nba_standings:
            print(f"✅ NBA API Library returned {len(nba_standings)} Western Conference teams")
            
            # Find Thunder
            thunder_standing = None
            for standing in nba_standings:
                team_name = standing.get('team_name', '').lower()
                if 'thunder' in team_name or 'okc' in team_name or 'oklahoma' in team_name:
                    thunder_standing = standing
                    break
            
            if thunder_standing:
                rank = thunder_standing.get('conference_rank', 0)
                wins = thunder_standing.get('wins', 0)
                losses = thunder_standing.get('losses', 0)
                win_pct = thunder_standing.get('win_percentage', 0)
                is_top3 = rank <= 3
                
                print(f"  Team: {thunder_standing.get('team_name')}")
                print(f"  Conference Rank: {rank}")
                print(f"  Record: {wins}-{losses} ({win_pct:.3f})")
                print(f"  In Top 3: {'YES' if is_top3 else 'NO'}")
            else:
                print("  ⚠️  Thunder not found in NBA API standings")
        else:
            print("  ⚠️  NBA API Library returned no standings")
    except Exception as e:
        print(f"  ❌ NBA API Library Error: {e}")
    
    # Step 3: Test Standings Agent
    print("\n--- Step 3: Testing Standings Agent ---")
    try:
        agent = StandingsAgent()
        result = agent.process_query(query)
        
        if result and result.get('team_position_query'):
            team = result.get('team', '')
            actual_rank = result.get('actual_rank', 0)
            target_position = result.get('target_position', 0)
            is_in_top = result.get('is_in_top', False)
            wins = result.get('wins', 0)
            losses = result.get('losses', 0)
            win_pct = result.get('win_percentage', 0)
            conference = result.get('conference', '')
            
            print(f"✅ Standings Agent processed query successfully")
            print(f"  Team: {team}")
            print(f"  Conference: {conference}")
            print(f"  Actual Rank: {actual_rank}")
            print(f"  Target Position: Top {target_position}")
            print(f"  In Top {target_position}: {'YES' if is_in_top else 'NO'}")
            print(f"  Record: {wins}-{losses} ({win_pct:.3f})")
            print(f"  Source: {result.get('source', 'unknown')}")
            
            # Validation
            if actual_rank <= 0 or actual_rank > 15:
                print(f"  ⚠️  WARNING: Invalid rank {actual_rank}")
            if wins < 0 or losses < 0:
                print(f"  ⚠️  WARNING: Invalid record {wins}-{losses}")
            if is_in_top != (actual_rank <= target_position):
                print(f"  ❌ ERROR: is_in_top mismatch! {is_in_top} vs expected {actual_rank <= target_position}")
            else:
                print(f"  ✅ Validation passed")
        else:
            print(f"  ⚠️  Standings Agent did not process as team_position_query")
            if result:
                print(f"  Result type: {result.get('type', 'unknown')}")
                print(f"  Error: {result.get('error', 'None')}")
    except Exception as e:
        print(f"  ❌ Standings Agent Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 4: Test Full Pipeline (Agent + Response Formatter)
    print("\n--- Step 4: Testing Full Pipeline (Agent + Response Formatter) ---")
    try:
        agent = StandingsAgent()
        formatter = ResponseFormatterAgent()
        
        result = agent.process_query(query)
        if result and result.get('team_position_query'):
            response = formatter.format_response(result)
            print(f"✅ Full pipeline response:")
            print(f"  {response}")
            
            # Validate response contains key information
            team_name = result.get('team', '').title()
            if team_name.lower() in response.lower():
                print(f"  ✅ Response contains team name")
            else:
                print(f"  ⚠️  Response missing team name")
            
            if str(result.get('actual_rank', 0)) in response or 'rank' in response.lower():
                print(f"  ✅ Response contains rank information")
            else:
                print(f"  ⚠️  Response missing rank information")
            
            if ('yes' in response.lower() and result.get('is_in_top')) or ('no' in response.lower() and not result.get('is_in_top')):
                print(f"  ✅ Response correctly indicates top 3 status")
            else:
                print(f"  ⚠️  Response may not correctly indicate top 3 status")
        else:
            print(f"  ⚠️  Could not process query through full pipeline")
    except Exception as e:
        print(f"  ❌ Full Pipeline Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("VALIDATION COMPLETE")
    print("="*80)


if __name__ == "__main__":
    validate_thunder_top3_query()

