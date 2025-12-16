"""
STEP 5: Minimal Agent Tool Function (No Abstraction)
Direct tool function for top 5 PPG players
"""
from nba_api.stats.endpoints import leagueleaders
from nba_api.stats.library.http import NBAStatsHTTP

# Set headers (MANDATORY - prevents NBA from blocking requests)
NBAStatsHTTP.headers = {
    "Host": "stats.nba.com",
    "Connection": "keep-alive",
    "Accept": "application/json, text/plain, */*",
    "x-nba-stats-token": "true",
    "User-Agent": "Mozilla/5.0",
    "x-nba-stats-origin": "stats",
    "Referer": "https://www.nba.com/",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9"
}


def top_5_ppg_tool():
    """
    Get top 5 players by points per game for 2024-25 season
    
    Returns:
        list: List of dicts with 'player' and 'ppg' keys
    """
    try:
        import time
        print("Calling LeagueLeaders API...", flush=True)
        leaders = leagueleaders.LeagueLeaders(
            season="2024-25",
            season_type_all_star="Regular Season",
            stat_category_abbreviation="PTS",
            per_mode48="PerGame",
            scope="S"
        )
        
        print("Waiting for API response...", flush=True)
        time.sleep(1)
        
        # Use dictionary method (more reliable than DataFrame)
        print("Getting dictionary data...", flush=True)
        data_dict = leaders.get_dict()
        print(f"Got dict keys: {list(data_dict.keys())}", flush=True)
        
        # Try both 'resultSets' (plural) and 'resultSet' (singular)
        result_sets = data_dict.get('resultSets', [])
        if not result_sets:
            # Some API versions return 'resultSet' (singular)
            result_set_single = data_dict.get('resultSet')
            if result_set_single:
                result_sets = [result_set_single]
        
        print(f"Found {len(result_sets)} result sets", flush=True)
        
        if not result_sets:
            print("ERROR: No result sets found", flush=True)
            return []
        
        if not result_sets[0].get('rowSet'):
            print("ERROR: First result set has no rowSet", flush=True)
            print(f"Result set keys: {list(result_sets[0].keys())}", flush=True)
            return []
        
        result_set = result_sets[0]
        headers = result_set.get('headers', [])
        row_set = result_set.get('rowSet', [])
        
        print(f"Found {len(row_set)} players", flush=True)
        
        result = []
        # Get top 5 (already sorted by API)
        for row in row_set[:5]:
            player_dict = dict(zip(headers, row))
            player_name = player_dict.get("PLAYER", "Unknown")
            pts = player_dict.get("PTS", 0)
            result.append({
                "player": player_name,
                "ppg": float(pts) if pts else 0.0
            })
        
        return result
        
    except Exception as e:
        import traceback
        print(f"ERROR in top_5_ppg_tool: {type(e).__name__}: {str(e)}", flush=True)
        traceback.print_exc()
        return []


if __name__ == "__main__":
    # STEP 7: Hard-Test (Bypass Agent Thinking)
    print("Testing top_5_ppg_tool() directly...")
    print("=" * 50)
    result = top_5_ppg_tool()
    
    if result:
        print("\n✅ SUCCESS! Tool returned data:")
        print("-" * 50)
        for idx, player_data in enumerate(result, 1):
            print(f"{idx}. {player_data['player']} – {player_data['ppg']} PPG")
        print("\n✅ Tool is working - Agent can use this!")
    else:
        print("\n❌ FAILED: Tool returned empty list")
        print("Check NBA API connection and headers")

