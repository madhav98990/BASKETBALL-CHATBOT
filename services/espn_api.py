"""
ESPN NBA API Service - Alternative data source
Uses ESPN's public API for NBA data
"""
import requests
import logging
from datetime import date, timedelta
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ESPNNBAApi:
    """ESPN NBA API service as alternative data source"""
    
    BASE_URL = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_standings(self) -> List[Dict]:
        """Get current standings from ESPN API"""
        try:
            # Use ESPN standings endpoint if available
            # Try to get standings from scoreboard data for current season
            today = date.today()
            
            # Calculate season start (October of current or previous year)
            if today.month >= 10:
                season_start = date(today.year, 10, 1)
            else:
                season_start = date(today.year - 1, 10, 1)
            
            standings = {}
            
            # Get games from last 30 days to calculate recent standings
            # For full season, we'd need to aggregate more games, but this gives current form
            start_date = max(season_start, today - timedelta(days=60))  # Last 60 days or season start
            
            # Process in 7-day batches to avoid timeouts
            current_date = start_date
            batch_size = 7
            games_processed = 0
            max_games = 500  # Limit to avoid too many API calls
            
            while current_date < today and games_processed < max_games:
                batch_end = min(current_date + timedelta(days=batch_size), today)
                
                url = f"{self.BASE_URL}/scoreboard"
                params = {
                    'dates': f"{current_date.strftime('%Y%m%d')}-{batch_end.strftime('%Y%m%d')}"
                }
                
                try:
                    response = self.session.get(url, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        
                        for event in data.get('events', []):
                            competitions = event.get('competitions', [])
                            if competitions:
                                comp = competitions[0]
                                status_type = comp.get('status', {}).get('type', {})
                                
                                # Only count completed games
                                if status_type.get('completed', False) or status_type.get('name', '') == 'STATUS_FINAL':
                                    competitors = comp.get('competitors', [])
                                    if len(competitors) >= 2:
                                        away = competitors[0]
                                        home = competitors[1]
                                        
                                        away_abbrev = away.get('team', {}).get('abbreviation', '')
                                        home_abbrev = home.get('team', {}).get('abbreviation', '')
                                        away_score = int(away.get('score', '0') or '0')
                                        home_score = int(home.get('score', '0') or '0')
                                        
                                        # Only count if scores are valid
                                        if away_score >= 0 and home_score >= 0:
                                            # Initialize teams if not exists
                                            if away_abbrev not in standings:
                                                standings[away_abbrev] = {'wins': 0, 'losses': 0, 'team': away_abbrev}
                                            if home_abbrev not in standings:
                                                standings[home_abbrev] = {'wins': 0, 'losses': 0, 'team': home_abbrev}
                                            
                                            # Update wins/losses
                                            if away_score > home_score:
                                                standings[away_abbrev]['wins'] += 1
                                                standings[home_abbrev]['losses'] += 1
                                            elif home_score > away_score:
                                                standings[home_abbrev]['wins'] += 1
                                                standings[away_abbrev]['losses'] += 1
                                            
                                            games_processed += 1
                except Exception as e:
                    logger.warning(f"Error fetching games for {current_date}: {e}")
                
                current_date = batch_end + timedelta(days=1)
            
            # Convert to list and calculate win percentage
            result = []
            for team, record in standings.items():
                total = record['wins'] + record['losses']
                win_pct = record['wins'] / total if total > 0 else 0
                result.append({
                    'team_name': team,
                    'wins': record['wins'],
                    'losses': record['losses'],
                    'win_percentage': round(win_pct, 3),
                    'games_played': total,
                    'conference_rank': 0  # Will be set after sorting
                })
            
            # Sort by win percentage
            result.sort(key=lambda x: x['win_percentage'], reverse=True)
            
            # Add rankings
            for idx, team in enumerate(result, 1):
                team['conference_rank'] = idx
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating standings: {e}")
            return []
    
    def get_recent_games(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """Get recent game results from ESPN"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            # ESPN uses scoreboard endpoint
            url = f"{self.BASE_URL}/scoreboard"
            params = {
                'dates': f"{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}"
            }
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                games = []
                
                for event in data.get('events', []):
                    try:
                        competitions = event.get('competitions', [])
                        if competitions:
                            comp = competitions[0]
                            competitors = comp.get('competitors', [])
                            if len(competitors) >= 2:
                                away = competitors[0]
                                home = competitors[1]
                                
                                # Get scores
                                away_score = int(away.get('score', '0') or '0')
                                home_score = int(home.get('score', '0') or '0')
                                
                                games.append({
                                    'team1_name': away.get('team', {}).get('abbreviation', ''),
                                    'team2_name': home.get('team', {}).get('abbreviation', ''),
                                    'team1_score': away_score,
                                    'team2_score': home_score,
                                    'match_date': event.get('date', '')[:10],
                                    'venue': home.get('team', {}).get('location', ''),
                                    'winner': away.get('team', {}).get('abbreviation', '') if away_score > home_score else home.get('team', {}).get('abbreviation', ''),
                                    'event_id': event.get('id', '')  # Store event ID for boxscore access
                                })
                    except Exception as e:
                        logger.debug(f"Error processing event in recent_games: {e}")
                        continue
                
                return games[:limit]
        except Exception as e:
            logger.error(f"Error fetching from ESPN: {e}")
            return []
        
        return []
    
    def get_player_stats_for_game(self, player_name: str, team_abbrev: str = None, game_date: str = None) -> List[Dict]:
        """Get player stats for a specific game or recent games using ESPN boxscore"""
        try:
            # Get recent games first to find game IDs
            days_to_check = 7 if not game_date else 30
            recent_games = self.get_recent_games(days=days_to_check, limit=100)
            
            results = []
            player_name_lower = player_name.lower()
            
            # Try to find player name parts (first name, last name)
            name_parts = player_name_lower.split()
            
            for game in recent_games:
                game_date_str = game.get('match_date', '')
                
                # If specific date requested, filter by date
                if game_date and game_date_str != game_date:
                    continue
                
                # If specific team requested, filter by team
                if team_abbrev:
                    team1 = game.get('team1_name', '').upper()
                    team2 = game.get('team2_name', '').upper()
                    if team_abbrev.upper() not in [team1, team2]:
                        continue
                
                # Try to get boxscore for this game
                # ESPN uses event ID format - we'll try to extract from date
                try:
                    # For now, we'll search through recent games and look for player in boxscore
                    # ESPN boxscore format: /apis/site/v2/sports/basketball/nba/summary?event={eventId}
                    # Since we don't have event IDs easily, we'll use a different approach
                    # Search through game summaries if available
                    pass
                except Exception:
                    continue
            
            return results
        except Exception as e:
            logger.error(f"Error fetching player stats: {e}")
            return []
    
    def get_player_recent_stats(self, player_name: str, limit: int = 5) -> List[Dict]:
        """
        Get player's most recent game stats from ESPN boxscores
        Returns list of player stat dictionaries
        """
        try:
            logger.info(f"🔍 Fetching REAL-TIME stats for {player_name} from ESPN")
            
            # OPTIMIZATION: Search last 7 days for player stats (more likely to find data)
            recent_games = self.get_recent_games(days=7, limit=20)
            
            if not recent_games:
                logger.warning("No recent games found from ESPN")
                return []
            
            # Extract player name parts for matching
            name_parts = player_name.lower().split()
            first_name = name_parts[0] if len(name_parts) > 0 else ""
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            # Player name variations for matching
            name_variations = [player_name.lower(), f"{first_name} {last_name}"]
            if len(name_parts) > 2:
                # Handle names like "Karl-Anthony Towns"
                name_variations.append(" ".join(name_parts[:2]))
            
            results = []
            
            # For each recent game, get boxscore and search for player
            for game in recent_games:
                try:
                    event_id = game.get('event_id')
                    if not event_id:
                        # If no event_id stored, try to get it from date
                        game_date = game.get('match_date', '')
                        if not game_date:
                            continue
                        
                        date_parts = game_date.split('-')
                        if len(date_parts) == 3:
                            year, month, day = date_parts
                            url = f"{self.BASE_URL}/scoreboard"
                            params = {'dates': f"{year}{month}{day}"}
                            
                            response = self.session.get(url, params=params, timeout=3)  # Very aggressive timeout
                            if response.status_code == 200:
                                data = response.json()
                                team1 = game.get('team1_name', '').upper()
                                team2 = game.get('team2_name', '').upper()
                                
                                for event in data.get('events', []):
                                    comps = event.get('competitions', [])
                                    if comps:
                                        comp = comps[0]
                                        competitors = comp.get('competitors', [])
                                        if len(competitors) >= 2:
                                            away_abbrev = competitors[0].get('team', {}).get('abbreviation', '').upper()
                                            home_abbrev = competitors[1].get('team', {}).get('abbreviation', '').upper()
                                            
                                            if (away_abbrev == team1 and home_abbrev == team2) or \
                                               (away_abbrev == team2 and home_abbrev == team1):
                                                event_id = event.get('id', '')
                                                break
                    
                    if event_id:
                        # Get boxscore/summary for this event
                        summary_url = f"{self.BASE_URL}/summary"
                        summary_params = {'event': event_id}
                        
                        summary_response = self.session.get(summary_url, params=summary_params, timeout=10)
                        if summary_response.status_code == 200:
                            summary_data = summary_response.json()
                            
                            # Extract player stats from boxscore - ESPN has multiple possible structures
                            # Get competitors info first
                            competitions = summary_data.get('boxscore', {}).get('competitions', [])
                            if not competitions:
                                competitions = summary_data.get('competitions', [])
                            
                            competitors_info = []
                            if competitions and len(competitions) > 0:
                                competitors_info = competitions[0].get('competitors', [])
                            
                            away_team = competitors_info[0] if len(competitors_info) > 0 else None
                            home_team = competitors_info[1] if len(competitors_info) > 1 else None
                            
                            team1_abbrev = game.get('team1_name', '')
                            team2_abbrev = game.get('team2_name', '')
                            
                            # Try to find player stats in boxscore structure
                            boxscore = summary_data.get('boxscore', {})
                            
                            # Method 1: Check boxscore.players
                            players_list = boxscore.get('players', [])
                            
                            # Method 2: Check boxscore.statistics (if players not found)
                            if not players_list:
                                statistics = boxscore.get('statistics', [])
                                if statistics:
                                    for stat_group in statistics:
                                        players_list.extend(stat_group.get('athletes', []))
                            
                            # Method 3: Check competitors directly
                            if not players_list and competitors_info:
                                for competitor in competitors_info:
                                    roster = competitor.get('roster', {}).get('entries', [])
                                    if roster:
                                        players_list.extend(roster)
                            
                            # Process each player entry
                            for player_entry in players_list:
                                try:
                                    # Handle different structures
                                    player_info = player_entry.get('athlete', {})
                                    if not player_info:
                                        player_info = player_entry
                                    
                                    if not player_info:
                                        continue
                                    
                                    full_name = player_info.get('fullName', '').lower()
                                    display_name = player_info.get('displayName', '').lower()
                                    short_name = player_info.get('shortName', '').lower()
                                    
                                    # Check if this player matches
                                    matches = False
                                    for name_var in name_variations:
                                        if name_var in full_name or name_var in display_name or name_var in short_name:
                                            matches = True
                                            break
                                        # Also check if first and last name match
                                        if first_name and last_name:
                                            if (first_name in full_name and last_name in full_name) or \
                                               (first_name in display_name and last_name in display_name):
                                                matches = True
                                                break
                                    
                                    if matches:
                                        # Extract stats - ESPN uses different structures
                                        stats_array = player_entry.get('stats', [])
                                        if not stats_array:
                                            stats_array = player_entry.get('statistics', [])
                                        
                                        # Build stat dictionary
                                        stat_dict = {}
                                        for stat_item in stats_array:
                                            if isinstance(stat_item, dict):
                                                stat_name = stat_item.get('name', '').lower()
                                                stat_value = stat_item.get('value', stat_item.get('displayValue', 0))
                                                try:
                                                    stat_dict[stat_name] = float(stat_value) if stat_value else 0
                                                except:
                                                    stat_dict[stat_name] = 0
                                        
                                        # Map ESPN stat names to our format (case-insensitive)
                                        points = int(stat_dict.get('points', 0) or stat_dict.get('pts', 0) or 0)
                                        rebounds = int(stat_dict.get('rebounds', 0) or stat_dict.get('reb', 0) or stat_dict.get('totalrebounds', 0) or 0)
                                        assists = int(stat_dict.get('assists', 0) or stat_dict.get('ast', 0) or 0)
                                        steals = int(stat_dict.get('steals', 0) or stat_dict.get('stl', 0) or 0)
                                        blocks = int(stat_dict.get('blocks', 0) or stat_dict.get('blk', 0) or 0)
                                        
                                        # Determine player's team
                                        team_id = player_entry.get('team', {}).get('id', '') if isinstance(player_entry.get('team'), dict) else None
                                        if not team_id:
                                            team_id = player_info.get('team', {}).get('id', '') if isinstance(player_info.get('team'), dict) else None
                                        
                                        player_team = team1_abbrev  # Default
                                        if team_id and away_team:
                                            away_team_id = away_team.get('team', {}).get('id', '')
                                            home_team_id = home_team.get('team', {}).get('id', '') if home_team else ''
                                            if str(team_id) == str(away_team_id):
                                                player_team = team1_abbrev
                                            elif str(team_id) == str(home_team_id):
                                                player_team = team2_abbrev
                                        
                                        player_stat = {
                                            'player_name': player_info.get('fullName', player_info.get('displayName', player_name)),
                                            'points': points,
                                            'rebounds': rebounds,
                                            'assists': assists,
                                            'steals': steals,
                                            'blocks': blocks,
                                            'match_date': game.get('match_date', ''),
                                            'team1_name': team1_abbrev,
                                            'team2_name': team2_abbrev,
                                            'player_team': player_team
                                        }
                                        
                                        # Only add if we have meaningful stats
                                        if points > 0 or rebounds > 0 or assists > 0:
                                            results.append(player_stat)
                                            logger.info(f"✓ Found REAL-TIME stats: {player_name} - {points} pts, {rebounds} reb, {assists} ast on {player_stat['match_date']}")
                                            if len(results) >= limit:
                                                # Sort by date descending and return
                                                results.sort(key=lambda x: x.get('match_date', ''), reverse=True)
                                                return results[:limit]
                                except Exception as pe:
                                    logger.debug(f"Error processing player entry: {pe}")
                                    continue
                except Exception as e:
                    logger.debug(f"Error processing game {game.get('match_date')}: {e}")
                    continue
            
            # Sort by date descending (most recent first)
            results.sort(key=lambda x: x.get('match_date', ''), reverse=True)
            logger.info(f"Found {len(results)} real-time stats for {player_name}")
            return results[:limit]
        except Exception as e:
            logger.error(f"Error fetching recent player stats: {e}", exc_info=True)
            return []
    
    def get_upcoming_games(self, days: int = 7, limit: int = 20) -> List[Dict]:
        """Get upcoming games from ESPN"""
        try:
            start_date = date.today()
            end_date = start_date + timedelta(days=days)
            
            url = f"{self.BASE_URL}/scoreboard"
            params = {
                'dates': f"{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}"
            }
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                games = []
                
                for event in data.get('events', []):
                    status = event.get('status', {}).get('type', {}).get('name', '')
                    if status not in ['STATUS_FINAL', 'STATUS_POSTPONED']:
                        competitions = event.get('competitions', [])
                        if competitions:
                            comp = competitions[0]
                            competitors = comp.get('competitors', [])
                            if len(competitors) >= 2:
                                away = competitors[0]
                                home = competitors[1]
                                
                                games.append({
                                    'team1_name': away.get('team', {}).get('abbreviation', ''),
                                    'team2_name': home.get('team', {}).get('abbreviation', ''),
                                    'match_date': event.get('date', '')[:10],
                                    'venue': home.get('team', {}).get('location', ''),
                                    'status': 'upcoming'
                                })
                
                return games[:limit]
        except Exception as e:
            logger.error(f"Error fetching upcoming games from ESPN: {e}")
            return []
        
        return []
    
    def get_top_players_by_stat(self, stat_type: str = 'points', limit: int = 10, season: str = None) -> List[Dict]:
        """
        Get top players by a specific statistic using ESPN API
        Aggregates player stats from recent games and calculates per-game averages
        stat_type: 'points', 'assists', 'rebounds', 'steals', 'blocks'
        limit: number of players to return
        season: season string (e.g., '2024-25'), defaults to current season
        """
        try:
            logger.info(f"Getting top {limit} players by {stat_type} using ESPN API (aggregating from recent games)")
            
            # Map stat types to our internal format
            stat_map = {
                'points': 'points',
                'assists': 'assists',
                'rebounds': 'rebounds',
                'steals': 'steals',
                'blocks': 'blocks',
                'score': 'points',
                'scoring': 'points'
            }
            
            stat_key = stat_map.get(stat_type.lower(), 'points')
            
            # Calculate date range - get last 60 days of current season
            today = date.today()
            if today.month >= 10:
                season_start = date(today.year, 10, 1)
            else:
                season_start = date(today.year - 1, 10, 1)
            
            # Use last 60 days or season start, whichever is more recent
            start_date = max(season_start, today - timedelta(days=60))
            
            # Get recent games
            days_back = (today - start_date).days
            recent_games = self.get_recent_games(days=days_back, limit=200)
            
            if not recent_games:
                logger.warning("No recent games found from ESPN for top players aggregation")
                return []
            
            # Aggregate player stats from all games
            player_stats_accum = {}  # {player_name: {points: [], rebounds: [], assists: [], steals: [], blocks: [], games: 0, team: ''}}
            
            # Process each game's boxscore
            for game in recent_games:
                try:
                    event_id = game.get('event_id')
                    # If no event_id, try to get it from match_date
                    if not event_id:
                        game_date = game.get('match_date', '')
                        if game_date:
                            # Try to get event_id from scoreboard for this date
                            try:
                                date_parts = game_date.split('-')
                                if len(date_parts) == 3:
                                    year, month, day = date_parts
                                    url = f"{self.BASE_URL}/scoreboard"
                                    params = {'dates': f"{year}{month}{day}"}
                                    response = self.session.get(url, params=params, timeout=5)
                                    if response.status_code == 200:
                                        data = response.json()
                                        team1 = game.get('team1_name', '').upper()
                                        team2 = game.get('team2_name', '').upper()
                                        for event in data.get('events', []):
                                            comps = event.get('competitions', [])
                                            if comps:
                                                comp = comps[0]
                                                competitors = comp.get('competitors', [])
                                                if len(competitors) >= 2:
                                                    away_abbrev = competitors[0].get('team', {}).get('abbreviation', '').upper()
                                                    home_abbrev = competitors[1].get('team', {}).get('abbreviation', '').upper()
                                                    if (away_abbrev == team1 and home_abbrev == team2) or \
                                                       (away_abbrev == team2 and home_abbrev == team1):
                                                        event_id = event.get('id', '')
                                                        break
                            except Exception:
                                pass
                    
                    if not event_id:
                        continue
                    
                    # Get boxscore/summary for this event
                    summary_url = f"{self.BASE_URL}/summary"
                    summary_params = {'event': event_id}
                    
                    summary_response = self.session.get(summary_url, params=summary_params, timeout=8)
                    if summary_response.status_code != 200:
                        continue
                    
                    summary_data = summary_response.json()
                    
                    # Extract player stats from boxscore
                    competitions = summary_data.get('boxscore', {}).get('competitions', [])
                    if not competitions:
                        competitions = summary_data.get('competitions', [])
                    
                    if not competitions:
                        continue
                    
                    competitors_info = competitions[0].get('competitors', [])
                    if len(competitors_info) < 2:
                        continue
                    
                    # Get boxscore players
                    boxscore = summary_data.get('boxscore', {})
                    players_list = boxscore.get('players', [])
                    
                    if not players_list:
                        statistics = boxscore.get('statistics', [])
                        if statistics:
                            for stat_group in statistics:
                                players_list.extend(stat_group.get('athletes', []))
                    
                    if not players_list and competitors_info:
                        for competitor in competitors_info:
                            roster = competitor.get('roster', {}).get('entries', [])
                            if roster:
                                players_list.extend(roster)
                    
                    # Process each player entry
                    for player_entry in players_list:
                        try:
                            player_info = player_entry.get('athlete', {})
                            if not player_info:
                                player_info = player_entry
                            
                            if not player_info:
                                continue
                            
                            full_name = player_info.get('fullName', '')
                            if not full_name:
                                continue
                            
                            # Extract stats
                            stats_array = player_entry.get('stats', [])
                            if not stats_array:
                                stats_array = player_entry.get('statistics', [])
                            
                            stat_dict = {}
                            for stat_item in stats_array:
                                if isinstance(stat_item, dict):
                                    stat_name = stat_item.get('name', '').lower()
                                    stat_value = stat_item.get('value', stat_item.get('displayValue', 0))
                                    try:
                                        stat_dict[stat_name] = float(stat_value) if stat_value else 0
                                    except:
                                        stat_dict[stat_name] = 0
                            
                            # Extract stat values
                            points = int(stat_dict.get('points', 0) or stat_dict.get('pts', 0) or 0)
                            rebounds = int(stat_dict.get('rebounds', 0) or stat_dict.get('reb', 0) or stat_dict.get('totalrebounds', 0) or 0)
                            assists = int(stat_dict.get('assists', 0) or stat_dict.get('ast', 0) or 0)
                            steals = int(stat_dict.get('steals', 0) or stat_dict.get('stl', 0) or 0)
                            blocks = int(stat_dict.get('blocks', 0) or stat_dict.get('blk', 0) or 0)
                            
                            # Get team abbreviation
                            team_id = player_entry.get('team', {}).get('id', '') if isinstance(player_entry.get('team'), dict) else None
                            team_abbrev = ''
                            if competitors_info:
                                for competitor in competitors_info:
                                    if str(competitor.get('team', {}).get('id', '')) == str(team_id):
                                        team_abbrev = competitor.get('team', {}).get('abbreviation', '')
                                        break
                            
                            # Initialize player if not exists
                            if full_name not in player_stats_accum:
                                player_stats_accum[full_name] = {
                                    'points': [],
                                    'rebounds': [],
                                    'assists': [],
                                    'steals': [],
                                    'blocks': [],
                                    'games': 0,
                                    'team': team_abbrev
                                }
                            
                            # Accumulate stats
                            player_stats_accum[full_name]['points'].append(points)
                            player_stats_accum[full_name]['rebounds'].append(rebounds)
                            player_stats_accum[full_name]['assists'].append(assists)
                            player_stats_accum[full_name]['steals'].append(steals)
                            player_stats_accum[full_name]['blocks'].append(blocks)
                            player_stats_accum[full_name]['games'] += 1
                            if not player_stats_accum[full_name]['team'] and team_abbrev:
                                player_stats_accum[full_name]['team'] = team_abbrev
                        
                        except Exception as pe:
                            logger.debug(f"Error processing player entry in boxscore: {pe}")
                            continue
                
                except Exception as e:
                    logger.debug(f"Error processing game boxscore: {e}")
                    continue
            
            if not player_stats_accum:
                logger.warning("No player stats accumulated from ESPN games")
                return []
            
            # Calculate per-game averages and filter by minimum games
            MIN_GAMES = 5  # Minimum games to qualify
            players_with_averages = []
            
            for player_name, stats in player_stats_accum.items():
                if stats['games'] < MIN_GAMES:
                    continue
                
                points_avg = sum(stats['points']) / len(stats['points']) if stats['points'] else 0
                rebounds_avg = sum(stats['rebounds']) / len(stats['rebounds']) if stats['rebounds'] else 0
                assists_avg = sum(stats['assists']) / len(stats['assists']) if stats['assists'] else 0
                steals_avg = sum(stats['steals']) / len(stats['steals']) if stats['steals'] else 0
                blocks_avg = sum(stats['blocks']) / len(stats['blocks']) if stats['blocks'] else 0
                
                # Get the stat value based on stat_type
                stat_value_map = {
                    'points': points_avg,
                    'assists': assists_avg,
                    'rebounds': rebounds_avg,
                    'steals': steals_avg,
                    'blocks': blocks_avg
                }
                
                stat_value = stat_value_map.get(stat_key, points_avg)
                
                players_with_averages.append({
                    'player_name': player_name,
                    'team': stats['team'],
                    'stat_value': round(stat_value, 2),
                    'stat_type': stat_type,
                    'games_played': stats['games'],
                    'points': round(points_avg, 2),
                    'rebounds': round(rebounds_avg, 2),
                    'assists': round(assists_avg, 2),
                    'steals': round(steals_avg, 2),
                    'blocks': round(blocks_avg, 2),
                    'field_goal_pct': 0.0,  # ESPN doesn't provide FG% in boxscore easily
                    'three_point_pct': 0.0,
                    'free_throw_pct': 0.0,
                    'minutes_per_game': 0.0
                })
            
            # Sort by stat_value descending and take top N
            players_with_averages.sort(key=lambda x: x['stat_value'], reverse=True)
            top_players = players_with_averages[:limit]
            
            logger.info(f"✓ Successfully retrieved {len(top_players)} top players by {stat_type} from ESPN API (aggregated from {len(recent_games)} games)")
            return top_players
            
        except Exception as e:
            logger.error(f"Error getting top players by {stat_type} from ESPN API: {e}", exc_info=True)
            return []

