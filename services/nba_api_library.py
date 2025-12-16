"""
NBA API Library Service - Uses official nba_api to fetch player stats
This provides real NBA statistics using the nba_api Python library
"""
import logging
from datetime import datetime
from typing import Dict, Optional, List
import time

try:
    from nba_api.stats.endpoints import playergamelog, leaguestandingsv3, leagueleaders, leaguedashplayerstats, playerdashboardbygeneralsplits
    from nba_api.stats.static import players
    # Set headers to avoid blocking (MOST COMMON FIX)
    try:
        from nba_api.stats.library.http import NBAStatsHTTP
        NBAStatsHTTP.headers = {
            "Host": "stats.nba.com",
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "x-nba-stats-token": "true",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "x-nba-stats-origin": "stats",
            "Referer": "https://www.nba.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9"
        }
    except Exception:
        pass  # Headers might already be set or not available
except ImportError:
    raise ImportError("nba_api library not installed. Install with: pip install nba_api")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NBAAPILibrary:
    """Uses official NBA API library to fetch real player statistics"""
    
    def __init__(self):
        self.current_season = self._get_current_season()
        logger.info(f"Initialized NBA API Library for season {self.current_season}")
    
    def _get_current_season(self) -> str:
        """Calculate current NBA season based on date"""
        today = datetime.now()
        # NBA season starts in October
        if today.month >= 10:
            # October onwards - current year to next year
            return f"{today.year}-{str(today.year + 1)[2:]}"
        else:
            # Before October - previous year to current year
            return f"{today.year - 1}-{str(today.year)[2:]}"
    
    def find_player_id(self, player_name: str) -> Optional[int]:
        """
        Find player ID from player name using nba_api
        Uses fuzzy matching if exact match not found
        Handles special characters and accents
        """
        try:
            logger.info(f"Searching for player: {player_name}")
            
            # Get all players
            player_dict = players.get_players()
            
            player_name_lower = player_name.lower()
            
            # First try exact match
            for player in player_dict:
                if player['full_name'].lower() == player_name_lower:
                    logger.info(f"✓ Found player: {player['full_name']} (ID: {player['id']})")
                    return player['id']
            
            # Try removing accents and special characters
            import unicodedata
            normalized_search = ''.join(c for c in unicodedata.normalize('NFD', player_name_lower) if unicodedata.category(c) != 'Mn')
            
            for player in player_dict:
                normalized_player = ''.join(c for c in unicodedata.normalize('NFD', player['full_name'].lower()) if unicodedata.category(c) != 'Mn')
                if normalized_player == normalized_search:
                    logger.info(f"✓ Found player: {player['full_name']} (ID: {player['id']})")
                    return player['id']
            
            # Try partial match (first name or last name)
            for player in player_dict:
                full_name_lower = player['full_name'].lower()
                if player_name_lower in full_name_lower or full_name_lower.endswith(player_name_lower):
                    logger.info(f"✓ Found player (partial): {player['full_name']} (ID: {player['id']})")
                    return player['id']
                
                # Also try with normalized names
                normalized_player = ''.join(c for c in unicodedata.normalize('NFD', full_name_lower) if unicodedata.category(c) != 'Mn')
                if player_name_lower in normalized_player or normalized_player.endswith(player_name_lower):
                    logger.info(f"✓ Found player (partial, normalized): {player['full_name']} (ID: {player['id']})")
                    return player['id']
            
            logger.warning(f"Player not found: {player_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error finding player ID: {e}")
            return None
    
    def get_triple_double_count(self, player_name: str) -> Dict:
        """
        Get triple-double count for a player in current season
        
        Process:
        1. Find player ID
        2. Get player game log for current season
        3. Iterate through games and count triple-doubles
        4. Return count and detailed list
        """
        try:
            # Step 1: Find player ID
            player_id = self.find_player_id(player_name)
            if not player_id:
                logger.warning(f"Could not find player ID for {player_name}")
                return {
                    'player_name': player_name,
                    'count': 0,
                    'games': [],
                    'error': f"Player '{player_name}' not found in NBA database"
                }
            
            # Step 2: Get player game log
            logger.info(f"Fetching game log for {player_name} (ID: {player_id}) for season {self.current_season}")
            
            game_log = playergamelog.PlayerGameLog(
                player_id=player_id,
                season=self.current_season
            )
            
            # Add delay to respect NBA API rate limits
            time.sleep(0.6)
            
            # Step 3: Parse game log data - try dictionary method first
            triple_double_games = []
            triple_double_count = 0
            
            try:
                # Method 1: Dictionary parsing
                data_dict = game_log.get_dict()
                result_sets = data_dict.get('resultSets', [])
                
                if not result_sets:
                    logger.warning(f"No result sets found for {player_name}")
                    return {
                        'player_name': player_name,
                        'count': 0,
                        'games': []
                    }
                
                result_set = result_sets[0]
                headers = result_set.get('headers', [])
                row_set = result_set.get('rowSet', [])
                
                logger.info(f"Found {len(row_set)} games for {player_name}")
                
                # Step 4: Find triple-doubles
                for row in row_set:
                    # Create dictionary from row
                    row_dict = dict(zip(headers, row))
                    
                    # Extract stats (handle None and string values)
                    pts = self._safe_int(row_dict.get('PTS', 0))
                    reb = self._safe_int(row_dict.get('REB', 0))
                    ast = self._safe_int(row_dict.get('AST', 0))
                    
                    # Check for triple-double (10+ in each category)
                    if pts >= 10 and reb >= 10 and ast >= 10:
                        game_date = row_dict.get('GAME_DATE', 'Unknown')
                        matchup = row_dict.get('MATCHUP', 'Unknown')
                        wl = row_dict.get('WL', '')
                        
                        triple_double_count += 1
                        triple_double_games.append({
                            'date': game_date,
                            'matchup': matchup,
                            'points': pts,
                            'rebounds': reb,
                            'assists': ast,
                            'result': wl
                        })
                        
                        logger.info(f"✓ Triple-double: {game_date} {matchup} - {pts}pts, {reb}reb, {ast}ast")
                
            except Exception as e:
                logger.warning(f"Dictionary parsing failed, trying DataFrame method: {e}")
                
                # Method 2: DataFrame fallback
                try:
                    df = game_log.get_data_frames()[0]
                    
                    for _, row in df.iterrows():
                        pts = self._safe_int(row.get('PTS', 0))
                        reb = self._safe_int(row.get('REB', 0))
                        ast = self._safe_int(row.get('AST', 0))
                        
                        if pts >= 10 and reb >= 10 and ast >= 10:
                            triple_double_count += 1
                            triple_double_games.append({
                                'date': str(row.get('GAME_DATE', 'Unknown')),
                                'matchup': str(row.get('MATCHUP', 'Unknown')),
                                'points': pts,
                                'rebounds': reb,
                                'assists': ast,
                                'result': str(row.get('WL', ''))
                            })
                            
                            logger.info(f"✓ Triple-double: {row.get('GAME_DATE')} - {pts}pts, {reb}reb, {ast}ast")
                
                except Exception as df_err:
                    logger.error(f"DataFrame parsing also failed: {df_err}")
                    return {
                        'player_name': player_name,
                        'count': 0,
                        'games': [],
                        'error': "Could not parse NBA API response"
                    }
            
            # Step 5: Return result
            logger.info(f"Found {triple_double_count} triple-doubles for {player_name}")
            
            return {
                'player_name': player_name,
                'count': triple_double_count,
                'games': triple_double_games,
                'season': self.current_season
            }
            
        except Exception as e:
            logger.error(f"Error getting triple-double count: {e}", exc_info=True)
            return {
                'player_name': player_name,
                'count': 0,
                'games': [],
                'error': f"Error fetching data from NBA API: {str(e)}"
            }
    
    def get_player_season_averages(self, player_name: str, season: str = None) -> Optional[Dict]:
        """
        Get player's season averages using NBA API
        Uses PlayerDashboardByGeneralSplits or calculates from game log
        """
        try:
            if not season:
                season = self.current_season
            
            # Step 1: Find player ID
            player_id = self.find_player_id(player_name)
            if not player_id:
                logger.warning(f"Could not find player ID for {player_name}")
                return None
            
            logger.info(f"Fetching season averages for {player_name} (ID: {player_id}) for season {season}")
            
            # Step 2: Try PlayerDashboardByGeneralSplits first (most efficient)
            try:
                dashboard = playerdashboardbygeneralsplits.PlayerDashboardByGeneralSplits(
                    player_id=player_id,
                    season=season,
                    season_type_all_star='Regular Season'
                )
                time.sleep(0.6)  # Rate limit
                
                try:
                    data_dict = dashboard.get_dict()
                    result_sets = data_dict.get('resultSets', [])
                    
                    # Look for OverallSplits which contains season totals
                    for rs in result_sets:
                        if rs.get('name') == 'OverallSplits':
                            headers = rs.get('headers', [])
                            row_set = rs.get('rowSet', [])
                            
                            if row_set and len(row_set) > 0:
                                row = row_set[0]
                                row_dict = dict(zip(headers, row))
                                
                                # Extract stats
                                games_played = self._safe_int(row_dict.get('GP', 0))
                                if games_played == 0:
                                    break
                                
                                # Get per-game averages (PTS, REB, AST, etc. are already per-game in this endpoint)
                                avg_points = self._safe_float(row_dict.get('PTS', 0))
                                avg_rebounds = self._safe_float(row_dict.get('REB', 0))
                                avg_assists = self._safe_float(row_dict.get('AST', 0))
                                avg_steals = self._safe_float(row_dict.get('STL', 0))
                                avg_blocks = self._safe_float(row_dict.get('BLK', 0))
                                
                                # Shooting percentages
                                fg_pct = self._safe_float(row_dict.get('FG_PCT', 0))
                                fg3_pct = self._safe_float(row_dict.get('FG3_PCT', 0))
                                ft_pct = self._safe_float(row_dict.get('FT_PCT', 0))
                                
                                # Minutes per game
                                minutes_per_game = self._safe_float(row_dict.get('MIN', 0))
                                
                                logger.info(f"✓ Got season averages for {player_name} from PlayerDashboard: {games_played} games")
                                
                                return {
                                    'player_name': player_name,
                                    'player_id': player_id,
                                    'games_played': games_played,
                                    'points_per_game': round(avg_points, 1),
                                    'rebounds_per_game': round(avg_rebounds, 1),
                                    'assists_per_game': round(avg_assists, 1),
                                    'steals_per_game': round(avg_steals, 1),
                                    'blocks_per_game': round(avg_blocks, 1),
                                    'field_goal_percentage': round(fg_pct, 3) if fg_pct else 0,
                                    'three_point_percentage': round(fg3_pct, 3) if fg3_pct else 0,
                                    'free_throw_percentage': round(ft_pct, 3) if ft_pct else 0,
                                    'minutes_per_game': round(minutes_per_game, 1),
                                    'season': season,
                                    'source': 'nba_api_dashboard'
                                }
                except Exception as e:
                    logger.debug(f"PlayerDashboard parsing failed: {e}, trying game log calculation")
            except Exception as e:
                logger.debug(f"PlayerDashboard endpoint failed: {e}, trying game log calculation")
            
            # Step 3: Fallback - Calculate from game log
            logger.info(f"Calculating season averages from game log for {player_name}")
            game_log = playergamelog.PlayerGameLog(
                player_id=player_id,
                season=season
            )
            time.sleep(0.6)  # Rate limit
            
            try:
                data_dict = game_log.get_dict()
                result_sets = data_dict.get('resultSets', [])
                
                if not result_sets:
                    logger.warning(f"No game log data found for {player_name}")
                    return None
                
                # Get game log data
                game_log_data = result_sets[0]
                headers = game_log_data.get('headers', [])
                row_set = game_log_data.get('rowSet', [])
                
                if not row_set:
                    logger.warning(f"No games found for {player_name} in season {season}")
                    return None
                
                # Calculate averages
                total_points = 0
                total_rebounds = 0
                total_assists = 0
                total_steals = 0
                total_blocks = 0
                total_minutes = 0
                
                games_played = len(row_set)
                
                for row in row_set:
                    row_dict = dict(zip(headers, row))
                    total_points += self._safe_float(row_dict.get('PTS', 0))
                    total_rebounds += self._safe_float(row_dict.get('REB', 0))
                    total_assists += self._safe_float(row_dict.get('AST', 0))
                    total_steals += self._safe_float(row_dict.get('STL', 0))
                    total_blocks += self._safe_float(row_dict.get('BLK', 0))
                    # Minutes might be in format "MM:SS", need to parse
                    min_str = str(row_dict.get('MIN', '0'))
                    if ':' in min_str:
                        parts = min_str.split(':')
                        total_minutes += float(parts[0]) + float(parts[1]) / 60.0
                    else:
                        total_minutes += self._safe_float(min_str)
                
                # Calculate averages
                avg_points = total_points / games_played if games_played > 0 else 0
                avg_rebounds = total_rebounds / games_played if games_played > 0 else 0
                avg_assists = total_assists / games_played if games_played > 0 else 0
                avg_steals = total_steals / games_played if games_played > 0 else 0
                avg_blocks = total_blocks / games_played if games_played > 0 else 0
                avg_minutes = total_minutes / games_played if games_played > 0 else 0
                
                logger.info(f"✓ Calculated season averages for {player_name} from {games_played} games")
                
                return {
                    'player_name': player_name,
                    'player_id': player_id,
                    'games_played': games_played,
                    'points_per_game': round(avg_points, 1),
                    'rebounds_per_game': round(avg_rebounds, 1),
                    'assists_per_game': round(avg_assists, 1),
                    'steals_per_game': round(avg_steals, 1),
                    'blocks_per_game': round(avg_blocks, 1),
                    'field_goal_percentage': 0.0,  # Would need FGA/FGM data
                    'three_point_percentage': 0.0,  # Would need 3PA/3PM data
                    'free_throw_percentage': 0.0,  # Would need FTA/FTM data
                    'minutes_per_game': round(avg_minutes, 1),
                    'season': season,
                    'source': 'nba_api_game_log'
                }
                
            except Exception as e:
                logger.error(f"Error calculating averages from game log: {e}", exc_info=True)
                return None
                
        except Exception as e:
            logger.error(f"Error getting player season averages: {e}", exc_info=True)
            return None
    
    def get_player_stats_vs_team(self, player_name: str, opponent_team: str) -> Optional[Dict]:
        """
        Get player stats for a specific game vs opponent team using NBA API
        Returns the most recent game where player faced the opponent team
        """
        try:
            # Step 1: Find player ID
            player_id = self.find_player_id(player_name)
            if not player_id:
                logger.warning(f"Could not find player ID for {player_name}")
                return None
            
            # Step 2: Get player game log
            logger.info(f"Fetching game log for {player_name} (ID: {player_id}) vs {opponent_team}")
            
            game_log = playergamelog.PlayerGameLog(
                player_id=player_id,
                season=self.current_season
            )
            
            # Add delay to respect NBA API rate limits
            time.sleep(0.6)
            
            # Step 3: Team name mapping for matching
            team_mapping = {
                'thunder': ['OKC', 'OKLAHOMA CITY', 'THUNDER'],
                'lakers': ['LAL', 'LOS ANGELES LAKERS', 'LAKERS'],
                'warriors': ['GS', 'GSW', 'GOLDEN STATE', 'WARRIORS'],
                'celtics': ['BOS', 'BOSTON', 'CELTICS'],
                'bucks': ['MIL', 'MILWAUKEE', 'BUCKS'],
                'nuggets': ['DEN', 'DENVER', 'NUGGETS'],
                'suns': ['PHX', 'PHOENIX', 'SUNS'],
                'heat': ['MIA', 'MIAMI', 'HEAT'],
                'mavericks': ['DAL', 'DALLAS', 'MAVERICKS'],
                'clippers': ['LAC', 'LA CLIPPERS', 'CLIPPERS'],
                '76ers': ['PHI', 'PHILADELPHIA', '76ERS', 'SIXERS'],
                'cavaliers': ['CLE', 'CLEVELAND', 'CAVALIERS', 'CAVS'],
                'knicks': ['NYK', 'NEW YORK', 'KNICKS'],
                'hawks': ['ATL', 'ATLANTA', 'HAWKS'],
                'timberwolves': ['MIN', 'MINNESOTA', 'TIMBERWOLVES', 'WOLVES'],
                'kings': ['SAC', 'SACRAMENTO', 'KINGS'],
                'pelicans': ['NO', 'NOP', 'NEW ORLEANS', 'PELICANS'],
                'grizzlies': ['MEM', 'MEMPHIS', 'GRIZZLIES'],
                'raptors': ['TOR', 'TORONTO', 'RAPTORS'],
                'nets': ['BKN', 'BROOKLYN', 'NETS'],
                'bulls': ['CHI', 'CHICAGO', 'BULLS'],
                'pistons': ['DET', 'DETROIT', 'PISTONS'],
                'pacers': ['IND', 'INDIANA', 'PACERS'],
                'hornets': ['CHA', 'CHARLOTTE', 'HORNETS'],
                'magic': ['ORL', 'ORLANDO', 'MAGIC'],
                'wizards': ['WSH', 'WASHINGTON', 'WIZARDS'],
                'trail blazers': ['POR', 'PORTLAND', 'TRAIL BLAZERS', 'BLAZERS'],
                'jazz': ['UTAH', 'UTA', 'JAZZ'],
                'rockets': ['HOU', 'HOUSTON', 'ROCKETS'],
                'spurs': ['SA', 'SAS', 'SAN ANTONIO', 'SPURS']
            }
            
            opponent_variations = team_mapping.get(opponent_team.lower(), [opponent_team.upper()])
            
            # Step 4: Parse game log and find game vs opponent
            try:
                data_dict = game_log.get_dict()
                result_sets = data_dict.get('resultSets', [])
                
                if not result_sets:
                    logger.warning(f"No result sets found for {player_name}")
                    return None
                
                result_set = result_sets[0]
                headers = result_set.get('headers', [])
                row_set = result_set.get('rowSet', [])
                
                logger.info(f"Found {len(row_set)} games for {player_name}, searching for vs {opponent_team}")
                
                # Step 5: Find most recent game vs opponent
                for row in row_set:
                    row_dict = dict(zip(headers, row))
                    matchup = str(row_dict.get('MATCHUP', '')).upper()
                    
                    # Check if opponent is in matchup (format: "SAS @ OKC" or "OKC vs SAS")
                    opponent_found = any(
                        variation in matchup for variation in opponent_variations
                    )
                    
                    if opponent_found:
                        # Found the game! Extract stats
                        game_date = row_dict.get('GAME_DATE', '')
                        pts = self._safe_int(row_dict.get('PTS', 0))
                        reb = self._safe_int(row_dict.get('REB', 0))
                        ast = self._safe_int(row_dict.get('AST', 0))
                        stl = self._safe_int(row_dict.get('STL', 0))
                        blk = self._safe_int(row_dict.get('BLK', 0))
                        wl = row_dict.get('WL', '')
                        
                        # Parse matchup to get teams
                        # Format: "SAS @ OKC" means SAS (away) @ OKC (home)
                        # The player's team is the first team (before @)
                        original_matchup = str(row_dict.get('MATCHUP', ''))
                        if '@' in original_matchup:
                            # Format: "SAS @ OKC" - SAS is away team (player's team)
                            parts = original_matchup.split('@')
                            player_team = parts[0].strip() if len(parts) > 0 else 'Unknown'
                            opponent_team = parts[1].strip() if len(parts) > 1 else 'Unknown'
                        elif 'vs' in original_matchup.upper() or 'VS' in original_matchup:
                            # Format: "SAS vs OKC" 
                            parts = original_matchup.replace('vs', 'VS').split('VS')
                            player_team = parts[0].strip() if len(parts) > 0 else 'Unknown'
                            opponent_team = parts[1].strip() if len(parts) > 1 else 'Unknown'
                        else:
                            # Fallback
                            parts = original_matchup.split()
                            player_team = parts[0] if len(parts) > 0 else 'Unknown'
                            opponent_team = parts[-1] if len(parts) > 1 else 'Unknown'
                        
                        logger.info(f"✓ Found game: {game_date} {original_matchup} - {pts}pts, {reb}reb, {ast}ast")
                        
                        return {
                            'player_name': player_name,
                            'points': pts,
                            'rebounds': reb,
                            'assists': ast,
                            'steals': stl,
                            'blocks': blk,
                            'match_date': game_date,
                            'team1_name': player_team,
                            'team2_name': opponent_team,
                            'matchup': original_matchup,
                            'result': wl,
                            'player_team': player_team
                        }
                
                logger.warning(f"No game found for {player_name} vs {opponent_team}")
                return None
                
            except Exception as e:
                logger.warning(f"Dictionary parsing failed, trying DataFrame method: {e}")
                
                # Method 2: DataFrame fallback
                try:
                    df = game_log.get_data_frames()[0]
                    
                    for _, row in df.iterrows():
                        matchup = str(row.get('MATCHUP', '')).upper()
                        
                        opponent_found = any(
                            variation in matchup for variation in opponent_variations
                        )
                        
                        if opponent_found:
                            game_date = str(row.get('GAME_DATE', ''))
                            pts = self._safe_int(row.get('PTS', 0))
                            reb = self._safe_int(row.get('REB', 0))
                            ast = self._safe_int(row.get('AST', 0))
                            stl = self._safe_int(row.get('STL', 0))
                            blk = self._safe_int(row.get('BLK', 0))
                            wl = str(row.get('WL', ''))
                            
                            # Parse matchup correctly
                            original_matchup = str(row.get('MATCHUP', ''))
                            if '@' in original_matchup:
                                parts = original_matchup.split('@')
                                player_team = parts[0].strip() if len(parts) > 0 else 'Unknown'
                                opponent_team = parts[1].strip() if len(parts) > 1 else 'Unknown'
                            elif 'vs' in original_matchup.upper() or 'VS' in original_matchup:
                                parts = original_matchup.replace('vs', 'VS').split('VS')
                                player_team = parts[0].strip() if len(parts) > 0 else 'Unknown'
                                opponent_team = parts[1].strip() if len(parts) > 1 else 'Unknown'
                            else:
                                parts = original_matchup.split()
                                player_team = parts[0] if len(parts) > 0 else 'Unknown'
                                opponent_team = parts[-1] if len(parts) > 1 else 'Unknown'
                            
                            logger.info(f"✓ Found game: {game_date} {original_matchup} - {pts}pts")
                            
                            return {
                                'player_name': player_name,
                                'points': pts,
                                'rebounds': reb,
                                'assists': ast,
                                'steals': stl,
                                'blocks': blk,
                                'match_date': game_date,
                                'team1_name': player_team,
                                'team2_name': opponent_team,
                                'matchup': original_matchup,
                                'result': wl,
                                'player_team': player_team
                            }
                    
                    logger.warning(f"No game found for {player_name} vs {opponent_team}")
                    return None
                    
                except Exception as df_err:
                    logger.error(f"DataFrame parsing also failed: {df_err}")
                    return None
            
        except Exception as e:
            logger.error(f"Error getting player stats vs team: {e}", exc_info=True)
            return None
    
    def get_team_game_leader(self, team_name: str, stat_type: str = 'points') -> Optional[Dict]:
        """
        Get the leading scorer (or stat leader) for a team's most recent game using NBA API
        Returns the player with highest points (or specified stat) from the team's latest game
        """
        try:
            from nba_api.stats.endpoints import teamgamelog
            from nba_api.stats.static import teams
            
            logger.info(f"Finding {stat_type} leader for {team_name}'s latest game using NBA API")
            
            # Step 1: Find team ID
            team_dict = teams.get_teams()
            team_id = None
            team_name_lower = team_name.lower().strip()
            
            # Map common team name variations
            team_name_map = {
                'warriors': ['golden state warriors', 'gsw', 'gs'],
                'lakers': ['los angeles lakers', 'lal'],
                'celtics': ['boston celtics', 'bos'],
                'bucks': ['milwaukee bucks', 'mil'],
                'nuggets': ['denver nuggets', 'den'],
                'suns': ['phoenix suns', 'phx'],
                'heat': ['miami heat', 'mia'],
                'mavericks': ['dallas mavericks', 'dal'],
                'clippers': ['la clippers', 'los angeles clippers', 'lac'],
                '76ers': ['philadelphia 76ers', 'phi'],
                'cavaliers': ['cleveland cavaliers', 'cle'],
                'knicks': ['new york knicks', 'nyk'],
                'hawks': ['atlanta hawks', 'atl'],
                'thunder': ['oklahoma city thunder', 'okc'],
                'timberwolves': ['minnesota timberwolves', 'min'],
                'kings': ['sacramento kings', 'sac'],
                'pelicans': ['new orleans pelicans', 'nop', 'no'],
                'grizzlies': ['memphis grizzlies', 'mem'],
                'raptors': ['toronto raptors', 'tor'],
                'nets': ['brooklyn nets', 'bkn'],
                'bulls': ['chicago bulls', 'chi'],
                'pistons': ['detroit pistons', 'det'],
                'pacers': ['indiana pacers', 'ind'],
                'hornets': ['charlotte hornets', 'cha'],
                'magic': ['orlando magic', 'orl'],
                'wizards': ['washington wizards', 'was', 'wsh'],
                'trail blazers': ['portland trail blazers', 'por'],
                'jazz': ['utah jazz', 'uta', 'utah'],
                'rockets': ['houston rockets', 'hou'],
                'spurs': ['san antonio spurs', 'sas', 'sa']
            }
            
            # Check if we have a mapped name
            search_terms = [team_name_lower]
            if team_name_lower in team_name_map:
                search_terms.extend(team_name_map[team_name_lower])
            
            # First, try exact matches (most specific)
            for team in team_dict:
                full_name = team['full_name'].lower()
                abbreviation = team['abbreviation'].lower()
                nickname = team['nickname'].lower()
                
                # Check for exact match first (most reliable)
                for search_term in search_terms:
                    # Exact match on nickname (e.g., "warriors" matches "Warriors")
                    if nickname == search_term:
                        team_id = team['id']
                        team_abbrev = team['abbreviation']
                        logger.info(f"✓ Found team (exact nickname match): {team['full_name']} (ID: {team_id}, Abbrev: {team_abbrev})")
                        break
                    # Exact match on abbreviation
                    elif abbreviation == search_term:
                        team_id = team['id']
                        team_abbrev = team['abbreviation']
                        logger.info(f"✓ Found team (exact abbrev match): {team['full_name']} (ID: {team_id}, Abbrev: {team_abbrev})")
                    break
            
                if team_id:
                    break
            
            # If no exact match, try partial matches (but be more careful)
            if not team_id:
                for team in team_dict:
                    full_name = team['full_name'].lower()
                    abbreviation = team['abbreviation'].lower()
                    nickname = team['nickname'].lower()
                    
                    # Check all search terms for partial matches
                    for search_term in search_terms:
                        # Only match if search term is in the full name, abbreviation, or nickname
                        # Don't match if full_name is in search_term (that's too broad)
                        if (search_term in full_name or 
                            search_term in abbreviation or 
                            search_term in nickname):
                            team_id = team['id']
                            team_abbrev = team['abbreviation']
                            logger.info(f"✓ Found team (partial match): {team['full_name']} (ID: {team_id}, Abbrev: {team_abbrev})")
                            break
                    
                    if team_id:
                        break
            
            if not team_id:
                logger.warning(f"Could not find team ID for {team_name}. Searched terms: {search_terms}")
                return None
            
            # Step 2: Get team's game log - try multiple seasons to find games
            # Only try current and previous season (ESPN will handle very recent games)
            seasons_to_try = [self.current_season]
            try:
                year = int(self.current_season.split('-')[0])
                # Previous season only
                prev_season = f"{year-1}-{str(year)[2:]}"
                if prev_season not in seasons_to_try:
                    seasons_to_try.append(prev_season)
            except:
                pass
            
            game_id = None
            game_date = None
            matchup = None
            
            for try_season in seasons_to_try:
                logger.info(f"Fetching game log for {team_name} (ID: {team_id}) for season {try_season}")
                
                try:
                    game_log = teamgamelog.TeamGameLog(
                        team_id=team_id,
                        season=try_season
                    )
                    
                    time.sleep(0.6)  # Rate limit
                    
                    # Step 3: Get the most recent game
                    data_dict = game_log.get_dict()
                    result_sets = data_dict.get('resultSets', [])
                    
                    if not result_sets:
                        logger.warning(f"No result sets found for {team_name} in season {try_season}")
                        continue
                    
                    result_set = result_sets[0]
                    headers = result_set.get('headers', [])
                    row_set = result_set.get('rowSet', [])
                    
                    if not row_set:
                        logger.warning(f"No games found for {team_name} in season {try_season}")
                        continue
                    
                    # Found games! Use this season
                    latest_game = dict(zip(headers, row_set[0]))
                    game_id = latest_game.get('Game_ID')
                    game_date = latest_game.get('GAME_DATE', '')
                    matchup = latest_game.get('MATCHUP', '')
                    logger.info(f"✓ Found games in season {try_season}: {len(row_set)} games. Latest: {game_date} {matchup} (Game ID: {game_id})")
                    break
                    
                except Exception as season_err:
                    logger.warning(f"Error fetching season {try_season}: {season_err}")
                    continue
            
            if not game_id:
                logger.warning(f"Could not find any recent games for {team_name} in any season")
                return None
                
                # Step 4: Get boxscore for this game to find leading scorer
                from nba_api.stats.endpoints import boxscoretraditionalv2
                
            logger.info(f"Fetching boxscore for game {game_id}")
            try:
                boxscore = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
                time.sleep(0.6)  # Rate limit
            except Exception as boxscore_err:
                logger.error(f"Failed to fetch boxscore for game {game_id}: {boxscore_err}")
                return None
            
            # Try to get player stats - use DataFrame method first (more reliable)
            try:
                boxscore_df = boxscore.player_stats.get_data_frame()
                logger.info(f"✓ Got boxscore DataFrame with {len(boxscore_df)} rows")
                
                # Filter for target team
                team_players = boxscore_df[boxscore_df['TEAM_ID'] == team_id]
                
                if team_players.empty:
                    logger.warning(f"No players found for team {team_id} in boxscore DataFrame")
                    return None
                
                # Get leader by stat
                stat_column_map = {
                    'points': 'PTS',
                    'rebounds': 'REB',
                    'assists': 'AST',
                    'steals': 'STL',
                    'blocks': 'BLK'
                }
                stat_column = stat_column_map.get(stat_type.lower(), 'PTS')
                
                if stat_column not in team_players.columns:
                    logger.warning(f"Stat column {stat_column} not found in boxscore DataFrame")
                    return None
                
                leader_row = team_players.loc[team_players[stat_column].idxmax()]
                
                leader_result = {
                    'player_name': str(leader_row.get('PLAYER_NAME', 'Unknown')),
                    stat_type: self._safe_int(leader_row.get(stat_column, 0)),
                    'points': self._safe_int(leader_row.get('PTS', 0)),
                    'rebounds': self._safe_int(leader_row.get('REB', 0)),
                    'assists': self._safe_int(leader_row.get('AST', 0)),
                    'steals': self._safe_int(leader_row.get('STL', 0)),
                    'blocks': self._safe_int(leader_row.get('BLK', 0)),
                    'team': team_name,
                    'game_date': game_date,
                    'match_date': game_date,
                    'matchup': matchup,
                    'game_id': game_id
                }
                logger.info(f"✓ Found {stat_type} leader via DataFrame: {leader_result['player_name']} with {leader_result[stat_type]} {stat_type}")
                return leader_result
                
            except Exception as df_err:
                logger.warning(f"DataFrame method failed: {df_err}, trying dict method")
                
                # Fallback to dictionary method
                boxscore_dict = boxscore.get_dict()
                result_sets = boxscore_dict.get('resultSets', [])
                logger.info(f"Boxscore dict has {len(result_sets)} result sets")
                
                # Find player stats result set
                player_stats_set = None
                for rs in result_sets:
                    rs_name = rs.get('name', '')
                    if rs_name == 'PlayerStats':
                        player_stats_set = rs
                        break
                
                if not player_stats_set:
                    logger.warning(f"No PlayerStats in boxscore. Available: {[rs.get('name') for rs in result_sets]}")
                    return None
                
                # Continue with dict method processing
                player_headers = player_stats_set.get('headers', [])
                player_rows = player_stats_set.get('rowSet', [])
                
                # Find players from the target team and get the leader
                highest_value = -1
                leader_player = None
                
                # Map stat type to column index
                stat_column_map = {
                    'points': 'PTS',
                    'rebounds': 'REB',
                    'assists': 'AST',
                    'steals': 'STL',
                    'blocks': 'BLK'
                }
                stat_column = stat_column_map.get(stat_type.lower(), 'PTS')
                
                logger.info(f"Looking for {stat_type} leader (column: {stat_column}) for team {team_abbrev} (ID: {team_id})")
                logger.info(f"Processing {len(player_rows)} players from boxscore")
                players_found = 0
                
                for row in player_rows:
                    player_dict = dict(zip(player_headers, row))
                    
                    # Check if player is from target team (TEAM_ABBREVIATION or TEAM_ID)
                    player_team_abbrev = player_dict.get('TEAM_ABBREVIATION', '')
                    player_team_id = player_dict.get('TEAM_ID', 0)
                    
                    if player_team_id == team_id or player_team_abbrev.upper() == team_abbrev.upper():
                        players_found += 1
                        # Get the stat value
                        stat_value = self._safe_int(player_dict.get(stat_column, 0))
                        
                        if stat_value > highest_value:
                            highest_value = stat_value
                            leader_player = {
                                'player_name': player_dict.get('PLAYER_NAME', 'Unknown'),
                                stat_type: stat_value,
                                'points': self._safe_int(player_dict.get('PTS', 0)),
                                'rebounds': self._safe_int(player_dict.get('REB', 0)),
                                'assists': self._safe_int(player_dict.get('AST', 0)),
                                'steals': self._safe_int(player_dict.get('STL', 0)),
                                'blocks': self._safe_int(player_dict.get('BLK', 0)),
                                'team': team_name,
                                'game_date': game_date,
                                'match_date': game_date,
                                'matchup': matchup,
                                'game_id': game_id
                            }
                
                logger.info(f"Found {players_found} players from team {team_abbrev} in boxscore")
                
                if leader_player:
                    logger.info(f"✓ Found {stat_type} leader for {team_name}: {leader_player['player_name']} with {highest_value} {stat_type}")
                    return leader_player
                else:
                    logger.warning(f"Could not find {stat_type} leader for {team_name}")
                    return None
            
        except Exception as e:
            logger.error(f"Error getting team game leader from NBA API: {e}", exc_info=True)
            return None
    
    def get_team_most_recent_game_result(self, team_name: str) -> Optional[Dict]:
        """
        Get a team's most recent game result using NBA API
        Returns whether the team won or lost, opponent, score, and date
        """
        try:
            from nba_api.stats.endpoints import teamgamelog
            from nba_api.stats.static import teams
            
            logger.info(f"Getting most recent game result for {team_name} using NBA API")
            
            # Step 1: Find team ID
            team_dict = teams.get_teams()
            team_id = None
            team_name_lower = team_name.lower()
            team_abbrev = None
            team_full_name = None
            
            for team in team_dict:
                full_name = team['full_name'].lower()
                abbreviation = team['abbreviation'].lower()
                nickname = team['nickname'].lower()
                
                if (team_name_lower in full_name or 
                    team_name_lower in abbreviation or 
                    team_name_lower in nickname or
                    full_name in team_name_lower):
                    team_id = team['id']
                    team_abbrev = team['abbreviation']
                    team_full_name = team['full_name']
                    logger.info(f"✓ Found team: {team_full_name} (ID: {team_id}, Abbrev: {team_abbrev})")
                    break
            
            if not team_id:
                logger.warning(f"Could not find team ID for {team_name}")
                return None
            
            # Step 2: Get team's game log - try multiple seasons
            # Try current season first, then previous seasons
            seasons_to_try = [self.current_season]
            
            # Extract year from current season (e.g., "2025-26" -> 2025)
            try:
                current_year = int(self.current_season.split('-')[0])
                # Add previous seasons as fallbacks
                for year_offset in range(1, 3):  # Try up to 2 previous seasons
                    prev_year = current_year - year_offset
                    prev_season = f"{prev_year}-{str(prev_year + 1)[2:]}"
                    seasons_to_try.append(prev_season)
            except:
                pass  # If season parsing fails, just try current season
            
            logger.info(f"Trying seasons: {seasons_to_try} for {team_name}")
            
            for season in seasons_to_try:
                try:
                    logger.info(f"Fetching game log for {team_name} (ID: {team_id}) for season {season}")
                    
                    game_log = teamgamelog.TeamGameLog(
                        team_id=team_id,
                        season=season
                    )
                    
                    time.sleep(0.6)  # Rate limit
                    
                    # Step 3: Get the most recent game
                    data_dict = game_log.get_dict()
                    result_sets = data_dict.get('resultSets', [])
                    
                    if not result_sets:
                        logger.debug(f"No result sets found for {team_name} in season {season}")
                        continue
                    
                    result_set = result_sets[0]
                    headers = result_set.get('headers', [])
                    row_set = result_set.get('rowSet', [])
                    
                    if not row_set:
                        logger.debug(f"No games found for {team_name} in season {season}")
                        continue
                    
                    # Get most recent game (first row is most recent)
                    latest_game = dict(zip(headers, row_set[0]))
                    game_id = latest_game.get('Game_ID')
                    game_date = latest_game.get('GAME_DATE', '')
                    matchup = latest_game.get('MATCHUP', '')  # Format: "LAL @ GSW" or "LAL vs. GSW"
                    wl = latest_game.get('WL', '')  # 'W' or 'L'
                    team_score = self._safe_int(latest_game.get('PTS', 0))
                    
                    logger.info(f"Found latest game in season {season}: {game_date} {matchup} (WL: {wl}, Score: {team_score})")
                    
                    # Parse matchup to get opponent
                    opponent_name = None
                    if '@' in matchup:
                        # Away game: "LAL @ GSW" means LAL is away, GSW is home
                        parts = matchup.split('@')
                        if len(parts) == 2:
                            team_part = parts[0].strip()
                            opponent_part = parts[1].strip()
                            if team_abbrev in team_part:
                                opponent_name = opponent_part
                            else:
                                opponent_name = team_part
                    elif 'vs.' in matchup or 'vs' in matchup:
                        # Home game: "LAL vs. GSW" means LAL is home, GSW is away
                        parts = matchup.replace('vs.', 'vs').split('vs')
                        if len(parts) == 2:
                            team_part = parts[0].strip()
                            opponent_part = parts[1].strip()
                            if team_abbrev in team_part:
                                opponent_name = opponent_part
                            else:
                                opponent_name = team_part
                    
                    # Get opponent score from boxscore
                    opponent_score = 0
                    try:
                        from nba_api.stats.endpoints import boxscoretraditionalv2
                        boxscore = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
                        time.sleep(0.6)  # Rate limit
                        
                        boxscore_dict = boxscore.get_dict()
                        result_sets = boxscore_dict.get('resultSets', [])
                        
                        # Find team stats result set
                        team_stats_set = None
                        for rs in result_sets:
                            if rs.get('name') == 'TeamStats':
                                team_stats_set = rs
                                break
                        
                        if team_stats_set:
                            team_headers = team_stats_set.get('headers', [])
                            team_rows = team_stats_set.get('rowSet', [])
                            
                            for row in team_rows:
                                team_dict = dict(zip(team_headers, row))
                                team_id_in_box = team_dict.get('TEAM_ID', 0)
                                if team_id_in_box == team_id:
                                    team_score = self._safe_int(team_dict.get('PTS', team_score))
                                else:
                                    opponent_score = self._safe_int(team_dict.get('PTS', 0))
                    except Exception as e:
                        logger.warning(f"Could not get opponent score from boxscore: {e}")
                    
                    did_win = wl == 'W'
                    
                    return {
                        'team_name': team_full_name or team_name,
                        'team_abbrev': team_abbrev,
                        'opponent_name': opponent_name or 'Unknown',
                        'did_win': did_win,
                        'team_score': team_score,
                        'opponent_score': opponent_score,
                        'game_date': game_date,
                        'matchup': matchup,
                        'game_id': game_id
                    }
                except Exception as season_error:
                    logger.debug(f"Error processing season {season}: {season_error}")
                    continue
            
            # If we get here, no season had games
            logger.warning(f"No games found for {team_name} in any season tried")
            return None
                    
        except Exception as e:
            logger.error(f"Error getting team most recent game result from NBA API: {e}", exc_info=True)
            return None
    
    def get_top_players_by_stat(self, stat_type: str = 'points', limit: int = 10, season: str = None) -> List[Dict]:
        """
        Get top players by a specific statistic using NBA API LeagueLeaders endpoint
        
        Logic:
        1. Get player season stats using LeagueLeaders endpoint
        2. PPG is already calculated (PerGame mode)
        3. Sort players by stat value (descending) - already sorted by API
        4. Return top N players
        
        Uses LeagueLeaders endpoint as specified:
        - stat_category_abbreviation = "PTS" (or other stat)
        - per_mode_simple = "PerGame" 
        - season_type_all_star = "Regular Season"
        
        stat_type: 'points', 'assists', 'rebounds', 'steals', 'blocks'
        limit: number of players to return
        season: season string (e.g., '2024-25'), defaults to current season
        
        Returns empty list if API fails (fallback APIs will be used by calling agent)
        """
        try:
            if not season:
                season = self.current_season
            
            # Map stat types to NBA API stat category abbreviation
            # Note: field_goal_pct and three_point_pct are not valid stat_categories, so we'll query by PTS and sort by FG_PCT or FG3_PCT
            stat_category_map = {
                'points': 'PTS',
                'assists': 'AST',
                'rebounds': 'REB',
                'steals': 'STL',
                'blocks': 'BLK',
                'three_pointers_made': 'FG3M',  # 3-pointers made (total)
                'three_pointers_made_per_game': 'FG3M',  # 3-pointers made per game
                'field_goal_pct': 'PTS',  # Use PTS as base query, then sort by FG_PCT
                'three_point_pct': 'FG3M',  # Use FG3M as base query (players who shoot 3s), then sort by FG3_PCT
                'score': 'PTS',  # Alias for points
                'scoring': 'PTS'  # Alias for points
            }
            
            # For field goal percentage and 3-point percentage, we query by points but sort by the percentage column
            is_fg_pct = stat_type.lower() == 'field_goal_pct'
            is_3pt_pct = stat_type.lower() == 'three_point_pct'
            # Check if this is total 3-pointers (not per game)
            is_total_3pm = stat_type.lower() == 'three_pointers_made'
            # For 3-point percentage, use Totals mode to get season totals (more accurate for percentage calculations)
            use_totals_mode = is_3pt_pct or is_total_3pm
            stat_category = stat_category_map.get(stat_type.lower(), 'PTS')
            if is_fg_pct:
                sort_by_column = 'FG_PCT'
            elif is_3pt_pct:
                sort_by_column = 'FG3_PCT'
            else:
                sort_by_column = stat_category
            
            logger.info(f"Getting top {limit} players by {stat_type} (query: {stat_category}, sort: {sort_by_column}) for season {season} using LeagueLeaders")
            
            # Try multiple seasons to get the most recent available data
            seasons_to_try = []
            if season == self.current_season:
                # Extract year from season string (e.g., "2025-26" -> 2025)
                year = int(season.split('-')[0])
                # Try CURRENT season FIRST (2025-26) - user wants current season data
                seasons_to_try.append(season)
                # Then try previous season as fallback if current season has no data
                prev_year = year - 1
                seasons_to_try.append(f"{prev_year}-{str(year)[2:]}")
            else:
                seasons_to_try = [season]
            
            for try_season in seasons_to_try:
                try:
                    logger.info(f"Using LeagueLeaders endpoint for {try_season} (stat: {stat_category})")
                    
                    # Step 1: Use LeagueLeaders endpoint with CORRECT parameters
                    # per_mode48="PerGame" for per-game stats, "Totals" for total stats
                    # For 3-point percentage, use Totals mode to get season totals (NBA standard)
                    # scope="S" - all players
                    per_mode = 'Totals' if (is_total_3pm or is_3pt_pct) else 'PerGame'
                    leaders = leagueleaders.LeagueLeaders(
                        season=try_season,
                        season_type_all_star='Regular Season',
                        stat_category_abbreviation=stat_category,
                        per_mode48=per_mode,
                        scope='S'
                    )
                    
                    time.sleep(0.6)  # Rate limit
                    
                    # Step 2: Try dictionary method first (more reliable than DataFrame)
                    # DataFrame can have pandas conversion issues, so use dict method
                    try:
                        data_dict = leaders.get_dict()
                        result_sets = data_dict.get('resultSets', [])
                        # Some API versions return 'resultSet' (singular)
                        if not result_sets:
                            result_set_single = data_dict.get('resultSet')
                            if result_set_single:
                                result_sets = [result_set_single]
                        
                        if not result_sets or not result_sets[0].get('rowSet'):
                            logger.warning(f"Season {try_season} returned empty data, trying next season")
                            continue
                        
                        result_set = result_sets[0]
                        headers = result_set.get('headers', [])
                        row_set = result_set.get('rowSet', [])
                        
                        if not row_set:
                            logger.warning(f"Season {try_season} has no players, trying next season")
                            continue
                        
                        # Parse and sort by stat value descending, then take top N
                        all_players_data = []
                        for row in row_set:
                            player_dict = dict(zip(headers, row))
                            games_played = self._safe_int(player_dict.get('GP', 0))
                            
                            # For field goal percentage, use FG_PCT; for 3-point percentage, use FG3_PCT
                            if is_fg_pct:
                                player_stat_value = self._safe_float(player_dict.get('FG_PCT', 0))
                                # Filter: at least 5 games and minimum field goal attempts (FGA > 0)
                                fga = self._safe_float(player_dict.get('FGA', 0))
                                if games_played >= 5 and fga > 0 and player_stat_value > 0:
                                    all_players_data.append((player_stat_value, player_dict))
                            elif is_3pt_pct:
                                player_stat_value = self._safe_float(player_dict.get('FG3_PCT', 0))
                                # Filter: NBA qualification criteria for 3-point percentage
                                # NBA standard: minimum 82 attempts (1 per game over full season) OR at least 2.5 attempts per game
                                fg3a = self._safe_float(player_dict.get('FG3A', 0))
                                # For players with 20+ games, require 82 attempts; for fewer games, require 2.5 per game
                                min_attempts_required = 82 if games_played >= 20 else max(82, games_played * 2.5)
                                if games_played >= 5 and fg3a >= min_attempts_required and player_stat_value > 0:
                                    all_players_data.append((player_stat_value, player_dict))
                            else:
                                player_stat_value = self._safe_float(player_dict.get(stat_category, 0))
                            # Filter valid players
                            if games_played > 0 and player_stat_value > 0:
                                all_players_data.append((player_stat_value, player_dict))
                        
                        # Sort by stat value descending and take top N
                        all_players_data.sort(key=lambda x: x[0], reverse=True)
                        top_players_data = all_players_data[:limit]
                        
                        # Format results
                        top_players = []
                        for player_stat_value, player_dict in top_players_data:
                            player_name = player_dict.get('PLAYER', 'Unknown')
                            team_abbrev = player_dict.get('TEAM', '')
                            games_played = self._safe_int(player_dict.get('GP', 0))
                            
                            # For field goal percentage and 3-point percentage, stat_value should be the percentage (0-1 range)
                            # We'll convert it to percentage for display later
                            fg_pct_value = player_stat_value if is_fg_pct else self._safe_float(player_dict.get('FG_PCT', 0))
                            fg3_pct_value = player_stat_value if is_3pt_pct else self._safe_float(player_dict.get('FG3_PCT', 0))
                            
                            top_players.append({
                                'player_name': player_name,
                                'team': team_abbrev,
                                'stat_value': player_stat_value,  # For FG% and 3PT%, this is already 0-1 range
                                'stat_type': stat_type,
                                'games_played': games_played,
                                'points': self._safe_float(player_dict.get('PTS', 0)),
                                'rebounds': self._safe_float(player_dict.get('REB', 0)),
                                'assists': self._safe_float(player_dict.get('AST', 0)),
                                'steals': self._safe_float(player_dict.get('STL', 0)),
                                'blocks': self._safe_float(player_dict.get('BLK', 0)),
                                'field_goal_pct': fg_pct_value,
                                'three_point_pct': fg3_pct_value,
                                'free_throw_pct': self._safe_float(player_dict.get('FT_PCT', 0)),
                                'minutes_per_game': self._safe_float(player_dict.get('MIN', 0))
                            })
                        
                        if top_players:
                            logger.info(f"✓ Successfully retrieved top {len(top_players)} players by {stat_type} for season {try_season} using LeagueLeaders (dictionary method)")
                            return top_players
                        
                    except Exception as dict_err:
                        logger.warning(f"Dictionary method failed for {try_season}: {dict_err}, trying DataFrame method")
                        
                        # Fallback to DataFrame method
                        try:
                            df = leaders.get_data_frames()[0]
                            
                            if df.empty:
                                logger.warning(f"Season {try_season} returned empty DataFrame, trying next season")
                                continue
                            
                            # Step 3: Filter valid players
                            if is_fg_pct:
                                # For field goal percentage, filter by games and field goal attempts
                                df = df[(df['GP'] >= 5) & (df['FGA'] > 0) & (df['FG_PCT'] > 0)]
                                sort_column = 'FG_PCT'
                            elif is_3pt_pct:
                                # For 3-point percentage, filter by games and meaningful 3-point attempts
                                # NBA standard: minimum 82 attempts (1 per game over full season) OR at least 2.5 attempts per game
                                df = df[(df['GP'] >= 5) & (df['FG3_PCT'] > 0)]
                                # Calculate minimum attempts required based on games played
                                # For players with 20+ games, require 82 attempts; for fewer games, require 2.5 per game
                                df['MIN_FG3A'] = df.apply(lambda row: 82 if row['GP'] >= 20 else max(82, row['GP'] * 2.5), axis=1)
                                df = df[df['FG3A'] >= df['MIN_FG3A']]
                                sort_column = 'FG3_PCT'
                            else:
                                df = df[(df['GP'] > 0) & (df[stat_category] > 0)]
                                sort_column = stat_category
                            
                            if df.empty:
                                logger.warning(f"Season {try_season} has no valid players, trying next season")
                                continue
                            
                            # Step 4: Sort by stat category descending and get top N
                            # LeagueLeaders may already be sorted, but explicitly sort to ensure correctness
                            if sort_column not in df.columns:
                                logger.warning(f"Stat column {sort_column} not found. Available: {list(df.columns)}")
                                continue
                            
                            # Sort by stat value descending (e.g., PTS for points per game, FG_PCT for field goal %)
                            top_df = df.nlargest(limit, sort_column)
                            
                            # Step 5: Format and return results
                            top_players = []
                            for _, row in top_df.iterrows():
                                player_name = str(row.get('PLAYER', row.get('PLAYER_NAME', 'Unknown')))
                                team_abbrev = str(row.get('TEAM', row.get('TEAM_ABBREVIATION', '')))
                                
                                # PPG is already calculated (it's in PTS column when per_mode_simple='PerGame')
                                ppg = self._safe_float(row.get('PTS', 0))
                                
                                # For field goal percentage and 3-point percentage, use the percentage column
                                if is_fg_pct:
                                    stat_value = self._safe_float(row.get('FG_PCT', 0))
                                elif is_3pt_pct:
                                    stat_value = self._safe_float(row.get('FG3_PCT', 0))
                                else:
                                    stat_value = self._safe_float(row.get(stat_category, 0))
                                
                                top_players.append({
                                    'player_name': player_name,
                                    'team': team_abbrev,
                                    'stat_value': stat_value,  # For FG%, this is 0-1 range
                                    'stat_type': stat_type,
                                    'games_played': self._safe_int(row.get('GP', 0)),
                                    'points': ppg,  # Points per game
                                    'rebounds': self._safe_float(row.get('REB', 0)),
                                    'assists': self._safe_float(row.get('AST', 0)),
                                    'steals': self._safe_float(row.get('STL', 0)),
                                    'blocks': self._safe_float(row.get('BLK', 0)),
                                    'field_goal_pct': self._safe_float(row.get('FG_PCT', 0)),
                                    'three_point_pct': self._safe_float(row.get('FG3_PCT', 0)),
                                    'free_throw_pct': self._safe_float(row.get('FT_PCT', 0)),
                                    'minutes_per_game': self._safe_float(row.get('MIN', 0))
                                })
                            
                            if top_players:
                                logger.info(f"✓ Successfully retrieved top {len(top_players)} players by {stat_type} for season {try_season} using LeagueLeaders (DataFrame)")
                                return top_players
                        except Exception as df_err:
                            logger.warning(f"DataFrame method also failed for {try_season}: {df_err}")
                            continue
                        
                        # Fallback to dictionary method
                        try:
                            data_dict = leaders.get_dict()
                            result_sets = data_dict.get('resultSets', [])
                            # Some API versions return 'resultSet' (singular)
                            if not result_sets:
                                result_set_single = data_dict.get('resultSet')
                                if result_set_single:
                                    result_sets = [result_set_single]
                            
                            if not result_sets or not result_sets[0].get('rowSet'):
                                logger.warning(f"Season {try_season} returned empty data, trying next season")
                                continue
                            
                            result_set = result_sets[0]
                            headers = result_set.get('headers', [])
                            row_set = result_set.get('rowSet', [])
                            
                            if not row_set:
                                logger.warning(f"Season {try_season} has no players, trying next season")
                                continue
                            
                            # Parse and sort by stat value descending, then take top N
                            all_players_data = []
                            for row in row_set:
                                player_dict = dict(zip(headers, row))
                                games_played = self._safe_int(player_dict.get('GP', 0))
                                player_stat_value = self._safe_float(player_dict.get(stat_category, 0))
                                
                                # Filter valid players
                                if games_played > 0 and player_stat_value > 0:
                                    all_players_data.append((player_stat_value, player_dict))
                            
                            # Sort by stat value descending and take top N
                            all_players_data.sort(key=lambda x: x[0], reverse=True)
                            top_players_data = all_players_data[:limit]
                            
                            # Format results
                            top_players = []
                            for player_stat_value, player_dict in top_players_data:
                                player_name = player_dict.get('PLAYER', 'Unknown')
                                team_abbrev = player_dict.get('TEAM', '')
                                games_played = self._safe_int(player_dict.get('GP', 0))
                                
                                top_players.append({
                                    'player_name': player_name,
                                    'team': team_abbrev,
                                    'stat_value': player_stat_value,
                                    'stat_type': stat_type,
                                    'games_played': games_played,
                                    'points': self._safe_float(player_dict.get('PTS', 0)),
                                    'rebounds': self._safe_float(player_dict.get('REB', 0)),
                                    'assists': self._safe_float(player_dict.get('AST', 0)),
                                    'steals': self._safe_float(player_dict.get('STL', 0)),
                                    'blocks': self._safe_float(player_dict.get('BLK', 0)),
                                    'field_goal_pct': self._safe_float(player_dict.get('FG_PCT', 0)),
                                    'three_point_pct': self._safe_float(player_dict.get('FG3_PCT', 0)),
                                    'free_throw_pct': self._safe_float(player_dict.get('FT_PCT', 0)),
                                    'minutes_per_game': self._safe_float(player_dict.get('MIN', 0))
                                })
                            
                            if top_players:
                                logger.info(f"✓ Successfully retrieved top {len(top_players)} players by {stat_type} for season {try_season} using LeagueLeaders (dictionary method)")
                                return top_players
                        except Exception as dict_err:
                            logger.warning(f"Dictionary method also failed for {try_season}: {dict_err}")
                            continue
                        
                except Exception as api_err:
                    error_msg = str(api_err)
                    logger.warning(f"Season {try_season} failed: {error_msg[:100]}")
                    # Continue to next season
                    continue
            
            # All seasons failed
            logger.error(f"Failed to get top players by {stat_type} from all seasons tried: {seasons_to_try}")
            return []
            
        except Exception as e:
            logger.error(f"Error getting top players by {stat_type} from NBA API: {e}", exc_info=True)
            return []
    
    def _safe_float(self, value) -> float:
        """Safely convert value to float"""
        try:
            if value is None:
                return 0.0
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def get_standings(self, conference: str = None) -> List[Dict]:
        """
        Get current NBA standings using official NBA API
        conference: 'East', 'West', or None for all teams
        Returns list of team standings with conference information
        """
        try:
            logger.info(f"Fetching NBA standings" + (f" for {conference}ern Conference" if conference else " for all teams"))
            
            # Get league standings from NBA API
            standings = leaguestandingsv3.LeagueStandingsV3(season=self.current_season)
            time.sleep(0.6)  # Rate limit
            
            try:
                # Try dictionary method first
                data_dict = standings.get_dict()
                result_sets = data_dict.get('resultSets', [])
                
                if not result_sets:
                    logger.warning("No result sets found in standings")
                    return []
                
                # Find the standings result set
                standings_set = None
                for rs in result_sets:
                    if rs.get('name') == 'Standings':
                        standings_set = rs
                        break
                
                if not standings_set:
                    logger.warning("Standings result set not found")
                    return []
                
                headers = standings_set.get('headers', [])
                row_set = standings_set.get('rowSet', [])
                
                # Parse standings
                all_standings = []
                for row in row_set:
                    row_dict = dict(zip(headers, row))
                    
                    team_name = row_dict.get('TeamName', '')
                    conference_name = row_dict.get('Conference', '')
                    wins = self._safe_int(row_dict.get('WINS', row_dict.get('W', 0)))
                    losses = self._safe_int(row_dict.get('LOSSES', row_dict.get('L', 0)))
                    win_pct = row_dict.get('WinPCT', row_dict.get('PCT', 0))
                    # Try multiple possible field names for conference rank
                    conference_rank = self._safe_int(row_dict.get('ConferenceRank', row_dict.get('CONF_RANK', row_dict.get('CONFERENCE_RANK', 0))))
                    division_rank = self._safe_int(row_dict.get('DivisionRank', row_dict.get('DIV_RANK', 0)))
                    games_back = row_dict.get('ConferenceGamesBack', row_dict.get('CONF_GB', 0))
                    streak = row_dict.get('Streak', row_dict.get('STRK', ''))
                    
                    # Filter by conference if specified
                    if conference:
                        # Check if conference matches (handles "West" vs "Western Conference", "East" vs "Eastern Conference")
                        conf_upper = conference.upper()
                        conf_name_upper = conference_name.upper()
                        # Match if conference is in the name (e.g., "WEST" in "WESTERN CONFERENCE")
                        # or if name starts with conference (e.g., "WESTERN" starts with "WEST")
                        if conf_upper not in conf_name_upper and not conf_name_upper.startswith(conf_upper):
                            continue
                    
                    all_standings.append({
                        'team_name': team_name,
                        'conference': conference_name,
                        'wins': wins,
                        'losses': losses,
                        'win_percentage': round(float(win_pct), 3) if win_pct else 0,
                        'conference_rank': conference_rank,
                        'division_rank': division_rank,
                        'games_back': float(games_back) if games_back else 0,
                        'streak': streak,
                        'games_played': wins + losses
                    })
                
                # Sort by conference, then by win percentage (if rank is 0, calculate rank)
                # Calculate rank if missing
                for conf in ['East', 'West']:
                    conf_teams = [s for s in all_standings if conf in s['conference']]
                    conf_teams.sort(key=lambda x: x['win_percentage'], reverse=True)
                    for idx, team in enumerate(conf_teams, 1):
                        if team['conference_rank'] == 0:
                            team['conference_rank'] = idx
                
                # Sort by conference, then by rank
                all_standings.sort(key=lambda x: (x['conference'], x['conference_rank']))
                
                logger.info(f"✓ Retrieved {len(all_standings)} team standings from NBA API")
                return all_standings
                
            except Exception as e:
                logger.warning(f"Dictionary parsing failed, trying DataFrame method: {e}")
                
                # DataFrame fallback
                try:
                    df = standings.get_data_frames()[0]
                    
                    all_standings = []
                    for _, row in df.iterrows():
                        team_name = str(row.get('TeamName', ''))
                        conference_name = str(row.get('Conference', ''))
                        
                        # Filter by conference if specified
                        if conference:
                            # Check if conference matches (handles "West" vs "Western Conference", "East" vs "Eastern Conference")
                            conf_upper = conference.upper()
                            conf_name_upper = conference_name.upper()
                            # Match if conference is in the name (e.g., "WEST" in "WESTERN CONFERENCE")
                            # or if name starts with conference (e.g., "WESTERN" starts with "WEST")
                            if conf_upper not in conf_name_upper and not conf_name_upper.startswith(conf_upper):
                                continue
                        
                        wins = self._safe_int(row.get('WINS', row.get('W', 0)))
                        losses = self._safe_int(row.get('LOSSES', row.get('L', 0)))
                        win_pct = float(row.get('WinPCT', row.get('PCT', 0))) if (row.get('WinPCT') or row.get('PCT')) else 0
                        conference_rank = self._safe_int(row.get('ConferenceRank', row.get('CONF_RANK', row.get('CONFERENCE_RANK', 0))))
                        division_rank = self._safe_int(row.get('DivisionRank', row.get('DIV_RANK', 0)))
                        games_back = float(row.get('ConferenceGamesBack', row.get('CONF_GB', 0))) if (row.get('ConferenceGamesBack') or row.get('CONF_GB')) else 0
                        streak = str(row.get('Streak', row.get('STRK', '')))
                        
                        all_standings.append({
                            'team_name': team_name,
                            'conference': conference_name,
                            'wins': wins,
                            'losses': losses,
                            'win_percentage': round(win_pct, 3),
                            'conference_rank': conference_rank,
                            'division_rank': division_rank,
                            'games_back': games_back,
                            'streak': streak,
                            'games_played': wins + losses
                        })
                    
                    # Calculate rank if missing, then sort
                    for conf in ['East', 'West']:
                        conf_teams = [s for s in all_standings if conf in s['conference']]
                        conf_teams.sort(key=lambda x: x['win_percentage'], reverse=True)
                        for idx, team in enumerate(conf_teams, 1):
                            if team['conference_rank'] == 0:
                                team['conference_rank'] = idx
                    
                    # Sort by conference, then by rank
                    all_standings.sort(key=lambda x: (x['conference'], x['conference_rank']))
                    
                    logger.info(f"✓ Retrieved {len(all_standings)} team standings from NBA API (DataFrame)")
                    return all_standings
                    
                except Exception as df_err:
                    logger.error(f"DataFrame parsing also failed: {df_err}")
                    return []
            
        except Exception as e:
            logger.error(f"Error getting standings from NBA API: {e}", exc_info=True)
            return []
    
    def _safe_int(self, value) -> int:
        """Safely convert value to int, handling None and string values"""
        if value is None:
            return 0
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0
