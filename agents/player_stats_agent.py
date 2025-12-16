"""
Player Stats Agent - Handles player statistics queries
Uses agent orchestration: Resolver -> Fetcher -> Responder -> Verifier
"""
import logging
import re
import sys
import os
import requests
from datetime import datetime, date, timedelta
from typing import Optional, Dict, List
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_connection import db
from services.nba_api import NBAApiService
from services.nba_api_library import NBAAPILibrary
from services.balldontlie_api import BallDontLieAPI
from agents.resolver_agent import ResolverAgent
from agents.fetcher_agent import FetcherAgent
from agents.responder_agent import ResponderAgent
from agents.verifier_agent import VerifierAgent
from agents.cache_agent import CacheAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlayerStatsAgent:
    """Handles player statistics queries using agent orchestration: Resolver → Fetcher → Cache → Responder"""
    
    def __init__(self):
        self.api_service = NBAApiService()
        self.nba_api_lib = NBAAPILibrary()
        self.balldontlie = BallDontLieAPI()
        try:
            from services.espn_api import ESPNNBAApi
            self.espn_api = ESPNNBAApi()
        except ImportError:
            logger.warning("ESPN API not available")
            self.espn_api = None
        self.resolver = ResolverAgent()
        self.fetcher = FetcherAgent()
        self.cache = CacheAgent(ttl_minutes=30)  # 30 minute cache
        self.responder = ResponderAgent()
        self.verifier = VerifierAgent()
    
    def get_player_stats(self, player_name: str, limit: int = 5):
        """Get stats for a specific player from current season"""
        query = """
            SELECT 
                ps.stat_id,
                ps.points,
                ps.rebounds,
                ps.assists,
                ps.steals,
                ps.blocks,
                m.match_date,
                t1.team_name as team1_name,
                t2.team_name as team2_name,
                m.team1_score,
                m.team2_score,
                t.team_name as player_team
            FROM player_stats ps
            JOIN players p ON ps.player_id = p.player_id
            JOIN matches m ON ps.match_id = m.match_id
            JOIN teams t ON p.team_id = t.team_id
            JOIN teams t1 ON m.team1_id = t1.team_id
            JOIN teams t2 ON m.team2_id = t2.team_id
            WHERE LOWER(p.player_name) LIKE %s
            AND m.match_date >= DATE '2023-10-01'
            AND m.match_date <= CURRENT_DATE
            ORDER BY m.match_date DESC
            LIMIT %s
        """
        
        try:
            results = db.execute_query(query, [f"%{player_name.lower()}%", limit])
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting player stats: {e}")
            return []
    
    def get_player_latest_stats(self, player_name: str):
        """Get latest game stats for a player"""
        stats = self.get_player_stats(player_name, limit=1)
        return stats[0] if stats else None
    
    def get_player_average_stats(self, player_name: str):
        """Get average stats for a player from current season"""
        query = """
            SELECT 
                AVG(ps.points) as avg_points,
                AVG(ps.rebounds) as avg_rebounds,
                AVG(ps.assists) as avg_assists,
                AVG(ps.steals) as avg_steals,
                AVG(ps.blocks) as avg_blocks,
                COUNT(*) as games_played
            FROM player_stats ps
            JOIN players p ON ps.player_id = p.player_id
            JOIN matches m ON ps.match_id = m.match_id
            WHERE LOWER(p.player_name) LIKE %s
            AND m.match_date >= DATE '2023-10-01'
            AND m.match_date <= CURRENT_DATE
        """
        
        try:
            results = db.execute_query(query, [f"%{player_name.lower()}%"])
            if results and len(results) > 0:
                result = dict(results[0])
                # Ensure we have valid averages
                if result.get('games_played', 0) > 0:
                    logger.info(f"Found season averages for {player_name}: {result.get('games_played')} games")
                    return result
            logger.warning(f"No season averages found for {player_name}")
            return None
        except Exception as e:
            logger.error(f"Error getting player average stats: {e}")
            return None
    
    def _calculate_similarity(self, s1: str, s2: str) -> float:
        """Calculate similarity between two strings (0-1)"""
        s1, s2 = s1.lower(), s2.lower()
        if s1 == s2:
            return 1.0
        
        # Levenshtein-like similarity
        longer = s1 if len(s1) > len(s2) else s2
        shorter = s2 if len(s1) > len(s2) else s1
        
        if len(longer) == 0:
            return 1.0
        
        # Count matching characters in order
        matches = 0
        j = 0
        for i in range(len(shorter)):
            while j < len(longer) and shorter[i] != longer[j]:
                j += 1
            if j < len(longer):
                matches += 1
                j += 1
        
        return matches / len(longer)
    
    def extract_player_name(self, question: str) -> str:
        """Extract player name from question with fuzzy matching for typos"""
        # Common NBA player names - expanded list
        player_names = [
            'lebron james', 'jayson tatum', 'jaylen brown', 'stephen curry',
            'klay thompson', 'kevin durant', 'devin booker', 'giannis antetokounmpo',
            'damian lillard', 'nikola jokic', 'jamal murray', 'luka doncic',
            'kyrie irving', 'joel embiid', 'tyrese maxey', 'jimmy butler',
            'bam adebayo', 'donovan mitchell', 'darius garland', 'anthony edwards',
            'karl-anthony towns', 'shai gilgeous-alexander', 'trae young',
            'dejounte murray', 'jalen brunson', 'julius randle', 'pascal siakam',
            'demar derozan', 'zach lavine', 'cade cunningham', 'tyrese haliburton',
            'de\'aaron fox', 'domantas sabonis', 'ja morant', 'jaren jackson',
            'zion williamson', 'brandon ingram', 'victor wembanyama', 'anthony davis',
            'austin reaves', 'kawhi leonard', 'paul george', 'james harden',
            'chris paul', 'russell westbrook', 'jimmy butler', 'kyrie irving',
            'kawhi leonard', 'paul george', 'damian lillard', 'devin booker'
        ]
        
        # Build single name mapping for matching
        single_names = {}
        for full_name in player_names:
            parts = full_name.split()
            for part in parts:
                if part not in single_names:
                    single_names[part] = []
                single_names[part].append(full_name)
        
        # Player abbreviations mapping
        abbreviations = {
            'lbj': 'lebron james',
            'kd': 'kevin durant',
            'nj': 'nikola jokic',
            'jt': 'jayson tatum',
            'sc': 'stephen curry',
            'kt': 'klay thompson',
            'db': 'devin booker',
            'ga': 'giannis antetokounmpo',
            'jm': 'jamal murray',
            'ld': 'luka doncic',
            'ki': 'kyrie irving',
            'je': 'joel embiid',
            'tm': 'tyrese maxey',
            'jb': 'jimmy butler',
            'ad': 'anthony davis',
            'kl': 'kawhi leonard',
            'pg': 'paul george',
            'dm': 'damian lillard',
            'jh': 'james harden',
            'rw': 'russell westbrook',
            'ba': 'bam adebayo'
        }
        
        question_lower = question.lower()
        
        # Check for abbreviations first
        words_lower = question_lower.split()
        for word in words_lower:
            # Remove punctuation
            clean_word = word.strip('.,!?;:')
            if clean_word in abbreviations:
                player_name = abbreviations[clean_word]
                logger.info(f"Found player from abbreviation: {clean_word} -> {player_name}")
                return player_name
        
        # Try to find full player name (most accurate)
        for name in player_names:
            if name in question_lower:
                logger.info(f"Found player name: {name}")
                return name
        
        # Try fuzzy matching for typos (two-word sequences)

        words = question.split()
        for i in range(len(words) - 1):
            potential_pair = f"{words[i]} {words[i+1]}".lower()
            best_match = None
            best_score = 0.7  # Minimum 70% similarity threshold
            
            for name in player_names:
                similarity = self._calculate_similarity(potential_pair, name)
                if similarity > best_score:
                    best_score = similarity
                    best_match = name
            
            if best_match:
                logger.info(f"Found player name with fuzzy matching: {best_match} (from '{potential_pair}')")
                return best_match
        
        # Try to find first name + last name pattern from capitalized words
        for i in range(len(words) - 1):
            if words[i] and words[i+1] and words[i][0].isupper() and words[i+1][0].isupper():
                # Skip common words that start with capitals
                skip_words = ['How', 'What', 'Who', 'When', 'Where', 'The', 'A', 'An', 'Is', 'In', 'For']
                if words[i] not in skip_words and words[i+1] not in skip_words:
                    potential_name = f"{words[i]} {words[i+1]}"
                    logger.info(f"Extracted player name from pattern: {potential_name}")
                    return potential_name
        
        # Try fuzzy matching for single names (typos in first or last name only)
        words_lower = question_lower.split()
        for word in words_lower:
            clean_word = word.strip('.,!?;:')
            if len(clean_word) > 2:  # Skip short words
                # First try exact match on any part of player names
                for name in player_names:
                    name_parts = name.split()
                    for part in name_parts:
                        if clean_word == part or clean_word == part[:-1]:  # Exact or singular match
                            logger.info(f"Found player name with exact single-word match: {name} (from '{clean_word}')")
                            return name
                
                # Then try fuzzy matching
                best_match = None
                best_score = 0.70  # Minimum 70% similarity for single names
                
                # Try matching against all full names
                for name in player_names:
                    similarity = self._calculate_similarity(clean_word, name)
                    if similarity > best_score:
                        best_score = similarity
                        best_match = name
                
                if best_match:
                    logger.info(f"Found player name with single-word fuzzy matching: {best_match} (from '{clean_word}')")
                    return best_match
        
        # Fallback: return any capitalized word sequence (excluding first word if it's a question word)
        capitalized_words = [w for w in words if w and w[0].isupper() and w not in ['How', 'What', 'Who', 'When', 'Where', 'The', 'A', 'An', 'Is', 'In', 'For']]
        if capitalized_words:
            name = ' '.join(capitalized_words[:2])
            logger.info(f"Extracted player name from capitalized words: {name}")
            return name
        
        logger.warning(f"Could not extract player name from: {question}")
        return ""
    
    def validate_player_name(self, player_name: str) -> str:
        """
        Validate and normalize player name using NBA API
        If exact match found in NBA API, return it. Otherwise return original.
        This allows handling of any NBA player, not just hardcoded ones.
        """
        if not player_name or len(player_name.strip()) == 0:
            return player_name
        
        try:
            # Try to find the player using NBA API
            player_id = self.nba_api_lib.find_player_id(player_name)
            if player_id:
                # If found, use the NBA API to get the canonical name
                logger.info(f"✓ Player name validated via NBA API: {player_name}")
                return player_name
        except Exception as e:
            logger.debug(f"Could not validate {player_name} with NBA API: {e}")
        
        # If NBA API doesn't find it, return original (may not be a current NBA player)
        return player_name
    
    def _extract_team_filter(self, question: str, player_name: str = None) -> str:
        """Extract team name filter from question, prioritizing teams after vs/against"""
        question_lower = question.lower()
        teams = [
            'lakers', 'warriors', 'celtics', 'bucks', 'nuggets', 'suns', 'heat',
            'mavericks', 'clippers', '76ers', 'cavaliers', 'knicks', 'hawks',
            'thunder', 'timberwolves', 'kings', 'pelicans', 'grizzlies', 'raptors',
            'nets', 'bulls', 'pistons', 'pacers', 'hornets', 'magic', 'wizards',
            'trail blazers', 'jazz', 'rockets', 'spurs'
        ]
        
        team_filter = None
        # Look for patterns like "vs [team]", "against [team]", "versus [team]", "scored against"
        # Also handle "against the [team]" and "scored against the [team]"
        vs_patterns = [
            ' vs ', ' against ', ' versus ', ' vs. ', 
            ' vs the ', ' against the ', ' versus the ',
            'scored against', 'scored against the',
            'played against', 'played against the',
            'faced', 'faced the'
        ]
        
        for pattern in vs_patterns:
            if pattern in question_lower:
                # Find the team after the pattern
                parts = question_lower.split(pattern, 1)
                if len(parts) > 1:
                    after_pattern = parts[1].strip()
                    # Remove "the" if present at the start
                    if after_pattern.startswith('the '):
                        after_pattern = after_pattern[4:].strip()
                    
                    # Find team name in the text after the pattern
                    # Check if any team name appears at the start or early in the text
                    for team in teams:
                        # Check if team name appears right after the pattern (at start or with space)
                        if after_pattern.startswith(team) or f' {team} ' in after_pattern or after_pattern.endswith(f' {team}'):
                            team_filter = team
                            logger.info(f"Found opponent team after '{pattern}': {team_filter}")
                            break
                    if team_filter:
                        break
        
        # If no team found after vs/against patterns, look for any team mention
        if not team_filter:
            found_teams = [team for team in teams if team in question_lower]
            if found_teams:
                # Exclude player's likely team (if player name contains team name)
                if player_name:
                    player_name_lower = player_name.lower()
                    filtered_teams = [t for t in found_teams if t not in player_name_lower]
                    team_filter = filtered_teams[0] if filtered_teams else found_teams[0]
                else:
                    team_filter = found_teams[0]
                logger.info(f"Found team in query: {team_filter}")
        
        return team_filter
    
    def _handle_season_averages_query(self, question: str) -> dict:
        """Handle season averages queries using NBA API Library (PRIMARY) and ESPN API (fallback)"""
        player_name = self.extract_player_name(question)
        if not player_name:
            return {
                'type': 'season_averages',
                'data': [],
                'error': 'Could not identify player name',
                'query': question
            }
        
        logger.info(f"Getting season averages for {player_name}")
        
        # Try NBA API Library first (PRIMARY - most accurate and comprehensive)
        try:
            from services.nba_api_library import NBAAPILibrary
            nba_api = NBAAPILibrary()
            logger.info(f"🔍 NBA API Library: Fetching season averages for {player_name}")
            season_avg = nba_api.get_player_season_averages(player_name)
            
            if season_avg:
                # Validate data
                games_played = season_avg.get('games_played', 0)
                if games_played <= 0:
                    logger.warning(f"Invalid games played ({games_played}) for {player_name}")
                else:
                    # Format data to match expected structure
                    avg_stats = {
                        'player_name': season_avg.get('player_name', player_name),
                        'games_played': games_played,
                        'points_per_game': season_avg.get('points_per_game', 0),
                        'rebounds_per_game': season_avg.get('rebounds_per_game', 0),
                        'assists_per_game': season_avg.get('assists_per_game', 0),
                        'steals_per_game': season_avg.get('steals_per_game', 0),
                        'blocks_per_game': season_avg.get('blocks_per_game', 0),
                        'field_goal_percentage': season_avg.get('field_goal_percentage', 0),
                        'three_point_percentage': season_avg.get('three_point_percentage', 0),
                        'free_throw_percentage': season_avg.get('free_throw_percentage', 0),
                        'minutes_per_game': season_avg.get('minutes_per_game', 0),
                        'season': season_avg.get('season', '')
                    }
                    
                    logger.info(f"✓ Got season averages for {player_name} from NBA API Library: {games_played} games")
                    
                    return {
                        'type': 'season_averages',
                        'data': avg_stats,
                        'player_name': player_name,
                        'query': question,
                        'source': 'nba_api_library'
                    }
        except Exception as e:
            logger.warning(f"NBA API Library failed: {e}, trying ESPN API")
        
        # Fallback to ESPN API
        try:
            logger.info(f"🔍 ESPN API: Fetching season averages for {player_name}")
            # Get recent games data from API
            recent_stats = self.api_service.get_player_stats(player_name, limit=50)
            
            if recent_stats and len(recent_stats) > 0:
                # Calculate averages from the API data
                total_games = len(recent_stats)
                avg_points = sum(s.get('points', 0) for s in recent_stats) / total_games
                avg_rebounds = sum(s.get('rebounds', 0) for s in recent_stats) / total_games
                avg_assists = sum(s.get('assists', 0) for s in recent_stats) / total_games
                avg_steals = sum(s.get('steals', 0) for s in recent_stats) / total_games
                avg_blocks = sum(s.get('blocks', 0) for s in recent_stats) / total_games
                
                avg_stats = {
                    'player_name': player_name,
                    'games_played': total_games,
                    'points_per_game': round(avg_points, 1),
                    'rebounds_per_game': round(avg_rebounds, 1),
                    'assists_per_game': round(avg_assists, 1),
                    'steals_per_game': round(avg_steals, 1),
                    'blocks_per_game': round(avg_blocks, 1),
                    'field_goal_percentage': 0.0,
                    'three_point_percentage': 0.0,
                    'free_throw_percentage': 0.0,
                    'minutes_per_game': 0.0
                }
                
                logger.info(f"✓ Got season averages for {player_name} from ESPN API: {total_games} games")
                
                return {
                    'type': 'season_averages',
                    'data': avg_stats,
                    'player_name': player_name,
                    'query': question,
                    'source': 'espn_api'
                }
            else:
                logger.warning(f"Could not find stats for {player_name} from ESPN API")
        
        except Exception as e:
            logger.error(f"Error getting season averages from ESPN API: {e}")
        
        return {
            'type': 'season_averages',
            'data': [],
            'error': f'Could not find season averages for {player_name}',
            'player_name': player_name,
            'query': question,
            'source': 'api_failed'
        }
    
    def _handle_game_leader_query(self, question: str) -> dict:
        """Handle game leader queries (e.g., 'Who led the scoring in Warriors' latest game?')
        Uses real-time ESPN API data instead of outdated database"""
        question_lower = question.lower()
        
        # Extract team name
        teams = [
            'lakers', 'warriors', 'celtics', 'bucks', 'nuggets', 'suns', 'heat',
            'mavericks', 'clippers', '76ers', 'cavaliers', 'knicks', 'hawks',
            'thunder', 'timberwolves', 'kings', 'pelicans', 'grizzlies', 'raptors',
            'nets', 'bulls', 'pistons', 'pacers', 'hornets', 'magic', 'wizards',
            'trail blazers', 'jazz', 'rockets', 'spurs'
        ]
        
        team_filter = None
        for team in teams:
            if team in question_lower:
                team_filter = team
                break
        
        if not team_filter:
            return {
                'type': 'game_leader',
                'data': [],
                'error': 'Could not identify team name',
                'query': question
            }
        
        logger.info(f"Finding game leader for {team_filter}'s latest game")
        
        try:
            # For recent games, ESPN API is more reliable and faster
            # Try ESPN API first (better for recent games, faster response)
            logger.info(f"🔍 ESPN API: Finding scoring leader for {team_filter}'s latest game")
            try:
                from services.direct_espn_fetcher import DirectESPNFetcher
                direct_fetcher = DirectESPNFetcher()
                leader_result = direct_fetcher.get_team_game_leader(team_filter, 'points', days_back=30)
                if leader_result:
                    # Transform to expected format
                    formatted_result = {
                        'player_name': leader_result.get('player_name', 'Unknown'),
                        'points': leader_result.get('points', 0),
                        'rebounds': leader_result.get('rebounds', 0),
                        'assists': leader_result.get('assists', 0),
                        'team': team_filter,
                        'game_date': leader_result.get('match_date', leader_result.get('game_date', '')),
                        'match_date': leader_result.get('match_date', leader_result.get('game_date', '')),
                        'matchup': leader_result.get('matchup', '')
                    }
                    logger.info(f"✓ Got game leader from DirectESPNFetcher: {formatted_result.get('player_name')} with {formatted_result.get('points')} points")
                    return {
                        'type': 'game_leader',
                        'data': formatted_result,
                        'team': team_filter,
                        'query': question,
                        'source': 'direct_espn_fetcher'
                    }
                else:
                    logger.warning(f"ESPN API didn't find game leader, trying NBA API")
            except Exception as espn_err:
                logger.warning(f"ESPN API failed: {espn_err}, trying NBA API")
            
            # Fallback to NBA API Library (for historical games)
            logger.info(f"🔍 NBA API Library: Finding scoring leader for {team_filter}")
            try:
                nba_api_result = self.nba_api_lib.get_team_game_leader(team_filter, 'points')
                
                if nba_api_result and nba_api_result.get('player_name'):
                    logger.info(f"✓ Got game leader from NBA API Library: {nba_api_result.get('player_name')} with {nba_api_result.get('points')} points")
                    # Ensure all required fields are present
                    if 'match_date' not in nba_api_result:
                        nba_api_result['match_date'] = nba_api_result.get('game_date', '')
                    return {
                        'type': 'game_leader',
                        'data': nba_api_result,
                        'team': team_filter,
                        'query': question,
                        'source': 'nba_api_library'
                    }
                else:
                    logger.warning(f"NBA API Library returned empty or invalid result: {nba_api_result}")
            except Exception as nba_err:
                logger.warning(f"NBA API Library failed: {nba_err}")
            
            # All APIs failed - return error
            logger.error(f"All APIs failed to find game leader for {team_filter}")
            return {
                    'type': 'game_leader',
                    'data': [],
                'error': f'Could not find recent game or player stats for {team_filter}. Please try again later.',
                    'query': question
                }
        
        except Exception as e:
            logger.error(f"Error handling game leader query: {e}", exc_info=True)
            return {
                'type': 'game_leader',
                'data': [],
                'error': f'An unexpected error occurred: {str(e)}',
                'query': question
            }
    
    def _handle_top_players_query(self, question: str) -> dict:
        """Handle top players by stat queries (e.g., 'top 5 players in assists across the NBA')"""
        question_lower = question.lower()
        
        # Check if this is a season-wide query (not date-specific)
        # Improved detection to catch more variations
        is_season_query = any(phrase in question_lower for phrase in [
            'across the nba', 'in the nba', 'in nba', 'across nba', 'across the league',
            'in the league', 'in league', 'league', 'season', 'this season', 'nba'
        ]) or ('top' in question_lower and 'in' in question_lower and any(stat in question_lower for stat in ['assists', 'points', 'rebounds', 'blocks', 'steals', 'score', 'scoring', 'field goal', 'field goal percentage', 'fg%', '3 pointer', 'three pointer', '3-pointers made', 'three-pointers made', '3 pointer percentage', 'three pointer percentage', '3pt percentage', '3pt%']))
        
        # Extract stat type - prioritize explicit stat mentions
        # Check for assists first (before points) to avoid conflicts
        stat_type = None
        
        # Priority order: check for specific stat mentions first
        # Check for 3-pointer percentage FIRST (highest priority, before points to avoid conflicts)
        # Check for percentage indicators first
        has_3pt_pct = (
            '3 pointer percentage' in question_lower or 
            'three pointer percentage' in question_lower or 
            '3pt percentage' in question_lower or 
            '3-point percentage' in question_lower or 
            'three-point percentage' in question_lower or 
            '3pt%' in question_lower or 
            '3p%' in question_lower or
            ('3 pointer' in question_lower and 'percentage' in question_lower) or
            ('three pointer' in question_lower and 'percentage' in question_lower) or
            ('3-point' in question_lower and 'percentage' in question_lower) or
            ('three-point' in question_lower and 'percentage' in question_lower)
        )
        
        if has_3pt_pct:
            stat_type = 'three_point_pct'
            logger.info(f"Detected stat type: three_point_pct (from query: '{question}')")
        # Check for 3-pointers made - default to total (not per game) unless "per game" is explicitly mentioned
        elif '3 pointer' in question_lower or 'three pointer' in question_lower or '3-pointers made' in question_lower or 'three-pointers made' in question_lower or '3pm' in question_lower or '3pt made' in question_lower:
            # Check if "per game" is mentioned - if not, use total
            if 'per game' in question_lower or 'ppg' in question_lower:
                stat_type = 'three_pointers_made_per_game'
                logger.info(f"Detected stat type: three_pointers_made_per_game (from query: '{question}')")
            else:
                stat_type = 'three_pointers_made'
                logger.info(f"Detected stat type: three_pointers_made (total) (from query: '{question}')")
        elif 'field goal' in question_lower or 'field goal percentage' in question_lower or 'fg%' in question_lower or 'fg pct' in question_lower or 'shooting percentage' in question_lower:
            stat_type = 'field_goal_pct'
            logger.info(f"Detected stat type: field_goal_pct (from query: '{question}')")
        elif 'assists' in question_lower or 'assist' in question_lower or 'apg' in question_lower:
            stat_type = 'assists'
            logger.info(f"Detected stat type: assists (from query: '{question}')")
        elif 'rebounds' in question_lower or 'rebound' in question_lower or 'rpg' in question_lower:
            stat_type = 'rebounds'
            logger.info(f"Detected stat type: rebounds (from query: '{question}')")
        elif 'steals' in question_lower or 'steal' in question_lower or 'spg' in question_lower:
            stat_type = 'steals'
            logger.info(f"Detected stat type: steals (from query: '{question}')")
        elif 'blocks' in question_lower or 'block' in question_lower or 'bpg' in question_lower:
            stat_type = 'blocks'
            logger.info(f"Detected stat type: blocks (from query: '{question}')")
        elif ('points' in question_lower and 'pointer' not in question_lower) or ('point' in question_lower and 'per game' in question_lower and 'pointer' not in question_lower) or ('ppg' in question_lower and 'pointer' not in question_lower) or 'score' in question_lower or 'scoring' in question_lower:
            # Only match points if "pointer" is not in the query (to avoid matching "3-pointer")
            stat_type = 'points'
            logger.info(f"Detected stat type: points (from query: '{question}')")
        
        if not stat_type:
            # Only default to points if no stat mentioned AND no pointer-related terms
            if 'pointer' not in question_lower:
                stat_type = 'points'  # Default to points only if no stat mentioned
                logger.warning(f"No stat type detected in query '{question}', defaulting to points")
            else:
                # Has "pointer" but didn't match - might be a 3-pointer query we didn't catch
                stat_type = 'three_point_pct'  # Default to 3-point percentage if pointer mentioned
                logger.warning(f"Pointer mentioned but no exact match in query '{question}', defaulting to three_point_pct")
        
        # Extract limit (top 5, top 10, etc.)
        limit = 10  # Default to 10 instead of 5
        import re
        limit_match = re.search(r'top\s+(\d+)', question_lower)
        if limit_match:
            limit = int(limit_match.group(1))
        
        # For season-wide queries, ALWAYS use NBA API Library first (most reliable and recent)
        # Default to season query if no date-specific keywords found
        has_date_keywords = any(phrase in question_lower for phrase in [
            'last night', 'yesterday', 'last week', 'on', 'date', 'specific date'
        ])
        
        if is_season_query or not has_date_keywords:
            # FALLBACK CHAIN: NBA API Library → ESPN API → Ball Don't Lie API
            top_players = None
            source = None
            error_message = None
            
            # Try 1: NBA API Library (PRIMARY - fastest, most accurate)
            try:
                logger.info(f"Getting top {limit} players by {stat_type} across NBA using NBA API Library")
                top_players = self.nba_api_lib.get_top_players_by_stat(stat_type, limit=limit)
                
                if top_players and len(top_players) > 0:
                    logger.info(f"✓ Got {len(top_players)} top players from NBA API Library")
                    source = 'nba_api_library'
                else:
                    logger.warning(f"NBA API Library returned empty results for top {limit} players by {stat_type}")
                    top_players = None
            except Exception as e:
                logger.error(f"NBA API Library failed for top players: {e}", exc_info=True)
                error_message = f"NBA API Library error: {str(e)[:100]}"
                top_players = None
            
            # Try 2: ESPN API (FALLBACK 1)
            if not top_players and self.espn_api:
                try:
                    logger.info(f"Trying ESPN API as fallback for top {limit} players by {stat_type}")
                    top_players = self.espn_api.get_top_players_by_stat(stat_type, limit=limit)
                    
                    if top_players and len(top_players) > 0:
                        logger.info(f"✓ Got {len(top_players)} top players from ESPN API (fallback)")
                        source = 'espn_api'
                    else:
                        logger.warning(f"ESPN API returned empty results for top {limit} players by {stat_type}")
                        top_players = None
                except Exception as e:
                    logger.warning(f"ESPN API fallback failed: {e}")
                    if not error_message:
                        error_message = f"ESPN API error: {str(e)[:100]}"
                    top_players = None
            
            # Try 3: Ball Don't Lie API (FALLBACK 2)
            if not top_players and self.balldontlie:
                try:
                    logger.info(f"Trying Ball Don't Lie API as fallback for top {limit} players by {stat_type}")
                    top_players = self.balldontlie.get_top_players_by_stat(stat_type, limit=limit)
                    
                    if top_players and len(top_players) > 0:
                        logger.info(f"✓ Got {len(top_players)} top players from Ball Don't Lie API (fallback)")
                        source = 'balldontlie_api'
                    else:
                        logger.warning(f"Ball Don't Lie API returned empty results for top {limit} players by {stat_type}")
                        top_players = None
                except Exception as e:
                    logger.warning(f"Ball Don't Lie API fallback failed: {e}")
                    if not error_message:
                        error_message = f"Ball Don't Lie API error: {str(e)[:100]}"
                    top_players = None
            
            # Return result or error
            if top_players and len(top_players) > 0:
                return {
                    'type': 'top_players',
                    'data': top_players,
                    'stat': stat_type,
                    'limit': limit,
                    'query': question,
                    'source': source or 'unknown'
                }
            else:
                # All APIs failed - return helpful error
                error_msg = f'Unable to retrieve top {limit} players in {stat_type} from any available API source'
                if error_message:
                    error_msg += f'. Last error: {error_message}'
                error_msg += '. The data may not be available for the current season, or all API services are currently unavailable.'
                
                logger.error(f"All API sources failed for top {limit} players by {stat_type}")
                return {
                    'type': 'top_players',
                    'data': [],
                    'stat': stat_type,
                    'limit': limit,
                    'query': question,
                    'error': error_msg,
                    'source': 'none'
                }
        
        # Check if it's for a specific date (last night, yesterday, etc.)
        # But fall back to most recent if date not found
        date_filter = None
        from datetime import date, timedelta
        if 'last night' in question_lower or 'yesterday' in question_lower:
            date_filter = date.today() - timedelta(days=1)
        elif 'last week' in question_lower:
            date_filter = date.today() - timedelta(days=7)
        
        logger.info(f"Getting top {limit} players by {stat_type}, date_filter: {date_filter}")
        
        try:
            # First try with date filter if specified
            if date_filter:
                query = f"""
                    SELECT 
                        p.player_name,
                        ps.{stat_type} as stat_value,
                        ps.points,
                        ps.rebounds,
                        ps.assists,
                        ps.steals,
                        ps.blocks,
                        m.match_date,
                        t1.team_name as team1_name,
                        t2.team_name as team2_name,
                        t.team_name as player_team
                    FROM player_stats ps
                    JOIN players p ON ps.player_id = p.player_id
                    JOIN matches m ON ps.match_id = m.match_id
                    JOIN teams t ON p.team_id = t.team_id
                    JOIN teams t1 ON m.team1_id = t1.team_id
                    JOIN teams t2 ON m.team2_id = t2.team_id
                    WHERE m.match_date = DATE %s
                    ORDER BY ps.{stat_type} DESC
                    LIMIT %s
                """
                
                params = [str(date_filter), limit * 2]  # Get more to filter duplicates
                results = db.execute_query(query, params)
                
                # If no results for exact date, fall back to most recent available
                if not results or len(results) == 0:
                    logger.info(f"No data for {date_filter}, falling back to most recent available")
                    date_filter = None
            
            # Query without date filter or as fallback
            if not date_filter:
                query = f"""
                    SELECT 
                        p.player_name,
                        ps.{stat_type} as stat_value,
                        ps.points,
                        ps.rebounds,
                        ps.assists,
                        ps.steals,
                        ps.blocks,
                        m.match_date,
                        t1.team_name as team1_name,
                        t2.team_name as team2_name,
                        t.team_name as player_team
                    FROM player_stats ps
                    JOIN players p ON ps.player_id = p.player_id
                    JOIN matches m ON ps.match_id = m.match_id
                    JOIN teams t ON p.team_id = t.team_id
                    JOIN teams t1 ON m.team1_id = t1.team_id
                    JOIN teams t2 ON m.team2_id = t2.team_id
                    WHERE m.match_date >= DATE '2023-10-01'
                    AND m.match_date <= CURRENT_DATE
                    ORDER BY m.match_date DESC, ps.{stat_type} DESC
                    LIMIT %s
                """
                
                params = [limit * 2]  # Get more to filter duplicates
                results = db.execute_query(query, params)
            
            if results:
                top_players = [dict(row) for row in results]
                # Remove duplicates by player_name, keeping highest stat from most recent game
                seen = {}
                for player in top_players:
                    name = player.get('player_name', '')
                    if name not in seen:
                        seen[name] = player
                    else:
                        # Keep the one with higher stat or more recent date
                        existing = seen[name]
                        if player.get('stat_value', 0) > existing.get('stat_value', 0):
                            seen[name] = player
                        elif player.get('stat_value', 0) == existing.get('stat_value', 0):
                            # Same stat value, keep more recent
                            if player.get('match_date', '') > existing.get('match_date', ''):
                                seen[name] = player
                
                top_players = list(seen.values())
                # Sort by stat value descending
                top_players.sort(key=lambda x: x.get('stat_value', 0), reverse=True)
                top_players = top_players[:limit]
                
                logger.info(f"Found {len(top_players)} top players by {stat_type}")
                return {
                    'type': 'top_players',
                    'data': top_players,
                    'stat': stat_type,
                    'limit': limit,
                    'query': question,
                    'source': 'database'
                }
        except Exception as e:
            logger.error(f"Error getting top players: {e}", exc_info=True)
        
        return {
            'type': 'top_players',
            'data': [],
            'error': 'Could not find top players',
            'query': question
        }
    
    def _get_player_stats_from_database(self, player_name: str, limit: int = 20) -> list:
        """Query player stats from database for triple-double counting"""
        try:
            logger.info(f"Querying database for {player_name} stats")
            
            # Query player stats from database
            query = """
                SELECT 
                    ps.points,
                    ps.rebounds,
                    ps.assists,
                    m.match_date,
                    t1.team_name as team1,
                    t2.team_name as team2
                FROM player_stats ps
                JOIN matches m ON ps.match_id = m.match_id
                JOIN players p ON ps.player_id = p.player_id
                JOIN teams t1 ON m.team1_id = t1.team_id
                JOIN teams t2 ON m.team2_id = t2.team_id
                WHERE LOWER(p.player_name) LIKE %s
                ORDER BY m.match_date DESC
                LIMIT %s
            """
            
            # Use case-insensitive search
            search_name = f"%{player_name.lower()}%"
            
            # Execute query using db connection
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (search_name, limit))
            rows = cursor.fetchall()
            cursor.close()
            
            if rows:
                logger.info(f"Found {len(rows)} games for {player_name} from database")
                # Convert to dict format for compatibility
                result = []
                for row in rows:
                    result.append({
                        'points': row[0],
                        'rebounds': row[1],
                        'assists': row[2],
                        'match_date': row[3],
                        'team1': row[4],
                        'team2': row[5]
                    })
                return result
            else:
                logger.warning(f"No stats found in database for {player_name}")
                return []
                
        except Exception as e:
            logger.error(f"Error querying database for player stats: {e}")
            return []
    
    def _handle_triple_double_query(self, question: str) -> dict:
        """Handle triple-double count queries using official NBA API library"""
        
        player_name = self.extract_player_name(question)
        if not player_name:
            return {
                'type': 'player_stats',
                'data': [],
                'error': 'Could not identify player name',
                'query': question
            }
        
        logger.info(f"Getting triple-double matches for {player_name} from NBA API Library")
        
        try:
            # Use NBA API Library (official nba_api) to get triple-doubles
            result = self.nba_api_lib.get_triple_double_count(player_name)
            
            if result['count'] > 0:
                logger.info(f"Found {result['count']} triple-doubles for {player_name}")
                
                return {
                    'type': 'triple_double_count',
                    'data': {
                        'player_name': player_name,
                        'count': result['count'],
                        'triple_doubles': result['games'],
                        'season': result.get('season', 'Unknown')
                    },
                    'player_name': player_name,
                    'query': question,
                    'source': 'nba_api_library'
                }
            else:
                # If NBA API has no data, try database as fallback
                logger.info(f"NBA API returned no triple-doubles, trying database for {player_name}")
                recent_stats = self._get_player_stats_from_database(player_name, limit=100)
                
                if recent_stats and len(recent_stats) > 0:
                    triple_double_count = 0
                    triple_double_games = []
                    
                    for game_stats in recent_stats:
                        points = game_stats.get('points', 0) or 0
                        rebounds = game_stats.get('rebounds', 0) or 0
                        assists = game_stats.get('assists', 0) or 0
                        
                        # Count triple-doubles (10+ in each of 3 categories)
                        if points >= 10 and rebounds >= 10 and assists >= 10:
                            triple_double_count += 1
                            triple_double_games.append({
                                'date': game_stats.get('match_date', ''),
                                'opponent': f"{game_stats.get('team1', '')} vs {game_stats.get('team2', '')}",
                                'points': points,
                                'rebounds': rebounds,
                                'assists': assists
                            })
                            logger.info(f"Found triple-double for {player_name}: {points}pts, {rebounds}reb, {assists}ast")
                    
                    if triple_double_count > 0:
                        logger.info(f"Found {triple_double_count} triple-doubles for {player_name} from database")
                        return {
                            'type': 'triple_double_count',
                            'data': {
                                'player_name': player_name,
                                'count': triple_double_count,
                                'triple_doubles': triple_double_games
                            },
                            'player_name': player_name,
                            'query': question,
                            'source': 'database'
                        }
                
        except Exception as e:
            logger.error(f"Error getting triple-double count: {e}")
        
        # Return error message if nothing found
        error_msg = result.get('error', 'Could not find triple-double data for this player from available sources')
        logger.warning(f"Triple-double query failed for {player_name}: {error_msg}")
        
        return {
            'type': 'triple_double_count',
            'data': [],
            'error': error_msg,
            'query': question,
            'source': 'unavailable'
        }
    
    def _extract_team_name_from_query(self, question: str) -> Optional[str]:
        """Extract team name from query for game leader questions"""
        question_lower = question.lower()
        
        # Common team names
        teams = [
            'warriors', 'lakers', 'celtics', 'bucks', 'nuggets', 'suns', 'heat',
            'mavericks', 'clippers', '76ers', 'cavaliers', 'knicks', 'hawks',
            'thunder', 'timberwolves', 'kings', 'pelicans', 'grizzlies', 'raptors',
            'nets', 'bulls', 'pistons', 'pacers', 'hornets', 'magic', 'wizards',
            'trail blazers', 'jazz', 'rockets', 'spurs'
        ]
        
        for team in teams:
            if team in question_lower:
                return team
        
        return None
    
    def _filter_stats_by_team(self, stats: list, team_filter: str, player_name: str) -> list:
        """Filter stats list by team, ensuring player is on the other team"""
        if not stats or not team_filter:
            return stats
        
        # Map team names to proper database team names and abbreviations (case-insensitive matching)
        team_name_map = {
            'lakers': ['Lakers', 'LAL', 'Los Angeles Lakers'],
            'warriors': ['Warriors', 'GS', 'GSW', 'Golden State Warriors'],
            'celtics': ['Celtics', 'BOS', 'Boston Celtics'],
            'bucks': ['Bucks', 'MIL', 'Milwaukee Bucks'],
            'nuggets': ['Nuggets', 'DEN', 'Denver Nuggets'],
            'suns': ['Suns', 'PHX', 'Phoenix Suns'],
            'heat': ['Heat', 'MIA', 'Miami Heat'],
            'mavericks': ['Mavericks', 'DAL', 'Dallas Mavericks'],
            'clippers': ['Clippers', 'LAC', 'LA Clippers'],
            '76ers': ['76ers', 'PHI', 'Philadelphia 76ers'],
            'cavaliers': ['Cavaliers', 'CLE', 'Cleveland Cavaliers'],
            'knicks': ['Knicks', 'NYK', 'New York Knicks'],
            'hawks': ['Hawks', 'ATL', 'Atlanta Hawks'],
            'thunder': ['Thunder', 'OKC', 'Oklahoma City Thunder'],
            'timberwolves': ['Timberwolves', 'MIN', 'Minnesota Timberwolves'],
            'kings': ['Kings', 'SAC', 'Sacramento Kings'],
            'pelicans': ['Pelicans', 'NO', 'NOP', 'New Orleans Pelicans'],
            'grizzlies': ['Grizzlies', 'MEM', 'Memphis Grizzlies'],
            'raptors': ['Raptors', 'TOR', 'Toronto Raptors'],
            'nets': ['Nets', 'BKN', 'Brooklyn Nets'],
            'bulls': ['Bulls', 'CHI', 'Chicago Bulls'],
            'pistons': ['Pistons', 'DET', 'Detroit Pistons'],
            'pacers': ['Pacers', 'IND', 'Indiana Pacers'],
            'hornets': ['Hornets', 'CHA', 'Charlotte Hornets'],
            'magic': ['Magic', 'ORL', 'Orlando Magic'],
            'wizards': ['Wizards', 'WSH', 'Washington Wizards'],
            'trail blazers': ['Trail Blazers', 'POR', 'Portland Trail Blazers'],
            'jazz': ['Jazz', 'UTAH', 'UTA', 'Utah Jazz'],
            'rockets': ['Rockets', 'HOU', 'Houston Rockets'],
            'spurs': ['Spurs', 'SA', 'SAS', 'San Antonio Spurs']
        }
        
        # Get all possible team name variations
        team_variations = team_name_map.get(team_filter.lower(), [team_filter.title()])
        team_variations_lower = [v.lower() for v in team_variations]
        
        filtered = []
        for stat in stats:
            if isinstance(stat, dict):
                team1 = str(stat.get('team1_name', '')).strip()
                team2 = str(stat.get('team2_name', '')).strip()
                player_team = str(stat.get('player_team', '')).strip()
                
                # Case-insensitive matching
                team1_lower = team1.lower()
                team2_lower = team2.lower()
                player_team_lower = player_team.lower()
                
                # Check if the opponent team matches any variation (case-insensitive)
                team1_matches = any(variation in team1_lower or team1_lower in variation for variation in team_variations_lower)
                team2_matches = any(variation in team2_lower or team2_lower in variation for variation in team_variations_lower)
                
                if team1_matches or team2_matches:
                    # Check which team the player is on (simple string matching)
                    player_on_team1 = player_team_lower == team1_lower or team1_lower in player_team_lower or player_team_lower in team1_lower
                    player_on_team2 = player_team_lower == team2_lower or team2_lower in player_team_lower or player_team_lower in team2_lower
                    
                    # Determine which team is the opponent
                    opponent_team = team1 if team1_matches else (team2 if team2_matches else None)
                    
                    # Player should be on the OTHER team (not the opponent)
                    if opponent_team:
                        if team1_matches:
                            # Opponent is team1, player should be on team2 (not team1)
                            if player_on_team2 and not player_on_team1:
                                filtered.append(stat)
                                logger.info(f"✓ Matched: {player_name} ({player_team}) vs {opponent_team} on {stat.get('match_date', 'N/A')} - {stat.get('points', 0)} pts")
                        elif team2_matches:
                            # Opponent is team2, player should be on team1 (not team2)
                            if player_on_team1 and not player_on_team2:
                                filtered.append(stat)
                                logger.info(f"✓ Matched: {player_name} ({player_team}) vs {opponent_team} on {stat.get('match_date', 'N/A')} - {stat.get('points', 0)} pts")
        
        logger.info(f"Filtered {len(stats)} stats to {len(filtered)} for {player_name} vs {team_filter}")
        if len(filtered) == 0 and len(stats) > 0:
            logger.warning(f"No matching stats found. Sample teams in data: {stats[0].get('team1_name')} vs {stats[0].get('team2_name')}, player on: {stats[0].get('player_team')}")
        return filtered
    
    def process_query(self, question: str) -> dict:
        """Process a player stats query - handles multiple query types"""
        question_lower = question.lower()
        
        # Check for different query types - prioritize specific patterns
        # Triple-double queries
        is_triple_double = 'triple-double' in question_lower or 'triple double' in question_lower or 'triple doubles' in question_lower
        
        # Season averages - must check first before "most" triggers top players
        is_season_average = any(phrase in question_lower for phrase in [
            'season average', 'season averages', 'averages', 'average stats',
            'season stats', 'per game', 'ppg', 'rpg', 'apg', 'right now'
        ]) and ('season' in question_lower or 'average' in question_lower or 'ppg' in question_lower or 'rpg' in question_lower or 'apg' in question_lower)
        
        # Game leader - check before top players
        is_game_leader = any(phrase in question_lower for phrase in [
            'led the scoring', 'led scoring', 'top scorer', 'leading scorer', 'who scored',
            'scoring leader', 'points leader', 'who led', 'who led the', 'who led the scoring',
            'who scored the most', 'most points'
        ])
        
        # Top players - must have explicit "top N" or be about multiple players
        # Improved detection to catch more query variations
        is_top_players = (
            ('top' in question_lower and any(word in question_lower for word in ['5', '10', 'players', 'in assists', 'in points', 'in rebounds', 'in blocks', 'in steals', 'in score', 'in scoring', 'field goal', 'field goal percentage', 'fg%', '3 pointer', 'three pointer', '3-pointers made', 'three-pointers made', 'across', 'nba', 'league'])) or
            ('leaders in' in question_lower) or
            ('leading' in question_lower and any(stat in question_lower for stat in ['assists', 'points', 'rebounds', 'blocks', 'steals', 'score', 'scoring', 'field goal', 'field goal percentage', 'fg%', '3 pointer', 'three pointer', '3-pointers made', 'three-pointers made'])) or
            ('best in' in question_lower and 'players' in question_lower) or
            ('top' in question_lower and 'across' in question_lower) or
            ('top' in question_lower and 'nba' in question_lower) or
            ('top' in question_lower and 'league' in question_lower) or
            (any(stat in question_lower for stat in ['assists', 'points', 'rebounds', 'blocks', 'steals', 'score', 'scoring', 'field goal', 'field goal percentage', 'fg%', '3 pointer', 'three pointer', '3-pointers made', 'three-pointers made', '3 pointer percentage', 'three pointer percentage', '3pt percentage', '3pt%']) and 'top' in question_lower)
        ) and not is_season_average
        
        # Recent game - check for explicit recent game patterns
        is_recent_game = any(phrase in question_lower for phrase in [
            'most recent game', 'last game', 'latest game', 'recent game',
            'last night', 'yesterday', 'in his most recent', 'in their most recent'
        ])
        
        # Handle triple-double count queries
        if is_triple_double:
            logger.info("Detected triple-double query")
            return self._handle_triple_double_query(question)
        
        # Handle game leaders query (team-focused)
        if is_game_leader:
            # Use the ESPN API method that properly sorts by date
            return self._handle_game_leader_query(question)
        
        # Handle top players query
        if is_top_players:
            return self._handle_top_players_query(question)
        
        # Handle season averages query FIRST (before other handlers)
        if is_season_average:
            logger.info("Detected season averages query")
            return self._handle_season_averages_query(question)
        
        # AGENT ORCHESTRATION FLOW: Resolver → Fetcher → Cache → Responder
        # Step 1: Resolver Agent - find ESPN playerId and canonicalize player name
        player_name = self.extract_player_name(question)
        
        if not player_name:
            return {
                'type': 'player_stats',
                'data': [],
                'error': 'Could not identify player name',
                'query': question
            }
        
        # Validate player name using NBA API (handles any valid NBA player)
        player_name = self.validate_player_name(player_name)
        
        logger.info(f"🔍 Resolver: Resolving player name '{player_name}' to ESPN playerId")
        player_info = self.resolver.resolve_player(player_name)
        
        if not player_info:
            # Player not found in resolver - fail fast without trying expensive API calls
            error_msg = f"Could not identify player: {player_name}. Please check the spelling."
            logger.warning(f"⚠ Resolver failed to find player: {player_name}")
            return {
                'type': 'player_stats',
                'data': [],
                'error': error_msg,
                'query': question
            }
        
        canonical_name = player_info.get('canonical_name', player_name)
        espn_player_id = player_info.get('espn_player_id')
        logger.info(f"✓ Resolved to: {canonical_name}" + (f" (ESPN ID: {espn_player_id})" if espn_player_id else " (no ESPN ID found)"))
        
        # NOTE: If no ESPN ID found, the fetcher will likely fail
        # This is normal - it means the player data isn't available in current ESPN data
        
        # Step 2: Check if query asks for vs specific team
        # Check for various patterns that indicate a player vs team query
        has_vs_pattern = any(p in question_lower for p in [
            ' vs ', ' against ', ' versus ', ' vs. ', 
            ' vs the ', ' against the ', ' versus the ',
            'scored against', 'played against', 'faced'
        ])
        team_filter = self._extract_team_filter(question, player_name) if has_vs_pattern else None
        
        # Step 3: Check Cache first
        logger.info("🔍 Cache: Checking for cached stats")
        cached_data = self.cache.get_player_stats(espn_player_id, canonical_name, team_filter)
        
        if cached_data:
            logger.info("✓ Cache hit - using cached data")
            # Use cached data
            cached_result = {
                'success': True,
                'data': cached_data.get('data') if isinstance(cached_data, dict) and 'data' in cached_data else cached_data,
                'metadata': cached_data.get('metadata', {}) if isinstance(cached_data, dict) else {},
                'error': None
            }
            formatted_response = self.responder.format_response(cached_result, question)
            return {
                'type': 'player_stats',
                'data': cached_result['data'],
                'player_name': canonical_name,
                'query': question,
                'source': 'cache',
                'metadata': cached_result.get('metadata', {}),
                'formatted_response': formatted_response
            }
        
        logger.info("⚠ Cache miss - fetching from API")
        
        # Step 4: Try NBA API Library first for vs_team queries (more reliable)
        # Then fall back to Fetcher Agent for real-time data from ESPN
        fetch_result = None
        
        if team_filter:
            # Try NBA API Library first (official NBA data, more reliable for historical games)
            logger.info(f"🔍 NBA API Library: Fetching stats for {canonical_name} vs {team_filter}")
            nba_api_result = self.nba_api_lib.get_player_stats_vs_team(canonical_name, team_filter)
            
            if nba_api_result:
                logger.info(f"✓ Got stats from NBA API Library for {canonical_name} vs {team_filter}")
                fetch_result = {
                    'success': True,
                    'data': nba_api_result,
                    'metadata': {
                        'source': 'NBA API Library',
                        'fetched_at': datetime.utcnow().isoformat() + 'Z',
                        'cache': 'miss'
                    },
                    'error': None
                }
            else:
                # Fall back to ESPN Fetcher
                logger.info(f"⚠ NBA API Library didn't find game, trying ESPN Fetcher")
                fetch_result = self.fetcher.fetch_player_stats_vs_team(player_info, team_filter)
        else:
            # For non-vs queries, use ESPN Fetcher (real-time data)
            logger.info(f"🔍 Fetcher: Fetching stats for {canonical_name}")
            fetch_result = self.fetcher.fetch_player_last_game(player_info)
        
        # Step 5: Cache the result if successful
        if fetch_result.get('success') and fetch_result.get('data'):
            logger.info("✓ Caching fetched data")
            self.cache.set_player_stats(espn_player_id, canonical_name, fetch_result, team_filter)
        
        # Step 6: Verifier Agent - validate the data (optional, for logging)
        verification = None
        if fetch_result.get('success') and fetch_result.get('data'):
            logger.info("🔍 Verifier: Validating fetched data")
            verification = self.verifier.verify_player_stats(fetch_result['data'], fetch_result.get('metadata', {}))
            logger.info(f"✓ Verification: {verification['confidence']:.1%} confidence - {verification['notes']}")
        
        # Step 7: Responder Agent - format response (reads retrieved_stats JSON, allows partial stats)
        if fetch_result.get('success') and fetch_result.get('data'):
            # Data successfully fetched - Responder reads retrieved_stats and formats
            formatted_response = self.responder.format_response(fetch_result, question)
            
            return {
                'type': 'player_stats',
                'data': fetch_result['data'],
                'player_name': canonical_name,
                'query': question,
                'source': 'api_realtime',
                'metadata': fetch_result.get('metadata', {}),
                'verification': verification,
                'formatted_response': formatted_response  # Pre-formatted for immediate use
            }
        
        # Fetch failed - Return clear error without unnecessary fallbacks
        error_msg = fetch_result.get('error', 'Unknown error')
        logger.warning(f"⚠ Fetcher failed: {error_msg}")
        
        # API failed - return error immediately (no database fallback for outdated data)
        error_message = f"I couldn't find recent statistics for {canonical_name} from current game data (as of 2025-12-11). \n\nThis could mean:\n• The player hasn't played recently\n• Game data isn't available yet\n• The player name might be spelled differently\n\nPlease try asking about a different player or rephrase your question."
        
        logger.error(f"All API sources failed for {canonical_name} - returning error")
        
        return {
            'type': 'player_stats',
            'data': [],
            'error': error_message,
            'query': question,
            'source': 'api_unavailable',
            'formatted_response': error_message
        }

