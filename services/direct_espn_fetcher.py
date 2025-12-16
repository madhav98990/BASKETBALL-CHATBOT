"""
Direct ESPN Fetcher - Simplified, more reliable approach
Queries ESPN API directly with improved error handling and parsing
"""
import requests
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DirectESPNFetcher:
    """Simplified direct ESPN API fetcher"""
    
    BASE_URL = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        })
    
    def get_player_recent_game_stats(self, player_name: str, days_back: int = 7) -> Optional[Dict]:
        """
        Get player's most recent game stats directly from ESPN
        Simplified approach - search through recent scoreboards
        """
        try:
            logger.info(f"Direct fetch: Searching for {player_name} in last {days_back} days")
            
            # Normalize player name for matching
            name_parts = player_name.strip().lower().split()
            if not name_parts:
                return None
            
            first_name = name_parts[0]
            last_name = name_parts[-1] if len(name_parts) > 1 else ""
            full_name_lower = " ".join(name_parts)
            
            # Search through recent days
            today = date.today()
            for i in range(days_back):
                check_date = today - timedelta(days=i)
                date_str = check_date.strftime('%Y%m%d')
                
                logger.debug(f"Checking games on {check_date}")
                
                # Get scoreboard for this date
                url = f"{self.BASE_URL}/scoreboard"
                try:
                    response = self.session.get(url, params={'dates': date_str}, timeout=8)
                    if response.status_code != 200:
                        continue
                    
                    scoreboard_data = response.json()
                    events = scoreboard_data.get('events', [])
                    
                    # Check each game on this date
                    for event in events:
                        event_id = event.get('id')
                        if not event_id:
                            continue
                        
                        # Get boxscore for this event
                        stats = self._get_boxscore_stats(event_id, full_name_lower, first_name, last_name)
                        if stats:
                            logger.info(f"✓ Found stats for {player_name} from {check_date}")
                            return stats
                
                except Exception as e:
                    logger.debug(f"Error checking {date_str}: {e}")
                    continue
            
            logger.warning(f"Could not find stats for {player_name} in last {days_back} days")
            return None
            
        except Exception as e:
            logger.error(f"Error in direct fetch: {e}", exc_info=True)
            return None
    
    def _get_boxscore_stats(self, event_id: str, full_name: str, first_name: str, last_name: str) -> Optional[Dict]:
        """Extract player stats from boxscore"""
        try:
            url = f"{self.BASE_URL}/summary"
            response = self.session.get(url, params={'event': event_id}, timeout=8)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            boxscore = data.get('boxscore', {})
            
            # NEW: Handle ESPN's boxscore.players structure
            # Structure: boxscore.players = [
            #   { team: {...}, statistics: [{ names: [stat_names], athletes: [...] }] },
            #   { team: {...}, statistics: [...] }
            # ]
            
            players_data = boxscore.get('players', [])
            
            if not players_data or len(players_data) < 2:
                # Fallback to old structure if new one not available
                return None
            
            # Iterate through teams (away, home)
            for team_idx, team_stats in enumerate(players_data):
                team_info = team_stats.get('team', {})
                team_abbrev = team_info.get('abbreviation', '')
                
                statistics = team_stats.get('statistics', [])
                if not statistics:
                    continue
                
                stat_group = statistics[0]
                names = stat_group.get('names', [])  # ['MIN', 'PTS', 'FG', '3PT', 'FT', 'REB', 'AST', 'TO', 'STL', 'BLK', 'OREB', 'DREB', 'PF', '+/-']
                athletes = stat_group.get('athletes', [])
                
                # Search for player in this team
                for athlete_entry in athletes:
                    athlete = athlete_entry.get('athlete', {})
                    if not athlete:
                        continue
                    
                    display_name = athlete.get('displayName', '').lower()
                    
                    # Check name match
                    matches = False
                    if full_name in display_name or display_name in full_name:
                        matches = True
                    elif first_name and last_name:
                        if first_name in display_name and last_name in display_name:
                            matches = True
                    
                    if matches:
                        # Extract stats
                        stat_values = athlete_entry.get('stats', [])
                        
                        # Map stat names to values
                        stat_dict = {}
                        for stat_name, stat_value in zip(names, stat_values):
                            stat_name_lower = stat_name.lower()
                            stat_dict[stat_name_lower] = stat_value
                        
                        # Parse stat values (could be "4-17" format)
                        def parse_stat(value):
                            if isinstance(value, (int, float)):
                                return int(value)
                            if isinstance(value, str):
                                if '-' in value and '/' not in value:
                                    try:
                                        return int(value.split('-')[0])
                                    except:
                                        return 0
                                try:
                                    return int(float(value))
                                except:
                                    return 0
                            return 0
                        
                        points = parse_stat(stat_dict.get('pts', 0))
                        rebounds = parse_stat(stat_dict.get('reb', 0))
                        assists = parse_stat(stat_dict.get('ast', 0))
                        steals = parse_stat(stat_dict.get('stl', 0))
                        blocks = parse_stat(stat_dict.get('blk', 0))
                        
                        # Accept if we have at least points or meaningful stats
                        if points >= 0 or rebounds > 0 or assists > 0:
                            # Get game date from main competition data
                            date_str = ''
                            article = data.get('article', {})
                            if article and 'date' in article:
                                date_str = article['date'][:10]
                            
                            return {
                                'player_name': athlete.get('displayName', full_name.title()),
                                'points': points,
                                'rebounds': rebounds,
                                'assists': assists,
                                'steals': steals,
                                'blocks': blocks,
                                'match_date': date_str,
                                'team1_name': players_data[0].get('team', {}).get('abbreviation', ''),
                                'team2_name': players_data[1].get('team', {}).get('abbreviation', ''),
                                'player_team': team_abbrev
                            }
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting boxscore stats: {e}")
            return None
    
    def get_team_game_leader(self, team_name: str, stat_type: str = 'points', days_back: int = 30) -> Optional[Dict]:
        """Get the leader in a stat category for a team's most recent game"""
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
            
            today = date.today()
            for i in range(days_back):
                check_date = today - timedelta(days=i)
                date_str = check_date.strftime('%Y%m%d')
                
                url = f"{self.BASE_URL}/scoreboard"
                try:
                    response = self.session.get(url, params={'dates': date_str}, timeout=8)
                    if response.status_code != 200:
                        continue
                    
                    scoreboard_data = response.json()
                    events = scoreboard_data.get('events', [])
                    
                    for event in events:
                        # Check if team is in this game
                        competitions = event.get('competitions', [])
                        if not competitions:
                            continue
                        
                        comp = competitions[0]
                        competitors = comp.get('competitors', [])
                        if len(competitors) < 2:
                            continue
                        
                        away_abbrev = competitors[0].get('team', {}).get('abbreviation', '')
                        home_abbrev = competitors[1].get('team', {}).get('abbreviation', '')
                        
                        if team_abbrev.upper() not in [away_abbrev.upper(), home_abbrev.upper()]:
                            continue
                        
                        # This is the team's game - get boxscore and find leader
                        event_id = event.get('id')
                        if event_id:
                            # Get game date and matchup from event
                            game_date = event.get('date', '')[:10] if event.get('date') else ''
                            team1_name = competitors[0].get('team', {}).get('displayName', '')
                            team2_name = competitors[1].get('team', {}).get('displayName', '')
                            matchup = f"{team1_name} vs {team2_name}" if team1_name and team2_name else ''
                            
                            leader = self._get_game_leader(event_id, team_abbrev, stat_type, game_date, matchup)
                            if leader:
                                return leader
                
                except Exception as e:
                    logger.debug(f"Error checking {date_str}: {e}")
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting team game leader: {e}")
            return None
    
    def _get_game_leader(self, event_id: str, team_abbrev: str, stat_type: str, game_date: str = '', matchup: str = '') -> Optional[Dict]:
        """Get the leader in a stat category for a specific game"""
        try:
            url = f"{self.BASE_URL}/summary"
            response = self.session.get(url, params={'event': event_id}, timeout=8)
            
            if response.status_code != 200:
                logger.warning(f"ESPN API returned status {response.status_code} for event {event_id}")
                return None
            
            data = response.json()
            
            # Try multiple boxscore structures
            boxscore = data.get('boxscore', {})
            if not boxscore:
                boxscore = data.get('gamepackageJSON', {}).get('boxscore', {})
            
            # Get game date from competitions (use passed values if available, otherwise extract)
            if not game_date or not matchup:
                competitions = data.get('boxscore', {}).get('competitions', [])
                if not competitions:
                    competitions = data.get('competitions', [])
                
                if competitions and len(competitions) > 0:
                    comp = competitions[0]
                    if not game_date:
                        game_date = comp.get('date', '')[:10] if comp.get('date') else ''
                    if not matchup:
                        competitors_list = comp.get('competitors', [])
                        if len(competitors_list) >= 2:
                            team1 = competitors_list[0].get('team', {}).get('displayName', '')
                            team2 = competitors_list[1].get('team', {}).get('displayName', '')
                            matchup = f"{team1} vs {team2}"
            
            # Try statistics from boxscore
            statistics = boxscore.get('statistics', [])
            
            # If no statistics in boxscore, try players structure
            if not statistics:
                players = boxscore.get('players', [])
                if players:
                    # Process players structure
                    leader_player = None
                    leader_value = -1
                    
                    for team_stats in players:
                        team_info = team_stats.get('team', {})
                        if team_info.get('abbreviation', '').upper() != team_abbrev.upper():
                            continue
                        
                        stat_groups = team_stats.get('statistics', [])
                        if not stat_groups:
                            continue
                        
                        # Get stat names and athletes
                        stat_group = stat_groups[0]
                        names = stat_group.get('names', [])
                        athletes = stat_group.get('athletes', [])
                        
                        # Find points index
                        stat_index = None
                        stat_key = stat_type.lower()
                        if stat_key == 'points':
                            for idx, name in enumerate(names):
                                if name.upper() in ['PTS', 'POINTS']:
                                    stat_index = idx
                                    break
                        elif stat_key == 'assists':
                            for idx, name in enumerate(names):
                                if name.upper() in ['AST', 'ASSISTS']:
                                    stat_index = idx
                                    break
                        elif stat_key == 'rebounds':
                            for idx, name in enumerate(names):
                                if name.upper() in ['REB', 'REBOUNDS']:
                                    stat_index = idx
                                    break
                        
                        if stat_index is None:
                            continue
                        
                        # Find leader
                        for athlete_entry in athletes:
                            athlete = athlete_entry.get('athlete', {})
                            stat_values = athlete_entry.get('stats', [])
                            
                            if not stat_values or len(stat_values) <= stat_index:
                                continue
                            
                            try:
                                value = stat_values[stat_index]
                                if isinstance(value, str):
                                    # Handle string values like "25" or "25.0"
                                    value_float = float(value.split('-')[0].split('/')[0]) if value else 0
                                else:
                                    value_float = float(value) if value else 0
                                
                                if value_float > leader_value:
                                    leader_value = value_float
                                    player_name = athlete.get('displayName', '') or athlete.get('fullName', '')
                                    # Get all stats safely
                                    points = 0
                                    rebounds = 0
                                    assists = 0
                                    try:
                                        if 'PTS' in names:
                                            pts_idx = names.index('PTS')
                                            if len(stat_values) > pts_idx:
                                                points = int(float(stat_values[pts_idx]))
                                    except:
                                        pass
                                    try:
                                        if 'REB' in names:
                                            reb_idx = names.index('REB')
                                            if len(stat_values) > reb_idx:
                                                rebounds = int(float(stat_values[reb_idx]))
                                    except:
                                        pass
                                    try:
                                        if 'AST' in names:
                                            ast_idx = names.index('AST')
                                            if len(stat_values) > ast_idx:
                                                assists = int(float(stat_values[ast_idx]))
                                    except:
                                        pass
                                    
                                    leader_player = {
                                        'player_name': player_name,
                                        stat_type: int(value_float),
                                        'points': points,
                                        'rebounds': rebounds,
                                        'assists': assists,
                                        'game_date': game_date,
                                        'match_date': game_date,
                                        'matchup': matchup
                                    }
                            except (ValueError, TypeError, IndexError) as e:
                                logger.debug(f"Error parsing stat value: {e}")
                                continue
                    
                    if leader_player:
                        logger.info(f"✓ Found {stat_type} leader from ESPN (players structure): {leader_player.get('player_name')} with {leader_value} {stat_type}")
                        return leader_player
            
            # Original statistics structure parsing
            stat_key = stat_type.lower()
            leader_player = None
            leader_value = -1
            
            for stat_group in statistics:
                team_info = stat_group.get('team', {})
                if team_info.get('abbreviation', '').upper() != team_abbrev.upper():
                    continue
                
                athletes = stat_group.get('athletes', [])
                for athlete_stat in athletes:
                    athlete = athlete_stat.get('athlete', {})
                    stats = athlete_stat.get('stats', [])
                    
                    for stat in stats:
                        name = stat.get('name', '').lower()
                        if name == stat_key or name == stat_key[:3]:
                            value = stat.get('value') or stat.get('displayValue') or 0
                            try:
                                value_float = float(value) if value else 0
                                if value_float > leader_value:
                                    leader_value = value_float
                                    player_name = athlete.get('fullName', '') or athlete.get('displayName', '')
                                    leader_player = {
                                        'player_name': player_name,
                                        stat_type: int(value_float),
                                        'match_date': game_date,
                                        'matchup': matchup
                                    }
                            except:
                                pass
            
            if leader_player:
                logger.info(f"✓ Found {stat_type} leader from ESPN (statistics structure): {leader_player.get('player_name')} with {leader_value} {stat_type}")
            
            return leader_player
            
        except Exception as e:
            logger.error(f"Error getting game leader from ESPN: {e}", exc_info=True)
            return None
    
    def get_team_most_recent_game_result(self, team_name: str, days_back: int = 30) -> Optional[Dict]:
        """
        Get a team's most recent game result following exact logic:
        1. Fetch completed games only (status = Final)
        2. Sort games by game_date descending
        3. Select the latest game
        4. Compare scores to determine win/loss
        5. Return result with final score
        """
        try:
            # Map team name to abbreviation - handle full names and common variations
            team_map = {
                'warriors': 'GS', 'golden state': 'GS', 'gsw': 'GS', 'golden state warriors': 'GS',
                'lakers': 'LAL', 'los angeles lakers': 'LAL',
                'celtics': 'BOS', 'boston celtics': 'BOS',
                'bucks': 'MIL', 'milwaukee bucks': 'MIL',
                'nuggets': 'DEN', 'denver nuggets': 'DEN',
                'suns': 'PHX', 'phoenix suns': 'PHX',
                'heat': 'MIA', 'miami heat': 'MIA',
                'mavericks': 'DAL', 'dallas mavericks': 'DAL',
                'clippers': 'LAC', 'la clippers': 'LAC', 'los angeles clippers': 'LAC',
                '76ers': 'PHI', 'sixers': 'PHI', 'philadelphia 76ers': 'PHI',
                'cavaliers': 'CLE', 'cleveland cavaliers': 'CLE',
                'knicks': 'NYK', 'new york knicks': 'NYK', 'new york': 'NYK',
                'hawks': 'ATL', 'atlanta hawks': 'ATL',
                'thunder': 'OKC', 'oklahoma city thunder': 'OKC',
                'timberwolves': 'MIN', 'minnesota timberwolves': 'MIN',
                'kings': 'SAC', 'sacramento kings': 'SAC',
                'pelicans': 'NO', 'new orleans pelicans': 'NO',
                'grizzlies': 'MEM', 'memphis grizzlies': 'MEM',
                'raptors': 'TOR', 'toronto raptors': 'TOR',
                'nets': 'BKN', 'brooklyn nets': 'BKN',
                'bulls': 'CHI', 'chicago bulls': 'CHI',
                'pistons': 'DET', 'detroit pistons': 'DET',
                'pacers': 'IND', 'indiana pacers': 'IND',
                'hornets': 'CHA', 'charlotte hornets': 'CHA',
                'magic': 'ORL', 'orlando magic': 'ORL',
                'wizards': 'WSH', 'washington wizards': 'WSH',
                'trail blazers': 'POR', 'portland trail blazers': 'POR', 'blazers': 'POR',
                'jazz': 'UTAH', 'utah jazz': 'UTAH',
                'rockets': 'HOU', 'houston rockets': 'HOU',
                'spurs': 'SAS', 'san antonio spurs': 'SAS'
            }
            team_name_lower = team_name.lower().strip()
            # Try exact match first, then check if any key is contained in the team name
            team_abbrev = team_map.get(team_name_lower)
            if not team_abbrev:
                # Check if any key is contained in the team name
                for key, abbrev in team_map.items():
                    if key in team_name_lower or team_name_lower in key:
                        team_abbrev = abbrev
                        break
            if not team_abbrev:
                # Fallback to first 3 characters
                team_abbrev = team_name[:3].upper()
            
            logger.info(f"Step 1: Fetching {team_name} (abbrev: {team_abbrev}) completed games only (status = Final) from last {days_back} days")
            
            # Step 1: Fetch all completed games
            completed_games = []
            today = date.today()
            
            for i in range(days_back):
                check_date = today - timedelta(days=i)
                date_str = check_date.strftime('%Y%m%d')
                
                url = f"{self.BASE_URL}/scoreboard"
                try:
                    response = self.session.get(url, params={'dates': date_str}, timeout=10)
                    if response.status_code != 200:
                        continue
                    
                    scoreboard_data = response.json()
                    events = scoreboard_data.get('events', [])
                    
                    for event in events:
                        competitions = event.get('competitions', [])
                        if not competitions:
                            continue
                        
                        comp = competitions[0]
                        competitors = comp.get('competitors', [])
                        if len(competitors) < 2:
                            continue
                        
                        away_team = competitors[0].get('team', {})
                        home_team = competitors[1].get('team', {})
                        away_abbrev = away_team.get('abbreviation', '')
                        home_abbrev = home_team.get('abbreviation', '')
                        
                        # Check if this is the team's game - identify by abbreviation, name, or team ID
                        away_team_name = away_team.get('displayName', '').upper()
                        home_team_name = home_team.get('displayName', '').upper()
                        away_team_id = away_team.get('id', '')
                        home_team_id = home_team.get('id', '')
                        
                        # Check if this is the requested team's game (by abbreviation, name, or ID)
                        # Works for ALL teams, not just Knicks
                        team_name_upper = team_name.upper()
                        team_name_parts = [part.upper() for part in team_name.split() if len(part) > 2]  # Get meaningful words
                        
                        is_team_game = (
                            team_abbrev.upper() in [away_abbrev.upper(), home_abbrev.upper()] or
                            team_name_upper in away_team_name or team_name_upper in home_team_name or
                            any(part in away_team_name for part in team_name_parts) or
                            any(part in home_team_name for part in team_name_parts)
                        )
                        
                        if not is_team_game:
                            continue
                        
                        # Step 1: Check if game is completed (status = Final) - IGNORE scheduled, postponed, or in-progress
                        status = comp.get('status', {})
                        status_type = status.get('type', {})
                        status_name = status_type.get('name', '')
                        is_completed = (
                            status_type.get('completed', False) or 
                            status_name == 'STATUS_FINAL'
                        )
                        
                        # Skip if not completed (scheduled, postponed, in-progress, etc.)
                        if not is_completed:
                            logger.debug(f"Skipping incomplete game: status={status_name}")
                            continue
                        
                        # Get scores - try multiple fields
                        away_score = 0
                        home_score = 0
                        
                        # Try different score fields
                        away_competitor = competitors[0]
                        home_competitor = competitors[1]
                        
                        # Try 'score' field first - handle both dict and int formats
                        away_score_raw = away_competitor.get('score', 0)
                        home_score_raw = home_competitor.get('score', 0)
                        
                        if isinstance(away_score_raw, dict):
                            away_score = int(away_score_raw.get('value', 0) or 0)
                        else:
                            away_score = int(away_score_raw or 0)
                        
                        if isinstance(home_score_raw, dict):
                            home_score = int(home_score_raw.get('value', 0) or 0)
                        else:
                            home_score = int(home_score_raw or 0)
                        
                        # If scores are 0, try 'linescore' or 'displayValue'
                        if away_score == 0 and home_score == 0:
                            # Try linescore array
                            away_linescore = away_competitor.get('linescore', [])
                            home_linescore = home_competitor.get('linescore', [])
                            
                            if away_linescore:
                                # Sum up all periods
                                away_score = sum(int(period.get('value', 0) or 0) for period in away_linescore)
                            if home_linescore:
                                home_score = sum(int(period.get('value', 0) or 0) for period in home_linescore)
                            
                            # If still 0, try getting from summary endpoint
                            if away_score == 0 and home_score == 0:
                                event_id = event.get('id')
                                if event_id:
                                    try:
                                        summary_url = f"{self.BASE_URL}/summary"
                                        summary_response = self.session.get(summary_url, params={'event': event_id}, timeout=8)
                                        if summary_response.status_code == 200:
                                            summary_data = summary_response.json()
                                            summary_comp = summary_data.get('competitions', [])
                                            if summary_comp and len(summary_comp) > 0:
                                                summary_competitors = summary_comp[0].get('competitors', [])
                                                if len(summary_competitors) >= 2:
                                                    away_score = int(summary_competitors[0].get('score', 0) or 0)
                                                    home_score = int(summary_competitors[1].get('score', 0) or 0)
                                    except Exception as e:
                                        logger.debug(f"Error getting score from summary: {e}")
                        
                        # Log scores for debugging
                        logger.debug(f"Raw scores - Away ({away_abbrev}): {away_score}, Home ({home_abbrev}): {home_score}")
                        
                        # Determine if team is home - check by abbreviation, name, or ID (works for ALL teams)
                        away_display = away_team.get('displayName', away_abbrev)
                        home_display = home_team.get('displayName', home_abbrev)
                        away_name_upper = away_display.upper()
                        home_name_upper = home_display.upper()
                        team_name_upper = team_name.upper()
                        team_name_parts = [part.upper() for part in team_name.split() if len(part) > 2]
                        
                        # Check if team is home by multiple methods (works for all teams)
                        is_home = (
                            team_abbrev.upper() == home_abbrev.upper() or
                            team_name_upper in home_name_upper or
                            any(part in home_name_upper for part in team_name_parts)
                        )
                        
                        # If not home, check if away
                        if not is_home:
                            is_away = (
                                team_abbrev.upper() == away_abbrev.upper() or
                                team_name_upper in away_name_upper or
                                any(part in away_name_upper for part in team_name_parts)
                            )
                            if not is_away:
                                # Fallback: use abbreviation match
                                is_home = team_abbrev.upper() == home_abbrev.upper()
                        
                        team_score = home_score if is_home else away_score
                        opponent_score = away_score if is_home else home_score
                        did_win = team_score > opponent_score
                        
                        # Additional validation: Double-check team identification by verifying the team name matches
                        # This helps catch cases where we might have misidentified home/away
                        identified_team_name = (home_team.get('displayName', '') if is_home else away_team.get('displayName', '')).upper()
                        team_name_check = team_name.upper()
                        team_abbrev_check = team_abbrev.upper()
                        identified_abbrev = (home_abbrev if is_home else away_abbrev).upper()
                        
                        # If the identified team doesn't match, try swapping
                        if (team_abbrev_check not in identified_abbrev and 
                            team_name_check not in identified_team_name and
                            not any(part in identified_team_name for part in team_name_parts)):
                            # Team identification might be wrong, try the other side
                            logger.warning(f"Team identification mismatch: Looking for {team_name} ({team_abbrev}) but found {identified_team_name} ({identified_abbrev}). Trying swap.")
                            is_home = not is_home
                            team_score = home_score if is_home else away_score
                            opponent_score = away_score if is_home else home_score
                            did_win = team_score > opponent_score
                            identified_team_name = (home_team.get('displayName', '') if is_home else away_team.get('displayName', '')).upper()
                            identified_abbrev = (home_abbrev if is_home else away_abbrev).upper()
                            
                            # Verify the swap worked
                            if (team_abbrev_check not in identified_abbrev and 
                                team_name_check not in identified_team_name and
                                not any(part in identified_team_name for part in team_name_parts)):
                                logger.warning(f"Team identification still wrong after swap. Skipping this game.")
                                continue
                        
                        # Get opponent name - if team is home, opponent is away; if team is away, opponent is home
                        opponent_team = away_team if is_home else home_team
                        opponent_name = opponent_team.get('displayName', '')
                        if not opponent_name:
                            opponent_name = opponent_team.get('abbreviation', '')
                        
                        # Final validation: ensure opponent is not the same as team (works for all teams)
                        team_display = team_name.title()
                        opponent_upper = opponent_name.upper().strip()
                        team_upper = team_display.upper().strip()
                        
                        # Check if opponent name matches team name (exact or significant parts)
                        opponent_invalid = (
                            opponent_upper == team_upper or
                            (opponent_name and team_name and len(team_name_parts) > 0 and
                             any(len(part) > 3 and part in opponent_upper for part in team_name_parts))
                        )
                        
                        if opponent_invalid:
                            # Wrong opponent detected, swap to the other team
                            logger.debug(f"Opponent validation failed: '{opponent_name}' matches team '{team_name}'. Swapping opponent.")
                            opponent_team = home_team if is_home else away_team
                            opponent_name = opponent_team.get('displayName', '')
                            if not opponent_name:
                                opponent_name = opponent_team.get('abbreviation', '')
                            
                            # Re-validate after swap
                            opponent_upper_swapped = opponent_name.upper().strip()
                            if opponent_upper_swapped == team_upper or not opponent_name:
                                # Still invalid after swap, skip this game
                                logger.warning(f"Could not determine valid opponent for {team_name} in game {away_name} @ {home_name}. Skipping game.")
                                continue
                            
                            logger.info(f"Corrected opponent name: {opponent_name} (team: {team_name})")
                        
                        # Get game date
                        game_date = event.get('date', '')[:10] if event.get('date') else check_date.strftime('%Y-%m-%d')
                        
                        # Get matchup
                        away_name = away_team.get('displayName', away_abbrev)
                        home_name = home_team.get('displayName', home_abbrev)
                        matchup = f"{away_name} @ {home_name}" if not is_home else f"{home_name} vs {away_name}"
                        
                        # Store completed game data
                        game_data = {
                            'game_date': game_date,
                            'team_score': team_score,
                            'opponent_score': opponent_score,
                            'opponent_name': opponent_name,
                            'did_win': did_win,
                            'matchup': matchup
                        }
                        
                        completed_games.append(game_data)
                        logger.debug(f"Found completed game: {game_date} - {matchup} - {team_score}-{opponent_score}")
                
                except Exception as e:
                    logger.debug(f"Error checking {date_str}: {e}")
                    continue
            
            # Step 2: Sort games by game_date descending (most recent first)
            if not completed_games:
                logger.warning(f"No completed games found for {team_name} in last {days_back} days")
                return None
            
            logger.info(f"Step 2: Sorting {len(completed_games)} completed games by game_date descending")
            completed_games.sort(key=lambda x: x['game_date'], reverse=True)
            
            # Step 3: Select the latest game
            latest_game = completed_games[0]
            logger.info(f"Step 3: Selected latest game from {latest_game['game_date']}")
            
            # Step 4: Validate and compare scores
            team_score = latest_game['team_score']
            opponent_score = latest_game['opponent_score']
            did_win = latest_game['did_win']
            
            # Validation: Ensure scores are valid (non-zero for completed games, reasonable NBA scores)
            if team_score <= 0 or opponent_score <= 0:
                logger.warning(f"Invalid scores detected: {team_name} {team_score} vs {latest_game['opponent_name']} {opponent_score}. Skipping result.")
                return None
            
            # Validation: Ensure scores are reasonable for NBA (typically 80-150 points)
            if team_score < 50 or team_score > 200 or opponent_score < 50 or opponent_score > 200:
                logger.warning(f"Unusual scores detected: {team_name} {team_score} vs {latest_game['opponent_name']} {opponent_score}. Proceeding with caution.")
            
            # Validation: Ensure win/loss determination is correct based on scores
            if did_win and team_score <= opponent_score:
                logger.warning(f"Win/loss mismatch detected: did_win={did_win} but {team_score} <= {opponent_score}. Correcting...")
                did_win = team_score > opponent_score
            elif not did_win and team_score > opponent_score:
                logger.warning(f"Win/loss mismatch detected: did_win={did_win} but {team_score} > {opponent_score}. Correcting...")
                did_win = True
            
            # Validation: Ensure opponent name is valid and not the same as team
            opponent_name = latest_game['opponent_name']
            team_name_upper = team_name.upper()
            opponent_name_fixed = False
            
            # Check if opponent name is invalid (empty or same as team)
            if not opponent_name or opponent_name.upper().strip() == team_name_upper.strip():
                logger.warning(f"Invalid opponent name detected: '{opponent_name}' for team {team_name}. Attempting to fix...")
                # Try to get opponent from matchup string
                matchup = latest_game.get('matchup', '')
                if matchup:
                    # Try splitting by ' vs ' or ' @ '
                    if ' vs ' in matchup:
                        matchup_parts = matchup.split(' vs ', 1)
                    elif ' @ ' in matchup:
                        matchup_parts = matchup.split(' @ ', 1)
                    else:
                        matchup_parts = []
                    
                    if len(matchup_parts) >= 2:
                        # Determine which part is the team and which is the opponent
                        part0_upper = matchup_parts[0].upper().strip()
                        part1_upper = matchup_parts[1].upper().strip()
                        
                        # Check which part matches the team name
                        if team_name_upper in part0_upper or any(word in part0_upper for word in team_name_upper.split() if len(word) > 2):
                            # Team is in first part, opponent is in second
                            potential_opponent = matchup_parts[1].strip()
                        elif team_name_upper in part1_upper or any(word in part1_upper for word in team_name_upper.split() if len(word) > 2):
                            # Team is in second part, opponent is in first
                            potential_opponent = matchup_parts[0].strip()
                        else:
                            # Can't determine, use the other part as fallback
                            potential_opponent = matchup_parts[1].strip() if len(matchup_parts) > 1 else matchup_parts[0].strip()
                        
                        # Validate the potential opponent is different from team
                        if potential_opponent and potential_opponent.upper().strip() != team_name_upper.strip():
                            opponent_name = potential_opponent
                            opponent_name_fixed = True
                            logger.info(f"Fixed opponent name to: {opponent_name}")
                
                # If still invalid after fix attempt, return None
                if not opponent_name_fixed or not opponent_name or opponent_name.upper().strip() == team_name_upper.strip():
                    logger.error(f"Could not fix invalid opponent name for {team_name}. Opponent: '{opponent_name}', Team: '{team_name}'. Returning None.")
                    return None
            
            # Final validation: double-check all required fields before returning
            # Opponent name validation (already checked above, but double-check)
            if not opponent_name or not opponent_name.strip():
                logger.error(f"Final validation failed: opponent name is invalid for {team_name}")
                return None
            
            if team_score <= 0 or opponent_score <= 0:
                logger.error(f"Final validation failed: invalid scores for {team_name} ({team_score}-{opponent_score})")
                return None
            
            if not latest_game.get('game_date'):
                logger.error(f"Final validation failed: missing game date for {team_name}")
                return None
            
            logger.info(f"Step 4: Validated score comparison - {team_name.title()} {team_score} vs {opponent_name} {opponent_score} → {'WIN' if did_win else 'LOSS'}")
            
            # Return result with validated final score
            return {
                'team_name': team_name.title(),
                'team_abbrev': team_abbrev,
                'opponent_name': opponent_name.strip(),  # Clean whitespace
                'did_win': did_win,
                'team_score': team_score,
                'opponent_score': opponent_score,
                'game_date': latest_game['game_date'],
                'matchup': latest_game.get('matchup', f"{team_name.title()} vs {opponent_name}")
            }
            
        except Exception as e:
            logger.error(f"Error getting team game result from ESPN: {e}", exc_info=True)
            return None
    
    def get_team_recent_game_results(self, team_name: str, num_games: int = 5, days_back: int = 60) -> Optional[List[Dict]]:
        """
        Get a team's last N game results using ESPN scoreboard API
        Returns a list of game results sorted by date (most recent first)
        
        Args:
            team_name: Name of the team (e.g., 'heat', 'miami heat')
            num_games: Number of recent games to return (default: 5)
            days_back: How many days back to search (default: 60)
        
        Returns:
            List of game result dictionaries, or None if no games found
        """
        try:
            logger.info(f"Fetching last {num_games} game results for {team_name} from ESPN API")
            
            # Map team name to ESPN team abbreviation
            team_map = {
                'warriors': 'GS', 'golden state': 'GS', 'gsw': 'GS', 'golden state warriors': 'GS',
                'lakers': 'LAL', 'los angeles lakers': 'LAL',
                'celtics': 'BOS', 'boston celtics': 'BOS',
                'bucks': 'MIL', 'milwaukee bucks': 'MIL',
                'nuggets': 'DEN', 'denver nuggets': 'DEN',
                'suns': 'PHX', 'phoenix suns': 'PHX',
                'heat': 'MIA', 'miami heat': 'MIA',
                'mavericks': 'DAL', 'dallas mavericks': 'DAL',
                'clippers': 'LAC', 'la clippers': 'LAC', 'los angeles clippers': 'LAC',
                '76ers': 'PHI', 'sixers': 'PHI', 'philadelphia 76ers': 'PHI',
                'cavaliers': 'CLE', 'cleveland cavaliers': 'CLE',
                'knicks': 'NYK', 'new york knicks': 'NYK', 'new york': 'NYK',
                'hawks': 'ATL', 'atlanta hawks': 'ATL',
                'thunder': 'OKC', 'oklahoma city thunder': 'OKC',
                'timberwolves': 'MIN', 'minnesota timberwolves': 'MIN',
                'kings': 'SAC', 'sacramento kings': 'SAC',
                'pelicans': 'NO', 'new orleans pelicans': 'NO',
                'grizzlies': 'MEM', 'memphis grizzlies': 'MEM',
                'raptors': 'TOR', 'toronto raptors': 'TOR',
                'nets': 'BKN', 'brooklyn nets': 'BKN',
                'bulls': 'CHI', 'chicago bulls': 'CHI',
                'pistons': 'DET', 'detroit pistons': 'DET',
                'pacers': 'IND', 'indiana pacers': 'IND',
                'hornets': 'CHA', 'charlotte hornets': 'CHA',
                'magic': 'ORL', 'orlando magic': 'ORL',
                'wizards': 'WSH', 'washington wizards': 'WSH',
                'trail blazers': 'POR', 'portland trail blazers': 'POR', 'blazers': 'POR',
                'jazz': 'UTAH', 'utah jazz': 'UTAH',
                'rockets': 'HOU', 'houston rockets': 'HOU',
                'spurs': 'SAS', 'san antonio spurs': 'SAS'
            }
            team_name_lower = team_name.lower().strip()
            team_abbrev = team_map.get(team_name_lower)
            if not team_abbrev:
                for key, abbrev in team_map.items():
                    if key in team_name_lower or team_name_lower in key:
                        team_abbrev = abbrev
                        break
                if not team_abbrev:
                    team_abbrev = team_name[:3].upper()
            
            # Fetch all completed games from scoreboard
            completed_games = []
            today = date.today()
            
            for i in range(days_back):
                check_date = today - timedelta(days=i)
                date_str = check_date.strftime('%Y%m%d')
                
                url = f"{self.BASE_URL}/scoreboard"
                try:
                    response = self.session.get(url, params={'dates': date_str}, timeout=10)
                    if response.status_code != 200:
                        continue
                    
                    scoreboard_data = response.json()
                    events = scoreboard_data.get('events', [])
                    
                    for event in events:
                        competitions = event.get('competitions', [])
                        if not competitions:
                            continue
                        
                        comp = competitions[0]
                        competitors = comp.get('competitors', [])
                        if len(competitors) < 2:
                            continue
                        
                        away_team = competitors[0].get('team', {})
                        home_team = competitors[1].get('team', {})
                        away_abbrev = away_team.get('abbreviation', '')
                        home_abbrev = home_team.get('abbreviation', '')
                        
                        # Check if this is the team's game
                        if team_abbrev.upper() not in [away_abbrev.upper(), home_abbrev.upper()]:
                            continue
                        
                        # Filter only completed games
                        status = comp.get('status', {})
                        status_type = status.get('type', {}) if isinstance(status, dict) else {}
                        is_completed = (
                            status_type.get('completed', False) if isinstance(status_type, dict) else False
                        ) or (
                            status_type.get('name', '') == 'STATUS_FINAL' if isinstance(status_type, dict) else False
                        )
                        
                        # Get scores
                        away_score_raw = competitors[0].get('score', 0)
                        home_score_raw = competitors[1].get('score', 0)
                        
                        if isinstance(away_score_raw, dict):
                            away_score = int(away_score_raw.get('value', 0) or 0)
                        else:
                            away_score = int(away_score_raw or 0)
                        
                        if isinstance(home_score_raw, dict):
                            home_score = int(home_score_raw.get('value', 0) or 0)
                        else:
                            home_score = int(home_score_raw or 0)
                        
                        # If scores are 0, try linescore
                        if away_score == 0 and home_score == 0:
                            away_linescore = competitors[0].get('linescore', [])
                            home_linescore = competitors[1].get('linescore', [])
                            if away_linescore:
                                away_score = sum(int(period.get('value', 0) or 0) for period in away_linescore)
                            if home_linescore:
                                home_score = sum(int(period.get('value', 0) or 0) for period in home_linescore)
                        
                        # Game is completed if status says so OR has scores > 0
                        if not is_completed and away_score > 0 and home_score > 0:
                            is_completed = True
                        
                        if not is_completed or away_score == 0 or home_score == 0:
                            continue
                        
                        # Determine team and opponent
                        is_home = team_abbrev.upper() == home_abbrev.upper()
                        team_score = home_score if is_home else away_score
                        opponent_score = away_score if is_home else home_score
                        
                        opponent_team = home_team if not is_home else away_team
                        opponent_name = opponent_team.get('displayName', '')
                        if not opponent_name:
                            opponent_name = opponent_team.get('abbreviation', '')
                        
                        # Get game date
                        game_date = event.get('date', '')[:10] if event.get('date') else check_date.strftime('%Y-%m-%d')
                        
                        # Get matchup
                        away_name = away_team.get('displayName', away_abbrev)
                        home_name = home_team.get('displayName', home_abbrev)
                        matchup = f"{away_name} @ {home_name}" if not is_home else f"{home_name} vs {away_name}"
                        
                        # Store completed game
                        completed_games.append({
                            'team_name': team_name.title(),
                            'team_abbrev': team_abbrev.upper(),
                            'game_date': game_date,
                            'team_score': team_score,
                            'opponent_score': opponent_score,
                            'opponent_name': opponent_name,
                            'did_win': team_score > opponent_score,
                            'matchup': matchup,
                            'source': 'espn_scoreboard'
                        })
                        
                        # Stop if we have enough games
                        if len(completed_games) >= num_games:
                            break
                
                except Exception as e:
                    logger.debug(f"Error checking {date_str}: {e}")
                    continue
                
                # Stop if we have enough games
                if len(completed_games) >= num_games:
                    break
            
            if not completed_games:
                logger.warning(f"No completed games found for {team_name} in last {days_back} days")
                return None
            
            # Sort by date descending (most recent first)
            completed_games.sort(key=lambda x: x['game_date'], reverse=True)
            
            # Return only the requested number of games
            logger.info(f"Found {len(completed_games)} completed games, returning last {num_games}")
            return completed_games[:num_games]
            
        except Exception as e:
            logger.error(f"Error in get_team_recent_game_results: {e}", exc_info=True)
            return None
    
    def get_standings(self, conference: str = None) -> List[Dict]:
        """
        Get current NBA standings from ESPN API with conference rankings
        conference: 'East', 'West', or None for all teams
        """
        try:
            logger.info(f"Fetching standings from ESPN API" + (f" for {conference}ern Conference" if conference else " for all teams"))
            
            # ESPN API standings endpoint
            url = f"{self.BASE_URL}/standings"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"ESPN API returned status {response.status_code} for standings")
                return []
            
            data = response.json()
            
            # ESPN API structure - try multiple possible paths
            children = []
            
            # Try direct children path
            if 'children' in data:
                children = data.get('children', [])
            # Try standings path
            elif 'standings' in data:
                standings_data = data.get('standings', [])
                if isinstance(standings_data, list):
                    children = standings_data
                elif isinstance(standings_data, dict) and 'children' in standings_data:
                    children = standings_data.get('children', [])
            # Try groups path (ESPN sometimes uses this)
            elif 'groups' in data:
                groups = data.get('groups', [])
                for group in groups:
                    if 'standings' in group:
                        children.extend(group.get('standings', []))
                    elif 'entries' in group:
                        children.extend(group.get('entries', []))
            
            if not children:
                logger.warning("Could not find standings data in ESPN API response structure")
                logger.debug(f"Available keys in response: {list(data.keys())[:10]}")
                return []
            
            all_standings = []
            
            # Process each conference/division
            for child in children:
                # Get conference name
                child_name = child.get('name', '').upper()
                is_east = 'EAST' in child_name
                is_west = 'WEST' in child_name
                
                # Filter by conference if specified
                if conference:
                    conf_upper = conference.upper()
                    if conf_upper == 'EAST' and not is_east:
                        continue
                    if conf_upper == 'WEST' and not is_west:
                        continue
                
                # Get teams in this conference/division
                teams = child.get('teams', [])
                for team_data in teams:
                    team = team_data.get('team', {})
                    team_name = team.get('displayName', team.get('name', ''))
                    team_abbrev = team.get('abbreviation', '')
                    
                    # Get stats
                    stats = team_data.get('stats', [])
                    wins = 0
                    losses = 0
                    win_pct = 0.0
                    conference_rank = 0
                    
                    for stat in stats:
                        stat_name = stat.get('name', '').upper()
                        stat_value = stat.get('value', 0)
                        
                        if stat_name in ['WINS', 'W']:
                            wins = int(stat_value) if stat_value else 0
                        elif stat_name in ['LOSSES', 'L']:
                            losses = int(stat_value) if stat_value else 0
                        elif stat_name in ['WINPCT', 'WIN_PCT', 'PCT']:
                            win_pct = float(stat_value) if stat_value else 0.0
                        elif stat_name in ['CONF_RANK', 'CONFERENCE_RANK', 'RANK']:
                            conference_rank = int(stat_value) if stat_value else 0
                    
                    # Calculate win percentage if not provided
                    total_games = wins + losses
                    if total_games > 0 and win_pct == 0:
                        win_pct = wins / total_games
                    
                    # Determine conference
                    conference_name = 'West' if is_west else ('East' if is_east else '')
                    
                    all_standings.append({
                        'team_name': team_name,
                        'team_abbrev': team_abbrev,
                        'conference': conference_name,
                        'wins': wins,
                        'losses': losses,
                        'win_percentage': round(win_pct, 3),
                        'conference_rank': conference_rank,
                        'games_played': total_games
                    })
            
            # If conference_rank is 0, calculate it by sorting within conference
            if any(s.get('conference_rank', 0) == 0 for s in all_standings):
                for conf in ['East', 'West']:
                    conf_teams = [s for s in all_standings if s.get('conference', '') == conf]
                    conf_teams.sort(key=lambda x: x['win_percentage'], reverse=True)
                    for idx, team in enumerate(conf_teams, 1):
                        if team.get('conference_rank', 0) == 0:
                            team['conference_rank'] = idx
            
            # Sort by conference, then by rank
            all_standings.sort(key=lambda x: (x.get('conference', ''), x.get('conference_rank', 0)))
            
            logger.info(f"✓ Retrieved {len(all_standings)} team standings from ESPN API")
            return all_standings
            
        except Exception as e:
            logger.error(f"Error getting standings from ESPN API: {e}", exc_info=True)
            return []
    
    def get_games_for_date(self, target_date: date, include_completed: bool = False, include_upcoming: bool = True) -> List[Dict]:
        """Get games for a specific date from ESPN API"""
        try:
            date_str = target_date.strftime('%Y%m%d')
            url = f"{self.BASE_URL}/scoreboard"
            response = self.session.get(url, params={'dates': date_str}, timeout=8)
            
            if response.status_code != 200:
                logger.warning(f"ESPN API returned status {response.status_code} for date {date_str}")
                return []
            
            data = response.json()
            events = data.get('events', [])
            games = []
            
            for event in events:
                competitions = event.get('competitions', [])
                if not competitions:
                    continue
                
                comp = competitions[0]
                competitors = comp.get('competitors', [])
                if len(competitors) < 2:
                    continue
                
                # Get game status
                status = comp.get('status', {})
                status_type = status.get('type', {})
                is_completed = status_type.get('completed', False) or status_type.get('name', '') == 'STATUS_FINAL'
                is_upcoming = not is_completed and status_type.get('name', '') not in ['STATUS_POSTPONED', 'STATUS_CANCELED']
                
                # Filter based on what we want
                if is_completed and not include_completed:
                    continue
                if is_upcoming and not include_upcoming:
                    continue
                
                away_team = competitors[0].get('team', {})
                home_team = competitors[1].get('team', {})
                away_abbrev = away_team.get('abbreviation', '')
                home_abbrev = home_team.get('abbreviation', '')
                away_name = away_team.get('displayName', away_abbrev)
                home_name = home_team.get('displayName', home_abbrev)
                
                # Get scores if completed
                away_score = int(competitors[0].get('score', 0) or 0)
                home_score = int(competitors[1].get('score', 0) or 0)
                
                # Get game date and time
                # IMPORTANT: Check the actual event date to ensure it matches target_date
                # ESPN returns dates in UTC, but NBA games are played in US timezones
                # We need to convert to US Eastern time (primary NBA timezone) to get the correct date
                game_time = ''
                event_date_str = None
                if event.get('date'):
                    try:
                        # Parse ISO format datetime
                        from datetime import datetime, timezone, timedelta
                        
                        # Parse UTC datetime
                        dt_utc = datetime.fromisoformat(event['date'].replace('Z', '+00:00'))
                        
                        # Convert to US Eastern time (EST/EDT)
                        # EST is UTC-5, EDT is UTC-4
                        # For simplicity, we'll use UTC-5 (EST) as the standard offset
                        # This is close enough for date matching purposes
                        eastern_offset = timedelta(hours=-5)
                        dt_eastern = dt_utc + eastern_offset
                        
                        # Get the actual date of the event in Eastern time
                        event_date_str = dt_eastern.date().strftime('%Y-%m-%d')
                        game_time = dt_eastern.strftime('%I:%M %p') if dt_eastern else ''
                    except Exception as e:
                        # Fallback: try without timezone conversion
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(event['date'].replace('Z', '+00:00'))
                            # Use UTC date as fallback, but subtract 5 hours to approximate EST
                            from datetime import timedelta
                            dt_est = dt - timedelta(hours=5)
                            event_date_str = dt_est.date().strftime('%Y-%m-%d')
                            game_time = dt_est.strftime('%I:%M %p') if dt_est else ''
                            logger.debug(f"Using EST approximation for date: {event_date_str}")
                        except Exception as e2:
                            logger.debug(f"Date parsing failed: {e2}")
                            game_time = ''
                
                # CRITICAL: Only include games that match the exact target_date
                # This prevents timezone issues where games from adjacent dates might be included
                target_date_str = target_date.strftime('%Y-%m-%d')
                if event_date_str and event_date_str != target_date_str:
                    logger.debug(f"Skipping game from {event_date_str} (requested {target_date_str})")
                    continue
                
                # If event_date_str is None (parsing failed), still include the game
                # but use target_date as the date (this handles edge cases)
                if not event_date_str:
                    logger.debug(f"Could not parse event date, using target_date {target_date_str}")
                    event_date_str = target_date_str
                
                # Use the parsed event date (in Eastern time) as the authoritative date
                game_date = event_date_str
                
                # Get game status for live games
                game_status = 'completed' if is_completed else ('live' if status_type.get('name', '') not in ['STATUS_SCHEDULED', 'STATUS_FINAL', 'STATUS_POSTPONED', 'STATUS_CANCELED'] else 'upcoming')
                
                game_info = {
                    'team1_name': away_abbrev,
                    'team2_name': home_abbrev,
                    'team1_display': away_name,
                    'team2_display': home_name,
                    'match_date': game_date,
                    'game_time': game_time,
                    'venue': home_team.get('location', ''),
                    'status': game_status,
                    'game_status': status_type.get('name', ''),
                    'team1_score': away_score if (is_completed or away_score > 0) else None,
                    'team2_score': home_score if (is_completed or home_score > 0) else None
                }
                
                games.append(game_info)
            
            logger.info(f"✓ Found {len(games)} games for {target_date}")
            return games
            
        except Exception as e:
            logger.error(f"Error getting games for date from ESPN: {e}", exc_info=True)
            return []
    
    def get_games_for_date_range(self, start_date: date, end_date: date) -> List[Dict]:
        """Get games for a date range from ESPN API"""
        all_games = []
        current_date = start_date
        
        while current_date <= end_date:
            games = self.get_games_for_date(current_date, include_completed=False, include_upcoming=True)
            all_games.extend(games)
            current_date += timedelta(days=1)
        
        return all_games

