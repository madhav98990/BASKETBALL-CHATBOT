"""
Ball Don't Lie API Service - Free NBA API
https://www.balldontlie.io/ - Free, no API key required
"""
import requests
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BallDontLieAPI:
    """Ball Don't Lie API - Free NBA API"""
    
    BASE_URL = "https://www.balldontlie.io/api/v1"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_player(self, player_name: str) -> Optional[Dict]:
        """Search for player by name"""
        try:
            # Ball Don't Lie API - try searching by first name and last name separately
            name_parts = player_name.strip().split()
            if not name_parts:
                return None
            
            first_name = name_parts[0]
            last_name = name_parts[-1] if len(name_parts) > 1 else ""
            
            # Try searching with first name first
            url = f"{self.BASE_URL}/players"
            
            # Try multiple search strategies
            search_terms = []
            if first_name and last_name:
                search_terms = [f"{first_name} {last_name}", first_name, last_name]
            else:
                search_terms = [first_name]
            
            for search_term in search_terms:
                params = {'search': search_term, 'per_page': 50}
                
                response = self.session.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    players = data.get('data', [])
                    
                    if players:
                        # Find best match - exact match first
                        target_name_lower = player_name.lower()
                        for player in players:
                            full_name = f"{player.get('first_name', '')} {player.get('last_name', '')}".lower()
                            
                            # Exact match
                            if full_name == target_name_lower:
                                logger.info(f"Found exact match in Ball Don't Lie: {player.get('first_name')} {player.get('last_name')}")
                                return player
                        
                        # Partial match - all parts must be in name
                        name_parts_lower = [part.lower() for part in name_parts]
                        for player in players:
                            full_name = f"{player.get('first_name', '')} {player.get('last_name', '')}".lower()
                            if all(part in full_name for part in name_parts_lower):
                                logger.info(f"Found partial match in Ball Don't Lie: {player.get('first_name')} {player.get('last_name')}")
                                return player
            
            # Ball Don't Lie API appears to be down or changed - return None gracefully
            logger.debug(f"Player '{player_name}' not found in Ball Don't Lie API (API may be unavailable)")
            return None
        except Exception as e:
            logger.error(f"Error searching player in Ball Don't Lie: {e}", exc_info=True)
            return None
    
    def get_player_recent_stats(self, player_name: str, limit: int = 5) -> List[Dict]:
        """
        Get player's recent game stats from Ball Don't Lie API
        """
        try:
            logger.info(f"Fetching stats for {player_name} from Ball Don't Lie API")
            
            # Step 1: Search for player
            player = self.search_player(player_name)
            if not player:
                logger.warning(f"Player {player_name} not found in Ball Don't Lie API")
                return []
            
            player_id = player.get('id')
            if not player_id:
                return []
            
            # Step 2: Get current season
            current_season = self._get_current_season()
            
            # Step 3: Get player stats for current season
            url = f"{self.BASE_URL}/stats"
            params = {
                'player_ids[]': player_id,
                'seasons[]': current_season,
                'per_page': limit
            }
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                stats_list = data.get('data', [])
                
                results = []
                for stat_entry in stats_list[:limit]:
                    game = stat_entry.get('game', {})
                    player_info = stat_entry.get('player', {})
                    
                    # Get game details
                    game_id = game.get('id')
                    game_date = game.get('date', '')[:10] if game.get('date') else ''
                    
                    # Get team info from stat entry
                    team = stat_entry.get('team', {})
                    player_team = team.get('abbreviation', '')
                    
                    # Get opponent team from game
                    home_team = game.get('home_team', {})
                    visitor_team = game.get('visitor_team', {})
                    home_abbrev = home_team.get('abbreviation', '') if isinstance(home_team, dict) else ''
                    visitor_abbrev = visitor_team.get('abbreviation', '') if isinstance(visitor_team, dict) else ''
                    
                    # Determine which is team1 and team2
                    if player_team == home_abbrev:
                        team1_name = visitor_abbrev
                        team2_name = home_abbrev
                    else:
                        team1_name = visitor_abbrev
                        team2_name = home_abbrev
                    
                    results.append({
                        'player_name': f"{player_info.get('first_name', '')} {player_info.get('last_name', '')}",
                        'points': int(stat_entry.get('pts', 0) or 0),
                        'rebounds': int(stat_entry.get('reb', 0) or 0),
                        'assists': int(stat_entry.get('ast', 0) or 0),
                        'steals': int(stat_entry.get('stl', 0) or 0),
                        'blocks': int(stat_entry.get('blk', 0) or 0),
                        'match_date': game_date,
                        'team1_name': team1_name,
                        'team2_name': team2_name,
                        'player_team': player_team
                    })
                
                if results:
                    logger.info(f"✓ Got {len(results)} stats from Ball Don't Lie API")
                    return results
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching player stats from Ball Don't Lie: {e}", exc_info=True)
            return []
    
    def _get_current_season(self) -> int:
        """Get current NBA season year"""
        today = date.today()
        # NBA season starts in October, so if month >= 10, season is current year, else previous year
        if today.month >= 10:
            return today.year
        else:
            return today.year - 1
    
    def _get_game_details(self, game_id: int) -> Optional[Dict]:
        """Get game details by game ID"""
        try:
            url = f"{self.BASE_URL}/games/{game_id}"
            response = self.session.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.debug(f"Error getting game details: {e}")
            return None
    
    def get_games_for_date(self, target_date: date) -> List[Dict]:
        """
        Get all NBA games for a specific date (today, yesterday, or any date)
        Returns list of games with team names, times, and status
        
        Args:
            target_date: The date to fetch games for
            
        Returns:
            List of game dictionaries with team info, scores, and status
        """
        try:
            date_str = target_date.strftime('%Y-%m-%d')
            current_season = self._get_current_season()
            
            # Determine if this is today, yesterday, or another date
            today = date.today()
            if target_date == today:
                date_label = "today"
            elif target_date == today - timedelta(days=1):
                date_label = "yesterday"
            else:
                date_label = date_str
            
            logger.info(f"Fetching games for {date_label} ({date_str}) from Ball Don't Lie API")
            
            # Ball Don't Lie API uses start_date and end_date parameters
            # Try multiple parameter formats for compatibility
            url = f"{self.BASE_URL}/games"
            
            # Try format 1: start_date and end_date (same date)
            params = {
                'start_date': date_str,
                'end_date': date_str,
                'seasons[]': current_season,
                'per_page': 50
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            # If that doesn't work, try dates[] format
            if response.status_code != 200:
                params = {
                    'dates[]': date_str,
                    'seasons[]': current_season,
                    'per_page': 50
                }
                response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Ball Don't Lie API returned status {response.status_code} for {date_label}'s games")
                return []
            
            data = response.json()
            games_data = data.get('data', [])
            
            if not games_data:
                logger.info(f"No games found for {date_label} ({date_str})")
                return []
            
            games = []
            for game in games_data:
                visitor_team = game.get('visitor_team', {})
                home_team = game.get('home_team', {})
                
                visitor_abbrev = visitor_team.get('abbreviation', '')
                home_abbrev = home_team.get('abbreviation', '')
                visitor_name = visitor_team.get('full_name', visitor_abbrev)
                home_name = home_team.get('full_name', home_abbrev)
                
                # Get game status
                status = game.get('status', '')
                is_completed = status == 'Final'
                is_live = status and status != 'Final' and status != ''
                
                # Get scores if available
                visitor_score = game.get('visitor_team_score')
                home_score = game.get('home_team_score')
                
                # Get game time
                game_date = game.get('date', '')
                game_time = ''
                if game_date:
                    try:
                        # Parse ISO format datetime
                        dt = datetime.fromisoformat(game_date.replace('Z', '+00:00'))
                        game_time = dt.strftime('%I:%M %p') if dt else ''
                    except:
                        game_time = ''
                
                game_info = {
                    'team1_name': visitor_abbrev,
                    'team2_name': home_abbrev,
                    'team1_display': visitor_name,
                    'team2_display': home_name,
                    'match_date': date_str,
                    'game_time': game_time,
                    'venue': home_team.get('city', ''),
                    'status': 'completed' if is_completed else ('live' if is_live else 'upcoming'),
                    'game_status': status,
                    'team1_score': visitor_score if visitor_score is not None else None,
                    'team2_score': home_score if home_score is not None else None
                }
                
                games.append(game_info)
            
            logger.info(f"✓ Found {len(games)} games for {date_label} from Ball Don't Lie API")
            return games
            
        except Exception as e:
            logger.error(f"Error fetching games for {target_date} from Ball Don't Lie API: {e}", exc_info=True)
            return []
    
    def get_games_for_today(self) -> List[Dict]:
        """
        Get all NBA games scheduled for today
        Returns list of games with team names, times, and status
        """
        return self.get_games_for_date(date.today())
    
    def get_games_for_yesterday(self) -> List[Dict]:
        """
        Get all NBA games from yesterday
        Returns list of games with team names, times, and status
        """
        yesterday = date.today() - timedelta(days=1)
        return self.get_games_for_date(yesterday)
    
    def get_team_most_recent_game_result(self, team_name: str, days_back: int = 30) -> Optional[Dict]:
        """
        Get a team's most recent game result using Ball Don't Lie API
        Returns whether the team won or lost, opponent, score, and date
        
        Args:
            team_name: Team name (e.g., 'knicks', 'lakers', 'warriors')
            days_back: Number of days to look back for games (default: 30)
            
        Returns:
            Dictionary with game result info or None if not found
        """
        try:
            # Map team name to abbreviation
            team_map = {
                'warriors': 'GS', 'golden state': 'GS', 'gsw': 'GS',
                'lakers': 'LAL', 'celtics': 'BOS', 'bucks': 'MIL',
                'nuggets': 'DEN', 'suns': 'PHX', 'heat': 'MIA',
                'mavericks': 'DAL', 'clippers': 'LAC', '76ers': 'PHI',
                'cavaliers': 'CLE', 'knicks': 'NYK', 'hawks': 'ATL',
                'thunder': 'OKC', 'timberwolves': 'MIN', 'kings': 'SAC',
                'pelicans': 'NO', 'grizzlies': 'MEM', 'raptors': 'TOR',
                'nets': 'BKN', 'bulls': 'CHI', 'pistons': 'DET',
                'pacers': 'IND', 'hornets': 'CHA', 'magic': 'ORL',
                'wizards': 'WSH', 'trail blazers': 'POR', 'jazz': 'UTAH',
                'rockets': 'HOU', 'spurs': 'SAS'
            }
            team_abbrev = team_map.get(team_name.lower(), team_name[:3].upper())
            
            logger.info(f"Getting most recent game result for {team_name} (abbrev: {team_abbrev}) from Ball Don't Lie API")
            
            # Get current season
            current_season = self._get_current_season()
            
            # Search for games in the last N days
            today = date.today()
            start_date = today - timedelta(days=days_back)
            
            url = f"{self.BASE_URL}/games"
            params = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': today.strftime('%Y-%m-%d'),
                'seasons[]': current_season,
                'per_page': 100  # Get more games to find the most recent
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Ball Don't Lie API returned status {response.status_code} for team game result")
                return None
            
            data = response.json()
            games_data = data.get('data', [])
            
            if not games_data:
                logger.info(f"No games found for {team_name} in the last {days_back} days")
                return None
            
            # Find games involving this team, sorted by date (most recent first)
            team_games = []
            for game in games_data:
                visitor_team = game.get('visitor_team', {})
                home_team = game.get('home_team', {})
                
                visitor_abbrev = visitor_team.get('abbreviation', '')
                home_abbrev = home_team.get('abbreviation', '')
                
                # Check if this game involves our team
                if team_abbrev.upper() in [visitor_abbrev.upper(), home_abbrev.upper()]:
                    # Only include completed games
                    status = game.get('status', '')
                    if status == 'Final':
                        team_games.append(game)
            
            if not team_games:
                logger.info(f"No completed games found for {team_name} in the last {days_back} days")
                return None
            
            # Sort by date (most recent first)
            team_games.sort(key=lambda g: g.get('date', ''), reverse=True)
            most_recent_game = team_games[0]
            
            # Extract game information
            visitor_team = most_recent_game.get('visitor_team', {})
            home_team = most_recent_game.get('home_team', {})
            
            visitor_abbrev = visitor_team.get('abbreviation', '')
            home_abbrev = home_team.get('abbreviation', '')
            visitor_name = visitor_team.get('full_name', visitor_abbrev)
            home_name = home_team.get('full_name', home_abbrev)
            
            visitor_score = most_recent_game.get('visitor_team_score')
            home_score = most_recent_game.get('home_team_score')
            
            # Validate scores are available
            if visitor_score is None or home_score is None:
                logger.warning(f"Missing scores for game: visitor={visitor_score}, home={home_score}")
                return None
            
            # Determine if team is home or visitor - use case-insensitive comparison
            is_home = team_abbrev.upper() == home_abbrev.upper()
            is_visitor = team_abbrev.upper() == visitor_abbrev.upper()
            
            # Validate team is actually in this game
            if not is_home and not is_visitor:
                logger.warning(f"Team {team_name} (abbrev: {team_abbrev}) not found in game (home: {home_abbrev}, visitor: {visitor_abbrev})")
                return None
            
            # Assign team and opponent scores correctly
            if is_home:
                team_score = home_score
                opponent_score = visitor_score
            else:  # is_visitor
                team_score = visitor_score
                opponent_score = home_score
            
            # Determine win/loss - team wins if their score is higher than opponent's
            did_win = team_score > opponent_score
            
            # Final validation: ensure win/loss determination is correct
            if did_win != (team_score > opponent_score):
                logger.error(f"Critical error: win/loss determination failed for {team_name}. Scores: {team_score}-{opponent_score}")
                # Force correct determination
                did_win = team_score > opponent_score
            
            # Get opponent name
            opponent_team = home_team if not is_home else visitor_team
            opponent_name = opponent_team.get('full_name', '')
            if not opponent_name:
                opponent_name = opponent_team.get('abbreviation', '')
            
            # Get game date
            game_date_str = most_recent_game.get('date', '')
            game_date = game_date_str[:10] if game_date_str else ''
            
            # Format date for display
            try:
                if game_date:
                    date_obj = datetime.fromisoformat(game_date_str.replace('Z', '+00:00'))
                    game_date_display = date_obj.strftime('%b %d, %Y')
                else:
                    game_date_display = game_date
            except:
                game_date_display = game_date
            
            # Get matchup
            matchup = f"{visitor_name} @ {home_name}" if not is_home else f"{home_name} vs {opponent_name}"
            
            logger.info(f"✓ Found most recent game for {team_name}: {game_date_display} {matchup} - {'W' if did_win else 'L'} {team_score}-{opponent_score}")
            
            return {
                'team_name': team_name.title(),
                'team_abbrev': team_abbrev,
                'opponent_name': opponent_name,
                'did_win': did_win,
                'team_score': team_score if team_score is not None else 0,
                'opponent_score': opponent_score if opponent_score is not None else 0,
                'game_date': game_date_display,
                'matchup': matchup
            }
            
        except Exception as e:
            logger.error(f"Error getting team game result from Ball Don't Lie API: {e}", exc_info=True)
            return None
    
    def get_top_players_by_stat(self, stat_type: str = 'points', limit: int = 10, season: str = None) -> List[Dict]:
        """
        Get top players by a specific statistic using Ball Don't Lie API
        Aggregates player stats from season games
        Note: This method may be slower as it requires aggregating stats from multiple API calls
        stat_type: 'points', 'assists', 'rebounds', 'steals', 'blocks'
        limit: number of players to return
        season: season year (e.g., 2024), defaults to current season
        """
        try:
            logger.info(f"Getting top {limit} players by {stat_type} using Ball Don't Lie API")
            
            # Map stat types
            stat_map = {
                'points': 'pts',
                'assists': 'ast',
                'rebounds': 'reb',
                'steals': 'stl',
                'blocks': 'blk',
                'score': 'pts',
                'scoring': 'pts'
            }
            
            stat_key = stat_map.get(stat_type.lower(), 'pts')
            
            # Get current season
            if not season:
                current_season = self._get_current_season()
            else:
                # Extract year from season string like "2024-25" -> 2024
                try:
                    current_season = int(season.split('-')[0])
                except:
                    current_season = self._get_current_season()
            
            # Get all stats for the season (this endpoint returns stats from all players)
            url = f"{self.BASE_URL}/stats"
            all_stats = []
            page = 0
            per_page = 100
            
            # Fetch stats in pages (Ball Don't Lie API paginates)
            max_pages = 10  # Limit to avoid too many API calls
            while page < max_pages:
                try:
                    params = {
                        'seasons[]': current_season,
                        'per_page': per_page,
                        'page': page
                    }
                    
                    response = self.session.get(url, params=params, timeout=10)
                    if response.status_code != 200:
                        break
                    
                    data = response.json()
                    stats_list = data.get('data', [])
                    
                    if not stats_list:
                        break
                    
                    all_stats.extend(stats_list)
                    
                    # Check if there are more pages
                    meta = data.get('meta', {})
                    next_page = meta.get('next_page')
                    if not next_page or next_page == page:
                        break
                    
                    page += 1
                    
                    # Rate limiting
                    import time
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.warning(f"Error fetching stats page {page} from Ball Don't Lie: {e}")
                    break
            
            if not all_stats:
                logger.warning("No stats found from Ball Don't Lie API for season aggregation")
                return []
            
            # Aggregate stats by player
            player_stats_accum = {}  # {player_id: {stats: [], games: 0, name: '', team: ''}}
            
            for stat_entry in all_stats:
                try:
                    player_info = stat_entry.get('player', {})
                    if not player_info:
                        continue
                    
                    player_id = player_info.get('id')
                    if not player_id:
                        continue
                    
                    # Initialize player if not exists
                    if player_id not in player_stats_accum:
                        first_name = player_info.get('first_name', '')
                        last_name = player_info.get('last_name', '')
                        full_name = f"{first_name} {last_name}".strip()
                        
                        team = stat_entry.get('team', {})
                        team_abbrev = team.get('abbreviation', '') if isinstance(team, dict) else ''
                        
                        player_stats_accum[player_id] = {
                            'player_name': full_name,
                            'team': team_abbrev,
                            'pts': [],
                            'reb': [],
                            'ast': [],
                            'stl': [],
                            'blk': [],
                            'games': 0
                        }
                    
                    # Accumulate stats
                    pts = float(stat_entry.get('pts', 0) or 0)
                    reb = float(stat_entry.get('reb', 0) or 0)
                    ast = float(stat_entry.get('ast', 0) or 0)
                    stl = float(stat_entry.get('stl', 0) or 0)
                    blk = float(stat_entry.get('blk', 0) or 0)
                    
                    player_stats_accum[player_id]['pts'].append(pts)
                    player_stats_accum[player_id]['reb'].append(reb)
                    player_stats_accum[player_id]['ast'].append(ast)
                    player_stats_accum[player_id]['stl'].append(stl)
                    player_stats_accum[player_id]['blk'].append(blk)
                    player_stats_accum[player_id]['games'] += 1
                    
                except Exception as e:
                    logger.debug(f"Error processing stat entry: {e}")
                    continue
            
            # Calculate per-game averages
            MIN_GAMES = 5  # Minimum games to qualify
            players_with_averages = []
            
            for player_id, stats in player_stats_accum.items():
                if stats['games'] < MIN_GAMES:
                    continue
                
                points_avg = sum(stats['pts']) / len(stats['pts']) if stats['pts'] else 0
                rebounds_avg = sum(stats['reb']) / len(stats['reb']) if stats['reb'] else 0
                assists_avg = sum(stats['ast']) / len(stats['ast']) if stats['ast'] else 0
                steals_avg = sum(stats['stl']) / len(stats['stl']) if stats['stl'] else 0
                blocks_avg = sum(stats['blk']) / len(stats['blk']) if stats['blk'] else 0
                
                # Get the stat value based on stat_type
                stat_value_map = {
                    'pts': points_avg,
                    'ast': assists_avg,
                    'reb': rebounds_avg,
                    'stl': steals_avg,
                    'blk': blocks_avg
                }
                
                stat_value = stat_value_map.get(stat_key, points_avg)
                
                players_with_averages.append({
                    'player_name': stats['player_name'],
                    'team': stats['team'],
                    'stat_value': round(stat_value, 2),
                    'stat_type': stat_type,
                    'games_played': stats['games'],
                    'points': round(points_avg, 2),
                    'rebounds': round(rebounds_avg, 2),
                    'assists': round(assists_avg, 2),
                    'steals': round(steals_avg, 2),
                    'blocks': round(blocks_avg, 2),
                    'field_goal_pct': 0.0,
                    'three_point_pct': 0.0,
                    'free_throw_pct': 0.0,
                    'minutes_per_game': 0.0
                })
            
            # Sort by stat_value descending and take top N
            players_with_averages.sort(key=lambda x: x['stat_value'], reverse=True)
            top_players = players_with_averages[:limit]
            
            logger.info(f"✓ Successfully retrieved {len(top_players)} top players by {stat_type} from Ball Don't Lie API (aggregated from {len(all_stats)} game stats)")
            return top_players
            
        except Exception as e:
            logger.error(f"Error getting top players by {stat_type} from Ball Don't Lie API: {e}", exc_info=True)
            return []

