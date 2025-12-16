"""
NBA Web Scraper - Direct scraping from NBA.com and ESPN for player stats
This is a fallback approach when APIs fail
"""
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import re
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NBAScraper:
    """Scrapes NBA.com and ESPN for player statistics"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
    
    def get_player_recent_stats_espn(self, player_name: str) -> Optional[Dict]:
        """
        Scrape ESPN player page for recent game stats
        ESPN URL format: https://www.espn.com/nba/player/_/id/{player_id}/{name}
        """
        try:
            # ESPN search for player
            search_url = f"https://www.espn.com/nba/players/_/search/{player_name.replace(' ', '%20')}"
            logger.info(f"Searching ESPN for: {player_name}")
            
            response = self.session.get(search_url, timeout=10)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find player link
            # ESPN player pages often have data embedded in JSON-LD or script tags
            scripts = soup.find_all('script', type='application/json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    # Look for player game log data
                    if 'page' in data and 'content' in data.get('page', {}):
                        content = data['page'].get('content', {})
                        # Extract game log if available
                        pass
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error scraping ESPN: {e}")
            return None
    
    def get_player_recent_stats_nba_com(self, player_name: str) -> Optional[Dict]:
        """
        Scrape NBA.com player stats page
        Format: https://www.nba.com/player/{player_id}/{name}
        """
        try:
            # NBA.com uses a search API that returns player IDs
            search_url = "https://stats.nba.com/stats/commonallplayers"
            params = {
                'IsOnlyCurrentSeason': '0',
                'LeagueID': '00',
                'Season': '2024-25'
            }
            
            # This requires more complex authentication, so skip for now
            return None
            
        except Exception as e:
            logger.error(f"Error scraping NBA.com: {e}")
            return None

