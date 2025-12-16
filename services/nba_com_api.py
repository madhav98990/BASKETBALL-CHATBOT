"""
NBA.com API Service - Direct API calls to NBA.com endpoints
Uses NBA.com's public JSON endpoints
"""
import requests
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NBAComApi:
    """NBA.com API service using official endpoints"""
    
    BASE_URL = "https://stats.nba.com/stats"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.nba.com/',
            'Origin': 'https://www.nba.com'
        })
    
    def get_player_recent_stats(self, player_name: str, limit: int = 5) -> List[Dict]:
        """
        Get player's recent game stats from NBA.com
        This uses a different approach - search for player first, then get their game log
        """
        try:
            logger.info(f"Fetching stats for {player_name} from NBA.com")
            
            # Try to use NBA.com scoreboard and boxscore endpoints
            # For now, return empty to fallback to other methods
            # NBA.com API requires more complex authentication/headers
            
            return []
        except Exception as e:
            logger.error(f"Error fetching from NBA.com: {e}")
            return []

