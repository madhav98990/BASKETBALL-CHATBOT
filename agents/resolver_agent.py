"""
Resolver Agent - Canonicalizes player names to ESPN player IDs
Finds ESPN playerId from player name
"""
import logging
import re
import requests
from typing import Optional, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResolverAgent:
    """Resolves player names to ESPN player IDs"""
    
    BASE_URL = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Player name to canonical form mapping
        self.player_name_map = {
            'lebron james': {'canonical': 'LeBron James', 'variations': ['lebron', 'james', 'lebron james']},
            'luka doncic': {'canonical': 'Luka Doncic', 'variations': ['luka', 'doncic', 'luka doncic']},
            'jayson tatum': {'canonical': 'Jayson Tatum', 'variations': ['jayson', 'tatum', 'jayson tatum']},
            'stephen curry': {'canonical': 'Stephen Curry', 'variations': ['curry', 'steph curry', 'stephen curry']},
            'nikola jokic': {'canonical': 'Nikola Jokic', 'variations': ['jokic', 'nikola jokic', 'joker']},
            'kevin durant': {'canonical': 'Kevin Durant', 'variations': ['durant', 'kd', 'kevin durant']},
            'giannis antetokounmpo': {'canonical': 'Giannis Antetokounmpo', 'variations': ['giannis', 'antetokounmpo']},
            'joel embiid': {'canonical': 'Joel Embiid', 'variations': ['embiid', 'joel embiid']},
            'jimmy butler': {'canonical': 'Jimmy Butler', 'variations': ['butler', 'jimmy butler']},
            'anthony davis': {'canonical': 'Anthony Davis', 'variations': ['davis', 'anthony davis', 'ad']},
            'devin booker': {'canonical': 'Devin Booker', 'variations': ['booker', 'devin booker']},
            'chris paul': {'canonical': 'Chris Paul', 'variations': ['chris paul', 'cp3', 'cp']},
            'james harden': {'canonical': 'James Harden', 'variations': ['harden', 'james harden']},
            'kawhi leonard': {'canonical': 'Kawhi Leonard', 'variations': ['leonard', 'kawhi leonard']},
            'damian lillard': {'canonical': 'Damian Lillard', 'variations': ['lillard', 'dame', 'damian lillard']},
        }
    
    def find_espn_player_id(self, canonical_name: str) -> Optional[str]:
        """
        Find ESPN playerId by searching recent games and boxscores
        Returns ESPN playerId or None if not found
        """
        try:
            from datetime import date, timedelta
            
            logger.info(f"Searching for ESPN playerId for: {canonical_name}")
            
            # Search last 7 days of games to find player
            end_date = date.today()
            name_parts = canonical_name.lower().split()
            first_name = name_parts[0] if len(name_parts) > 0 else ""
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            for days_back in range(7):
                check_date = end_date - timedelta(days=days_back)
                date_str = check_date.strftime('%Y%m%d')
                
                url = f"{self.BASE_URL}/scoreboard"
                params = {'dates': date_str}
                
                try:
                    response = self.session.get(url, params=params, timeout=5)
                    if response.status_code != 200:
                        continue
                    
                    data = response.json()
                    events = data.get('events', [])
                    
                    for event in events[:5]:  # Check first 5 games
                        event_id = event.get('id', '')
                        if not event_id:
                            continue
                        
                        # Get boxscore
                        summary_url = f"{self.BASE_URL}/summary"
                        summary_params = {'event': event_id}
                        
                        try:
                            summary_response = self.session.get(summary_url, params=summary_params, timeout=5)
                            if summary_response.status_code != 200:
                                continue
                            
                            summary_data = summary_response.json()
                            boxscore = summary_data.get('boxscore', {})
                            competitions_box = boxscore.get('competitions', [])
                            
                            if not competitions_box:
                                continue
                            
                            comp_box = competitions_box[0]
                            competitors_box = comp_box.get('competitors', [])
                            
                            for competitor in competitors_box:
                                roster = competitor.get('roster', {})
                                if not roster:
                                    continue
                                
                                entries = roster.get('entries', [])
                                for entry in entries:
                                    athlete = entry.get('athlete', {})
                                    if not athlete:
                                        continue
                                    
                                    full_name = athlete.get('fullName', '').lower()
                                    display_name = athlete.get('displayName', '').lower()
                                    
                                    # Check if this player matches
                                    if (first_name in full_name and last_name in full_name) or \
                                       (first_name in display_name and last_name in display_name):
                                        # Found player! Get their ESPN ID
                                        player_id = athlete.get('id', '')
                                        if player_id:
                                            logger.info(f"✓ Found ESPN playerId {player_id} for {canonical_name}")
                                            return str(player_id)
                        
                        except Exception as e:
                            logger.debug(f"Error checking event {event_id}: {e}")
                            continue
                
                except Exception as e:
                    logger.debug(f"Error fetching scoreboard for {date_str}: {e}")
                    continue
            
            logger.warning(f"Could not find ESPN playerId for {canonical_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error finding ESPN playerId: {e}", exc_info=True)
            return None
    
    def resolve_player(self, player_name: str) -> Optional[Dict]:
        """
        Resolve player name to canonical form AND ESPN playerId
        Returns: {'canonical_name': str, 'search_terms': list, 'normalized': str, 'espn_player_id': str} or None
        """
        if not player_name:
            return None
        
        player_name_lower = player_name.lower().strip()
        found_in_map = False
        
        # First, get canonical name
        canonical_name = None
        search_terms = []
        
        # Try exact match first
        if player_name_lower in self.player_name_map:
            entry = self.player_name_map[player_name_lower]
            canonical_name = entry['canonical']
            search_terms = entry['variations']
            found_in_map = True
        else:
            # Try to match against variations
            for key, entry in self.player_name_map.items():
                if any(variation in player_name_lower for variation in entry['variations']):
                    name_parts = player_name_lower.split()
                    if len(name_parts) >= 2:
                        if any(part in entry['canonical'].lower() for part in name_parts):
                            canonical_name = entry['canonical']
                            search_terms = entry['variations']
                            found_in_map = True
                            break
            
            # Fallback: normalize the input
            if not canonical_name:
                words = player_name.strip().split()
                if len(words) >= 2:
                    canonical_name = ' '.join([w.capitalize() for w in words[:2]])
                    search_terms = [canonical_name.lower(), words[0].lower(), words[1].lower()]
                elif len(words) == 1:
                    canonical_name = words[0].capitalize()
                    search_terms = [canonical_name.lower()]
        
        if not canonical_name:
            logger.warning(f"Could not resolve player name: {player_name}")
            return None
        
        # OPTIMIZATION: Never try expensive ESPN ID lookup via boxscore search
        # Instead, rely on player_name for matching in boxscores
        # If ESPN ID is needed, it will be determined during fetching
        espn_player_id = None
        
        if found_in_map:
            logger.info(f"✓ Player found in known players map: {canonical_name}")
        else:
            logger.info(f"Player '{canonical_name}' not in hardcoded map - will attempt API lookup during fetch")
        
        return {
            'canonical_name': canonical_name,
            'search_terms': search_terms,
            'normalized': canonical_name,
            'espn_player_id': espn_player_id,  # Always None - let fetcher handle ESPN ID lookup
            'resolved': True
        }

