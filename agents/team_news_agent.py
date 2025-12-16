"""
Team News Agent - Handles queries about team news and updates
Provides latest team-related news and updates
"""
import logging
from datetime import date
from database.db_connection import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TeamNewsAgent:
    """Handles team news queries"""
    
    def get_team_news(self, team_name: str = None, limit: int = 10, news_type: str = None):
        """Get team news"""
        query = """
            SELECT 
                tn.news_id,
                t.team_name,
                tn.headline,
                tn.content,
                tn.news_type,
                tn.published_date,
                tn.source,
                tn.is_breaking
            FROM team_news tn
            JOIN teams t ON tn.team_id = t.team_id
            WHERE 1=1
        """
        params = []
        
        if team_name:
            query += " AND LOWER(t.team_name) LIKE %s"
            params.append(f"%{team_name.lower()}%")
        
        if news_type:
            query += " AND tn.news_type = %s"
            params.append(news_type)
        
        query += " ORDER BY tn.is_breaking DESC, tn.published_date DESC LIMIT %s"
        params.append(limit)
        
        try:
            results = db.execute_query(query, params)
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting team news: {e}")
            return []
    
    def get_breaking_news(self, limit: int = 5):
        """Get breaking news"""
        query = """
            SELECT 
                tn.news_id,
                t.team_name,
                tn.headline,
                tn.content,
                tn.news_type,
                tn.published_date,
                tn.source,
                tn.is_breaking
            FROM team_news tn
            JOIN teams t ON tn.team_id = t.team_id
            WHERE tn.is_breaking = TRUE
            ORDER BY tn.published_date DESC
            LIMIT %s
        """
        
        try:
            results = db.execute_query(query, [limit])
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting breaking news: {e}")
            return []
    
    def get_news_by_type(self, news_type: str, limit: int = 10):
        """Get news by type"""
        query = """
            SELECT 
                tn.news_id,
                t.team_name,
                tn.headline,
                tn.content,
                tn.news_type,
                tn.published_date,
                tn.source,
                tn.is_breaking
            FROM team_news tn
            JOIN teams t ON tn.team_id = t.team_id
            WHERE tn.news_type = %s
            ORDER BY tn.published_date DESC
            LIMIT %s
        """
        
        try:
            results = db.execute_query(query, [news_type, limit])
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting news by type: {e}")
            return []
    
    def process_query(self, question: str) -> dict:
        """Process a team news query"""
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
        
        # Check for news type
        news_type = None
        if 'trade' in question_lower:
            news_type = 'trade'
        elif 'injury' in question_lower:
            news_type = 'injury'
        elif 'signing' in question_lower or 'signed' in question_lower:
            news_type = 'signing'
        elif 'roster' in question_lower:
            news_type = 'roster'
        elif 'coaching' in question_lower or 'coach' in question_lower:
            news_type = 'coaching'
        
        # Check for breaking news
        if 'breaking' in question_lower:
            news = self.get_breaking_news(limit=5)
            return {
                'type': 'team_news',
                'data': news,
                'query': question
            }
        elif found_teams:
            # Get news for specific team
            news = self.get_team_news(team_name=found_teams[0], limit=10, news_type=news_type)
            return {
                'type': 'team_news',
                'data': news,
                'team': found_teams[0],
                'query': question
            }
        elif news_type:
            # Get news by type
            news = self.get_news_by_type(news_type, limit=10)
            return {
                'type': 'team_news',
                'data': news,
                'news_type': news_type,
                'query': question
            }
        else:
            # Get all recent news
            news = self.get_team_news(limit=10)
            return {
                'type': 'team_news',
                'data': news,
                'query': question
            }

