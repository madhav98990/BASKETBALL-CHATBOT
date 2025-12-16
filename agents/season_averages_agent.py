"""
Season Averages Agent - Handles queries about player season statistics
Provides season-long averages and totals
"""
import logging
from database.db_connection import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SeasonAveragesAgent:
    """Handles season averages queries"""
    
    def get_player_season_average(self, player_name: str, season: str = '2025-26'):
        """Get season averages for a specific player - uses NBA API Library first, then database"""
        # Try NBA API Library first (PRIMARY - most accurate and up-to-date)
        try:
            from services.nba_api_library import NBAAPILibrary
            nba_api = NBAAPILibrary()
            logger.info(f"🔍 NBA API Library: Fetching season averages for {player_name}")
            season_avg = nba_api.get_player_season_averages(player_name, season)
            
            if season_avg:
                # Format to match database structure
                formatted_result = {
                    'player_name': season_avg.get('player_name', player_name),
                    'team_name': '',  # Would need to fetch separately
                    'games_played': season_avg.get('games_played', 0),
                    'points_per_game': season_avg.get('points_per_game', 0),
                    'rebounds_per_game': season_avg.get('rebounds_per_game', 0),
                    'assists_per_game': season_avg.get('assists_per_game', 0),
                    'steals_per_game': season_avg.get('steals_per_game', 0),
                    'blocks_per_game': season_avg.get('blocks_per_game', 0),
                    'field_goal_percentage': season_avg.get('field_goal_percentage', 0),
                    'three_point_percentage': season_avg.get('three_point_percentage', 0),
                    'free_throw_percentage': season_avg.get('free_throw_percentage', 0),
                    'minutes_per_game': season_avg.get('minutes_per_game', 0),
                    'season': season_avg.get('season', season),
                    'source': 'nba_api_library'
                }
                logger.info(f"✓ Got season averages for {player_name} from NBA API Library")
                return formatted_result
        except Exception as e:
            logger.warning(f"NBA API Library failed: {e}, trying database")
        
        # Fallback to database
        query = """
            SELECT 
                sa.average_id,
                p.player_name,
                t.team_name,
                sa.games_played,
                sa.points_per_game,
                sa.rebounds_per_game,
                sa.assists_per_game,
                sa.steals_per_game,
                sa.blocks_per_game,
                sa.field_goal_percentage,
                sa.three_point_percentage,
                sa.free_throw_percentage,
                sa.minutes_per_game,
                sa.season
            FROM season_averages sa
            JOIN players p ON sa.player_id = p.player_id
            JOIN teams t ON p.team_id = t.team_id
            WHERE LOWER(p.player_name) LIKE %s
            AND sa.season = %s
            LIMIT 1
        """
        
        try:
            results = db.execute_query(query, [f"%{player_name.lower()}%", season])
            if results:
                result = dict(results[0])
                result['source'] = 'database'
                return result
            return None
        except Exception as e:
            logger.error(f"Error getting player season average from database: {e}")
            return None
    
    def get_team_season_averages(self, team_name: str, season: str = '2025-26'):
        """Get season averages for all players on a team"""
        query = """
            SELECT 
                sa.average_id,
                p.player_name,
                t.team_name,
                sa.games_played,
                sa.points_per_game,
                sa.rebounds_per_game,
                sa.assists_per_game,
                sa.steals_per_game,
                sa.blocks_per_game,
                sa.field_goal_percentage,
                sa.three_point_percentage,
                sa.free_throw_percentage,
                sa.minutes_per_game,
                sa.season
            FROM season_averages sa
            JOIN players p ON sa.player_id = p.player_id
            JOIN teams t ON p.team_id = t.team_id
            WHERE LOWER(t.team_name) LIKE %s
            AND sa.season = %s
            ORDER BY sa.points_per_game DESC
        """
        
        try:
            results = db.execute_query(query, [f"%{team_name.lower()}%", season])
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting team season averages: {e}")
            return []
    
    def get_top_players_by_stat(self, stat: str, limit: int = 10, season: str = '2025-26'):
        """Get top players by a specific stat"""
        valid_stats = {
            'points': 'points_per_game',
            'rebounds': 'rebounds_per_game',
            'assists': 'assists_per_game',
            'steals': 'steals_per_game',
            'blocks': 'blocks_per_game'
        }
        
        if stat.lower() not in valid_stats:
            return []
        
        stat_column = valid_stats[stat.lower()]
        
        query = f"""
            SELECT 
                sa.average_id,
                p.player_name,
                t.team_name,
                sa.games_played,
                sa.points_per_game,
                sa.rebounds_per_game,
                sa.assists_per_game,
                sa.steals_per_game,
                sa.blocks_per_game,
                sa.field_goal_percentage,
                sa.three_point_percentage,
                sa.free_throw_percentage,
                sa.minutes_per_game,
                sa.season
            FROM season_averages sa
            JOIN players p ON sa.player_id = p.player_id
            JOIN teams t ON p.team_id = t.team_id
            WHERE sa.season = %s
            ORDER BY sa.{stat_column} DESC
            LIMIT %s
        """
        
        try:
            results = db.execute_query(query, [season, limit])
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting top players by stat: {e}")
            return []
    
    def process_query(self, question: str) -> dict:
        """Process a season averages query"""
        question_lower = question.lower()
        
        # Extract player names
        player_names = [
            'lebron', 'james', 'curry', 'durant', 'giannis', 'tatum', 'jokic',
            'luka', 'doncic', 'embiid', 'butler', 'antetokounmpo', 'davis',
            'booker', 'mitchell', 'morant', 'edwards', 'haliburton', 'fox',
            'young', 'brown', 'siakam', 'randle', 'brunson', 'maxey', 'murray'
        ]
        
        found_players = [name for name in player_names if name in question_lower]
        
        # Extract team names
        teams = [
            'lakers', 'warriors', 'celtics', 'bucks', 'nuggets', 'suns', 'heat',
            'mavericks', 'clippers', '76ers', 'cavaliers', 'knicks', 'hawks',
            'thunder', 'timberwolves', 'kings', 'pelicans', 'grizzlies', 'raptors',
            'nets', 'bulls', 'pistons', 'pacers', 'hornets', 'magic', 'wizards',
            'trail blazers', 'jazz', 'rockets', 'spurs'
        ]
        
        found_teams = [team for team in teams if team in question_lower]
        
        # Check for top players queries
        if 'top' in question_lower or 'leading' in question_lower or 'best' in question_lower:
            # Determine which stat
            if 'points' in question_lower or 'scoring' in question_lower:
                players = self.get_top_players_by_stat('points', limit=10)
            elif 'rebounds' in question_lower or 'rebounding' in question_lower:
                players = self.get_top_players_by_stat('rebounds', limit=10)
            elif 'assists' in question_lower:
                players = self.get_top_players_by_stat('assists', limit=10)
            elif 'steals' in question_lower:
                players = self.get_top_players_by_stat('steals', limit=10)
            elif 'blocks' in question_lower:
                players = self.get_top_players_by_stat('blocks', limit=10)
            else:
                # Default to points
                players = self.get_top_players_by_stat('points', limit=10)
            
            return {
                'type': 'season_averages',
                'data': players,
                'query': question
            }
        elif found_players:
            # Get season average for specific player
            average = self.get_player_season_average(found_players[0])
            return {
                'type': 'season_averages',
                'data': [average] if average else [],
                'player_name': found_players[0],
                'query': question
            }
        elif found_teams:
            # Get season averages for team
            averages = self.get_team_season_averages(found_teams[0])
            return {
                'type': 'season_averages',
                'data': averages,
                'team': found_teams[0],
                'query': question
            }
        else:
            return {
                'type': 'season_averages',
                'data': [],
                'error': 'Could not identify player or team',
                'query': question
            }

