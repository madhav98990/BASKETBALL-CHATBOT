"""
Standings Agent - Handles team standings and rankings queries
Fetches real-time standings from external APIs
"""
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_connection import db
from services.nba_api import NBAApiService
from services.nba_api_library import NBAAPILibrary

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StandingsAgent:
    """Handles standings queries"""
    
    def __init__(self):
        self.api_service = NBAApiService()
        self.nba_api_lib = NBAAPILibrary()
    
    def get_conference_standings(self, conference: str = None):
        """Get standings by conference"""
        query = """
            SELECT 
                s.standing_id,
                t.team_name,
                t.conference,
                t.division,
                s.wins,
                s.losses,
                s.win_percentage,
                s.conference_rank,
                s.division_rank,
                s.games_back,
                s.streak
            FROM standings s
            JOIN teams t ON s.team_id = t.team_id
            WHERE 1=1
        """
        params = []
        
        if conference:
            query += " AND t.conference = %s"
            params.append(conference)
        
        query += " ORDER BY s.conference_rank ASC, s.win_percentage DESC"
        
        try:
            results = db.execute_query(query, params)
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting conference standings: {e}")
            return []
    
    def get_division_standings(self, division: str):
        """Get standings by division"""
        query = """
            SELECT 
                s.standing_id,
                t.team_name,
                t.conference,
                t.division,
                s.wins,
                s.losses,
                s.win_percentage,
                s.conference_rank,
                s.division_rank,
                s.games_back,
                s.streak
            FROM standings s
            JOIN teams t ON s.team_id = t.team_id
            WHERE t.division = %s
            ORDER BY s.division_rank ASC, s.win_percentage DESC
        """
        
        try:
            results = db.execute_query(query, [division])
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting division standings: {e}")
            return []
    
    def get_team_standing(self, team_name: str):
        """Get standing for a specific team"""
        query = """
            SELECT 
                s.standing_id,
                t.team_name,
                t.conference,
                t.division,
                s.wins,
                s.losses,
                s.win_percentage,
                s.conference_rank,
                s.division_rank,
                s.games_back,
                s.streak
            FROM standings s
            JOIN teams t ON s.team_id = t.team_id
            WHERE LOWER(t.team_name) LIKE %s
            LIMIT 1
        """
        
        try:
            results = db.execute_query(query, [f"%{team_name.lower()}%"])
            return dict(results[0]) if results else None
        except Exception as e:
            logger.error(f"Error getting team standing: {e}")
            return None
    
    def _extract_seed_number(self, question: str) -> int:
        """Extract seed number from question (e.g., '10th seed' -> 10, '1st seed' -> 1)"""
        import re
        question_lower = question.lower()
        
        # Pattern to match ordinal numbers: 1st, 2nd, 3rd, 4th, 10th, etc.
        ordinal_pattern = r'(\d+)(?:st|nd|rd|th)'
        match = re.search(ordinal_pattern, question_lower)
        if match:
            return int(match.group(1))
        
        # Also check for "seed number" or "number seed" patterns
        seed_number_pattern = r'(\d+)\s*seed|seed\s*(\d+)'
        match = re.search(seed_number_pattern, question_lower)
        if match:
            return int(match.group(1) or match.group(2))
        
        return None
    
    def _extract_team_position_query(self, question: str) -> dict:
        """Extract team name and position/rank from queries like 'Are the Thunder still in the top 3 of the West?'"""
        import re
        question_lower = question.lower()
        
        # Team name mapping - ordered list with longer names first for better matching
        # This ensures "oklahoma city thunder" matches before just "thunder"
        team_map_list = [
            # Full names first (most specific) - tuple format: (key, [variations sorted by length])
            ('thunder', ['oklahoma city thunder', 'oklahoma city', 'okc', 'thunder']),
            ('lakers', ['los angeles lakers', 'lakers']),
            ('warriors', ['golden state warriors', 'golden state', 'gsw', 'warriors']),
            ('celtics', ['boston celtics', 'boston', 'celtics']),
            ('nuggets', ['denver nuggets', 'denver', 'nuggets']),
            ('suns', ['phoenix suns', 'phoenix', 'suns']),
            ('heat', ['miami heat', 'miami', 'heat']),
            ('bucks', ['milwaukee bucks', 'milwaukee', 'bucks']),
            ('knicks', ['new york knicks', 'new york', 'knicks']),
            ('76ers', ['philadelphia 76ers', 'philadelphia', 'sixers', '76ers']),
            ('cavaliers', ['cleveland cavaliers', 'cleveland', 'cavs', 'cavaliers']),
            ('hawks', ['atlanta hawks', 'atlanta', 'hawks']),
            ('magic', ['orlando magic', 'orlando', 'magic']),
            ('raptors', ['toronto raptors', 'toronto', 'raptors']),
            ('pistons', ['detroit pistons', 'detroit', 'pistons']),
            ('bulls', ['chicago bulls', 'chicago', 'bulls']),
            ('hornets', ['charlotte hornets', 'charlotte', 'hornets']),
            ('nets', ['brooklyn nets', 'brooklyn', 'nets']),
            ('pacers', ['indiana pacers', 'indiana', 'pacers']),
            ('wizards', ['washington wizards', 'washington', 'wizards']),
            ('rockets', ['houston rockets', 'houston', 'rockets']),
            ('spurs', ['san antonio spurs', 'san antonio', 'spurs']),
            ('timberwolves', ['minnesota timberwolves', 'minnesota', 'wolves', 'timberwolves']),
            ('kings', ['sacramento kings', 'sacramento', 'kings']),
            ('pelicans', ['new orleans pelicans', 'new orleans', 'pelicans']),
            ('grizzlies', ['memphis grizzlies', 'memphis', 'grizzlies']),
            ('mavericks', ['dallas mavericks', 'dallas', 'mavs', 'mavericks']),
            ('jazz', ['utah jazz', 'utah', 'jazz']),
            ('trail blazers', ['portland trail blazers', 'portland', 'blazers', 'trail blazers']),
            ('clippers', ['los angeles clippers', 'la clippers', 'clippers'])
        ]
        
        # Find team in question - check longer names first
        found_team = None
        for team_key, team_variations in team_map_list:
            # Sort variations by length (longest first) to match more specific names first
            sorted_variations = sorted(team_variations, key=len, reverse=True)
            for variation in sorted_variations:
                if variation in question_lower:
                    found_team = team_key
                    break
            if found_team:
                break
        
        if not found_team:
            return None
        
        # Extract position/rank (e.g., "top 3", "top 5", "in the top 3")
        position_match = re.search(r'top\s+(\d+)', question_lower)
        if not position_match:
            # Try "rank" or "position" patterns
            position_match = re.search(r'(?:rank|position|seed)\s+(\d+)', question_lower)
        
        if not position_match:
            return None
        
        position = int(position_match.group(1))
        
        # Extract conference
        conference = None
        if 'west' in question_lower or 'western' in question_lower:
            conference = 'West'
        elif 'east' in question_lower or 'eastern' in question_lower:
            conference = 'East'
        
        return {
            'team': found_team,
            'position': position,
            'conference': conference
        }
    
    def _extract_games_behind_query(self, question: str) -> dict:
        """Extract team name from queries like 'How far behind first place are the Celtics?'"""
        question_lower = question.lower()
        
        # Check for games behind queries
        is_games_behind_query = any(phrase in question_lower for phrase in [
            'how far behind', 'games behind', 'games back', 'behind first',
            'behind first place', 'how many games behind'
        ])
        
        if not is_games_behind_query:
            return None
        
        # Team name mapping
        team_map = {
            'thunder': ['thunder', 'okc', 'oklahoma city'],
            'lakers': ['lakers', 'los angeles lakers'],
            'warriors': ['warriors', 'golden state'],
            'celtics': ['celtics', 'boston'],
            'nuggets': ['nuggets', 'denver'],
            'suns': ['suns', 'phoenix'],
            'heat': ['heat', 'miami'],
            'bucks': ['bucks', 'milwaukee'],
            'knicks': ['knicks', 'new york'],
            '76ers': ['76ers', 'sixers', 'philadelphia'],
            'cavaliers': ['cavaliers', 'cavs', 'cleveland'],
            'hawks': ['hawks', 'atlanta'],
            'magic': ['magic', 'orlando'],
            'raptors': ['raptors', 'toronto'],
            'pistons': ['pistons', 'detroit'],
            'bulls': ['bulls', 'chicago'],
            'hornets': ['hornets', 'charlotte'],
            'nets': ['nets', 'brooklyn'],
            'pacers': ['pacers', 'indiana'],
            'wizards': ['wizards', 'washington'],
            'rockets': ['rockets', 'houston'],
            'spurs': ['spurs', 'san antonio'],
            'timberwolves': ['timberwolves', 'wolves', 'minnesota'],
            'kings': ['kings', 'sacramento'],
            'pelicans': ['pelicans', 'new orleans'],
            'grizzlies': ['grizzlies', 'memphis'],
            'mavericks': ['mavericks', 'mavs', 'dallas'],
            'jazz': ['jazz', 'utah'],
            'trail blazers': ['trail blazers', 'blazers', 'portland'],
            'clippers': ['clippers', 'la clippers', 'los angeles clippers']
        }
        
        # Find team in question
        found_team = None
        for team_key, team_variations in team_map.items():
            if any(variation in question_lower for variation in team_variations):
                found_team = team_key
                break
        
        if not found_team:
            return None
        
        # Extract conference
        conference = None
        if 'west' in question_lower or 'western' in question_lower:
            conference = 'West'
        elif 'east' in question_lower or 'eastern' in question_lower:
            conference = 'East'
        
        return {
            'team': found_team,
            'conference': conference
        }
    
    def process_query(self, question: str) -> dict:
        """Process a standings query - uses NBA API Library first, then fallback"""
        question_lower = question.lower()
        
        # Check for games behind queries (e.g., "How far behind first place are the Celtics?")
        games_behind_info = self._extract_games_behind_query(question)
        if games_behind_info:
            logger.info(f"Detected games behind query: {games_behind_info['team']}")
            try:
                conference = games_behind_info.get('conference')
                if not conference:
                    # Try to determine conference from team name
                    team_name = games_behind_info.get('team', '').lower()
                    # Map teams to their conferences
                    western_teams = ['thunder', 'lakers', 'warriors', 'nuggets', 'suns', 'mavericks', 
                                    'clippers', 'rockets', 'spurs', 'timberwolves', 'kings', 'pelicans', 
                                    'grizzlies', 'jazz', 'trail blazers']
                    eastern_teams = ['celtics', 'heat', 'bucks', 'knicks', '76ers', 'cavaliers', 'hawks', 
                                    'magic', 'raptors', 'pistons', 'bulls', 'hornets', 'nets', 'pacers', 
                                    'wizards']
                    
                    if team_name in western_teams:
                        conference = 'West'
                    elif team_name in eastern_teams:
                        conference = 'East'
                    else:
                        # Default to East if team not found (shouldn't happen, but safety)
                        conference = 'East'
                
                # Get standings for the conference (only one API call now)
                standings = self.nba_api_lib.get_standings(conference)
                
                if standings:
                    # Find the team in standings
                    team_name = games_behind_info['team']
                    
                    # Team name variations for matching
                    team_variations = {
                        'thunder': ['thunder', 'okc'],
                        'lakers': ['lakers'],
                        'warriors': ['warriors'],
                        'celtics': ['celtics'],
                        'nuggets': ['nuggets'],
                        'suns': ['suns'],
                        'heat': ['heat'],
                        'bucks': ['bucks'],
                        'knicks': ['knicks'],
                        '76ers': ['76ers', 'sixers'],
                        'cavaliers': ['cavaliers', 'cavs'],
                        'hawks': ['hawks'],
                        'magic': ['magic'],
                        'raptors': ['raptors'],
                        'pistons': ['pistons'],
                        'bulls': ['bulls'],
                        'hornets': ['hornets'],
                        'nets': ['nets'],
                        'pacers': ['pacers'],
                        'wizards': ['wizards'],
                        'rockets': ['rockets'],
                        'spurs': ['spurs'],
                        'timberwolves': ['timberwolves', 'wolves'],
                        'kings': ['kings'],
                        'pelicans': ['pelicans'],
                        'grizzlies': ['grizzlies'],
                        'mavericks': ['mavericks', 'mavs'],
                        'jazz': ['jazz'],
                        'trail blazers': ['trail blazers', 'blazers'],
                        'clippers': ['clippers']
                    }
                    
                    team_found = None
                    for standing in standings:
                        team_name_in_standing = standing.get('team_name', '').lower()
                        variations = team_variations.get(team_name, [team_name])
                        # Check if any variation matches the team name in standings
                        if any(variation in team_name_in_standing or team_name_in_standing in variation for variation in variations):
                            team_found = standing
                            break
                        # Also check if team name key matches
                        if team_name in team_name_in_standing or team_name_in_standing in team_name:
                            team_found = standing
                            break
                    
                    if team_found:
                        games_back = team_found.get('games_back', 0)
                        team_rank = team_found.get('conference_rank', 0)
                        
                        # Find first place team
                        first_place_team = None
                        for standing in standings:
                            if standing.get('conference_rank') == 1:
                                first_place_team = standing
                                break
                        
                        return {
                            'type': 'standings',
                            'data': team_found,
                            'games_behind_query': True,
                            'team': team_name,
                            'games_back': games_back,
                            'rank': team_rank,
                            'first_place_team': first_place_team,
                            'conference': conference or team_found.get('conference', ''),
                            'query': question,
                            'source': 'nba_api_library'
                        }
            except Exception as e:
                logger.warning(f"Error processing games behind query: {e}")
        
        # Check for team position queries (e.g., "Are the Thunder still in the top 3?")
        team_position_info = self._extract_team_position_query(question)
        if team_position_info:
            logger.info(f"Detected team position query: {team_position_info['team']} in top {team_position_info['position']}")
            try:
                conference = team_position_info.get('conference')
                if not conference:
                    # Try to determine conference from team
                    team_name_lower = team_position_info['team'].lower()
                    western_teams = ['thunder', 'lakers', 'warriors', 'nuggets', 'suns', 'mavericks', 
                                    'clippers', 'rockets', 'spurs', 'timberwolves', 'kings', 'pelicans', 
                                    'grizzlies', 'jazz', 'trail blazers']
                    eastern_teams = ['celtics', 'heat', 'bucks', 'knicks', '76ers', 'cavaliers', 'hawks', 
                                    'magic', 'raptors', 'pistons', 'bulls', 'hornets', 'nets', 'pacers', 
                                    'wizards']
                    if team_name_lower in western_teams:
                        conference = 'West'
                    elif team_name_lower in eastern_teams:
                        conference = 'East'
                    else:
                        conference = 'West'  # Default
                
                # Try ESPN API first (PRIMARY)
                standings = None
                try:
                    from services.direct_espn_fetcher import DirectESPNFetcher
                    espn_fetcher = DirectESPNFetcher()
                    logger.info(f"🔍 ESPN API: Fetching {conference}ern Conference standings")
                    standings = espn_fetcher.get_standings(conference)
                    if standings:
                        logger.info(f"✓ Got {len(standings)} team standings from ESPN API")
                except Exception as e:
                    logger.warning(f"ESPN API failed: {e}, trying NBA API Library")
                
                # Fallback to NBA API Library
                if not standings:
                    logger.info(f"🔍 NBA API Library: Fetching {conference}ern Conference standings")
                    standings = self.nba_api_lib.get_standings(conference)
                    if standings:
                        logger.info(f"✓ Got {len(standings)} team standings from NBA API Library")
                
                if not standings and conference:
                    # Try the other conference as last resort
                    other_conf = 'East' if conference == 'West' else 'West'
                    logger.info(f"Trying {other_conf}ern Conference as fallback")
                    standings = self.nba_api_lib.get_standings(other_conf)
                    if standings:
                        conference = other_conf
                
                if standings:
                    # Find the team in standings
                    team_name = team_position_info['team']
                    target_position = team_position_info['position']
                    
                    # Team name variations for matching - includes full names for better matching
                    team_variations = {
                        'thunder': ['oklahoma city thunder', 'oklahoma city', 'thunder', 'okc'],
                        'lakers': ['los angeles lakers', 'lakers'],
                        'warriors': ['golden state warriors', 'golden state', 'warriors', 'gsw'],
                        'celtics': ['boston celtics', 'boston', 'celtics'],
                        'nuggets': ['denver nuggets', 'denver', 'nuggets'],
                        'suns': ['phoenix suns', 'phoenix', 'suns'],
                        'heat': ['miami heat', 'miami', 'heat'],
                        'bucks': ['milwaukee bucks', 'milwaukee', 'bucks'],
                        'knicks': ['new york knicks', 'new york', 'knicks'],
                        '76ers': ['philadelphia 76ers', 'philadelphia', 'sixers', '76ers'],
                        'cavaliers': ['cleveland cavaliers', 'cleveland', 'cavaliers', 'cavs'],
                        'hawks': ['atlanta hawks', 'atlanta', 'hawks'],
                        'magic': ['orlando magic', 'orlando', 'magic'],
                        'raptors': ['toronto raptors', 'toronto', 'raptors'],
                        'pistons': ['detroit pistons', 'detroit', 'pistons'],
                        'bulls': ['chicago bulls', 'chicago', 'bulls'],
                        'hornets': ['charlotte hornets', 'charlotte', 'hornets'],
                        'nets': ['brooklyn nets', 'brooklyn', 'nets'],
                        'pacers': ['indiana pacers', 'indiana', 'pacers'],
                        'wizards': ['washington wizards', 'washington', 'wizards'],
                        'rockets': ['houston rockets', 'houston', 'rockets'],
                        'spurs': ['san antonio spurs', 'san antonio', 'spurs'],
                        'timberwolves': ['minnesota timberwolves', 'minnesota', 'timberwolves', 'wolves'],
                        'kings': ['sacramento kings', 'sacramento', 'kings'],
                        'pelicans': ['new orleans pelicans', 'new orleans', 'pelicans'],
                        'grizzlies': ['memphis grizzlies', 'memphis', 'grizzlies'],
                        'mavericks': ['dallas mavericks', 'dallas', 'mavericks', 'mavs'],
                        'jazz': ['utah jazz', 'utah', 'jazz'],
                        'trail blazers': ['portland trail blazers', 'portland', 'trail blazers', 'blazers'],
                        'clippers': ['los angeles clippers', 'la clippers', 'clippers']
                    }
                    
                    team_found = None
                    for standing in standings:
                        team_name_in_standing = standing.get('team_name', '').lower()
                        variations = team_variations.get(team_name, [team_name])
                        
                        # Sort variations by length (longest first) for better matching
                        sorted_variations = sorted(variations, key=len, reverse=True)
                        
                        # Check if any variation matches the team name in standings
                        for variation in sorted_variations:
                            # Check if variation is in team name or vice versa
                            if variation in team_name_in_standing or team_name_in_standing in variation:
                                team_found = standing
                                break
                        
                        if team_found:
                            break
                        
                        # Fallback: check if key word matches (e.g., "thunder" in "Oklahoma City Thunder")
                        if team_name in team_name_in_standing:
                            team_found = standing
                            break
                    
                    if team_found:
                        actual_rank = team_found.get('conference_rank', 0)
                        wins = team_found.get('wins', 0)
                        losses = team_found.get('losses', 0)
                        win_pct = team_found.get('win_percentage', 0)
                        team_conference = team_found.get('conference', conference or '')
                        
                        # Validation: Ensure rank is valid (1-15 for each conference)
                        if actual_rank <= 0 or actual_rank > 15:
                            logger.warning(f"Invalid conference rank {actual_rank} for {team_name}. Recalculating...")
                            # Recalculate rank within conference
                            conf_teams = [s for s in standings if s.get('conference', '') == team_conference]
                            conf_teams.sort(key=lambda x: x.get('win_percentage', 0), reverse=True)
                            for idx, team in enumerate(conf_teams, 1):
                                if team.get('team_name', '').lower() == team_found.get('team_name', '').lower():
                                    actual_rank = idx
                                    team_found['conference_rank'] = actual_rank
                                    break
                        
                        # Validation: Ensure win/loss data is valid
                        if wins < 0 or losses < 0:
                            logger.warning(f"Invalid win/loss data for {team_name}: {wins}-{losses}")
                        
                        is_in_top = actual_rank <= target_position
                        
                        logger.info(f"✓ Validated result: {team_name} is ranked {actual_rank} in {team_conference} ({'IN' if is_in_top else 'NOT IN'} top {target_position})")
                        
                        return {
                            'type': 'standings',
                            'data': team_found,
                            'team_position_query': True,
                            'team': team_name,
                            'target_position': target_position,
                            'actual_rank': actual_rank,
                            'is_in_top': is_in_top,
                            'wins': wins,
                            'losses': losses,
                            'win_percentage': win_pct,
                            'conference': team_conference,
                            'query': question,
                            'source': 'espn_api' if standings and any('espn' in str(s).lower() for s in standings) else 'nba_api_library'
                        }
                    else:
                        logger.warning(f"Could not find {team_name} in {conference}ern Conference standings")
            except Exception as e:
                logger.error(f"Error processing team position query: {e}", exc_info=True)
            except Exception as e:
                logger.warning(f"Error processing team position query: {e}")
        
        # Check for playoff spot queries (teams ranked 1-6 in each conference)
        is_playoff_query = any(phrase in question_lower for phrase in [
            'playoff spot', 'playoff spots', 'playoff position', 'in the playoff',
            'in playoffs', 'playoff teams'
        ]) and 'out' not in question_lower
        
        # Check for out of playoffs queries (teams ranked 11-15)
        is_out_of_playoffs_query = any(phrase in question_lower for phrase in [
            'out of playoff', 'out of playoffs', 'out of the playoff', 'out of the playoffs',
            'eliminated', 'not in playoff', 'not in playoffs', 'missed playoff',
            'missed playoffs', 'eliminated from playoff'
        ])
        
        # Check for play-in queries (teams ranked 7-10 in each conference)
        is_playin_query = any(phrase in question_lower for phrase in [
            'play-in', 'playin', 'play in', 'play-in positions', 'play-in tournament'
        ]) and not is_playoff_query and not is_out_of_playoffs_query
        
        if is_playoff_query:
            logger.info("Detected playoff spots query")
            # Get standings for both conferences
            try:
                east_standings = self.nba_api_lib.get_standings('East')
                west_standings = self.nba_api_lib.get_standings('West')
                
                if east_standings and west_standings:
                    # Filter for teams ranked 1-6 (playoff positions)
                    east_playoff = [team for team in east_standings if 1 <= team.get('conference_rank', 0) <= 6]
                    west_playoff = [team for team in west_standings if 1 <= team.get('conference_rank', 0) <= 6]
                    
                    # Sort by rank
                    east_playoff.sort(key=lambda x: x.get('conference_rank', 0))
                    west_playoff.sort(key=lambda x: x.get('conference_rank', 0))
                    
                    logger.info(f"Found {len(east_playoff)} Eastern and {len(west_playoff)} Western playoff teams")
                    
                    return {
                        'type': 'standings',
                        'data': {
                            'east': east_playoff,
                            'west': west_playoff
                        },
                        'playoff': True,
                        'query': question,
                        'source': 'nba_api_library'
                    }
            except Exception as e:
                logger.warning(f"Error getting playoff teams: {e}")
        
        elif is_out_of_playoffs_query:
            logger.info("Detected out of playoffs query")
            # Get standings for both conferences
            try:
                east_standings = self.nba_api_lib.get_standings('East')
                west_standings = self.nba_api_lib.get_standings('West')
                
                if east_standings and west_standings:
                    # Filter for teams ranked 11-15 (out of playoffs)
                    east_out = [team for team in east_standings if 11 <= team.get('conference_rank', 0) <= 15]
                    west_out = [team for team in west_standings if 11 <= team.get('conference_rank', 0) <= 15]
                    
                    # Sort by rank
                    east_out.sort(key=lambda x: x.get('conference_rank', 0))
                    west_out.sort(key=lambda x: x.get('conference_rank', 0))
                    
                    logger.info(f"Found {len(east_out)} Eastern and {len(west_out)} Western teams out of playoffs")
                    
                    return {
                        'type': 'standings',
                        'data': {
                            'east': east_out,
                            'west': west_out
                        },
                        'out_of_playoffs': True,
                        'query': question,
                        'source': 'nba_api_library'
                    }
            except Exception as e:
                logger.warning(f"Error getting teams out of playoffs: {e}")
        
        elif is_playin_query:
            logger.info("Detected play-in tournament query")
            # Get standings for both conferences
            try:
                east_standings = self.nba_api_lib.get_standings('East')
                west_standings = self.nba_api_lib.get_standings('West')
                
                if east_standings and west_standings:
                    # Filter for teams ranked 7-10 (play-in positions)
                    east_playin = [team for team in east_standings if 7 <= team.get('conference_rank', 0) <= 10]
                    west_playin = [team for team in west_standings if 7 <= team.get('conference_rank', 0) <= 10]
                    
                    # Sort by rank
                    east_playin.sort(key=lambda x: x.get('conference_rank', 0))
                    west_playin.sort(key=lambda x: x.get('conference_rank', 0))
                    
                    logger.info(f"Found {len(east_playin)} Eastern and {len(west_playin)} Western play-in teams")
                    
                    return {
                        'type': 'standings',
                        'data': {
                            'east': east_playin,
                            'west': west_playin
                        },
                        'playin': True,
                        'query': question,
                        'source': 'nba_api_library'
                    }
            except Exception as e:
                logger.warning(f"Error getting play-in teams: {e}")
        
        # Check for seed queries (e.g., "10th seed", "1st seed")
        seed_number = None
        if 'seed' in question_lower:
            seed_number = self._extract_seed_number(question)
            if seed_number:
                logger.info(f"Detected seed query: {seed_number}th seed")
        
        # Try NBA API Library first (official NBA data with proper conference info)
        try:
            logger.info("🔍 NBA API Library: Fetching standings")
            
            # Determine conference filter
            conference_filter = None
            if 'eastern' in question_lower or 'east' in question_lower:
                conference_filter = 'East'
            elif 'western' in question_lower or 'west' in question_lower:
                conference_filter = 'West'
            
            # Get standings from NBA API
            nba_standings = self.nba_api_lib.get_standings(conference_filter)
            
            if nba_standings:
                logger.info(f"✓ Got {len(nba_standings)} team standings from NBA API Library")
                
                # Handle seed queries - find team at specific seed position
                if seed_number:
                    # Filter by conference if specified
                    filtered_standings = nba_standings
                    if conference_filter:
                        filtered_standings = [s for s in nba_standings if conference_filter in str(s.get('conference', ''))]
                    
                    # Find team at the specified seed (conference_rank should match seed number)
                    seed_team = None
                    for standing in filtered_standings:
                        if standing.get('conference_rank') == seed_number:
                            seed_team = standing
                            break
                    
                    if seed_team:
                        logger.info(f"✓ Found {seed_number}th seed: {seed_team.get('team_name')}")
                        return {
                            'type': 'standings',
                            'data': [seed_team],
                            'seed': seed_number,
                            'conference': conference_filter if conference_filter else None,
                            'query': question,
                            'source': 'nba_api_library'
                        }
                    else:
                        logger.warning(f"Could not find {seed_number}th seed in {conference_filter or 'all'} conference")
                        return {
                            'type': 'standings',
                            'data': [],
                            'error': f"Could not find the {seed_number}th seed in the {conference_filter or 'NBA'} conference.",
                            'seed': seed_number,
                            'conference': conference_filter if conference_filter else None,
                            'query': question,
                            'source': 'nba_api_library'
                        }
                
                # Extract team names for filtering
                teams = [
                    'lakers', 'warriors', 'celtics', 'bucks', 'nuggets', 'suns', 'heat',
                    'mavericks', 'clippers', '76ers', 'cavaliers', 'knicks', 'hawks',
                    'thunder', 'timberwolves', 'kings', 'pelicans', 'grizzlies', 'raptors',
                    'nets', 'bulls', 'pistons', 'pacers', 'hornets', 'magic', 'wizards',
                    'trail blazers', 'jazz', 'rockets', 'spurs'
                ]
                
                found_teams = [team for team in teams if team in question_lower]
                
                # Filter by team if specified
                if found_teams:
                    team_name_lower = found_teams[0].lower()
                    # Try to match team name in standings
                    filtered = []
                    for standing in nba_standings:
                        team_name = standing.get('team_name', '').lower()
                        if team_name_lower in team_name or any(word in team_name for word in team_name_lower.split()):
                            filtered.append(standing)
                            break
                    
                    if filtered:
                        return {
                            'type': 'standings',
                            'data': filtered,
                            'team': found_teams[0],
                            'query': question,
                            'source': 'nba_api_library'
                        }
                
                # Return conference standings or all standings
                return {
                    'type': 'standings',
                    'data': nba_standings,
                    'conference': conference_filter if conference_filter else None,
                    'query': question,
                    'source': 'nba_api_library'
                }
        except Exception as e:
            logger.warning(f"NBA API Library fetch failed, trying ESPN API: {e}")
        
        # Fallback to ESPN API
        try:
            api_standings = self.api_service.get_standings()
            
            if api_standings:
                # Extract team names
                teams = [
                    'lakers', 'warriors', 'celtics', 'bucks', 'nuggets', 'suns', 'heat',
                    'mavericks', 'clippers', '76ers', 'cavaliers', 'knicks', 'hawks',
                    'thunder', 'timberwolves', 'kings', 'pelicans', 'grizzlies', 'raptors',
                    'nets', 'bulls', 'pistons', 'pacers', 'hornets', 'magic', 'wizards',
                    'trail blazers', 'jazz', 'rockets', 'spurs'
                ]
                
                found_teams = [team for team in teams if team in question_lower]
                
                # Filter by team if specified
                if found_teams:
                    team_abbrev = found_teams[0][:3].upper() if len(found_teams[0]) >= 3 else found_teams[0].upper()
                    filtered = [s for s in api_standings if team_abbrev in s.get('team_name', '')]
                    if filtered:
                        return {
                            'type': 'standings',
                            'data': filtered,
                            'team': found_teams[0],
                            'query': question,
                            'source': 'api'
                        }
                
                # Filter by conference if specified (ESPN doesn't have conference, so approximate)
                if 'eastern' in question_lower or 'east' in question_lower:
                    return {
                        'type': 'standings',
                        'data': api_standings[:15],  # Top 15 for Eastern (approximation)
                        'conference': 'East',
                        'query': question,
                        'source': 'api'
                    }
                elif 'western' in question_lower or 'west' in question_lower:
                    return {
                        'type': 'standings',
                        'data': api_standings[15:],  # Bottom 15 for Western (approximation)
                        'conference': 'West',
                        'query': question,
                        'source': 'api'
                    }
                
                return {
                    'type': 'standings',
                    'data': api_standings,
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
        
        if 'eastern' in question_lower or 'east' in question_lower:
            standings = self.get_conference_standings('East')
            return {
                'type': 'standings',
                'data': standings,
                'conference': 'East',
                'query': question,
                'source': 'database'
            }
        elif 'western' in question_lower or 'west' in question_lower:
            standings = self.get_conference_standings('West')
            return {
                'type': 'standings',
                'data': standings,
                'conference': 'West',
                'query': question,
                'source': 'database'
            }
        elif found_teams:
            standing = self.get_team_standing(found_teams[0])
            return {
                'type': 'standings',
                'data': [standing] if standing else [],
                'team': found_teams[0],
                'query': question,
                'source': 'database'
            }
        else:
            standings = self.get_conference_standings()
            return {
                'type': 'standings',
                'data': standings,
                'query': question,
                'source': 'database'
            }

