"""
Schedule Agent - Handles upcoming match schedule queries with date awareness
Fetches real-time NBA schedules from external APIs
"""
import logging
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime, date, timedelta
from database.db_connection import db
from services.nba_api import NBAApiService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScheduleAgent:
    """Handles schedule queries"""
    
    def __init__(self):
        self.api_service = NBAApiService()
    
    def get_upcoming_matches(self, team_name: str = None, limit: int = 20):
        """Get upcoming matches for current season"""
        query = """
            SELECT 
                s.schedule_id,
                t1.team_name as team1_name,
                t2.team_name as team2_name,
                s.match_date,
                s.venue,
                s.status
            FROM schedule s
            JOIN teams t1 ON s.team1_id = t1.team_id
            JOIN teams t2 ON s.team2_id = t2.team_id
            WHERE s.status = 'upcoming'
            AND s.match_date >= CURRENT_DATE
        """
        params = []
        
        if team_name:
            query += " AND (LOWER(t1.team_name) LIKE %s OR LOWER(t2.team_name) LIKE %s)"
            params.extend([f"%{team_name.lower()}%", f"%{team_name.lower()}%"])
        
        query += " ORDER BY s.match_date ASC LIMIT %s"
        params.append(limit)
        
        try:
            results = db.execute_query(query, params)
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting upcoming matches: {e}")
            return []
    
    def get_team_upcoming_matches(self, team_name: str, limit: int = 10):
        """Get upcoming matches for a specific team"""
        return self.get_upcoming_matches(team_name=team_name, limit=limit)
    
    def get_next_match(self, team_name: str = None):
        """Get the next upcoming match"""
        matches = self.get_upcoming_matches(team_name=team_name, limit=1)
        return matches[0] if matches else None
    
    def extract_date(self, question: str):
        """Extract date from question (today, tomorrow, specific date, etc.)"""
        question_lower = question.lower()
        today = date.today()
        
        # Check for relative dates
        # Check "day after tomorrow" first to avoid matching "tomorrow" in it
        if 'day after tomorrow' in question_lower or 'day after' in question_lower:
            return today + timedelta(days=2)
        elif 'today' in question_lower:
            return today
        elif ('tomorrow' in question_lower or 'tommorow' in question_lower or 
              'tomorow' in question_lower or 'tomarrow' in question_lower or 
              'tommorrow' in question_lower):
            return today + timedelta(days=1)
        elif 'yesterday' in question_lower:
            return today - timedelta(days=1)
        elif 'next week' in question_lower:
            return today + timedelta(days=7)
        elif 'this week' in question_lower:
            return today
        
        # Try to extract specific date (MM/DD, MM-DD, or month day format)
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})',  # MM/DD or MM-DD
            r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})',  # Month Day
            r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})'  # YYYY-MM-DD
        ]
        
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        
        for pattern in date_patterns:
            match = re.search(pattern, question_lower)
            if match:
                try:
                    if len(match.groups()) == 2:
                        if match.group(1).isdigit():
                            # MM/DD format
                            month, day = int(match.group(1)), int(match.group(2))
                            return date(today.year, month, day)
                        else:
                            # Month Day format
                            month_name = match.group(1)
                            day = int(match.group(2))
                            month = months.get(month_name.lower(), today.month)
                            return date(today.year, month, day)
                    elif len(match.groups()) == 3:
                        # YYYY-MM-DD format
                        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                        return date(year, month, day)
                except ValueError:
                    continue
        
        return None
    
    def get_schedule_by_date(self, target_date: date, team_name: str = None):
        """Get schedule for a specific date"""
        query = """
            SELECT 
                s.schedule_id,
                t1.team_name as team1_name,
                t2.team_name as team2_name,
                s.match_date,
                s.venue,
                s.status
            FROM schedule s
            JOIN teams t1 ON s.team1_id = t1.team_id
            JOIN teams t2 ON s.team2_id = t2.team_id
            WHERE s.match_date = %s
            AND s.status = 'upcoming'
        """
        params = [target_date]
        
        if team_name:
            query += " AND (LOWER(t1.team_name) LIKE %s OR LOWER(t2.team_name) LIKE %s)"
            params.extend([f"%{team_name.lower()}%", f"%{team_name.lower()}%"])
        
        query += " ORDER BY s.match_date ASC"
        
        try:
            results = db.execute_query(query, params)
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting schedule by date: {e}")
            return []
    
    def process_query(self, question: str) -> dict:
        """Process a schedule query with date awareness - uses ESPN API directly"""
        question_lower = question.lower()
        
        # CRITICAL: Check for "tomorrow" FIRST before anything else
        # This ensures tomorrow queries are ALWAYS handled correctly
        # Check for ANY mention of "tomorrow" in the query - MUST be first check
        # Handle common typos: tommorow, tomorow, tomarrow, tommorrow
        has_tomorrow = (
            'tomorrow' in question_lower or 
            'tommorow' in question_lower or 
            'tomorow' in question_lower or
            'tomarrow' in question_lower or
            'tommorrow' in question_lower
        ) and 'day after' not in question_lower
        has_day_after = 'day after tomorrow' in question_lower or ('day after' in question_lower and 'tomorrow' not in question_lower and 'tommorow' not in question_lower)
        
        # CRITICAL: If query mentions "tomorrow" anywhere, handle it immediately and RETURN
        # This MUST prevent fallthrough to general handler
        if has_tomorrow or has_day_after:
            # Extract tomorrow date immediately
            if has_tomorrow:
                tomorrow_date = date.today() + timedelta(days=1)
                day_after_date = date.today() + timedelta(days=2)
            else:
                tomorrow_date = date.today() + timedelta(days=2)
                day_after_date = None  # User asked for day after, don't check further
            
            logger.info(f"CRITICAL: Detected tomorrow/day after query - handling immediately for date {tomorrow_date}")
            
            try:
                from services.direct_espn_fetcher import DirectESPNFetcher
                espn_fetcher = DirectESPNFetcher()
                games = espn_fetcher.get_games_for_date(tomorrow_date, include_completed=False, include_upcoming=True)
                
                # Filter to exact date
                target_date_str = tomorrow_date.strftime('%Y-%m-%d')
                filtered_games = []
                for game in games:
                    game_date = game.get('match_date', '')
                    game_date_part = game_date[:10] if len(game_date) >= 10 else game_date
                    if game_date_part == target_date_str:
                        filtered_games.append(game)
                
                # If user asked for tomorrow and no games found, check day after tomorrow
                if has_tomorrow and not filtered_games and day_after_date:
                    logger.info(f"CRITICAL: No games for tomorrow ({tomorrow_date}), checking day after tomorrow ({day_after_date})")
                    day_after_games = espn_fetcher.get_games_for_date(day_after_date, include_completed=False, include_upcoming=True)
                    
                    # Filter day after games to exact date
                    day_after_str = day_after_date.strftime('%Y-%m-%d')
                    filtered_day_after = []
                    for game in day_after_games:
                        game_date = game.get('match_date', '')
                        game_date_part = game_date[:10] if len(game_date) >= 10 else game_date
                        if game_date_part == day_after_str:
                            filtered_day_after.append(game)
                    
                    if filtered_day_after:
                        logger.info(f"CRITICAL: Found {len(filtered_day_after)} games for day after tomorrow ({day_after_date}), using those instead")
                        return {
                            'type': 'date_schedule',
                            'data': filtered_day_after,
                            'date': day_after_date.isoformat(),  # Use day_after_date, not tomorrow_date
                            'team': None,
                            'query': question,
                            'source': 'espn_api',
                            'is_next_available': True  # Flag to indicate we're showing next available games
                        }
                
                logger.info(f"CRITICAL: Returning {len(filtered_games)} games for {target_date_str}")
                # ALWAYS return here - never fall through
                result = {
                    'type': 'date_schedule',
                    'data': filtered_games,
                    'date': tomorrow_date.isoformat(),
                    'team': None,
                    'query': question,
                    'source': 'espn_api' if filtered_games else 'api_failed'
                }
                logger.info(f"CRITICAL: Returning immediately with type={result['type']}, games={len(filtered_games)}")
                return result
            except Exception as e:
                logger.error(f"CRITICAL: Error in immediate tomorrow handler: {e}")
                # ALWAYS return here - never fall through
                result = {
                    'type': 'date_schedule',
                    'data': [],
                    'date': tomorrow_date.isoformat(),
                    'team': None,
                    'query': question,
                    'source': 'api_failed',
                    'error': 'Unable to fetch schedule for the requested date'
                }
                logger.info(f"CRITICAL: Returning error result with type={result['type']}")
                return result
        
        # CRITICAL: If we reach here and query has "tomorrow", something went wrong
        # This should NEVER happen, but add as absolute safety net
        # Also check for common typos
        has_tomorrow_variant = (
            'tomorrow' in question_lower or 
            'tommorow' in question_lower or 
            'tomorow' in question_lower or
            'tomarrow' in question_lower or
            'tommorrow' in question_lower
        )
        if has_tomorrow_variant and 'day after' not in question_lower:
            logger.error(f"CRITICAL ERROR: Tomorrow query bypassed initial handler! Query: {question}")
            tomorrow_date = date.today() + timedelta(days=1)
            return {
                'type': 'date_schedule',
                'data': [],
                'date': tomorrow_date.isoformat(),
                'team': None,
                'query': question,
                'source': 'api_failed',
                'error': 'Unable to process tomorrow query'
            }
        
        # Extract team names
        teams = [
            'lakers', 'warriors', 'celtics', 'bucks', 'nuggets', 'suns', 'heat',
            'mavericks', 'clippers', '76ers', 'cavaliers', 'knicks', 'hawks',
            'thunder', 'timberwolves', 'kings', 'pelicans', 'grizzlies', 'raptors',
            'nets', 'bulls', 'pistons', 'pacers', 'hornets', 'magic', 'wizards',
            'trail blazers', 'jazz', 'rockets', 'spurs'
        ]
        
        found_teams = [team for team in teams if team in question_lower]
        
        # Extract number of games if specified (e.g., "next 10 lakers games")
        num_games = None
        import re
        if 'next' in question_lower:
            # Look for patterns like "next 10", "next 5", "next ten", etc.
            num_match = re.search(r'next\s+(\d+)\s+games?', question_lower)
            if num_match:
                num_games = int(num_match.group(1))
            else:
                # Check for word numbers
                if 'ten' in question_lower or '10' in question_lower:
                    num_match = re.search(r'next\s+(?:ten|10)', question_lower)
                    if num_match:
                        num_games = 10
                elif 'five' in question_lower or '5' in question_lower:
                    num_match = re.search(r'next\s+(?:five|5)', question_lower)
                    if num_match:
                        num_games = 5
                elif 'three' in question_lower or '3' in question_lower:
                    num_match = re.search(r'next\s+(?:three|3)', question_lower)
                    if num_match:
                        num_games = 3
        
        # Extract date
        target_date = self.extract_date(question)
        is_yesterday = 'yesterday' in question_lower
        is_today = 'today' in question_lower
        is_tomorrow = 'tomorrow' in question_lower and 'day after' not in question_lower
        is_day_after_tomorrow = 'day after tomorrow' in question_lower or 'day after' in question_lower
        
        # Use ESPN API as PRIMARY for today's games (most reliable and up-to-date)
        if is_today and target_date:
            try:
                from services.direct_espn_fetcher import DirectESPNFetcher
                espn_fetcher = DirectESPNFetcher()
                
                # Get today's games (both completed and upcoming)
                check_date = target_date
                games = espn_fetcher.get_games_for_date(check_date, include_completed=True, include_upcoming=True)
                
                if games:
                    logger.info(f"✓ Found {len(games)} games for today from ESPN API")
                    # Filter by team if specified
                    if found_teams and games:
                        team_filter = found_teams[0].lower()
                        team_abbrev_map = {
                            'lakers': 'LAL', 'warriors': 'GS', 'celtics': 'BOS', 'bucks': 'MIL',
                            'nuggets': 'DEN', 'suns': 'PHX', 'heat': 'MIA', 'mavericks': 'DAL',
                            'clippers': 'LAC', '76ers': 'PHI', 'cavaliers': 'CLE', 'knicks': 'NYK',
                            'hawks': 'ATL', 'thunder': 'OKC', 'timberwolves': 'MIN', 'kings': 'SAC',
                            'pelicans': 'NO', 'grizzlies': 'MEM', 'raptors': 'TOR', 'nets': 'BKN',
                            'bulls': 'CHI', 'pistons': 'DET', 'pacers': 'IND', 'hornets': 'CHA',
                            'magic': 'ORL', 'wizards': 'WSH', 'trail blazers': 'POR', 'jazz': 'UTAH',
                            'rockets': 'HOU', 'spurs': 'SAS'
                        }
                        abbrev = team_abbrev_map.get(team_filter, team_filter[:3].upper())
                        games = [
                            g for g in games 
                            if abbrev in g.get('team1_name', '') or abbrev in g.get('team2_name', '')
                        ]
                    
                    if games:
                        return {
                            'type': 'date_schedule',
                            'data': games,
                            'date': target_date.isoformat(),
                            'team': found_teams[0] if found_teams else None,
                            'query': question,
                            'source': 'espn_api'
                        }
            except Exception as e:
                logger.warning(f"ESPN API failed for today's games: {e}, trying Ball Don't Lie fallback")
                # Fallback to Ball Don't Lie API
                try:
                    from services.balldontlie_api import BallDontLieAPI
                    bdl_api = BallDontLieAPI()
                    games = bdl_api.get_games_for_today()
                    
                    if games:
                        logger.info(f"✓ Found {len(games)} games for today from Ball Don't Lie API (fallback)")
                        # Filter by team if specified
                        if found_teams and games:
                            team_filter = found_teams[0].lower()
                            team_abbrev_map = {
                                'lakers': 'LAL', 'warriors': 'GS', 'celtics': 'BOS', 'bucks': 'MIL',
                                'nuggets': 'DEN', 'suns': 'PHX', 'heat': 'MIA', 'mavericks': 'DAL',
                                'clippers': 'LAC', '76ers': 'PHI', 'cavaliers': 'CLE', 'knicks': 'NYK',
                                'hawks': 'ATL', 'thunder': 'OKC', 'timberwolves': 'MIN', 'kings': 'SAC',
                                'pelicans': 'NO', 'grizzlies': 'MEM', 'raptors': 'TOR', 'nets': 'BKN',
                                'bulls': 'CHI', 'pistons': 'DET', 'pacers': 'IND', 'hornets': 'CHA',
                                'magic': 'ORL', 'wizards': 'WSH', 'trail blazers': 'POR', 'jazz': 'UTAH',
                                'rockets': 'HOU', 'spurs': 'SAS'
                            }
                            abbrev = team_abbrev_map.get(team_filter, team_filter[:3].upper())
                            games = [
                                g for g in games 
                                if abbrev in g.get('team1_name', '') or abbrev in g.get('team2_name', '')
                            ]
                        
                        if games:
                            return {
                                'type': 'date_schedule',
                                'data': games,
                                'date': target_date.isoformat(),
                                'team': found_teams[0] if found_teams else None,
                                'query': question,
                                'source': 'balldontlie_api'
                            }
                except Exception as e2:
                    logger.warning(f"Ball Don't Lie API also failed for today's games: {e2}")
        
        # Use ESPN API as PRIMARY for yesterday's games (most reliable and up-to-date)
        if is_yesterday and target_date:
            try:
                from services.direct_espn_fetcher import DirectESPNFetcher
                espn_fetcher = DirectESPNFetcher()
                
                # Get yesterday's games (completed)
                check_date = target_date
                games = espn_fetcher.get_games_for_date(check_date, include_completed=True, include_upcoming=False)
                
                if games:
                    logger.info(f"✓ Found {len(games)} games for yesterday from ESPN API")
                    # Filter by team if specified
                    if found_teams and games:
                        team_filter = found_teams[0].lower()
                        team_abbrev_map = {
                            'lakers': 'LAL', 'warriors': 'GS', 'celtics': 'BOS', 'bucks': 'MIL',
                            'nuggets': 'DEN', 'suns': 'PHX', 'heat': 'MIA', 'mavericks': 'DAL',
                            'clippers': 'LAC', '76ers': 'PHI', 'cavaliers': 'CLE', 'knicks': 'NYK',
                            'hawks': 'ATL', 'thunder': 'OKC', 'timberwolves': 'MIN', 'kings': 'SAC',
                            'pelicans': 'NO', 'grizzlies': 'MEM', 'raptors': 'TOR', 'nets': 'BKN',
                            'bulls': 'CHI', 'pistons': 'DET', 'pacers': 'IND', 'hornets': 'CHA',
                            'magic': 'ORL', 'wizards': 'WSH', 'trail blazers': 'POR', 'jazz': 'UTAH',
                            'rockets': 'HOU', 'spurs': 'SAS'
                        }
                        abbrev = team_abbrev_map.get(team_filter, team_filter[:3].upper())
                        games = [
                            g for g in games 
                            if abbrev in g.get('team1_name', '') or abbrev in g.get('team2_name', '')
                        ]
                    
                    if games:
                        return {
                            'type': 'date_schedule',
                            'data': games,
                            'date': target_date.isoformat(),
                            'team': found_teams[0] if found_teams else None,
                            'query': question,
                            'source': 'espn_api'
                        }
            except Exception as e:
                logger.warning(f"ESPN API failed for yesterday's games: {e}, trying Ball Don't Lie fallback")
                # Fallback to Ball Don't Lie API
                try:
                    from services.balldontlie_api import BallDontLieAPI
                    bdl_api = BallDontLieAPI()
                    games = bdl_api.get_games_for_yesterday()
                    
                    if games:
                        logger.info(f"✓ Found {len(games)} games for yesterday from Ball Don't Lie API (fallback)")
                        # Filter by team if specified
                        if found_teams and games:
                            team_filter = found_teams[0].lower()
                            team_abbrev_map = {
                                'lakers': 'LAL', 'warriors': 'GS', 'celtics': 'BOS', 'bucks': 'MIL',
                                'nuggets': 'DEN', 'suns': 'PHX', 'heat': 'MIA', 'mavericks': 'DAL',
                                'clippers': 'LAC', '76ers': 'PHI', 'cavaliers': 'CLE', 'knicks': 'NYK',
                                'hawks': 'ATL', 'thunder': 'OKC', 'timberwolves': 'MIN', 'kings': 'SAC',
                                'pelicans': 'NO', 'grizzlies': 'MEM', 'raptors': 'TOR', 'nets': 'BKN',
                                'bulls': 'CHI', 'pistons': 'DET', 'pacers': 'IND', 'hornets': 'CHA',
                                'magic': 'ORL', 'wizards': 'WSH', 'trail blazers': 'POR', 'jazz': 'UTAH',
                                'rockets': 'HOU', 'spurs': 'SAS'
                            }
                            abbrev = team_abbrev_map.get(team_filter, team_filter[:3].upper())
                            games = [
                                g for g in games 
                                if abbrev in g.get('team1_name', '') or abbrev in g.get('team2_name', '')
                            ]
                        
                        if games:
                            return {
                                'type': 'date_schedule',
                                'data': games,
                                'date': target_date.isoformat(),
                                'team': found_teams[0] if found_teams else None,
                                'query': question,
                                'source': 'balldontlie_api'
                            }
                except Exception as e2:
                    logger.warning(f"Ball Don't Lie API also failed for yesterday's games: {e2}")
        
        # Use ESPN API as PRIMARY for tomorrow's games (most reliable and up-to-date)
        # Return ONLY games for the exact date requested (tomorrow or day after tomorrow)
        # If tomorrow has no games and user asked for tomorrow, check day after tomorrow
        # Check if question contains "tomorrow" - this should ALWAYS be handled here
        # Handle common typos
        has_tomorrow_in_query = (
            'tomorrow' in question_lower or 
            'tommorow' in question_lower or 
            'tomorow' in question_lower or
            'tomarrow' in question_lower or
            'tommorrow' in question_lower
        ) and 'day after' not in question_lower
        has_day_after = 'day after tomorrow' in question_lower or ('day after' in question_lower and 'tomorrow' not in question_lower and 'tommorow' not in question_lower)
        
        # If query mentions tomorrow/day after, handle it here (even if target_date extraction failed)
        if is_tomorrow or has_tomorrow_in_query or is_day_after_tomorrow or has_day_after:
            # If target_date is None but query has "tomorrow", extract it
            if not target_date:
                if has_tomorrow_in_query or is_tomorrow:
                    target_date = date.today() + timedelta(days=1)
                    logger.info(f"Extracted tomorrow date: {target_date}")
                elif has_day_after or is_day_after_tomorrow:
                    target_date = date.today() + timedelta(days=2)
                    logger.info(f"Extracted day after tomorrow date: {target_date}")
            
            if target_date:
                check_date = target_date
                games = []
                
                # Try ESPN API first
                try:
                    from services.direct_espn_fetcher import DirectESPNFetcher
                    espn_fetcher = DirectESPNFetcher()
                    
                    # Get games for the exact date requested (tomorrow or day after tomorrow)
                    games = espn_fetcher.get_games_for_date(check_date, include_completed=False, include_upcoming=True)
                    logger.info(f"✓ Found {len(games)} games for {check_date} from ESPN API")
                except Exception as e:
                    logger.warning(f"ESPN API failed for {check_date}: {e}, trying Ball Don't Lie fallback")
                    # Fallback to Ball Don't Lie API
                    try:
                        from services.balldontlie_api import BallDontLieAPI
                        bdl_api = BallDontLieAPI()
                        games = bdl_api.get_games_for_date(check_date)
                        logger.info(f"✓ Found {len(games)} games for {check_date} from Ball Don't Lie API")
                    except Exception as e2:
                        logger.warning(f"Ball Don't Lie API also failed for {check_date}: {e2}")
                        games = []
                
                # Filter by team if specified
                if found_teams and games:
                    team_filter = found_teams[0].lower()
                    team_abbrev_map = {
                        'lakers': 'LAL', 'warriors': 'GS', 'celtics': 'BOS', 'bucks': 'MIL',
                        'nuggets': 'DEN', 'suns': 'PHX', 'heat': 'MIA', 'mavericks': 'DAL',
                        'clippers': 'LAC', '76ers': 'PHI', 'cavaliers': 'CLE', 'knicks': 'NYK',
                        'hawks': 'ATL', 'thunder': 'OKC', 'timberwolves': 'MIN', 'kings': 'SAC',
                        'pelicans': 'NO', 'grizzlies': 'MEM', 'raptors': 'TOR', 'nets': 'BKN',
                        'bulls': 'CHI', 'pistons': 'DET', 'pacers': 'IND', 'hornets': 'CHA',
                        'magic': 'ORL', 'wizards': 'WSH', 'trail blazers': 'POR', 'jazz': 'UTAH',
                        'rockets': 'HOU', 'spurs': 'SAS'
                    }
                    abbrev = team_abbrev_map.get(team_filter, team_filter[:3].upper())
                    games = [
                        g for g in games 
                        if abbrev in g.get('team1_name', '') or abbrev in g.get('team2_name', '')
                    ]
                
                # IMPORTANT: Do NOT check day after tomorrow if user asked for tomorrow
                # User explicitly asked for tomorrow, so return only tomorrow's games (even if empty)
                # Only return games that match the exact requested date
                if games:
                    # Double-check: filter games to ensure they match the exact target_date
                    target_date_str = check_date.strftime('%Y-%m-%d')
                    original_count = len(games)
                    filtered_games = []
                    for game in games:
                        game_date = game.get('match_date', '')
                        # Extract date part (first 10 characters: YYYY-MM-DD)
                        game_date_part = game_date[:10] if len(game_date) >= 10 else game_date
                        if game_date_part == target_date_str:
                            filtered_games.append(game)
                        else:
                            logger.debug(f"Filtering out game from {game_date_part} (requested {target_date_str})")
                    games = filtered_games
                    if original_count != len(filtered_games):
                        logger.info(f"Filtered {original_count} games to {len(filtered_games)} games matching exact date {target_date_str}")
                
                # ALWAYS return for tomorrow/day after tomorrow queries, even if empty
                return {
                    'type': 'date_schedule',
                    'data': games,
                    'date': check_date.isoformat(),
                    'team': found_teams[0] if found_teams else None,
                    'query': question,
                    'source': 'espn_api' if games else 'api_failed'
                }
        
        # Skip general handler if this was a tomorrow/day after tomorrow query (already handled above)
        # Also check if question contains "tomorrow" even if not explicitly detected
        has_tomorrow_in_query = 'tomorrow' in question_lower and 'day after' not in question_lower
        has_day_after = 'day after tomorrow' in question_lower or 'day after' in question_lower
        
        if (is_tomorrow or has_tomorrow_in_query or is_day_after_tomorrow or has_day_after) and target_date:
            # Should have returned above, but if we reach here, return empty
            return {
                'type': 'date_schedule',
                'data': [],
                'date': target_date.isoformat(),
                'team': found_teams[0] if found_teams else None,
                'query': question,
                'source': 'api_failed',
                'error': 'Unable to fetch schedule for the requested date'
            }
        
        # Use ESPN API directly for other dates (PRIMARY for non-today/yesterday/tomorrow queries)
        # CRITICAL: Double-check that this is NOT a tomorrow query before proceeding
        # This is a safety net in case the tomorrow handler above didn't catch it
        # Handle common typos
        has_tomorrow_final_check = (
            'tomorrow' in question_lower or 
            'tommorow' in question_lower or 
            'tomorow' in question_lower or
            'tomarrow' in question_lower or
            'tommorrow' in question_lower
        ) and 'day after' not in question_lower
        has_day_after_final_check = 'day after tomorrow' in question_lower or ('day after' in question_lower and 'tomorrow' not in question_lower and 'tommorow' not in question_lower)
        
        if has_tomorrow_final_check or has_day_after_final_check:
            # This should have been handled above, but if we reach here, handle it now
            if not target_date:
                if has_tomorrow_final_check:
                    target_date = date.today() + timedelta(days=1)
                elif has_day_after_final_check:
                    target_date = date.today() + timedelta(days=2)
            
            if target_date:
                try:
                    from services.direct_espn_fetcher import DirectESPNFetcher
                    espn_fetcher = DirectESPNFetcher()
                    games = espn_fetcher.get_games_for_date(target_date, include_completed=False, include_upcoming=True)
                    
                    # Filter games to exact date
                    target_date_str = target_date.strftime('%Y-%m-%d')
                    filtered_games = [g for g in games if g.get('match_date', '')[:10] == target_date_str]
                    
                    return {
                        'type': 'date_schedule',
                        'data': filtered_games,
                        'date': target_date.isoformat(),
                        'team': found_teams[0] if found_teams else None,
                        'query': question,
                        'source': 'espn_api' if filtered_games else 'api_failed'
                    }
                except Exception as e:
                    logger.warning(f"Error in final tomorrow handler: {e}")
                    return {
                        'type': 'date_schedule',
                        'data': [],
                        'date': target_date.isoformat(),
                        'team': found_teams[0] if found_teams else None,
                        'query': question,
                        'source': 'api_failed',
                        'error': 'Unable to fetch schedule for the requested date'
                    }
        
        try:
            from services.direct_espn_fetcher import DirectESPNFetcher
            espn_fetcher = DirectESPNFetcher()
            
            # Determine date range and what to include
            if target_date:
                # Specific date - determine if past or future
                days_diff = (target_date - date.today()).days
                if days_diff < 0:
                    # Past date - get completed games
                    games = espn_fetcher.get_games_for_date(target_date, include_completed=True, include_upcoming=False)
                else:
                    # Future date - get upcoming games
                    games = espn_fetcher.get_games_for_date(target_date, include_completed=False, include_upcoming=True)
            else:
                # No specific date - check if query mentions "tomorrow" or "day after tomorrow"
                # If so, don't get all games - only get tomorrow's games
                if 'tomorrow' in question_lower and 'day after' not in question_lower:
                    # User asked for tomorrow but date extraction failed - use tomorrow's date
                    tomorrow_date = date.today() + timedelta(days=1)
                    games = espn_fetcher.get_games_for_date(tomorrow_date, include_completed=False, include_upcoming=True)
                    target_date = tomorrow_date  # Set target_date for proper formatting
                    logger.info(f"Query mentions 'tomorrow' - getting games for {tomorrow_date} only")
                elif 'day after tomorrow' in question_lower or 'day after' in question_lower:
                    # User asked for day after tomorrow
                    day_after = date.today() + timedelta(days=2)
                    games = espn_fetcher.get_games_for_date(day_after, include_completed=False, include_upcoming=True)
                    target_date = day_after
                    logger.info(f"Query mentions 'day after tomorrow' - getting games for {day_after} only")
                else:
                    # No specific date mentioned - get upcoming games
                    # If number of games specified, calculate days needed (roughly 2-3 games per day)
                    if num_games is not None:
                        days_ahead = max(30, num_games * 2)  # Get enough days to find N games
                    else:
                        days_ahead = 30  # Default: next month
                    games = espn_fetcher.get_games_for_date_range(date.today(), date.today() + timedelta(days=days_ahead))
            
            # Filter by team if specified
            if found_teams and games:
                team_filter = found_teams[0].lower()
                team_abbrev_map = {
                    'lakers': 'LAL', 'warriors': 'GS', 'celtics': 'BOS', 'bucks': 'MIL',
                    'nuggets': 'DEN', 'suns': 'PHX', 'heat': 'MIA', 'mavericks': 'DAL',
                    'clippers': 'LAC', '76ers': 'PHI', 'cavaliers': 'CLE', 'knicks': 'NYK',
                    'hawks': 'ATL', 'thunder': 'OKC', 'timberwolves': 'MIN', 'kings': 'SAC',
                    'pelicans': 'NO', 'grizzlies': 'MEM', 'raptors': 'TOR', 'nets': 'BKN',
                    'bulls': 'CHI', 'pistons': 'DET', 'pacers': 'IND', 'hornets': 'CHA',
                    'magic': 'ORL', 'wizards': 'WSH', 'trail blazers': 'POR', 'jazz': 'UTAH',
                    'rockets': 'HOU', 'spurs': 'SAS'
                }
                abbrev = team_abbrev_map.get(team_filter, team_filter[:3].upper())
                games = [
                    g for g in games 
                    if abbrev in g.get('team1_name', '') or abbrev in g.get('team2_name', '')
                ]
            
            # Sort games by date (ascending) and apply limit if specified
            if games:
                # Sort by date to get chronological order
                games.sort(key=lambda x: x.get('match_date', ''))
                
                # Apply number limit if specified
                if num_games is not None:
                    games = games[:num_games]
                
                logger.info(f"✓ Found {len(games)} games from ESPN API for query: {question}")
                
                # Determine return type - use 'date_schedule' if target_date is set OR if query mentions tomorrow/day after
                # Handle common typos
                has_tomorrow_mention = (
                    'tomorrow' in question_lower or 
                    'tommorow' in question_lower or 
                    'tomorow' in question_lower or
                    'tomarrow' in question_lower or
                    'tommorrow' in question_lower
                ) and 'day after' not in question_lower
                has_day_after_mention = 'day after tomorrow' in question_lower or ('day after' in question_lower and 'tomorrow' not in question_lower and 'tommorow' not in question_lower)
                
                if target_date or has_tomorrow_mention or has_day_after_mention:
                    return_type = 'date_schedule'
                    # Ensure target_date is set if query mentions tomorrow
                    if not target_date and has_tomorrow_mention:
                        target_date = date.today() + timedelta(days=1)
                    elif not target_date and has_day_after_mention:
                        target_date = date.today() + timedelta(days=2)
                    
                    # CRITICAL: Filter games to only include those matching the exact target_date
                    if target_date:
                        target_date_str = target_date.strftime('%Y-%m-%d')
                        original_count = len(games)
                        filtered_games = []
                        for game in games:
                            game_date = game.get('match_date', '')
                            # Extract date part (first 10 characters: YYYY-MM-DD)
                            game_date_part = game_date[:10] if len(game_date) >= 10 else game_date
                            if game_date_part == target_date_str:
                                filtered_games.append(game)
                        games = filtered_games
                        if original_count != len(filtered_games):
                            logger.info(f"Filtered {original_count} games to {len(filtered_games)} games matching exact date {target_date_str}")
                else:
                    return_type = 'schedule'
                
                return {
                    'type': return_type,
                    'data': games,
                    'date': target_date.isoformat() if target_date else None,
                    'team': found_teams[0] if found_teams else None,
                    'query': question,
                    'source': 'espn_api',
                    'num_games': num_games if num_games else len(games)
                }
        except Exception as e:
            logger.warning(f"ESPN API fetch failed: {e}, trying fallback")
        
        # Fallback to NBAApiService (SECONDARY)
        # IMPORTANT: Skip fallback if query mentions tomorrow/day after - already handled above
        has_tomorrow_check = 'tomorrow' in question_lower and 'day after' not in question_lower
        has_day_after_check = 'day after tomorrow' in question_lower or 'day after' in question_lower
        
        if not (has_tomorrow_check or has_day_after_check or is_tomorrow or is_day_after_tomorrow):
            try:
                # Extract date to determine days ahead
                days_ahead = 7  # Default: next week
                
                if target_date:
                    days_diff = (target_date - date.today()).days
                    if 0 <= days_diff <= 30:
                        days_ahead = days_diff + 1
                    elif days_diff < 0:
                        # Past date - use recent games
                        days_ahead = abs(days_diff) + 1
                
                team_name = None
                if found_teams:
                    team_name = found_teams[0].title()
                
                # Use extracted number or default
                if num_games is not None:
                    limit = num_games
                elif 'next' in question_lower and found_teams:
                    limit = 1
                else:
                    limit = 20
                
                # Get games from API service
                if is_yesterday or (target_date and target_date < date.today()):
                    # Get recent games (completed)
                    api_matches = self.api_service.get_recent_games(
                        days=days_ahead if days_ahead > 0 else 1,
                        team_name=team_name,
                        limit=limit
                    )
                else:
                    # Get upcoming games
                    api_matches = self.api_service.get_upcoming_games(
                        days=days_ahead,
                        team_name=team_name,
                        limit=limit
                    )
                
                if api_matches:
                    # Filter by specific date if mentioned
                    if target_date:
                        date_str = target_date.isoformat()
                        api_matches = [m for m in api_matches if m.get('match_date', '')[:10] == date_str]
                    
                    if api_matches:
                        logger.info(f"✓ Found {len(api_matches)} games from NBA API for query: {question}")
                        return {
                            'type': 'schedule' if not target_date else 'date_schedule',
                            'data': api_matches,
                            'date': target_date.isoformat() if target_date else None,
                            'team': found_teams[0] if found_teams else None,
                            'query': question,
                            'source': 'nba_api'
                        }
            except Exception as e:
                logger.warning(f"Fallback API fetch failed: {e}")
        
        # Return empty with helpful message if all APIs fail
        logger.info(f"Schedule API returned no data for query: {question}")
        return {
            'type': 'schedule',
            'data': [],
            'query': question,
            'source': 'api_failed',
            'error': 'Unable to fetch schedule from API'
        }
