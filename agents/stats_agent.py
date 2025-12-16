"""
Stats Agent - Handles match statistics queries
Fetches real-time NBA data from external APIs
Supports date-based queries (yesterday, today, specific dates)
"""
import logging
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_connection import db
from services.nba_api import NBAApiService
from datetime import date, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StatsAgent:
    """Handles match statistics and results queries"""
    
    def __init__(self):
        self.api_service = NBAApiService()
    
    def _normalize_team_name(self, team_name: str) -> str:
        """Normalize team name variations to standard form"""
        team_name_lower = team_name.lower().strip()
        
        # Map full names and variations to standard names
        normalization_map = {
            'golden state': 'warriors', 'gsw': 'warriors', 'golden state warriors': 'warriors',
            'los angeles lakers': 'lakers', 'la lakers': 'lakers',
            'los angeles clippers': 'clippers', 'la clippers': 'clippers',
            'boston': 'celtics', 'boston celtics': 'celtics',
            'milwaukee': 'bucks', 'milwaukee bucks': 'bucks',
            'denver': 'nuggets', 'denver nuggets': 'nuggets',
            'phoenix': 'suns', 'phoenix suns': 'suns',
            'miami': 'heat', 'miami heat': 'heat',
            'dallas': 'mavericks', 'mavs': 'mavericks', 'dallas mavericks': 'mavericks',
            'philadelphia': '76ers', 'sixers': '76ers', 'philadelphia 76ers': '76ers',
            'cleveland': 'cavaliers', 'cavs': 'cavaliers', 'cleveland cavaliers': 'cavaliers',
            'new york': 'knicks', 'new york knicks': 'knicks',
            'atlanta': 'hawks', 'atlanta hawks': 'hawks',
            'oklahoma': 'thunder', 'okc': 'thunder', 'oklahoma city thunder': 'thunder',
            'minnesota': 'timberwolves', 'minnesota timberwolves': 'timberwolves',
            'sacramento': 'kings', 'sacramento kings': 'kings',
            'new orleans': 'pelicans', 'new orleans pelicans': 'pelicans',
            'memphis': 'grizzlies', 'memphis grizzlies': 'grizzlies',
            'toronto': 'raptors', 'toronto raptors': 'raptors',
            'brooklyn': 'nets', 'brooklyn nets': 'nets',
            'chicago': 'bulls', 'chicago bulls': 'bulls',
            'detroit': 'pistons', 'detroit pistons': 'pistons',
            'indiana': 'pacers', 'indiana pacers': 'pacers',
            'charlotte': 'hornets', 'charlotte hornets': 'hornets',
            'orlando': 'magic', 'orlando magic': 'magic',
            'washington': 'wizards', 'washington wizards': 'wizards',
            'portland': 'trail blazers', 'blazers': 'trail blazers', 'portland trail blazers': 'trail blazers',
            'utah': 'jazz', 'utah jazz': 'jazz',
            'houston': 'rockets', 'houston rockets': 'rockets',
            'san antonio': 'spurs', 'san antonio spurs': 'spurs'
        }
        
        # Try exact match first
        if team_name_lower in normalization_map:
            return normalization_map[team_name_lower]
        
        # Try partial match (check if any key is contained in the team name)
        for key, normalized in normalization_map.items():
            if key in team_name_lower or team_name_lower in key:
                return normalized
        
        # Return as-is if no normalization found (already in standard form)
        return team_name_lower
    
    def get_match_result(self, team1_name: str = None, team2_name: str = None, 
                        match_date: str = None, limit: int = 5):
        """Get match results from current season"""
        query = """
            SELECT 
                m.match_id,
                t1.team_name as team1_name,
                t2.team_name as team2_name,
                m.team1_score,
                m.team2_score,
                m.match_date,
                m.venue,
                CASE 
                    WHEN m.team1_score > m.team2_score THEN t1.team_name
                    ELSE t2.team_name
                END as winner
            FROM matches m
            JOIN teams t1 ON m.team1_id = t1.team_id
            JOIN teams t2 ON m.team2_id = t2.team_id
            WHERE m.match_date >= DATE '2023-10-01'
            AND m.match_date <= CURRENT_DATE
        """
        params = []
        
        if team1_name:
            query += " AND (LOWER(t1.team_name) LIKE %s OR LOWER(t2.team_name) LIKE %s)"
            params.extend([f"%{team1_name.lower()}%", f"%{team1_name.lower()}%"])
        
        if team2_name:
            query += " AND (LOWER(t1.team_name) LIKE %s OR LOWER(t2.team_name) LIKE %s)"
            params.extend([f"%{team2_name.lower()}%", f"%{team2_name.lower()}%"])
        
        if match_date:
            query += " AND m.match_date = %s"
            params.append(match_date)
        
        query += " ORDER BY m.match_date DESC LIMIT %s"
        params.append(limit)
        
        try:
            results = db.execute_query(query, params)
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting match results: {e}")
            return []
    
    def get_recent_matches(self, limit: int = 10):
        """Get most recent matches from current season"""
        query = """
            SELECT 
                m.match_id,
                t1.team_name as team1_name,
                t2.team_name as team2_name,
                m.team1_score,
                m.team2_score,
                m.match_date,
                m.venue,
                CASE 
                    WHEN m.team1_score > m.team2_score THEN t1.team_name
                    ELSE t2.team_name
                END as winner
            FROM matches m
            JOIN teams t1 ON m.team1_id = t1.team_id
            JOIN teams t2 ON m.team2_id = t2.team_id
            WHERE m.match_date >= DATE '2023-10-01'
            AND m.match_date <= CURRENT_DATE
            ORDER BY m.match_date DESC
            LIMIT %s
        """
        
        try:
            results = db.execute_query(query, [limit])
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting recent matches: {e}")
            return []
    
    def get_team_match_history(self, team_name: str, limit: int = 10):
        """Get match history for a specific team from current season"""
        query = """
            SELECT 
                m.match_id,
                t1.team_name as team1_name,
                t2.team_name as team2_name,
                m.team1_score,
                m.team2_score,
                m.match_date,
                m.venue,
                CASE 
                    WHEN m.team1_score > m.team2_score THEN t1.team_name
                    ELSE t2.team_name
                END as winner,
                CASE 
                    WHEN (m.team1_id = t.team_id AND m.team1_score > m.team2_score) 
                         OR (m.team2_id = t.team_id AND m.team2_score > m.team1_score)
                    THEN 'W'
                    ELSE 'L'
                END as result
            FROM matches m
            JOIN teams t1 ON m.team1_id = t1.team_id
            JOIN teams t2 ON m.team2_id = t2.team_id
            JOIN teams t ON (t.team_id = m.team1_id OR t.team_id = m.team2_id)
            WHERE LOWER(t.team_name) LIKE %s
            AND m.match_date >= DATE '2023-10-01'
            AND m.match_date <= CURRENT_DATE
            ORDER BY m.match_date DESC
            LIMIT %s
        """
        
        try:
            results = db.execute_query(query, [f"%{team_name.lower()}%", limit])
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting team match history: {e}")
            return []
    
    def extract_date(self, question: str):
        """Extract date from question (today, yesterday, specific date, etc.)"""
        question_lower = question.lower()
        today = date.today()
        
        # Check for relative dates
        if 'yesterday' in question_lower or 'last night' in question_lower:
            return today - timedelta(days=1)
        elif 'today' in question_lower:
            return today
        elif 'last week' in question_lower:
            return today - timedelta(days=7)
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
    
    def get_matches_by_date(self, target_date: date, team_name: str = None, limit: int = 20):
        """Get match results for a specific date"""
        # Define current season boundaries (2025-2026 season)
        season_start = date(2025, 10, 1)  # 2025-2026 season starts Oct 1, 2025
        season_end = date(2026, 6, 30)    # 2025-2026 season ends Jun 30, 2026

        query = """
            SELECT 
                m.match_id,
                t1.team_name as team1_name,
                t2.team_name as team2_name,
                m.team1_score,
                m.team2_score,
                m.match_date,
                m.venue,
                CASE 
                    WHEN m.team1_score > m.team2_score THEN t1.team_name
                    ELSE t2.team_name
                END as winner
            FROM matches m
            JOIN teams t1 ON m.team1_id = t1.team_id
            JOIN teams t2 ON m.team2_id = t2.team_id
            WHERE m.match_date = %s
            AND m.match_date >= %s AND m.match_date <= CURRENT_DATE
        """
        params = [target_date, season_start]
        
        if team_name:
            query += " AND (LOWER(t1.team_name) LIKE %s OR LOWER(t2.team_name) LIKE %s)"
            params.extend([f"%{team_name.lower()}%", f"%{team_name.lower()}%"])
        
        query += " ORDER BY m.match_date DESC LIMIT %s"
        params.append(limit)
        
        try:
            results = db.execute_query(query, params)
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting matches by date: {e}")
            return []
    
    def process_query(self, question: str) -> dict:
        """Process a match stats query with date awareness - uses real-time API
        
        Uses ESPN/NBA APIs to fetch latest game data from current date (2025-12-11).
        All date filtering is based on today's date, not outdated database dates.
        """
        question_lower = question.lower()
        today = date.today()
        logger.info(f"Processing stats query as of today: {today}")
        
        # Check for "result of [team] last/previous game" queries with various synonyms
        is_result_query = (
            any(phrase in question_lower for phrase in [
                'result of', 'result', 'score', 'final score', 'outcome', 'game result', 
                'match result', 'game score', 'final', 'what was', 'what is'
            ]) and any(phrase in question_lower for phrase in [
                'last game', 'previous game', 'most recent game', 'latest game', 
                'last matchup', 'previous matchup', 'last match', 'previous match',
                'yesterday', 'yesterday game', 'yesterday matchup'
            ])
        ) or (
            # Also handle queries like "bucks last game result?" or "lakers previous game?"
            any(team in question_lower for team in [
                'lakers', 'warriors', 'celtics', 'bucks', 'nuggets', 'suns', 'heat',
                'mavericks', 'clippers', '76ers', 'cavaliers', 'knicks', 'hawks',
                'thunder', 'timberwolves', 'kings', 'pelicans', 'grizzlies', 'raptors',
                'nets', 'bulls', 'pistons', 'pacers', 'hornets', 'magic', 'wizards',
                'trail blazers', 'jazz', 'rockets', 'spurs'
            ]) and any(phrase in question_lower for phrase in [
                'last game', 'previous game', 'most recent game', 'latest game',
                'last matchup', 'previous matchup', 'yesterday', 'yesterday game'
            ]) and any(phrase in question_lower for phrase in [
                'result', 'score', 'outcome', 'final'
            ])
        )
        
        # Check for "last N games" or "recent games" queries (multiple game results)
        is_multiple_games_query = (
            any(phrase in question_lower for phrase in [
                'last', 'recent', 'previous', 'past'
            ]) and any(phrase in question_lower for phrase in [
                'games', 'game results', 'results', 'matches', 'matchups'
            ]) and (
                any(num in question_lower for num in ['5', 'five', '10', 'ten', '3', 'three', '4', 'four']) or
                'show me' in question_lower or 'give me' in question_lower
            )
        )
        
        # Extract number of games if specified
        num_games = 5  # default
        if is_multiple_games_query:
            import re
            num_match = re.search(r'(\d+)\s*games?', question_lower)
            if num_match:
                num_games = int(num_match.group(1))
            elif 'five' in question_lower or '5' in question_lower:
                num_games = 5
            elif 'ten' in question_lower or '10' in question_lower:
                num_games = 10
            elif 'three' in question_lower or '3' in question_lower:
                num_games = 3
            elif 'four' in question_lower or '4' in question_lower:
                num_games = 4
        
        # Check for "win by" or "won by" queries (point differential for wins)
        is_win_by_query = any(phrase in question_lower for phrase in [
            'win by', 'won by', 'winning by', 'defeated by', 'beat by'
        ]) and ('points' in question_lower or 'point' in question_lower) and ('win' in question_lower or 'won' in question_lower) and not is_result_query and not is_multiple_games_query
        
        # Check for "lose by" or "lost by" queries (point differential for losses)
        is_lose_by_query = any(phrase in question_lower for phrase in [
            'lose by', 'lost by', 'losing by'
        ]) and ('points' in question_lower or 'point' in question_lower) and not is_win_by_query and not is_result_query and not is_multiple_games_query
        
        # Check for "did [team] win" queries
        is_win_query = any(phrase in question_lower for phrase in [
            'did', 'win', 'won', 'lose', 'lost'
        ]) and ('most recent' in question_lower or 'last game' in question_lower or 'latest game' in question_lower) and not is_lose_by_query and not is_win_by_query and not is_result_query and not is_multiple_games_query
        
        # Try NBA API Library first for "result of [team] last game" queries
        if is_result_query:
            # Extract team names
            teams = [
                'lakers', 'warriors', 'celtics', 'bucks', 'nuggets', 'suns', 'heat',
                'mavericks', 'clippers', '76ers', 'cavaliers', 'knicks', 'hawks',
                'thunder', 'timberwolves', 'kings', 'pelicans', 'grizzlies', 'raptors',
                'nets', 'bulls', 'pistons', 'pacers', 'hornets', 'magic', 'wizards',
                'trail blazers', 'jazz', 'rockets', 'spurs'
            ]
            
            found_teams = [team for team in teams if team in question_lower]
            
            # If no team found but query has result keywords, try to extract from context
            # For queries like "bucks last game result?" the team is at the start
            if not found_teams:
                # Check if query starts with a team name
                words = question_lower.split()
                for word in words[:3]:  # Check first 3 words
                    for team in teams:
                        if team in word or word in team:
                            found_teams = [team]
                            break
                    if found_teams:
                        break
            
            if found_teams:
                try:
                    from services.nba_api_library import NBAAPILibrary
                    nba_api_lib = NBAAPILibrary()
                    
                    team_name = found_teams[0]
                    logger.info(f"Trying NBA API Library for {team_name} last game result")
                    game_result = nba_api_lib.get_team_most_recent_game_result(team_name)
                    
                    if game_result:
                        logger.info(f"✓ Got game result from NBA API for {team_name}")
                        
                        # Check if query asks for yesterday's game specifically
                        is_yesterday_query = 'yesterday' in question_lower
                        game_date_str = game_result.get('game_date', '')
                        
                        # If asking for yesterday, verify the game was yesterday
                        if is_yesterday_query:
                            try:
                                from datetime import datetime, timedelta
                                yesterday = (datetime.now() - timedelta(days=1)).date()
                                
                                # Parse game date
                                if ',' in game_date_str:
                                    game_date_obj = datetime.strptime(game_date_str, '%b %d, %Y').date()
                                else:
                                    game_date_obj = datetime.strptime(game_date_str[:10], '%Y-%m-%d').date()
                                
                                # If game wasn't yesterday, still return most recent game
                                if game_date_obj != yesterday:
                                    logger.info(f"Game date {game_date_obj} is not yesterday {yesterday}, returning most recent game")
                            except Exception as e:
                                logger.warning(f"Could not parse date for yesterday check: {e}")
                        
                        return {
                            'type': 'match_stats',
                            'data': [game_result],
                            'result_query': True,
                            'team': team_name,
                            'did_win': game_result.get('did_win', False),
                            'team_score': game_result.get('team_score', 0),
                            'opponent_score': game_result.get('opponent_score', 0),
                            'opponent_name': game_result.get('opponent_name', ''),
                            'game_date': game_result.get('game_date', ''),
                            'query': question,
                            'source': 'nba_api_library'
                        }
                    else:
                        logger.warning(f"NBA API Library returned None for {team_name} result query")
                except Exception as e:
                    logger.error(f"NBA API Library failed for result query: {e}", exc_info=True)
                    return {
                        'type': 'match_stats',
                        'data': [],
                        'result_query': True,
                        'team': found_teams[0] if found_teams else '',
                        'query': question,
                        'source': 'nba_api_failed',
                        'error': f"I couldn't retrieve the most recent game result for the {found_teams[0].title()} from the NBA API. Please try again in a moment."
                    }
        
        # Try NBA API Library first for "win by" queries
        if is_win_by_query:
            # Extract team names
            teams = [
                'lakers', 'warriors', 'celtics', 'bucks', 'nuggets', 'suns', 'heat',
                'mavericks', 'clippers', '76ers', 'cavaliers', 'knicks', 'hawks',
                'thunder', 'timberwolves', 'kings', 'pelicans', 'grizzlies', 'raptors',
                'nets', 'bulls', 'pistons', 'pacers', 'hornets', 'magic', 'wizards',
                'trail blazers', 'jazz', 'rockets', 'spurs'
            ]
            
            found_teams = [team for team in teams if team in question_lower]
            
            if found_teams:
                try:
                    from services.nba_api_library import NBAAPILibrary
                    nba_api_lib = NBAAPILibrary()
                    
                    team_name = found_teams[0]
                    logger.info(f"Trying NBA API Library for {team_name} win by point differential query")
                    game_result = nba_api_lib.get_team_most_recent_game_result(team_name)
                    
                    if game_result:
                        did_win = game_result.get('did_win', False)
                        team_score = game_result.get('team_score', 0)
                        opponent_score = game_result.get('opponent_score', 0)
                        
                        if did_win:
                            # Team won - calculate point differential
                            point_differential = team_score - opponent_score
                            logger.info(f"✓ Got point differential for {team_name}: won by {point_differential}")
                            return {
                                'type': 'match_stats',
                                'data': [game_result],
                                'win_by_query': True,
                                'team': team_name,
                                'point_differential': point_differential,
                                'team_score': team_score,
                                'opponent_score': opponent_score,
                                'opponent_name': game_result.get('opponent_name', ''),
                                'game_date': game_result.get('game_date', ''),
                                'query': question,
                                'source': 'nba_api_library'
                            }
                        else:
                            # Team lost - return message that they didn't win
                            return {
                                'type': 'match_stats',
                                'data': [game_result],
                                'win_by_query': True,
                                'team': team_name,
                                'did_win': False,
                                'query': question,
                                'source': 'nba_api_library'
                            }
                    else:
                        logger.warning(f"NBA API Library returned None for {team_name} win by query, trying ESPN API")
                except Exception as e:
                    logger.warning(f"NBA API Library failed for win by query: {e}, trying ESPN API")
                
                # Fallback to ESPN API
                try:
                    from services.direct_espn_fetcher import DirectESPNFetcher
                    direct_fetcher = DirectESPNFetcher()
                    logger.info(f"🔍 ESPN API: Finding game result for {team_name}")
                    game_result = direct_fetcher.get_team_most_recent_game_result(team_name, days_back=30)
                    
                    if game_result:
                        did_win = game_result.get('did_win', False)
                        team_score = game_result.get('team_score', 0)
                        opponent_score = game_result.get('opponent_score', 0)
                        
                        if did_win:
                            # Team won - calculate point differential
                            point_differential = team_score - opponent_score
                            logger.info(f"✓ Got point differential from ESPN for {team_name}: won by {point_differential}")
                            return {
                                'type': 'match_stats',
                                'data': [game_result],
                                'win_by_query': True,
                                'team': team_name,
                                'point_differential': point_differential,
                                'team_score': team_score,
                                'opponent_score': opponent_score,
                                'opponent_name': game_result.get('opponent_name', ''),
                                'game_date': game_result.get('game_date', ''),
                                'query': question,
                                'source': 'direct_espn_fetcher'
                            }
                        else:
                            # Team lost - return message that they didn't win
                            return {
                                'type': 'match_stats',
                                'data': [game_result],
                                'win_by_query': True,
                                'team': team_name,
                                'did_win': False,
                                'query': question,
                                'source': 'direct_espn_fetcher'
                            }
                    else:
                        logger.warning(f"ESPN API also returned None for {team_name} win by query")
                except Exception as espn_err:
                    logger.error(f"ESPN API failed for win by query: {espn_err}", exc_info=True)
                
                # Both APIs failed
                return {
                    'type': 'match_stats',
                    'data': [],
                    'win_by_query': True,
                    'team': found_teams[0] if found_teams else '',
                    'query': question,
                    'source': 'api_failed',
                    'error': f"I couldn't retrieve the most recent game result for the {found_teams[0].title() if found_teams else 'team'}. Please try again in a moment."
                }
        
        # Try NBA API Library first for "lose by" queries
        if is_lose_by_query:
            # Extract team names
            teams = [
                'lakers', 'warriors', 'celtics', 'bucks', 'nuggets', 'suns', 'heat',
                'mavericks', 'clippers', '76ers', 'cavaliers', 'knicks', 'hawks',
                'thunder', 'timberwolves', 'kings', 'pelicans', 'grizzlies', 'raptors',
                'nets', 'bulls', 'pistons', 'pacers', 'hornets', 'magic', 'wizards',
                'trail blazers', 'jazz', 'rockets', 'spurs'
            ]
            
            found_teams = [team for team in teams if team in question_lower]
            
            if found_teams:
                team_name = found_teams[0]
                
                # Try ESPN API first (PRIMARY)
                try:
                    from services.direct_espn_fetcher import DirectESPNFetcher
                    direct_fetcher = DirectESPNFetcher()
                    logger.info(f"Trying ESPN API (primary) for {team_name} point differential query")
                    game_result = direct_fetcher.get_team_most_recent_game_result(team_name, days_back=30)
                    
                    if game_result and not game_result.get('error'):
                        did_win = game_result.get('did_win', False)
                        team_score = game_result.get('team_score', 0)
                        opponent_score = game_result.get('opponent_score', 0)
                        
                        if not did_win:
                            # Team lost - calculate point differential
                            point_differential = opponent_score - team_score
                            logger.info(f"✓ Got point differential from ESPN for {team_name}: lost by {point_differential}")
                            return {
                                'type': 'match_stats',
                                'data': [game_result],
                                'lose_by_query': True,
                                'team': team_name,
                                'point_differential': point_differential,
                                'team_score': team_score,
                                'opponent_score': opponent_score,
                                'opponent_name': game_result.get('opponent_name', ''),
                                'game_date': game_result.get('game_date', ''),
                                'query': question,
                                'source': 'espn_api'
                            }
                        else:
                            # Team won - return message that they didn't lose
                            return {
                                'type': 'match_stats',
                                'data': [game_result],
                                'lose_by_query': True,
                                'team': team_name,
                                'did_win': True,
                                'query': question,
                                'source': 'espn_api'
                            }
                    else:
                        logger.warning(f"ESPN API returned None or error for {team_name} point differential query, trying NBA API Library")
                except Exception as espn_err:
                    logger.warning(f"ESPN API failed for lose by query: {espn_err}, trying NBA API Library as fallback")
                
                # Fallback to NBA API Library
                try:
                    from services.nba_api_library import NBAAPILibrary
                    nba_api_lib = NBAAPILibrary()
                    
                    logger.info(f"Trying NBA API Library (fallback) for {team_name} point differential query")
                    game_result = nba_api_lib.get_team_most_recent_game_result(team_name)
                    
                    if game_result:
                        did_win = game_result.get('did_win', False)
                        team_score = game_result.get('team_score', 0)
                        opponent_score = game_result.get('opponent_score', 0)
                        
                        if not did_win:
                            # Team lost - calculate point differential
                            point_differential = opponent_score - team_score
                            logger.info(f"✓ Got point differential for {team_name}: lost by {point_differential}")
                            return {
                                'type': 'match_stats',
                                'data': [game_result],
                                'lose_by_query': True,
                                'team': team_name,
                                'point_differential': point_differential,
                                'team_score': team_score,
                                'opponent_score': opponent_score,
                                'opponent_name': game_result.get('opponent_name', ''),
                                'game_date': game_result.get('game_date', ''),
                                'query': question,
                                'source': 'nba_api_library'
                            }
                        else:
                            # Team won - return message that they didn't lose
                            return {
                                'type': 'match_stats',
                                'data': [game_result],
                                'lose_by_query': True,
                                'team': team_name,
                                'did_win': True,
                                'query': question,
                                'source': 'nba_api_library'
                            }
                    else:
                        logger.warning(f"NBA API Library also returned None for {team_name} point differential query")
                except Exception as e:
                    logger.error(f"NBA API Library failed for lose by query: {e}", exc_info=True)
                
                # Both APIs failed
                return {
                    'type': 'match_stats',
                    'data': [],
                    'lose_by_query': True,
                    'team': found_teams[0] if found_teams else '',
                    'query': question,
                    'source': 'api_failed',
                    'error': f"I couldn't retrieve the most recent game result for the {found_teams[0].title() if found_teams else 'team'}. Please try again in a moment."
                }
        
        # Use ESPN API as PRIMARY for "did team win" queries (most reliable)
        # Handle "last N games" queries
        if is_multiple_games_query:
            # Extract team names
            teams = [
                'lakers', 'warriors', 'celtics', 'bucks', 'nuggets', 'suns', 'heat',
                'mavericks', 'clippers', '76ers', 'cavaliers', 'knicks', 'hawks',
                'thunder', 'timberwolves', 'kings', 'pelicans', 'grizzlies', 'raptors',
                'nets', 'bulls', 'pistons', 'pacers', 'hornets', 'magic', 'wizards',
                'trail blazers', 'jazz', 'rockets', 'spurs'
            ]
            
            found_teams = [team for team in teams if team in question_lower]
            
            if not found_teams:
                # Check if query starts with a team name
                words = question_lower.split()
                for word in words[:3]:
                    for team in teams:
                        if team in word or word in team:
                            found_teams = [team]
                            break
                    if found_teams:
                        break
            
            if found_teams:
                team_name = self._normalize_team_name(found_teams[0])
                
                # Try ESPN API first
                try:
                    from services.direct_espn_fetcher import DirectESPNFetcher
                    espn_fetcher = DirectESPNFetcher()
                    
                    logger.info(f"Fetching last {num_games} game results for {team_name} from ESPN API")
                    game_results = espn_fetcher.get_team_recent_game_results(team_name, num_games=num_games, days_back=60)
                    
                    if game_results and len(game_results) > 0:
                        logger.info(f"✓ Got {len(game_results)} game results from ESPN API for {team_name}")
                        return {
                            'type': 'match_stats',
                            'data': game_results,
                            'multiple_games_query': True,
                            'team': team_name,
                            'num_games': len(game_results),
                            'query': question,
                            'source': 'espn_api'
                        }
                    else:
                        logger.warning(f"ESPN API returned no game results for {team_name}")
                except Exception as e:
                    logger.warning(f"ESPN API failed for multiple games query: {e}")
                
                # Return error if no results
                return {
                    'type': 'match_stats',
                    'data': [],
                    'multiple_games_query': True,
                    'team': team_name,
                    'error': f"I couldn't retrieve the last {num_games} game results for the {team_name.title()}. Please try again in a moment.",
                    'query': question
                }
        
        if is_win_query:
            # Extract team names - comprehensive list with proper ordering (longer names first to avoid partial matches)
            teams = [
                'golden state warriors', 'golden state', 'los angeles lakers', 'los angeles clippers',
                'boston celtics', 'milwaukee bucks', 'denver nuggets', 'phoenix suns',
                'miami heat', 'dallas mavericks', 'philadelphia 76ers', 'cleveland cavaliers',
                'new york knicks', 'atlanta hawks', 'oklahoma city thunder', 'minnesota timberwolves',
                'sacramento kings', 'new orleans pelicans', 'memphis grizzlies', 'toronto raptors',
                'brooklyn nets', 'chicago bulls', 'detroit pistons', 'indiana pacers',
                'charlotte hornets', 'orlando magic', 'washington wizards', 'portland trail blazers',
                'utah jazz', 'houston rockets', 'san antonio spurs',
                # Shorter names (check after longer ones to avoid false matches)
                'warriors', 'gsw', 'lakers', 'celtics', 'bucks', 'nuggets', 'suns', 'heat',
                'mavericks', 'clippers', '76ers', 'sixers', 'cavaliers', 'cavs', 'knicks', 'hawks',
                'thunder', 'timberwolves', 'kings', 'pelicans', 'grizzlies', 'raptors',
                'nets', 'bulls', 'pistons', 'pacers', 'hornets', 'magic', 'wizards',
                'trail blazers', 'blazers', 'jazz', 'rockets', 'spurs'
            ]
            
            # Find teams in question (prioritize longer matches first)
            found_teams = []
            question_lower_copy = question_lower
            for team in teams:
                if team in question_lower_copy:
                    found_teams.append(team)
                    # Remove matched text to avoid duplicate matches
                    question_lower_copy = question_lower_copy.replace(team, '', 1)
            
            if found_teams:
                # Use the first (most specific/longest) match and normalize it
                team_name = self._normalize_team_name(found_teams[0])
                
                # Try ESPN API first (PRIMARY) with ONE retry
                from services.direct_espn_fetcher import DirectESPNFetcher
                espn_fetcher = DirectESPNFetcher()
                
                game_result = None
                retry_count = 0
                max_retries = 1
                
                while retry_count <= max_retries and game_result is None:
                    try:
                        if retry_count > 0:
                            logger.info(f"Retry {retry_count}: Trying ESPN API for {team_name} most recent game result")
                        else:
                            logger.info(f"Trying ESPN API for {team_name} most recent game result")
                        
                        game_result = espn_fetcher.get_team_most_recent_game_result(team_name, days_back=30)
                        
                        if game_result:
                            # Validate the game result before returning
                            team_score = game_result.get('team_score', 0)
                            opponent_score = game_result.get('opponent_score', 0)
                            did_win = game_result.get('did_win', False)
                            opponent_name = game_result.get('opponent_name', '')
                            game_date = game_result.get('game_date', '')
                            
                            # Validate: scores must be positive and reasonable
                            if team_score <= 0 or opponent_score <= 0:
                                logger.warning(f"Invalid scores in game result for {team_name}: {team_score}-{opponent_score}. Retrying...")
                                game_result = None
                                retry_count += 1
                                continue
                            
                            # Validate: win/loss determination must match scores
                            expected_win = team_score > opponent_score
                            if did_win != expected_win:
                                logger.warning(f"Win/loss mismatch for {team_name}: did_win={did_win} but scores {team_score}-{opponent_score}. Correcting...")
                                did_win = expected_win
                                game_result['did_win'] = did_win
                            
                            # Validate: opponent name must be present and different from team
                            if not opponent_name or opponent_name.upper() == team_name.upper():
                                logger.warning(f"Invalid opponent name for {team_name}: {opponent_name}. Retrying...")
                                game_result = None
                                retry_count += 1
                                continue
                            
                            # Validate: game date must be present
                            if not game_date:
                                logger.warning(f"Missing game date for {team_name}. Retrying...")
                                game_result = None
                                retry_count += 1
                                continue
                            
                            logger.info(f"✓ Got validated game result from ESPN API for {team_name}: {'WIN' if did_win else 'LOSS'} {team_score}-{opponent_score} vs {opponent_name} on {game_date}")
                            return {
                                'type': 'match_stats',
                                'data': [game_result],
                                'win_query': True,
                                'team': team_name,
                                'did_win': did_win,
                                'team_score': team_score,
                                'opponent_score': opponent_score,
                                'opponent_name': opponent_name,
                                'game_date': game_date,
                                'matchup': game_result.get('matchup', ''),
                                'query': question,
                                'source': 'espn_api'
                            }
                        else:
                            retry_count += 1
                            if retry_count <= max_retries:
                                logger.warning(f"ESPN API returned None, retrying... (attempt {retry_count + 1})")
                            else:
                                logger.warning(f"ESPN API returned None after {max_retries + 1} attempts - trying NBA API Library as fallback")
                    except Exception as e:
                        retry_count += 1
                        if retry_count <= max_retries:
                            logger.warning(f"ESPN API failed: {e}, retrying... (attempt {retry_count + 1})")
                        else:
                            logger.warning(f"ESPN API failed after {max_retries + 1} attempts: {e}, trying NBA API Library fallback")
                
                # Fallback to NBA API Library
                try:
                    from services.nba_api_library import NBAAPILibrary
                    nba_api_lib = NBAAPILibrary()
                    
                    logger.info(f"Trying NBA API Library for {team_name} most recent game result (fallback)")
                    game_result = nba_api_lib.get_team_most_recent_game_result(team_name)
                    
                    if game_result:
                        logger.info(f"✓ Got game result from NBA API Library for {team_name}")
                        return {
                            'type': 'match_stats',
                            'data': [game_result],
                            'win_query': True,
                            'team': team_name,
                            'did_win': game_result.get('did_win', False),
                            'team_score': game_result.get('team_score', 0),
                            'opponent_score': game_result.get('opponent_score', 0),
                            'opponent_name': game_result.get('opponent_name', ''),
                            'game_date': game_result.get('game_date', ''),
                            'query': question,
                            'source': 'nba_api_library'
                        }
                    else:
                        logger.warning(f"NBA API Library also returned None for {team_name} - trying Ball Don't Lie API as fallback")
                except Exception as e:
                    logger.warning(f"NBA API Library failed for win query: {e}, trying Ball Don't Lie API fallback")
                
                # Fallback to Ball Don't Lie API (free, reliable)
                try:
                    from services.balldontlie_api import BallDontLieAPI
                    bdl_api = BallDontLieAPI()
                    
                    logger.info(f"Trying Ball Don't Lie API for {team_name} most recent game result (fallback)")
                    game_result = bdl_api.get_team_most_recent_game_result(team_name, days_back=30)
                    
                    if game_result:
                        logger.info(f"✓ Got game result from Ball Don't Lie API for {team_name}")
                        return {
                            'type': 'match_stats',
                            'data': [game_result],
                            'win_query': True,
                            'team': team_name,
                            'did_win': game_result.get('did_win', False),
                            'team_score': game_result.get('team_score', 0),
                            'opponent_score': game_result.get('opponent_score', 0),
                            'opponent_name': game_result.get('opponent_name', ''),
                            'game_date': game_result.get('game_date', ''),
                            'matchup': game_result.get('matchup', ''),
                            'query': question,
                            'source': 'balldontlie_api'
                        }
                    else:
                        logger.warning(f"Ball Don't Lie API also returned None for {team_name}")
                except Exception as e:
                    logger.error(f"Ball Don't Lie API failed for win query: {e}", exc_info=True)
                
                # Try alternative method: Use NBA API Service to get recent games
                try:
                    logger.info(f"Trying alternative method: NBA API Service for {team_name} recent games")
                    recent_games = self.api_service.get_recent_games(days=30, team_name=team_name, limit=50)
                    
                    if recent_games:
                        # Filter for completed games with the team
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
                        team_abbrev = team_abbrev_map.get(team_name.lower(), team_name[:3].upper())
                        
                        # Find most recent completed game
                        for game in recent_games:
                            team1 = game.get('team1_name', '').upper()
                            team2 = game.get('team2_name', '').upper()
                            
                            if team_abbrev.upper() in team1 or team_abbrev.upper() in team2:
                                # Check if game is completed
                                team1_score = game.get('team1_score')
                                team2_score = game.get('team2_score')
                                
                                if team1_score is not None and team2_score is not None:
                                    # Determine if team won
                                    is_team1 = team_abbrev.upper() in team1
                                    team_score = team1_score if is_team1 else team2_score
                                    opponent_score = team2_score if is_team1 else team1_score
                                    opponent_abbrev = team2 if is_team1 else team1
                                    
                                    # Get opponent name
                                    opponent_name = game.get('team2_display' if is_team1 else 'team1_display', opponent_abbrev)
                                    if not opponent_name:
                                        opponent_name = opponent_abbrev
                                    
                                    did_win = team_score > opponent_score
                                    
                                    game_result = {
                                        'team_name': team_name.title(),
                                        'team_abbrev': team_abbrev,
                                        'opponent_name': opponent_name,
                                        'did_win': did_win,
                                        'team_score': team_score,
                                        'opponent_score': opponent_score,
                                        'game_date': game.get('match_date', ''),
                                        'matchup': f"{game.get('team1_display', team1)} vs {game.get('team2_display', team2)}"
                                    }
                                    
                                    logger.info(f"✓ Got game result from NBA API Service for {team_name}")
                                    return {
                                        'type': 'match_stats',
                                        'data': [game_result],
                                        'win_query': True,
                                        'team': team_name,
                                        'did_win': did_win,
                                        'team_score': team_score,
                                        'opponent_score': opponent_score,
                                        'opponent_name': opponent_name,
                                        'game_date': game_result.get('game_date', ''),
                                        'query': question,
                                        'source': 'nba_api_service'
                                    }
                except Exception as e:
                    logger.warning(f"NBA API Service alternative method failed: {e}")
                
                # Try using Ball Don't Lie API get_games_for_date method (search backwards)
                try:
                    logger.info(f"Trying Ball Don't Lie API date search method for {team_name}")
                    from services.balldontlie_api import BallDontLieAPI
                    bdl_api = BallDontLieAPI()
                    
                    team_abbrev_map = {
                        'knicks': 'NYK', 'lakers': 'LAL', 'warriors': 'GS', 'celtics': 'BOS',
                        'bucks': 'MIL', 'nuggets': 'DEN', 'suns': 'PHX', 'heat': 'MIA',
                        'mavericks': 'DAL', 'clippers': 'LAC', '76ers': 'PHI', 'cavaliers': 'CLE',
                        'hawks': 'ATL', 'thunder': 'OKC', 'timberwolves': 'MIN', 'kings': 'SAC',
                        'pelicans': 'NO', 'grizzlies': 'MEM', 'raptors': 'TOR', 'nets': 'BKN',
                        'bulls': 'CHI', 'pistons': 'DET', 'pacers': 'IND', 'hornets': 'CHA',
                        'magic': 'ORL', 'wizards': 'WSH', 'trail blazers': 'POR', 'jazz': 'UTAH',
                        'rockets': 'HOU', 'spurs': 'SAS'
                    }
                    team_abbrev = team_abbrev_map.get(team_name.lower(), team_name[:3].upper())
                    
                    # Search backwards from today
                    for days_ago in range(30):
                        check_date = today - timedelta(days=days_ago)
                        games = bdl_api.get_games_for_date(check_date)
                        
                        for game in games:
                            team1 = game.get('team1_name', '').upper()
                            team2 = game.get('team2_name', '').upper()
                            
                            if team_abbrev.upper() in team1 or team_abbrev.upper() in team2:
                                # Check if completed
                                team1_score = game.get('team1_score')
                                team2_score = game.get('team2_score')
                                
                                if team1_score is not None and team2_score is not None:
                                    is_team1 = team_abbrev.upper() in team1
                                    team_score = team1_score if is_team1 else team2_score
                                    opponent_score = team2_score if is_team1 else team1_score
                                    opponent_abbrev = team2 if is_team1 else team1
                                    
                                    did_win = team_score > opponent_score
                                    
                                    game_result = {
                                        'team_name': team_name.title(),
                                        'team_abbrev': team_abbrev,
                                        'opponent_name': game.get('team2_display' if is_team1 else 'team1_display', opponent_abbrev),
                                        'did_win': did_win,
                                        'team_score': team_score,
                                        'opponent_score': opponent_score,
                                        'game_date': game.get('match_date', ''),
                                        'matchup': f"{game.get('team1_display', team1)} vs {game.get('team2_display', team2)}"
                                    }
                                    
                                    logger.info(f"✓ Got game result from Ball Don't Lie date search for {team_name}")
                                    return {
                                        'type': 'match_stats',
                                        'data': [game_result],
                                        'win_query': True,
                                        'team': team_name,
                                        'did_win': did_win,
                                        'team_score': team_score,
                                        'opponent_score': opponent_score,
                                        'opponent_name': game_result.get('opponent_name', ''),
                                        'game_date': game_result.get('game_date', ''),
                                        'query': question,
                                        'source': 'balldontlie_date_search'
                                    }
                except Exception as e:
                    logger.warning(f"Ball Don't Lie date search method failed: {e}")
                
                # Try using ESPN API get_recent_games method
                try:
                    logger.info(f"Trying ESPN API get_recent_games method for {team_name}")
                    from services.espn_api import ESPNNBAApi
                    espn_api = ESPNNBAApi()
                    
                    recent_games = espn_api.get_recent_games(days=30, limit=100)
                    
                    if recent_games:
                        team_abbrev_map = {
                            'knicks': 'NYK', 'lakers': 'LAL', 'warriors': 'GS', 'celtics': 'BOS',
                            'bucks': 'MIL', 'nuggets': 'DEN', 'suns': 'PHX', 'heat': 'MIA',
                            'mavericks': 'DAL', 'clippers': 'LAC', '76ers': 'PHI', 'cavaliers': 'CLE',
                            'hawks': 'ATL', 'thunder': 'OKC', 'timberwolves': 'MIN', 'kings': 'SAC',
                            'pelicans': 'NO', 'grizzlies': 'MEM', 'raptors': 'TOR', 'nets': 'BKN',
                            'bulls': 'CHI', 'pistons': 'DET', 'pacers': 'IND', 'hornets': 'CHA',
                            'magic': 'ORL', 'wizards': 'WSH', 'trail blazers': 'POR', 'jazz': 'UTAH',
                            'rockets': 'HOU', 'spurs': 'SAS'
                        }
                        team_abbrev = team_abbrev_map.get(team_name.lower(), team_name[:3].upper())
                        
                        # Find most recent game with this team
                        for game in recent_games:
                            team1 = game.get('team1_name', '').upper()
                            team2 = game.get('team2_name', '').upper()
                            
                            if team_abbrev.upper() in team1 or team_abbrev.upper() in team2:
                                team1_score = game.get('team1_score')
                                team2_score = game.get('team2_score')
                                
                                if team1_score is not None and team2_score is not None:
                                    is_team1 = team_abbrev.upper() in team1
                                    team_score = team1_score if is_team1 else team2_score
                                    opponent_score = team2_score if is_team1 else team1_score
                                    
                                    did_win = team_score > opponent_score
                                    
                                    game_result = {
                                        'team_name': team_name.title(),
                                        'team_abbrev': team_abbrev,
                                        'opponent_name': game.get('team2_name' if is_team1 else 'team1_name', ''),
                                        'did_win': did_win,
                                        'team_score': team_score,
                                        'opponent_score': opponent_score,
                                        'game_date': game.get('match_date', ''),
                                        'matchup': f"{game.get('team1_name', '')} vs {game.get('team2_name', '')}"
                                    }
                                    
                                    logger.info(f"✓ Got game result from ESPN get_recent_games for {team_name}")
                                    return {
                                        'type': 'match_stats',
                                        'data': [game_result],
                                        'win_query': True,
                                        'team': team_name,
                                        'did_win': did_win,
                                        'team_score': team_score,
                                        'opponent_score': opponent_score,
                                        'opponent_name': game_result.get('opponent_name', ''),
                                        'game_date': game_result.get('game_date', ''),
                                        'query': question,
                                        'source': 'espn_recent_games'
                                    }
                except Exception as e:
                    logger.warning(f"ESPN get_recent_games method failed: {e}")
                
                # All APIs failed after retries
                logger.error(f"All APIs failed to retrieve game result for {team_name} after retries")
                return {
                    'type': 'match_stats',
                    'data': [],
                    'win_query': True,
                    'team': found_teams[0] if found_teams else '',
                    'query': question,
                    'source': 'all_apis_failed',
                    'error': "Live game data is temporarily unavailable. Please try again shortly."
                }
        
        # Try API first for real-time data (only if not a win query or NBA API didn't handle it)
        try:
            # Extract team names
            teams = [
                'lakers', 'warriors', 'celtics', 'bucks', 'nuggets', 'suns', 'heat',
                'mavericks', 'clippers', '76ers', 'cavaliers', 'knicks', 'hawks',
                'thunder', 'timberwolves', 'kings', 'pelicans', 'grizzlies', 'raptors',
                'nets', 'bulls', 'pistons', 'pacers', 'hornets', 'magic', 'wizards',
                'trail blazers', 'jazz', 'rockets', 'spurs'
            ]
            
            found_teams = [team for team in teams if team in question_lower]
            
            # Extract date to determine days to look back
            target_date = self.extract_date(question)
            days_back = 7  # Default: last week
            
            if target_date:
                days_diff = (date.today() - target_date).days
                if 0 <= days_diff <= 30:
                    days_back = days_diff + 1
            
            # Get all recent games first, then filter
            api_results = self.api_service.get_recent_games(
                days=days_back,
                team_name=None,  # Don't filter in API
                limit=50  # Get more to filter from
            )
            
            if api_results:
                # Map team names to abbreviations for filtering
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
                
                # Filter by specific teams if mentioned
                if len(found_teams) >= 2:
                    team1_abbrev = team_abbrev_map.get(found_teams[0].lower(), found_teams[0][:3].upper())
                    team2_abbrev = team_abbrev_map.get(found_teams[1].lower(), found_teams[1][:3].upper())
                    
                    # Handle common abbreviation variations
                    abbrev_variations = {
                        'GS': ['GS', 'GSW', 'GOLDEN STATE'],
                        'PHX': ['PHX', 'PHO', 'PHOENIX'],
                        'NO': ['NO', 'NOP', 'NEW ORLEANS'],
                        'UTAH': ['UTAH', 'UTA', 'UTAH JAZZ']
                    }
                    
                    team1_variants = abbrev_variations.get(team1_abbrev, [team1_abbrev])
                    team2_variants = abbrev_variations.get(team2_abbrev, [team2_abbrev])
                    
                    filtered = []
                    for r in api_results:
                        team1 = r.get('team1_name', '').upper()
                        team2 = r.get('team2_name', '').upper()
                        
                        # Check if both teams are in this game
                        has_team1 = any(variant.upper() in team1 or variant.upper() in team2 for variant in team1_variants)
                        has_team2 = any(variant.upper() in team1 or variant.upper() in team2 for variant in team2_variants)
                        
                        # Also filter by specific date if extracted
                        if has_team1 and has_team2:
                            if target_date:
                                match_date_str = r.get('match_date', '')
                                # Compare just the date portion (YYYY-MM-DD)
                                if match_date_str and match_date_str[:10] == target_date.strftime('%Y-%m-%d'):
                                    filtered.append(r)
                            else:
                                filtered.append(r)
                    
                    if filtered:
                        # Sort by date (most recent first) and return ONLY the most recent matchup
                        filtered.sort(key=lambda x: x.get('match_date', ''), reverse=True)
                        api_results = [filtered[0]]  # Return only the single most recent game
                    else:
                        api_results = []
                elif len(found_teams) == 1:
                    # Single team mentioned - filter for that team's most recent game
                    team_abbrev = team_abbrev_map.get(found_teams[0].lower(), found_teams[0][:3].upper())
                    filtered = [
                        r for r in api_results
                        if team_abbrev in r.get('team1_name', '') or team_abbrev in r.get('team2_name', '')
                    ]
                    if filtered:
                        # Sort by date (most recent first) and return only the most recent game
                        filtered.sort(key=lambda x: x.get('match_date', ''), reverse=True)
                        api_results = [filtered[0]]  # Return only the single most recent game
                    else:
                        api_results = []
                else:
                    # No specific team - just limit to recent games (keep as list for generic queries)
                    api_results = api_results[:10]
                
                if api_results:
                    return {
                        'type': 'match_stats',
                        'data': api_results,
                        'query': question,
                        'source': 'api'
                    }
        except Exception as e:
            logger.warning(f"API fetch failed: {e}")
        
        # Don't fallback to database - API should be primary source
        logger.info(f"Stats API returned no data for query: {question}")
        return {
            'type': 'match_stats',
            'data': [],
            'query': question,
            'source': 'api_failed',
            'error': 'Unable to fetch stats from API'
        }

