"""
NBA API Service - Fetches real-time NBA data from external APIs
Uses Ball Don't Lie API (free, no key required) and ESPN as fallback
"""
import logging
import requests
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from .espn_api import ESPNNBAApi
except ImportError:
    from espn_api import ESPNNBAApi

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NBAApiService:
    """Service to fetch real-time NBA data from external APIs"""
    
    # Try multiple API endpoints
    BASE_URL = "https://www.balldontlie.io/api/v1"
    ALTERNATIVE_BASE = "https://api.balldontlie.io/v1"  # Alternative endpoint
    ESPN_BASE = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba"
    
    # Team name mapping from database to API
    TEAM_MAPPING = {
        'Lakers': 'Los Angeles Lakers',
        'Warriors': 'Golden State Warriors',
        'Celtics': 'Boston Celtics',
        'Bucks': 'Milwaukee Bucks',
        'Nuggets': 'Denver Nuggets',
        'Suns': 'Phoenix Suns',
        'Heat': 'Miami Heat',
        'Mavericks': 'Dallas Mavericks',
        'Clippers': 'LA Clippers',
        '76ers': 'Philadelphia 76ers',
        'Cavaliers': 'Cleveland Cavaliers',
        'Knicks': 'New York Knicks',
        'Hawks': 'Atlanta Hawks',
        'Thunder': 'Oklahoma City Thunder',
        'Timberwolves': 'Minnesota Timberwolves',
        'Kings': 'Sacramento Kings',
        'Pelicans': 'New Orleans Pelicans',
        'Grizzlies': 'Memphis Grizzlies',
        'Raptors': 'Toronto Raptors',
        'Nets': 'Brooklyn Nets',
        'Bulls': 'Chicago Bulls',
        'Pistons': 'Detroit Pistons',
        'Pacers': 'Indiana Pacers',
        'Hornets': 'Charlotte Hornets',
        'Magic': 'Orlando Magic',
        'Wizards': 'Washington Wizards',
        'Trail Blazers': 'Portland Trail Blazers',
        'Jazz': 'Utah Jazz',
        'Rockets': 'Houston Rockets',
        'Spurs': 'San Antonio Spurs'
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.espn_api = ESPNNBAApi()  # ESPN as fallback
    
    def _make_request(self, endpoint: str, params: dict = None, retries: int = 3):
        """Make HTTP request with retries and multiple base URLs"""
        # Try multiple base URLs
        base_urls = [self.BASE_URL, self.ALTERNATIVE_BASE]
        
        for base_url in base_urls:
            url = f"{base_url}/{endpoint}"
            for attempt in range(retries):
                try:
                    response = self.session.get(url, params=params, timeout=10)
                    if response.status_code == 200:
                        return response.json()
                    elif response.status_code != 404:
                        # Retry on non-404 errors
                        if attempt < retries - 1:
                            time.sleep(1)
                            continue
                except requests.exceptions.RequestException as e:
                    logger.warning(f"API request failed (attempt {attempt + 1}): {e}")
                    if attempt < retries - 1:
                        time.sleep(1)
                    continue
            
            # If 404 or all retries failed, try next base URL
            if response.status_code == 404:
                continue
        
        logger.error(f"Failed to fetch data from all endpoints for {endpoint}")
        return None
    
    def get_recent_games(self, days: int = 7, team_name: str = None, limit: int = 10) -> List[Dict]:
        """Get recent game results"""
        try:
            # Try ESPN API first (PRIMARY)
            logger.info("Trying ESPN API first for recent games")
            espn_games = self.espn_api.get_recent_games(days=days, limit=limit)
            if espn_games:
                return espn_games
            
            # Fallback to Ball Don't Lie API
            logger.info("Falling back to Ball Don't Lie API for recent games")
            end_date = date.today()
            start_date = end_date - timedelta(days=min(days, 30))  # Limit to 30 days
            
            # Try without season first, then with different seasons
            seasons_to_try = [None, self._get_current_season(), 2024, 2023]
            
            for season in seasons_to_try:
                params = {
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'per_page': min(limit, 100)
                }
                
                if season:
                    params['seasons[]'] = season
                
                if team_name:
                    team_id = self._get_team_id(team_name)
                    if team_id:
                        params['team_ids[]'] = team_id
                
                data = self._make_request('games', params)
                if data and 'data' in data and len(data['data']) > 0:
                    games = []
                    for game in data['data']:
                        if game.get('status') == 'Final':
                            visitor_team = game.get('visitor_team', {})
                            home_team = game.get('home_team', {})
                            visitor_score = game.get('visitor_team_score', 0)
                            home_score = game.get('home_team_score', 0)
                            
                            games.append({
                                'team1_name': visitor_team.get('abbreviation', ''),
                                'team2_name': home_team.get('abbreviation', ''),
                                'team1_score': visitor_score,
                                'team2_score': home_score,
                                'match_date': game.get('date', '')[:10] if game.get('date') else '',
                                'venue': home_team.get('city', ''),
                                'winner': visitor_team.get('abbreviation', '') if visitor_score > home_score else home_team.get('abbreviation', '')
                            })
                    
                    if games:
                        return games[:limit]
            
            # If all sources failed, return empty
            return []
        except Exception as e:
            logger.error(f"Error getting recent games: {e}")
            return []
    
    def get_upcoming_games(self, days: int = 7, team_name: str = None, limit: int = 20) -> List[Dict]:
        """Get upcoming scheduled games"""
        try:
            start_date = date.today()
            end_date = start_date + timedelta(days=days)
            
            # Try multiple seasons in case current season isn't available
            seasons_to_try = [self._get_current_season(), 2024, 2023]
            
            for season in seasons_to_try:
                params = {
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'per_page': min(limit, 100),
                    'seasons[]': season
                }
                
                if team_name:
                    team_id = self._get_team_id(team_name)
                    if team_id:
                        params['team_ids[]'] = team_id
                
                data = self._make_request('games', params)
                if data and 'data' in data and len(data['data']) > 0:
                    games = []
                    for game in data['data']:
                        status = game.get('status', '')
                        # Get upcoming games (not final)
                        if status and status != 'Final':
                            games.append({
                                'team1_name': game.get('visitor_team', {}).get('abbreviation', ''),
                                'team2_name': game.get('home_team', {}).get('abbreviation', ''),
                                'match_date': game.get('date', '')[:10] if game.get('date') else '',
                                'venue': game.get('home_team', {}).get('city', ''),
                                'status': 'upcoming'
                            })
                    
                    if games:
                        return games[:limit]
            
            # If no upcoming games found, try without season filter
            params = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'per_page': min(limit, 100)
            }
            
            data = self._make_request('games', params)
            if data and 'data' in data:
                games = []
                for game in data['data']:
                    status = game.get('status', '')
                    if status and status != 'Final':
                        games.append({
                            'team1_name': game.get('visitor_team', {}).get('abbreviation', ''),
                            'team2_name': game.get('home_team', {}).get('abbreviation', ''),
                            'match_date': game.get('date', '')[:10] if game.get('date') else '',
                            'venue': game.get('home_team', {}).get('city', ''),
                            'status': 'upcoming'
                        })
                
                return games[:limit]
            
            # Fallback to ESPN API
            logger.info("Falling back to ESPN API for upcoming games")
            espn_games = self.espn_api.get_upcoming_games(days=days, limit=limit)
            if espn_games:
                return espn_games
            
            return []
        except Exception as e:
            logger.error(f"Error getting upcoming games: {e}")
            return []
    
    def get_player_stats(self, player_name: str, limit: int = 5, team_filter: str = None) -> List[Dict]:
        """Get player statistics from recent games - PRIMARY: Use ESPN API for real-time data"""
        try:
            logger.info(f"Fetching real-time stats for {player_name} from ESPN API")
            
            # Use ESPN API to get recent player stats
            stats = self.espn_api.get_player_recent_stats(player_name, limit=limit)
            
            if stats and len(stats) > 0:
                logger.info(f"✓ Got {len(stats)} real-time stats from ESPN for {player_name}")
                
                # Filter by team if specified
                if team_filter:
                    # Map team filter to abbreviations
                    team_abbrev_map = {
                        'lakers': 'LAL', 'warriors': 'GS', 'celtics': 'BOS', 
                        'bucks': 'MIL', 'nuggets': 'DEN', 'suns': 'PHX',
                        'heat': 'MIA', 'mavericks': 'DAL', 'clippers': 'LAC',
                        '76ers': 'PHI', 'cavaliers': 'CLE', 'knicks': 'NYK',
                        'hawks': 'ATL', 'thunder': 'OKC', 'timberwolves': 'MIN',
                        'kings': 'SAC', 'pelicans': 'NO', 'grizzlies': 'MEM',
                        'raptors': 'TOR', 'nets': 'BKN', 'bulls': 'CHI',
                        'pistons': 'DET', 'pacers': 'IND', 'hornets': 'CHA',
                        'magic': 'ORL', 'wizards': 'WSH', 'trail blazers': 'POR',
                        'jazz': 'UTAH', 'rockets': 'HOU', 'spurs': 'SA'
                    }
                    team_abbrevs = [team_abbrev_map.get(team_filter.lower(), team_filter[:3].upper())]
                    # Also add variations
                    if team_filter.lower() == 'warriors':
                        team_abbrevs.extend(['GS', 'GSW'])
                    elif team_filter.lower() == 'suns':
                        team_abbrevs.extend(['PHX', 'PHO'])
                    elif team_filter.lower() == 'spurs':
                        team_abbrevs.extend(['SA', 'SAS'])
                    
                    filtered = []
                    for stat in stats:
                        team1 = stat.get('team1_name', '').upper()
                        team2 = stat.get('team2_name', '').upper()
                        player_team = stat.get('player_team', '').upper()
                        
                        for abbrev in team_abbrevs:
                            abbrev_upper = abbrev.upper()
                            if abbrev_upper in [team1, team2]:
                                # Make sure player is on the other team
                                if (abbrev_upper == team1 and player_team != team1) or \
                                   (abbrev_upper == team2 and player_team != team2):
                                    filtered.append(stat)
                                    logger.info(f"✓ Filtered match: {player_name} vs {abbrev_upper} on {stat.get('match_date')}")
                                    break
                    
                    if filtered:
                        logger.info(f"Filtered to {len(filtered)} stats matching {team_filter}")
                        return filtered[:limit]
                    else:
                        logger.warning(f"No stats found for {player_name} vs {team_filter} in real-time data")
                
                return stats[:limit]
            else:
                logger.warning(f"No real-time stats found for {player_name} from ESPN API")
                return []
                
        except Exception as e:
            logger.error(f"Error getting player stats from API: {e}", exc_info=True)
            return []
    
    def get_player_season_averages(self, player_name: str) -> Optional[Dict]:
        """Get player's season averages"""
        try:
            # For now, return None to trigger database calculation
            # The database can calculate averages from player_stats table
            logger.info(f"Using database fallback for {player_name} season averages")
            return None
        except Exception as e:
            logger.error(f"Error getting player season averages: {e}")
            return None
    
    def get_game_leaders(self, team_name: str = None, limit: int = 1) -> List[Dict]:
        """Get game leaders (top scorers, etc.) from recent games"""
        try:
            # Get recent games first
            games = self.get_recent_games(days=7, team_name=team_name, limit=limit)
            if not games:
                return []
            
            # For now, return game info - actual leader stats would need boxscore data
            leaders = []
            for game in games:
                leaders.append({
                    'game_date': game.get('match_date'),
                    'team1': game.get('team1_name'),
                    'team2': game.get('team2_name'),
                    'team1_score': game.get('team1_score'),
                    'team2_score': game.get('team2_score'),
                    'note': 'Leader stats require boxscore data - using database fallback'
                })
            return leaders
        except Exception as e:
            logger.error(f"Error getting game leaders: {e}")
            return []
    
    def get_top_players_by_stat(self, stat: str, limit: int = 5, date: str = None) -> List[Dict]:
        """Get top players by a specific stat (points, assists, rebounds, etc.)"""
        try:
            # This would require aggregating stats across all games
            # For now, return empty to trigger database calculation
            logger.info(f"Using database fallback for top {limit} players by {stat}")
            return []
        except Exception as e:
            logger.error(f"Error getting top players: {e}")
            return []
    
    def get_standings(self, conference: str = None) -> List[Dict]:
        """Get current team standings - calculated from game results"""
        try:
            # Try ESPN API first (better for standings)
            espn_standings = self.espn_api.get_standings()
            if espn_standings:
                return espn_standings
            
            # Fallback to calculating from games
            standings = self._calculate_standings_from_games()
            if standings:
                return standings
            logger.warning("Could not calculate standings from games")
            return []
        except Exception as e:
            logger.error(f"Error getting standings: {e}")
            return []
    
    def get_live_games(self) -> List[Dict]:
        """Get currently live games"""
        try:
            today = date.today().strftime('%Y-%m-%d')
            params = {
                'dates[]': today,
                'per_page': 50,
                'seasons[]': self._get_current_season()
            }
            
            data = self._make_request('games', params)
            if not data or 'data' not in data:
                return []
            
            live_games = []
            for game in data['data']:
                status = game.get('status', '')
                if status not in ['Final', '']:  # Not finished and has a status
                    live_games.append({
                        'team1_name': game['visitor_team']['abbreviation'],
                        'team2_name': game['home_team']['abbreviation'],
                        'team1_score': game.get('visitor_team_score', 0),
                        'team2_score': game.get('home_team_score', 0),
                        'game_status': status,
                        'match_date': game['date'][:10],
                        'venue': game.get('home_team', {}).get('city', '')
                    })
            
            return live_games
        except Exception as e:
            logger.error(f"Error getting live games: {e}")
            return []
    
    def _get_team_id(self, team_name: str) -> Optional[int]:
        """Get team ID from team name"""
        try:
            # Try abbreviation first
            abbrev_map = {
                'Lakers': 'LAL', 'Warriors': 'GSW', 'Celtics': 'BOS', 'Bucks': 'MIL',
                'Nuggets': 'DEN', 'Suns': 'PHX', 'Heat': 'MIA', 'Mavericks': 'DAL',
                'Clippers': 'LAC', '76ers': 'PHI', 'Cavaliers': 'CLE', 'Knicks': 'NYK',
                'Hawks': 'ATL', 'Thunder': 'OKC', 'Timberwolves': 'MIN', 'Kings': 'SAC',
                'Pelicans': 'NOP', 'Grizzlies': 'MEM', 'Raptors': 'TOR', 'Nets': 'BKN',
                'Bulls': 'CHI', 'Pistons': 'DET', 'Pacers': 'IND', 'Hornets': 'CHA',
                'Magic': 'ORL', 'Wizards': 'WAS', 'Trail Blazers': 'POR', 'Jazz': 'UTA',
                'Rockets': 'HOU', 'Spurs': 'SAS'
            }
            
            # Normalize team name
            team_lower = team_name.lower()
            for db_name, abbrev in abbrev_map.items():
                if db_name.lower() in team_lower or abbrev.lower() in team_lower:
                    # Get team ID from API
                    data = self._make_request('teams', {'search': abbrev})
                    if data and 'data' and len(data['data']) > 0:
                        return data['data'][0]['id']
            
            return None
        except Exception as e:
            logger.error(f"Error getting team ID: {e}")
            return None
    
    def _get_player_id(self, player_name: str) -> Optional[int]:
        """Get player ID from player name"""
        try:
            # Try to search for player
            params = {'search': player_name}
            data = self._make_request('players', params)
            
            if data and 'data' and len(data['data']) > 0:
                # Find best match
                name_parts = player_name.lower().split()
                for player in data['data']:
                    full_name = f"{player.get('first_name', '')} {player.get('last_name', '')}".lower()
                    if all(part in full_name for part in name_parts):
                        return player['id']
                
                # Return first match if no exact match
                return data['data'][0]['id']
            
            return None
        except Exception as e:
            logger.error(f"Error getting player ID: {e}")
            return None
    
    def _get_current_season(self) -> int:
        """Get current NBA season year"""
        today = date.today()
        # NBA season typically starts in October
        # For 2024-2025 season, use 2024 as the season identifier
        # Current date: December 2025, so we're in 2024-2025 season (use 2024)
        # Try 2024 first (most likely), then 2023 as fallback
        if today.year == 2025 and today.month >= 12:
            # December 2025 - likely still in 2024-2025 season
            return 2024
        elif today.month >= 10:
            # After October, season has started - use current year
            return today.year
        else:
            # Before October, we're in the previous season year
            return today.year - 1
    
    def _calculate_standings_from_games(self) -> List[Dict]:
        """Calculate standings from game results (fallback method)"""
        try:
            # Get all games from current season
            season = self._get_current_season()
            start_date = date(season, 10, 1)  # Season starts October 1
            end_date = date.today()
            
            params = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'seasons[]': season,
                'per_page': 100
            }
            
            standings = {}
            page = 0
            max_pages = 10  # Limit pages
            
            while page < max_pages:
                params['page'] = page
                data = self._make_request('games', params)
                
                if not data or 'data' not in data or len(data['data']) == 0:
                    break
                
                for game in data['data']:
                    if game.get('status') == 'Final':
                        visitor = game['visitor_team']['abbreviation']
                        home = game['home_team']['abbreviation']
                        visitor_score = game['visitor_team_score']
                        home_score = game['home_team_score']
                        
                        # Initialize if not exists
                        if visitor not in standings:
                            standings[visitor] = {'wins': 0, 'losses': 0, 'team': visitor}
                        if home not in standings:
                            standings[home] = {'wins': 0, 'losses': 0, 'team': home}
                        
                        # Update wins/losses
                        if visitor_score > home_score:
                            standings[visitor]['wins'] += 1
                            standings[home]['losses'] += 1
                        else:
                            standings[home]['wins'] += 1
                            standings[visitor]['losses'] += 1
                
                # Check if more pages
                if not data.get('next_cursor'):
                    break
                
                page += 1
            
            # Convert to list and calculate win percentage
            result = []
            for team, record in standings.items():
                total = record['wins'] + record['losses']
                win_pct = record['wins'] / total if total > 0 else 0
                result.append({
                    'team_name': team,
                    'wins': record['wins'],
                    'losses': record['losses'],
                    'win_percentage': win_pct,
                    'games_played': total
                })
            
            # Sort by win percentage
            result.sort(key=lambda x: x['win_percentage'], reverse=True)
            return result
            
        except Exception as e:
            logger.error(f"Error calculating standings: {e}")
            return []

