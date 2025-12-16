"""
Fetcher Agent - Calls multiple APIs to get player stats
Tries ESPN, Ball Don't Lie, and other sources
Returns raw JSON + HTTP metadata (status, headers, timestamps)
"""
import logging
import requests
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from typing import TYPE_CHECKING
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from services.balldontlie_api import BallDontLieAPI
except ImportError:
    BallDontLieAPI = None

try:
    from services.direct_espn_fetcher import DirectESPNFetcher
except ImportError:
    DirectESPNFetcher = None

if TYPE_CHECKING:
    from agents.resolver_agent import ResolverAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FetcherAgent:
    """Fetches real-time player stats from multiple API sources"""
    
    BASE_URL = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        # Initialize alternative API (but it may not work)
        if BallDontLieAPI:
            try:
                self.balldontlie_api = BallDontLieAPI()
            except:
                self.balldontlie_api = None
        else:
            self.balldontlie_api = None
        
        # Initialize direct ESPN fetcher (simpler, more reliable)
        if DirectESPNFetcher:
            try:
                self.direct_fetcher = DirectESPNFetcher()
                logger.info("✓ Direct ESPN Fetcher initialized")
            except Exception as e:
                logger.warning(f"Could not initialize Direct ESPN Fetcher: {e}")
                self.direct_fetcher = None
        else:
            self.direct_fetcher = None
    
    def fetch_player_last_game(self, player_info: Dict) -> Dict:
        """
        Fetch player's last game stats from ESPN using playerId or name search
        Returns: {'success': bool, 'data': dict, 'metadata': dict, 'error': str}
        """
        canonical_name = player_info.get('canonical_name', '')
        search_terms = player_info.get('search_terms', [])
        espn_player_id = player_info.get('espn_player_id')  # Get playerId from resolver
        
        logger.info(f"Fetching last game for: {canonical_name}" + (f" (ESPN ID: {espn_player_id})" if espn_player_id else ""))
        
        # NEW APPROACH: Try direct fetcher first (simpler, more reliable)
        if self.direct_fetcher:
            logger.info(f"🔄 Trying Direct ESPN Fetcher for {canonical_name}")
            try:
                direct_stats = self.direct_fetcher.get_player_recent_game_stats(canonical_name, days_back=10)
                if direct_stats:
                    logger.info(f"✓ Got stats from Direct ESPN Fetcher")
                    return {
                        'success': True,
                        'data': direct_stats,
                        'metadata': {
                            'source': 'Direct ESPN API',
                            'fetched_at': datetime.utcnow().isoformat() + 'Z',
                            'cache': 'miss'
                        },
                        'error': None
                    }
            except Exception as direct_error:
                logger.debug(f"Direct fetcher failed: {direct_error}, trying standard approach")
        
        # Fallback to standard approach
        # If we have playerId, we could use it, but ESPN boxscore API still requires searching through games
        # So we'll still search through recent games, but playerId helps verify matches
        
        # Get recent games - check last 14 days to increase chances of finding games
        end_date = date.today()
        
        try:
            # Check last 14 days to ensure we find player's most recent game
            logger.info(f"Searching last 14 days of games for {canonical_name}")
            for days_back in range(14):
                check_date = end_date - timedelta(days=days_back)
                date_str = check_date.strftime('%Y%m%d')
                
                url = f"{self.BASE_URL}/scoreboard"
                params = {'dates': date_str}
                
                try:
                    response = self.session.get(url, params=params, timeout=5)  # Reduced timeout
                except Exception as e:
                    logger.debug(f"Error fetching scoreboard for {date_str}: {e}")
                    continue
                
                if response.status_code != 200:
                    continue
                
                data = response.json()
                events = data.get('events', [])
                
                # Process each game for this date - check all games
                logger.debug(f"Found {len(events)} games on {check_date.strftime('%Y-%m-%d')}")
                for event in events:  # Check all games (no limit to find player)
                    event_id = event.get('id', '')
                    if not event_id:
                        continue
                    
                    # Get boxscore for this event
                    summary_url = f"{self.BASE_URL}/summary"
                    summary_params = {'event': event_id}
                    
                    try:
                        summary_response = self.session.get(summary_url, params=summary_params, timeout=5)  # Reduced timeout
                    except Exception as e:
                        logger.debug(f"Error fetching boxscore for event {event_id}: {e}")
                        continue
                    
                    if summary_response.status_code != 200:
                        continue
                    
                    summary_data = summary_response.json()
                    
                    # Search for player in boxscore
                    # If we have playerId, we can verify matches more accurately
                    espn_player_id = player_info.get('espn_player_id')
                    player_stats = self._extract_player_from_boxscore(
                        summary_data, 
                        canonical_name, 
                        search_terms,
                        event,
                        espn_player_id  # Pass playerId for verification
                    )
                    
                    if player_stats:
                        # Found player stats! Log what we got
                        logger.info(f"✓ Successfully fetched real-time stats for {canonical_name} from ESPN")
                        logger.debug(f"Stats data: {player_stats}")
                        
                        # Verify data is being passed correctly
                        if not isinstance(player_stats, dict):
                            logger.error(f"Player stats is not a dict: {type(player_stats)}")
                            continue
                        
                        metadata = {
                            'source': 'ESPN API',
                            'fetched_at': datetime.utcnow().isoformat() + 'Z',
                            'game_date': player_stats.get('match_date', ''),
                            'http_status': summary_response.status_code,
                            'cache': 'miss',
                            'event_id': event_id
                        }
                        
                        return {
                            'success': True,
                            'data': player_stats,  # Ensure this is a dict
                            'metadata': metadata,
                            'error': None
                        }
            
            # No stats found in ESPN - try Ball Don't Lie API as alternative
            logger.warning(f"❌ No stats found for {canonical_name} in last 14 days from ESPN")
            logger.info(f"   Search terms used: {search_terms}")
            logger.info(f"   ESPN playerId: {player_info.get('espn_player_id', 'Not found')}")
            
            # Try Ball Don't Lie API as alternative
            if self.balldontlie_api:
                logger.info(f"🔄 Trying Ball Don't Lie API for {canonical_name}")
                try:
                    balldontlie_stats = self.balldontlie_api.get_player_recent_stats(canonical_name, limit=1)
                    if balldontlie_stats and len(balldontlie_stats) > 0:
                        logger.info(f"✓ Got stats from Ball Don't Lie API")
                        stat_data = balldontlie_stats[0]
                        return {
                            'success': True,
                            'data': stat_data,
                            'metadata': {
                                'source': 'Ball Don\'t Lie API',
                                'fetched_at': datetime.utcnow().isoformat() + 'Z',
                                'cache': 'miss'
                            },
                            'error': None
                        }
                except Exception as bdl_error:
                    logger.warning(f"Ball Don't Lie API also failed: {bdl_error}")
            
            return {
                'success': False,
                'data': None,
                'metadata': {
                    'source': 'ESPN API + Ball Don\'t Lie',
                    'fetched_at': datetime.utcnow().isoformat() + 'Z',
                    'cache': 'miss',
                    'searched_days': 14,
                    'player_name': canonical_name,
                    'espn_player_id': player_info.get('espn_player_id')
                },
                'error': f'Player stats not found for {canonical_name} in recent games. The player may not have played recently, or the game data may not be available yet.'
            }
            
        except Exception as e:
            logger.error(f"Error fetching player stats: {e}", exc_info=True)
            return {
                'success': False,
                'data': None,
                'metadata': {
                    'source': 'ESPN API',
                    'fetched_at': datetime.utcnow().isoformat() + 'Z',
                    'error_type': type(e).__name__
                },
                'error': str(e)
            }
    
    def fetch_player_stats_vs_team(self, player_info: Dict, opponent_team: str) -> Dict:
        """Fetch player stats for a specific game vs opponent team"""
        canonical_name = player_info.get('canonical_name', '')
        search_terms = player_info.get('search_terms', [])
        
        logger.info(f"Fetching stats for {canonical_name} vs {opponent_team}")
        
        # Team abbreviation mapping
        team_map = {
            'spurs': 'SA', 'lakers': 'LAL', 'warriors': 'GS', 'celtics': 'BOS',
            'bucks': 'MIL', 'nuggets': 'DEN', 'suns': 'PHX', 'heat': 'MIA',
            'mavericks': 'DAL', 'clippers': 'LAC', '76ers': 'PHI', 'cavaliers': 'CLE',
            'knicks': 'NYK', 'hawks': 'ATL', 'thunder': 'OKC', 'timberwolves': 'MIN',
            'kings': 'SAC', 'pelicans': 'NO', 'grizzlies': 'MEM', 'raptors': 'TOR'
        }
        opponent_abbrev = team_map.get(opponent_team.lower(), opponent_team[:3].upper())
        
            # Check last 14 days for games
        end_date = date.today()
        
        try:
            for days_back in range(14):
                check_date = end_date - timedelta(days=days_back)
                date_str = check_date.strftime('%Y%m%d')
                
                url = f"{self.BASE_URL}/scoreboard"
                params = {'dates': date_str}
                
                try:
                    response = self.session.get(url, params=params, timeout=5)  # Reduced timeout
                except Exception as e:
                    logger.debug(f"Error fetching scoreboard for {date_str}: {e}")
                    continue
                
                if response.status_code != 200:
                    continue
                
                data = response.json()
                events = data.get('events', [])
                
                for event in events[:10]:  # Limit to first 10 games per day
                    competitions = event.get('competitions', [])
                    if not competitions:
                        continue
                    
                    comp = competitions[0]
                    competitors = comp.get('competitors', [])
                    if len(competitors) < 2:
                        continue
                    
                    away = competitors[0]
                    home = competitors[1]
                    away_abbrev = away.get('team', {}).get('abbreviation', '').upper()
                    home_abbrev = home.get('team', {}).get('abbreviation', '').upper()
                    
                    # Check if opponent team is in this game
                    if opponent_abbrev.upper() not in [away_abbrev, home_abbrev]:
                        continue
                    
                    # Get boxscore
                    event_id = event.get('id', '')
                    if not event_id:
                        continue
                    
                    summary_url = f"{self.BASE_URL}/summary"
                    summary_params = {'event': event_id}
                    
                    try:
                        summary_response = self.session.get(summary_url, params=summary_params, timeout=5)
                    except Exception as e:
                        logger.debug(f"Error fetching boxscore for event {event_id}: {e}")
                        continue
                    if summary_response.status_code != 200:
                        continue
                    
                    summary_data = summary_response.json()
                    
                    # Extract player stats
                    espn_player_id = player_info.get('espn_player_id')
                    player_stats = self._extract_player_from_boxscore(
                        summary_data,
                        canonical_name,
                        search_terms,
                        event,
                        espn_player_id  # Pass playerId for verification
                    )
                    
                    if player_stats:
                        # Verify opponent team matches
                        team1 = player_stats.get('team1_name', '').upper()
                        team2 = player_stats.get('team2_name', '').upper()
                        
                        if opponent_abbrev.upper() in [team1, team2]:
                            metadata = {
                                'source': 'ESPN API',
                                'fetched_at': datetime.utcnow().isoformat() + 'Z',
                                'game_date': player_stats.get('match_date', ''),
                                'http_status': summary_response.status_code,
                                'cache': 'miss',
                                'event_id': event_id
                            }
                            
                            return {
                                'success': True,
                                'data': player_stats,
                                'metadata': metadata,
                                'error': None
                            }
            
            # Try Ball Don't Lie API as fallback
            if self.balldontlie_api:
                logger.info(f"🔄 ESPN failed for vs {opponent_team}, trying Ball Don't Lie API")
                try:
                    balldontlie_stats = self.balldontlie_api.get_player_recent_stats(canonical_name, limit=10)
                    if balldontlie_stats:
                        # Filter by opponent team
                        for stat in balldontlie_stats:
                            team1 = stat.get('team1_name', '').upper()
                            team2 = stat.get('team2_name', '').upper()
                            if opponent_abbrev.upper() in [team1, team2]:
                                logger.info(f"✓ Found vs {opponent_team} in Ball Don't Lie API")
                                return {
                                    'success': True,
                                    'data': stat,
                                    'metadata': {
                                        'source': 'Ball Don\'t Lie API',
                                        'fetched_at': datetime.utcnow().isoformat() + 'Z'
                                    },
                                    'error': None
                                }
                except Exception as bdl_error:
                    logger.warning(f"Ball Don't Lie API also failed: {bdl_error}")
            
            return {
                'success': False,
                'data': None,
                'metadata': {
                    'source': 'ESPN API + Ball Don\'t Lie',
                    'fetched_at': datetime.utcnow().isoformat() + 'Z'
                },
                'error': f'No game found for {canonical_name} vs {opponent_team}'
            }
            
        except Exception as e:
            logger.error(f"Error fetching player stats vs team: {e}", exc_info=True)
            return {
                'success': False,
                'data': None,
                'metadata': {
                    'source': 'ESPN API',
                    'fetched_at': datetime.utcnow().isoformat() + 'Z',
                    'error_type': type(e).__name__
                },
                'error': str(e)
            }
    
    def _extract_player_from_boxscore(self, summary_data: Dict, canonical_name: str, 
                                     search_terms: List[str], event: Dict, espn_player_id: Optional[str] = None) -> Optional[Dict]:
        """Extract player stats from ESPN boxscore data"""
        try:
            # Get game info
            competitions = event.get('competitions', [])
            if not competitions:
                return None
            
            comp = competitions[0]
            competitors = comp.get('competitors', [])
            if len(competitors) < 2:
                return None
            
            away = competitors[0]
            home = competitors[1]
            away_abbrev = away.get('team', {}).get('abbreviation', '')
            home_abbrev = home.get('team', {}).get('abbreviation', '')
            game_date = event.get('date', '')[:10] if event.get('date') else ''
            
            # Search for player in boxscore - ESPN has multiple possible structures
            boxscore = summary_data.get('boxscore', {})
            competitions_box = boxscore.get('competitions', [])
            
            # Alternative: try getting from boxscore.statistics or boxscore.leaders
            if not competitions_box:
                # Try alternative structure - check if boxscore has direct stats
                statistics = boxscore.get('statistics', [])
                if statistics:
                    # This might be a different structure, try to extract from it
                    for stat_group in statistics:
                        athletes = stat_group.get('athletes', [])
                        for athlete_stat in athletes:
                            athlete_info = athlete_stat.get('athlete', {})
                            if not athlete_info:
                                continue
                            
                            full_name = athlete_info.get('fullName', '').lower()
                            display_name = athlete_info.get('displayName', '').lower()
                            
                            # Check if this player matches - improved matching
                            name_parts = canonical_name.lower().split()
                            matches = False
                            
                            # Try exact match first
                            if canonical_name.lower() in full_name or canonical_name.lower() in display_name:
                                matches = True
                            # Try all name parts match
                            elif len(name_parts) >= 2:
                                if all(part in full_name or part in display_name for part in name_parts):
                                    matches = True
                            # Try first and last name match
                            elif len(name_parts) >= 2:
                                first = name_parts[0]
                                last = name_parts[-1]
                                if first in full_name and last in full_name:
                                    matches = True
                            
                            if matches:
                                            # Found player - extract stats from statGroup
                                            stats = athlete_stat.get('stats', [])
                                            stat_dict = {}
                                            for stat in stats:
                                                stat_name = stat.get('name', '').lower()
                                                stat_value = stat.get('value', stat.get('displayValue', 0))
                                                try:
                                                    stat_dict[stat_name] = float(stat_value) if stat_value else 0
                                                except:
                                                    stat_dict[stat_name] = 0
                                            
                                            # Extract stats - handle None
                                            points = stat_dict.get('points') or stat_dict.get('pts') or 0
                                            rebounds = stat_dict.get('rebounds') or stat_dict.get('reb') or stat_dict.get('totalrebounds') or 0
                                            assists = stat_dict.get('assists') or stat_dict.get('ast') or 0
                                            steals = stat_dict.get('steals') or stat_dict.get('stl') or 0
                                            blocks = stat_dict.get('blocks') or stat_dict.get('blk') or 0
                                            
                                            # Convert to int, handling None
                                            try:
                                                points = int(float(points)) if points else 0
                                                rebounds = int(float(rebounds)) if rebounds else 0
                                                assists = int(float(assists)) if assists else 0
                                                steals = int(float(steals)) if steals else 0
                                                blocks = int(float(blocks)) if blocks else 0
                                            except (ValueError, TypeError):
                                                points = 0
                                                rebounds = 0
                                                assists = 0
                                                steals = 0
                                                blocks = 0
                                            
                                            # ACCEPT PARTIAL STATS
                                            if points == 0 and rebounds == 0 and assists == 0:
                                                logger.debug(f"Player {canonical_name} found but all stats are 0, skipping")
                                                continue
                                            
                                            # Determine team from statGroup
                                            team_info = stat_group.get('team', {})
                                            team_abbrev = team_info.get('abbreviation', '')
                                            
                                            return {
                                                'player_name': athlete_info.get('fullName', canonical_name),
                                                'points': points,
                                                'rebounds': rebounds,
                                                'assists': assists,
                                                'steals': steals,
                                                'blocks': blocks,
                                                'match_date': game_date,
                                                'team1_name': away_abbrev,
                                                'team2_name': home_abbrev,
                                                'player_team': team_abbrev if team_abbrev else away_abbrev
                                            }
            
            if not competitions_box:
                return None
            
            comp_box = competitions_box[0]
            competitors_box = comp_box.get('competitors', [])
            
            # Search through all competitors' rosters
            for competitor in competitors_box:
                roster = competitor.get('roster', {})
                if not roster:
                    continue
                
                entries = roster.get('entries', [])
                if not entries:
                    # Try alternative: check if roster has statistics directly
                    statistics = roster.get('statistics', [])
                    if statistics:
                        entries = statistics  # Use statistics as entries
                
                for entry in entries:
                    athlete = entry.get('athlete', {})
                    if not athlete:
                        continue
                    
                    full_name = athlete.get('fullName', '').lower()
                    display_name = athlete.get('displayName', '').lower()
                    
                    # Check if this player matches
                    matches = False
                    
                    # First check: if we have playerId, verify by ID
                    if espn_player_id:
                        athlete_id = athlete.get('id', '')
                        if str(athlete_id) == str(espn_player_id):
                            matches = True
                            logger.debug(f"Matched player by ESPN ID: {espn_player_id}")
                    
                    # If no ID match, try name matching
                    if not matches:
                        for search_term in search_terms:
                            if search_term in full_name or search_term in display_name:
                                # Verify it's a good match (not just partial)
                                name_parts = canonical_name.lower().split()
                                if len(name_parts) >= 2:
                                    if name_parts[0] in full_name and name_parts[1] in full_name:
                                        matches = True
                                        break
                                elif len(name_parts) == 1:
                                    if name_parts[0] in full_name:
                                        matches = True
                                        break
                    
                    if matches:
                        # Extract stats
                        stats = entry.get('stats', [])
                        stat_dict = {}
                        for stat in stats:
                            stat_name = stat.get('name', '').lower()
                            stat_value = stat.get('value', stat.get('displayValue', 0))
                            try:
                                stat_dict[stat_name] = float(stat_value) if stat_value else 0
                            except:
                                stat_dict[stat_name] = 0
                        
                        # Extract stats - handle None and convert to int, default to 0
                        points = stat_dict.get('points') or stat_dict.get('pts') or 0
                        rebounds = stat_dict.get('rebounds') or stat_dict.get('reb') or stat_dict.get('totalrebounds') or 0
                        assists = stat_dict.get('assists') or stat_dict.get('ast') or 0
                        steals = stat_dict.get('steals') or stat_dict.get('stl') or 0
                        blocks = stat_dict.get('blocks') or stat_dict.get('blk') or 0
                        
                        # Convert to int, handling None
                        try:
                            points = int(float(points)) if points else 0
                            rebounds = int(float(rebounds)) if rebounds else 0
                            assists = int(float(assists)) if assists else 0
                            steals = int(float(steals)) if steals else 0
                            blocks = int(float(blocks)) if blocks else 0
                        except (ValueError, TypeError):
                            points = 0
                            rebounds = 0
                            assists = 0
                            steals = 0
                            blocks = 0
                        
                        # ACCEPT PARTIAL STATS - return even if some stats are 0
                        # Only reject if ALL stats are 0 (player didn't play)
                        if points == 0 and rebounds == 0 and assists == 0:
                            logger.debug(f"Player {canonical_name} found but all stats are 0, skipping")
                            continue  # Skip this entry, try next
                        
                        # Determine player's team
                        team_id = competitor.get('id', '')
                        player_team = away_abbrev if str(away.get('id', '')) == str(team_id) else home_abbrev
                        
                        return {
                            'player_name': athlete.get('fullName', canonical_name),
                            'points': points,
                            'rebounds': rebounds,
                            'assists': assists,
                            'steals': steals,
                            'blocks': blocks,
                            'match_date': game_date,
                            'team1_name': away_abbrev,
                            'team2_name': home_abbrev,
                            'player_team': player_team
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting player from boxscore: {e}", exc_info=True)
            return None

