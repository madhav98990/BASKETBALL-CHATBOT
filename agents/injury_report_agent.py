"""
Injury Report Agent - Handles player injury queries
Provides injury status and updates
"""
import logging
from datetime import date
from database.db_connection import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InjuryReportAgent:
    """Handles injury report queries"""
    
    def get_all_injuries(self, status: str = None):
        """Get all current injuries"""
        query = """
            SELECT 
                i.injury_id,
                p.player_name,
                t.team_name,
                i.injury_type,
                i.status,
                i.date_reported,
                i.expected_return,
                i.description
            FROM injuries i
            JOIN players p ON i.player_id = p.player_id
            JOIN teams t ON p.team_id = t.team_id
            WHERE 1=1
        """
        params = []
        
        if status:
            query += " AND i.status = %s"
            params.append(status)
        else:
            # Only show active injuries (not healthy)
            query += " AND i.status != 'Healthy'"
        
        query += " ORDER BY i.date_reported DESC"
        
        try:
            results = db.execute_query(query, params)
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting injuries: {e}")
            return []
    
    def get_team_injuries(self, team_name: str):
        """Get injuries for a specific team"""
        query = """
            SELECT 
                i.injury_id,
                p.player_name,
                t.team_name,
                i.injury_type,
                i.status,
                i.date_reported,
                i.expected_return,
                i.description
            FROM injuries i
            JOIN players p ON i.player_id = p.player_id
            JOIN teams t ON p.team_id = t.team_id
            WHERE LOWER(t.team_name) LIKE %s
            AND i.status != 'Healthy'
            ORDER BY i.date_reported DESC
        """
        
        try:
            results = db.execute_query(query, [f"%{team_name.lower()}%"])
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting team injuries: {e}")
            return []
    
    def get_player_injury(self, player_name: str):
        """Get injury status for a specific player"""
        query = """
            SELECT 
                i.injury_id,
                p.player_name,
                t.team_name,
                i.injury_type,
                i.status,
                i.date_reported,
                i.expected_return,
                i.description
            FROM injuries i
            JOIN players p ON i.player_id = p.player_id
            JOIN teams t ON p.team_id = t.team_id
            WHERE LOWER(p.player_name) LIKE %s
            AND i.status != 'Healthy'
            ORDER BY i.date_reported DESC
            LIMIT 1
        """
        
        try:
            results = db.execute_query(query, [f"%{player_name.lower()}%"])
            return dict(results[0]) if results else None
        except Exception as e:
            logger.error(f"Error getting player injury: {e}")
            return None
    
    def process_query(self, question: str) -> dict:
        """Process an injury query"""
        question_lower = question.lower()
        
        # Extract team names
        teams = [
            'lakers', 'warriors', 'celtics', 'bucks', 'nuggets', 'suns', 'heat',
            'mavericks', 'clippers', '76ers', 'cavaliers', 'knicks', 'hawks',
            'thunder', 'timberwolves', 'kings', 'pelicans', 'grizzlies', 'raptors',
            'nets', 'bulls', 'pistons', 'pacers', 'hornets', 'magic', 'wizards',
            'trail blazers', 'jazz', 'rockets', 'spurs'
        ]
        
        found_teams = [team for team in teams if team in question_lower]
        
        # Extract player names
        player_names = [
            'lebron', 'james', 'curry', 'durant', 'giannis', 'tatum', 'jokic',
            'luka', 'doncic', 'embiid', 'butler', 'antetokounmpo', 'davis',
            'booker', 'mitchell', 'morant', 'edwards', 'haliburton', 'fox',
            'young', 'brown', 'siakam', 'randle', 'brunson', 'maxey', 'murray'
        ]
        
        found_players = [name for name in player_names if name in question_lower]
        
        # Check for status filters
        status = None
        if 'out' in question_lower:
            status = 'Out'
        elif 'questionable' in question_lower:
            status = 'Questionable'
        elif 'probable' in question_lower:
            status = 'Probable'
        elif 'day-to-day' in question_lower or 'day to day' in question_lower:
            status = 'Day-to-Day'
        
        if found_players:
            # Get injury for specific player
            injury = self.get_player_injury(found_players[0])
            return {
                'type': 'injuries',
                'data': [injury] if injury else [],
                'player': found_players[0],
                'query': question
            }
        elif found_teams:
            # Get injuries for specific team
            injuries = self.get_team_injuries(found_teams[0])
            return {
                'type': 'injuries',
                'data': injuries,
                'team': found_teams[0],
                'query': question
            }
        else:
            # Get all injuries (with optional status filter)
            injuries = self.get_all_injuries(status)
            return {
                'type': 'injuries',
                'data': injuries,
                'query': question
            }

