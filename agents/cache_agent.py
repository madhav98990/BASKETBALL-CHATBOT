"""
Cache Agent - Stores short-term results to avoid redundant API calls
"""
import logging
import time
from typing import Dict, Optional
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CacheAgent:
    """Stores and retrieves cached player stats data"""
    
    def __init__(self, ttl_minutes: int = 30):
        """
        Initialize cache with time-to-live in minutes
        Default: 30 minutes cache
        """
        self.cache: Dict[str, Dict] = {}
        self.ttl_minutes = ttl_minutes
    
    def get(self, cache_key: str) -> Optional[Dict]:
        """
        Get cached data if it exists and hasn't expired
        Returns: Cached data dict or None if not found/expired
        """
        if cache_key not in self.cache:
            return None
        
        cached_item = self.cache[cache_key]
        cached_at = cached_item.get('cached_at')
        
        # Check if cache has expired
        if cached_at:
            try:
                cached_time = datetime.fromisoformat(cached_at)
                age = datetime.utcnow() - cached_time
                if age > timedelta(minutes=self.ttl_minutes):
                    logger.debug(f"Cache expired for key: {cache_key} (age: {age})")
                    del self.cache[cache_key]
                    return None
            except Exception as e:
                logger.warning(f"Error checking cache expiration: {e}")
        
        logger.info(f"✓ Cache hit for key: {cache_key}")
        return cached_item.get('data')
    
    def set(self, cache_key: str, data: Dict) -> None:
        """
        Store data in cache with current timestamp
        """
        self.cache[cache_key] = {
            'data': data,
            'cached_at': datetime.utcnow().isoformat() + 'Z'
        }
        logger.info(f"✓ Cached data for key: {cache_key}")
    
    def _generate_key(self, player_id: Optional[str], player_name: str, team_filter: Optional[str] = None) -> str:
        """Generate cache key from player info"""
        parts = []
        if player_id:
            parts.append(f"id:{player_id}")
        else:
            parts.append(f"name:{player_name.lower()}")
        
        if team_filter:
            parts.append(f"team:{team_filter.lower()}")
        
        return "|".join(parts)
    
    def get_player_stats(self, player_id: Optional[str], player_name: str, team_filter: Optional[str] = None) -> Optional[Dict]:
        """Get cached player stats"""
        key = self._generate_key(player_id, player_name, team_filter)
        return self.get(key)
    
    def set_player_stats(self, player_id: Optional[str], player_name: str, data: Dict, team_filter: Optional[str] = None) -> None:
        """Cache player stats"""
        key = self._generate_key(player_id, player_name, team_filter)
        self.set(key, data)
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
        logger.info("Cache cleared")

