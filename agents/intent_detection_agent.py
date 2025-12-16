"""
Intent Detection Agent
Determines the type of query: match_stats, player_stats, schedule, articles, or mixed
"""
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntentDetectionAgent:
    """Detects user intent from questions"""
    
    def __init__(self):
        # Keywords for different intents
        self.match_keywords = [
            'score', 'result', 'game', 'match', 'won', 'lost', 'beat', 'defeated',
            'final score', 'who won', 'outcome', 'victory', 'defeat', 'results',
            'yesterday', 'yesterday games', 'yesterday results'
        ]
        
        self.player_keywords = [
            'points', 'rebounds', 'assists', 'steals', 'blocks', 'stats', 'statistics',
            'performance', 'how many', 'how much', 'scored', 'player', 'players', 'stat line', 
            'triple-double', 'double-double', 'double double', 'triple double', 'recent', 'latest',
            'top', 'leading', 'leader', 'leaders'
        ]
        
        self.schedule_keywords = [
            'schedule', 'upcoming', 'next game', 'when', 'date', 'time', 'fixture',
            'play', 'match', 'game', 'upcoming match', 'next match', 'tomorrow', 'today',
            'nba schedule', 'nba schedules', 'fixtures', 'games schedule', 'games for today',
            'schedule today', 'schedules for today', 'games today', 'nba games today',
            'schedule yesterday', 'nba schedule yesterday', 'games yesterday', 'yesterday games',
            'schedules for yesterday', 'nba schedules for yesterday'
        ]
        
        self.article_keywords = [
            'analysis', 'opinion', 'news', 'article', 'articles', 'breakdown', 'explain', 'why',
            'what happened', 'story', 'report', 'coverage', 'insight', 'perspective',
            'what does', 'what do', 'say about', 'says about', 'mentioned', 'discussed'
        ]
        
        self.live_game_keywords = [
            'live', 'currently playing', 'in progress', 'right now', 'happening now',
            'current game', 'ongoing', 'playing now'
        ]
        
        self.standings_keywords = [
            'standings', 'ranking', 'rank', 'position', 'record', 'wins', 'losses',
            'conference', 'division', 'leader', 'top team', 'best record', 'current',
            'nba standing', 'nba standings', 'league standing', 'league standings',
            'seed', 'seeds', '1st seed', '2nd seed', '3rd seed', '10th seed',
            'play-in', 'playin', 'play in', 'play-in positions', 'play-in tournament',
            'playoff', 'playoffs', 'playoff spot', 'playoff spots', 'playoff position',
            'out of playoff', 'out of playoffs', 'eliminated', 'not in playoff'
        ]
        
        self.injury_keywords = [
            'injury', 'injured', 'hurt', 'out', 'questionable', 'probable',
            'injury report', 'health', 'status', 'day-to-day'
        ]
        
        self.trend_keywords = [
            'trend', 'trending', 'recent form', 'lately', 'recently', 'improving',
            'declining', 'hot streak', 'cold streak', 'performance trend'
        ]
        
        self.season_avg_keywords = [
            'season average', 'season stats', 'averages', 'per game', 'season long',
            'yearly', 'overall', 'total stats', 'season averages', 'ppg', 'rpg', 'apg',
            'this season', 'season total', 'count', 'how many this season'
        ]
        
        self.team_news_keywords = [
            'news', 'update', 'report', 'announcement', 'breaking', 'trade', 'signing',
            'roster', 'coaching', 'transaction'
        ]
        
        self.team_scoring_leader_keywords = [
            'led the scoring', 'led scoring', 'leading scorer', 'top scorer',
            'most points', 'highest scorer', 'team leading scorer', 'scoring leader',
            'who led', 'who led the', 'who led the scoring', 'who scored the most',
            'who led in', 'who led the scoring in', 'scoring leader in', 'leading scorer in'
        ]
        
        self.general_keywords = [
            'hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening',
            'what can you do', 'what do you do', 'what are you', 'who are you', 'help',
            'capabilities', 'features', 'what questions', 'what can i ask', 'how can you help',
            'what do you know', 'what information', 'tell me about yourself', 'introduce yourself'
        ]
    
    def detect_intent(self, question: str) -> str:
        """
        Detect intent from user question
        Returns: 'general', 'match_stats', 'player_stats', 'schedule', 'date_schedule', 'articles',
                 'live_game', 'standings', 'injuries', 'player_trend', 'season_averages',
                 'team_news', 'team_scoring_leader', or 'mixed'
        """
        question_lower = question.lower().strip()
        
        # Check for general/greeting questions FIRST (high priority)
        general_score = sum(1 for keyword in self.general_keywords if keyword in question_lower)
        if general_score > 0:
            logger.info(f"✓ Detected general/greeting intent for query: '{question}'")
            return 'general'
        
        # Check for "top N players" queries (HIGH PRIORITY - these are always player_stats)
        # Examples: "top 5 players", "top 10 players by points", "top players in assists"
        has_top_players = (
            ('top' in question_lower and 'player' in question_lower) or
            ('top' in question_lower and any(stat in question_lower for stat in ['points', 'assists', 'rebounds', 'blocks', 'steals', 'ppg', 'rpg', 'apg', 'field goal', 'field goal percentage', 'fg%', 'shooting percentage', '3 pointer', 'three pointer', '3-pointers made', 'three-pointers made', '3pm', '3 pointer percentage', 'three pointer percentage', '3pt percentage', '3pt%', '3p%']))
        )
        if has_top_players:
            return 'player_stats'
        
        # Check for triple-double / double-double queries with player names (high priority)
        has_double_query = any(phrase in question_lower for phrase in ['triple-double', 'triple double', 'double-double', 'double double'])
        player_names = [
            'lebron', 'james', 'curry', 'durant', 'giannis', 'tatum', 'jokic',
            'luka', 'doncic', 'embiid', 'butler', 'antetokounmpo', 'davis',
            'booker', 'mitchell', 'morant', 'edwards', 'haliburton', 'fox',
            'young', 'brown', 'siakam', 'randle', 'brunson', 'maxey', 'murray',
            'wembanyama', 'victor', 'holmgren', 'banchero', 'cunningham'
        ]
        has_player_name = any(name in question_lower for name in player_names)
        
        # If asking about triple/double-doubles for a specific player, it's always player_stats
        # (player_stats will handle counting triple-doubles from available data)
        if has_double_query and has_player_name:
            return 'player_stats'
        
        # Check for team scoring leader first (high priority) - BEFORE counting other keywords
        # This prevents "game" from matching match_keywords when it's clearly a scoring leader query
        team_scoring_leader_score = sum(1 for keyword in self.team_scoring_leader_keywords if keyword in question_lower)
        logger.info(f"Team scoring leader keyword score: {team_scoring_leader_score} for query: '{question}'")
        
        # Also check for patterns like "who led [team] [latest/recent] game" or "scoring leader [team] [game]"
        if team_scoring_leader_score == 0:
            # Check for "who led" + team + "game" pattern - more flexible matching
            has_who_led = any(phrase in question_lower for phrase in ['who led', 'who scored', 'leading scorer', 'top scorer', 'scoring leader'])
            has_game = any(phrase in question_lower for phrase in ['game', 'match', 'latest game', 'recent game', 'last game'])
            has_team = any(team in question_lower for team in ['lakers', 'warriors', 'celtics', 'bucks', 'nuggets', 'suns', 'heat',
                'mavericks', 'clippers', '76ers', 'cavaliers', 'knicks', 'hawks', 'thunder', 'timberwolves', 
                'kings', 'pelicans', 'grizzlies', 'raptors', 'nets', 'bulls', 'pistons', 'pacers', 'hornets', 
                'magic', 'wizards', 'trail blazers', 'jazz', 'rockets', 'spurs'])
            
            if has_who_led and has_game and has_team:
                team_scoring_leader_score = 3  # High score to ensure it wins
                logger.info(f"✓ Detected team scoring leader pattern: has_who_led={has_who_led}, has_game={has_game}, has_team={has_team}")
        
        # If team scoring leader keywords found, return immediately (BEFORE counting match keywords)
        if team_scoring_leader_score > 0:
            logger.info(f"✓ Returning 'team_scoring_leader' intent for query: '{question}'")
            return 'team_scoring_leader'
        
        # Check for "top N" with team/conference queries (HIGH PRIORITY - these are standings)
        # Examples: "Are the Thunder still in the top 3 of the West?", "Is team in top 5?"
        has_top_number = bool(re.search(r'top\s+\d+', question_lower))
        has_team_for_top = any(team in question_lower for team in [
            'thunder', 'lakers', 'warriors', 'celtics', 'bucks', 'nuggets', 'suns', 'heat',
            'mavericks', 'clippers', '76ers', 'cavaliers', 'knicks', 'hawks',
            'timberwolves', 'kings', 'pelicans', 'grizzlies', 'raptors', 'nets', 'bulls',
            'pistons', 'pacers', 'hornets', 'magic', 'wizards', 'trail blazers', 'jazz',
            'rockets', 'spurs', 'oklahoma city', 'golden state', 'los angeles', 'boston',
            'milwaukee', 'denver', 'phoenix', 'miami', 'dallas', 'philadelphia', 'cleveland',
            'new york', 'atlanta', 'oklahoma', 'minnesota', 'sacramento', 'new orleans',
            'memphis', 'toronto', 'brooklyn', 'chicago', 'detroit', 'indiana', 'charlotte',
            'orlando', 'washington', 'portland', 'utah', 'houston', 'san antonio'
        ])
        has_conference = any(word in question_lower for word in ['west', 'east', 'western', 'eastern', 'conference'])
        if has_top_number and (has_team_for_top or has_conference):
            logger.info(f"✓ Detected 'top N' team/conference query as standings: '{question}'")
            return 'standings'
        
        # Check for "did [team] win" queries (HIGH PRIORITY - these are always match_stats)
        # Examples: "Did the Knicks win their most recent game?", "Did the Lakers win their last game?"
        has_did_win = any(phrase in question_lower for phrase in ['did', 'win', 'won', 'lose', 'lost'])
        has_recent_game = any(phrase in question_lower for phrase in ['most recent game', 'last game', 'latest game', 'most recent', 'last match', 'latest match'])
        
        # Check for "last N games" or "recent games" queries (multiple game results)
        has_multiple_games = (
            any(phrase in question_lower for phrase in ['last', 'recent', 'previous', 'past']) and
            any(phrase in question_lower for phrase in ['games', 'game results', 'results', 'matches', 'matchups']) and
            (any(num in question_lower for num in ['5', 'five', '10', 'ten', '3', 'three', '4', 'four']) or
             'show me' in question_lower or 'give me' in question_lower or 'what are' in question_lower)
        )
        has_team_for_win = any(team in question_lower for team in [
            'lakers', 'warriors', 'celtics', 'bucks', 'nuggets', 'suns', 'heat',
            'mavericks', 'clippers', '76ers', 'cavaliers', 'knicks', 'hawks',
            'thunder', 'timberwolves', 'kings', 'pelicans', 'grizzlies', 'raptors',
            'nets', 'bulls', 'pistons', 'pacers', 'hornets', 'magic', 'wizards',
            'trail blazers', 'jazz', 'rockets', 'spurs'
        ])
        
        if has_multiple_games and has_team_for_win:
            return 'match_stats'
        
        # Check for "lose by" or "lost by" queries (point differential for losses)
        has_lose_by = any(phrase in question_lower for phrase in [
            'lose by', 'lost by', 'losing by', 'points did', 'how many points'
        ]) and ('lose' in question_lower or 'lost' in question_lower)
        
        if has_lose_by and has_team_for_win:
            logger.info(f"✓ Detected 'lose by' pattern - returning 'match_stats'")
            return 'match_stats'
        
        if has_did_win and has_recent_game and has_team_for_win:
            logger.info(f"✓ Detected 'did [team] win' pattern - returning 'match_stats'")
            return 'match_stats'
        
        # Count keyword matches for each intent (only if not team_scoring_leader or did_win_query)
        match_score = sum(1 for keyword in self.match_keywords if keyword in question_lower)
        player_score = sum(1 for keyword in self.player_keywords if keyword in question_lower)
        schedule_score = sum(1 for keyword in self.schedule_keywords if keyword in question_lower)
        article_score = sum(1 for keyword in self.article_keywords if keyword in question_lower)
        live_game_score = sum(1 for keyword in self.live_game_keywords if keyword in question_lower)
        standings_score = sum(1 for keyword in self.standings_keywords if keyword in question_lower)
        injury_score = sum(1 for keyword in self.injury_keywords if keyword in question_lower)
        trend_score = sum(1 for keyword in self.trend_keywords if keyword in question_lower)
        season_avg_score = sum(1 for keyword in self.season_avg_keywords if keyword in question_lower)
        team_news_score = sum(1 for keyword in self.team_news_keywords if keyword in question_lower)
        
        # Check for date-specific schedule queries
        # CRITICAL: Prioritize "tomorrow" queries very highly
        # Handle common typos: "tommorow", "tomorow", "tomarrow", etc.
        date_keywords = ['today', 'tomorrow', 'yesterday', 'next week', 'this week']
        has_date = any(keyword in question_lower for keyword in date_keywords)
        
        # Check for "tomorrow" with typo handling (tommorow, tomorow, tomarrow, etc.)
        # Common typos: tommorow, tomorow, tomarrow, tommorrow
        has_tomorrow = (
            'tomorrow' in question_lower or 
            'tommorow' in question_lower or 
            'tomorow' in question_lower or
            'tomarrow' in question_lower or
            'tommorrow' in question_lower
        ) and 'day after' not in question_lower
        
        has_day_after = 'day after tomorrow' in question_lower or 'day after' in question_lower
        
        # If "tomorrow" (or common typo) is mentioned, ALWAYS return 'date_schedule' immediately
        if has_tomorrow or has_day_after:
            logger.info(f"CRITICAL: Query contains 'tomorrow' (or variant) - returning 'date_schedule' intent immediately")
            return 'date_schedule'
        
        date_schedule_score = schedule_score + (5 if has_date else 0)  # Increased boost from 3 to 5
        
        # Check for team names
        team_names = [
            'lakers', 'warriors', 'celtics', 'bucks', 'nuggets', 'suns', 'heat',
            'mavericks', 'clippers', '76ers', 'cavaliers', 'knicks', 'hawks',
            'thunder', 'timberwolves', 'kings', 'pelicans', 'grizzlies', 'raptors'
        ]
        has_team_name = any(team in question_lower for team in team_names)
        
        # Check for "season" keyword (indicates season stats)
        has_season = 'season' in question_lower
        
        # Check for "recent" or "latest" with player names (indicates player stats)
        has_recent = 'recent' in question_lower or 'latest' in question_lower
        
        # Check for explicit article keywords first
        explicit_article_phrases = ['what does', 'what do', 'say about', 'says about', 'article', 'articles']
        has_explicit_article = any(phrase in question_lower for phrase in explicit_article_phrases)
        
        # Determine intent based on scores and context
        scores = {
            'match_stats': match_score,
            'player_stats': player_score + (2 if has_player_name and not has_season else 0) + (3 if has_recent and has_player_name else 0),
            'schedule': schedule_score if not has_date else 0,
            'date_schedule': date_schedule_score,
            'live_game': live_game_score + (2 if 'live' in question_lower else 0),
            'standings': standings_score,
            'injuries': injury_score,
            'player_trend': trend_score + (2 if has_player_name else 0),
            'season_averages': season_avg_score + (5 if has_season and has_player_name else 2 if has_player_name else 0),
            'team_news': team_news_score,
            'articles': article_score + (5 if has_explicit_article else 0)  # Boost article score if explicit
        }
        
        max_score = max(scores.values())
        
        # If "articles" or "article" is explicitly mentioned, prioritize it
        if has_explicit_article and scores['articles'] > 0:
            return 'articles'
        
        # If multiple intents have high scores AND they're close, it's mixed
        # But if one is clearly higher (by more than 2 points), it's not mixed
        high_scores = [intent for intent, score in scores.items() if score > 0 and score >= max_score * 0.5]
        
        if len(high_scores) > 1 and not has_explicit_article:
            # Check if the scores are close (within 2 points of each other)
            # Only return "mixed" if they're within 2 points
            # If one is clearly higher (3+ points), return the winner
            min_high_score = min([scores[intent] for intent in high_scores])
            if max_score - min_high_score <= 2:  # Scores are close - truly mixed
                return 'mixed'
            # Difference is >= 3, so one is clearly winning - fall through to return max
        
        if max_score == 0:
            # Default to articles if no clear intent
            return 'articles'
        
        # Return intent with highest score
        return max(scores, key=scores.get)

