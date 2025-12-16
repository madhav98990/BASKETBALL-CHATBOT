"""
Live Game Agent - Handles queries about games currently in progress
Fetches real-time game updates from external APIs
"""
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime, date
from database.db_connection import db
from services.nba_api import NBAApiService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LiveGameAgent:
    """Handles live game queries"""
    
    def __init__(self):
        self.api_service = NBAApiService()
    
    def get_live_games(self):
        """Get all currently live games"""
        query = """
            SELECT 
                lg.live_game_id,
                t1.team_name as team1_name,
                t2.team_name as team2_name,
                lg.team1_score,
                lg.team2_score,
                lg.quarter,
                lg.time_remaining,
                lg.game_status,
                lg.venue,
                lg.game_date,
                lg.game_time,
                lg.last_updated
            FROM live_games lg
            JOIN teams t1 ON lg.team1_id = t1.team_id
            JOIN teams t2 ON lg.team2_id = t2.team_id
            WHERE lg.game_status IN ('live', 'halftime')
            ORDER BY lg.last_updated DESC
        """
        
        try:
            results = db.execute_query(query, [])
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting live games: {e}")
            return []
    
    def get_team_live_game(self, team_name: str):
        """Get live game for a specific team"""
        query = """
            SELECT 
                lg.live_game_id,
                t1.team_name as team1_name,
                t2.team_name as team2_name,
                lg.team1_score,
                lg.team2_score,
                lg.quarter,
                lg.time_remaining,
                lg.game_status,
                lg.venue,
                lg.game_date,
                lg.game_time,
                lg.last_updated
            FROM live_games lg
            JOIN teams t1 ON lg.team1_id = t1.team_id
            JOIN teams t2 ON lg.team2_id = t2.team_id
            WHERE lg.game_status IN ('live', 'halftime')
            AND (LOWER(t1.team_name) LIKE %s OR LOWER(t2.team_name) LIKE %s)
            ORDER BY lg.last_updated DESC
            LIMIT 1
        """
        
        try:
            results = db.execute_query(query, [f"%{team_name.lower()}%", f"%{team_name.lower()}%"])
            return dict(results[0]) if results else None
        except Exception as e:
            logger.error(f"Error getting team live game: {e}")
            return None
    
    def process_query(self, question: str) -> dict:
        """Process a live game query - uses real-time API"""
        question_lower = question.lower()
        
        # Try API first for real-time data
        try:
            api_games = self.api_service.get_live_games()
            
            if api_games:
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
                    # Filter by team
                    team_abbrev = found_teams[0][:3].upper() if len(found_teams[0]) >= 3 else found_teams[0].upper()
                    filtered = [
                        g for g in api_games
                        if team_abbrev in g['team1_name'] or team_abbrev in g['team2_name']
                    ]
                    if filtered:
                        return {
                            'type': 'live_game',
                            'data': filtered,
                            'team': found_teams[0],
                            'query': question,
                            'source': 'api'
                        }
                
                return {
                    'type': 'live_game',
                    'data': api_games,
                    'query': question,
                    'source': 'api'
                }
        except Exception as e:
            logger.warning(f"API fetch failed, falling back to database: {e}")
        
        # Fallback to database
        teams = [
            'lakers', 'warriors', 'celtics', 'bucks', 'nuggets', 'suns', 'heat',
            'mavericks', 'clippers', '76ers', 'cavaliers', 'knicks', 'hawks',
            'thunder', 'timberwolves', 'kings', 'pelicans', 'grizzlies', 'raptors',
            'nets', 'bulls', 'pistons', 'pacers', 'hornets', 'magic', 'wizards',
            'trail blazers', 'jazz', 'rockets', 'spurs'
        ]
        
        found_teams = [team for team in teams if team in question_lower]
        
        if found_teams:
            game = self.get_team_live_game(found_teams[0])
            return {
                'type': 'live_game',
                'data': [game] if game else [],
                'team': found_teams[0],
                'query': question,
                'source': 'database'
            }
        else:
            games = self.get_live_games()
            return {
                'type': 'live_game',
                'data': games,
                'query': question,
                'source': 'database'
            }

