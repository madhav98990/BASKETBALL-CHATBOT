"""
Responder Agent - Validates structure, checks freshness, formats final answer
MUST NOT invent numbers - only uses verified data from Fetcher
"""
import logging
from datetime import datetime
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResponderAgent:
    """Formats and validates responses - NEVER invents data"""
    
    def format_response(self, fetch_result: Dict, query: str) -> str:
        """
        Format response from fetch result
        Returns formatted string or error message
        """
        if not fetch_result.get('success'):
            error = fetch_result.get('error', 'Unknown error')
            metadata = fetch_result.get('metadata', {})
            
            return f"I couldn't retrieve verified data right now (ESPN API: {error}). Please try again in a moment or rephrase your question."
        
        data = fetch_result.get('data')
        metadata = fetch_result.get('metadata', {})
        
        if not data:
            return "I couldn't find verified player statistics. Please try asking about a different game or player."
        
        # Validate data structure
        if not isinstance(data, dict):
            return "Received invalid data format. Please try again."
        
        # Extract and validate stats - ACCEPT PARTIAL STATS
        player_name = data.get('player_name', 'Unknown Player')
        
        # Get stats with defaults - handle None values gracefully
        points = data.get('points')
        rebounds = data.get('rebounds')
        assists = data.get('assists')
        steals = data.get('steals')
        blocks = data.get('blocks')
        match_date = data.get('match_date', '')
        team1 = data.get('team1_name', '')
        team2 = data.get('team2_name', '')
        player_team = data.get('player_team', '')
        
        # Convert None to 0 for stats (partial stats are OK)
        points = int(points) if points is not None else 0
        rebounds = int(rebounds) if rebounds is not None else 0
        assists = int(assists) if assists is not None else 0
        steals = int(steals) if steals is not None else 0
        blocks = int(blocks) if blocks is not None else 0
        
        # ACCEPT PARTIAL STATS - only require at least ONE stat to be present
        # If all are 0/None, then reject
        if points == 0 and rebounds == 0 and assists == 0:
            # Check if we have at least player name and game info
            if not player_name or player_name == 'Unknown Player':
                return "I found game data but couldn't extract player statistics. Please try again."
            # If we have player name but no stats, still return what we have
            logger.warning(f"Player {player_name} found but no stats extracted")
        
        # Build stats string - include all available stats (even if 0 for some)
        stats_parts = []
        if points is not None and points >= 0:
            stats_parts.append(f"{points} points")
        if rebounds is not None and rebounds >= 0:
            stats_parts.append(f"{rebounds} rebounds")
        if assists is not None and assists >= 0:
            stats_parts.append(f"{assists} assists")
        if steals is not None and steals > 0:
            stats_parts.append(f"{steals} steals")
        if blocks is not None and blocks > 0:
            stats_parts.append(f"{blocks} blocks")
        
        # If we have at least one stat, proceed
        if not stats_parts:
            # No stats at all - return error
            return "I found game data but couldn't extract player statistics. Please try again."
        
        stats_str = ', '.join(stats_parts)
        
        # Format response based on context
        query_lower = query.lower()
        
        # Check if query asks about vs specific team
        if 'vs' in query_lower or 'versus' in query_lower or 'against' in query_lower:
            # Specific matchup query
            if team1 and team2:
                if match_date:
                    return f"{player_name} scored {stats_str} in the {team1} vs {team2} game on {match_date}."
                else:
                    return f"{player_name} scored {stats_str} in the {team1} vs {team2} game."
        
        # Recent game query
        if 'most recent' in query_lower or 'last game' in query_lower or 'latest' in query_lower:
            if team1 and team2 and match_date:
                # Determine opponent
                opponent = team2 if player_team == team1 else (team1 if player_team == team2 else team2)
                return f"{player_name} scored {stats_str} when {player_team} played {opponent} on {match_date}."
            elif match_date:
                return f"{player_name} scored {stats_str} in their game on {match_date}."
            else:
                return f"{player_name} scored {stats_str} in their most recent game."
        
        # General query
        if team1 and team2:
            if match_date:
                return f"{player_name} scored {stats_str} in the {team1} vs {team2} game on {match_date}."
            else:
                return f"{player_name} scored {stats_str} in the {team1} vs {team2} game."
        elif match_date:
            return f"{player_name} scored {stats_str} in their game on {match_date}."
        else:
            return f"{player_name} scored {stats_str}."
    
    def validate_data_freshness(self, metadata: Dict) -> bool:
        """Check if data is fresh (within last 7 days)"""
        try:
            fetched_at = metadata.get('fetched_at', '')
            if not fetched_at:
                return False
            
            # Parse ISO format timestamp
            fetched_time = datetime.fromisoformat(fetched_at.replace('Z', '+00:00'))
            now = datetime.utcnow()
            
            # Check if fetched within last 7 days
            days_old = (now - fetched_time).days
            return days_old <= 7
            
        except Exception as e:
            logger.error(f"Error validating freshness: {e}")
            return False
    
    def format_error_response(self, error: str, metadata: Dict) -> str:
        """Format error response"""
        source = metadata.get('source', 'ESPN API')
        error_msg = error.lower()
        
        if 'not found' in error_msg or 'no recent games' in error_msg:
            return f"I couldn't find recent game statistics for this player from ESPN. This could mean the player hasn't played recently, or the game data isn't available yet. Please try asking about a different player or check back later."
        elif 'timeout' in error_msg or 'timed out' in error_msg:
            return f"The ESPN API is taking longer than expected to respond. Please try again in a moment."
        else:
            return f"I couldn't retrieve verified real-time data from ESPN right now ({error}). The system is designed to only return verified, current data, not outdated information. Please try again in a moment."

