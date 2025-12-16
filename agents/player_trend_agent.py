"""
Player Trend Agent - Handles queries about player performance trends
Analyzes recent performance vs season averages
"""
import logging
from datetime import date, timedelta
from database.db_connection import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlayerTrendAgent:
    """Handles player trend queries"""
    
    def get_player_recent_trend(self, player_name: str, games: int = 5):
        """Get player's recent performance trend"""
        query = """
            SELECT 
                ps.points,
                ps.rebounds,
                ps.assists,
                ps.steals,
                ps.blocks,
                m.match_date,
                t1.team_name as team1_name,
                t2.team_name as team2_name
            FROM player_stats ps
            JOIN players p ON ps.player_id = p.player_id
            JOIN matches m ON ps.match_id = m.match_id
            JOIN teams t1 ON m.team1_id = t1.team_id
            JOIN teams t2 ON m.team2_id = t2.team_id
            WHERE LOWER(p.player_name) LIKE %s
            AND m.match_date >= DATE '2023-10-01'
            AND m.match_date <= CURRENT_DATE
            ORDER BY m.match_date DESC
            LIMIT %s
        """
        
        try:
            results = db.execute_query(query, [f"%{player_name.lower()}%", games])
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting player trend: {e}")
            return []
    
    def get_player_season_average(self, player_name: str):
        """Get player's season average for comparison"""
        query = """
            SELECT 
                sa.points_per_game,
                sa.rebounds_per_game,
                sa.assists_per_game,
                sa.steals_per_game,
                sa.blocks_per_game,
                sa.games_played
            FROM season_averages sa
            JOIN players p ON sa.player_id = p.player_id
            WHERE LOWER(p.player_name) LIKE %s
            AND sa.season = '2025-26'
            LIMIT 1
        """
        
        try:
            results = db.execute_query(query, [f"%{player_name.lower()}%"])
            return dict(results[0]) if results else None
        except Exception as e:
            logger.error(f"Error getting season average: {e}")
            return None
    
    def calculate_trend(self, recent_games: list, season_avg: dict):
        """Calculate if player is trending up or down"""
        if not recent_games or not season_avg:
            return None
        
        # Calculate averages for recent games
        recent_avg_points = sum(g.get('points', 0) for g in recent_games) / len(recent_games)
        recent_avg_rebounds = sum(g.get('rebounds', 0) for g in recent_games) / len(recent_games)
        recent_avg_assists = sum(g.get('assists', 0) for g in recent_games) / len(recent_games)
        
        season_avg_points = float(season_avg.get('points_per_game', 0))
        season_avg_rebounds = float(season_avg.get('rebounds_per_game', 0))
        season_avg_assists = float(season_avg.get('assists_per_game', 0))
        
        trend = {
            'points_trend': 'up' if recent_avg_points > season_avg_points else 'down',
            'rebounds_trend': 'up' if recent_avg_rebounds > season_avg_rebounds else 'down',
            'assists_trend': 'up' if recent_avg_assists > season_avg_assists else 'down',
            'recent_avg_points': recent_avg_points,
            'recent_avg_rebounds': recent_avg_rebounds,
            'recent_avg_assists': recent_avg_assists,
            'season_avg_points': season_avg_points,
            'season_avg_rebounds': season_avg_rebounds,
            'season_avg_assists': season_avg_assists
        }
        
        return trend
    
    def process_query(self, question: str) -> dict:
        """Process a player trend query"""
        question_lower = question.lower()
        
        # Extract player names
        player_names = [
            'lebron', 'james', 'curry', 'durant', 'giannis', 'tatum', 'jokic',
            'luka', 'doncic', 'embiid', 'butler', 'antetokounmpo', 'davis',
            'booker', 'mitchell', 'morant', 'edwards', 'haliburton', 'fox',
            'young', 'brown', 'siakam', 'randle', 'brunson', 'maxey', 'murray'
        ]
        
        found_players = [name for name in player_names if name in question_lower]
        
        if not found_players:
            return {
                'type': 'player_trend',
                'data': [],
                'error': 'Could not identify player name',
                'query': question
            }
        
        player_name = found_players[0]
        
        # Get recent games and season average
        recent_games = self.get_player_recent_trend(player_name, games=5)
        season_avg = self.get_player_season_average(player_name)
        
        # Calculate trend
        trend = self.calculate_trend(recent_games, season_avg) if recent_games and season_avg else None
        
        return {
            'type': 'player_trend',
            'data': {
                'recent_games': recent_games,
                'season_average': season_avg,
                'trend': trend
            },
            'player_name': player_name,
            'query': question
        }

