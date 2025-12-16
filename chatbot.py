"""
Chatbot Orchestration Engine
Main logic that routes queries to appropriate agents and formats responses
Now includes real-time agents for live games, standings, injuries, trends, and news
"""
import logging
from agents.intent_detection_agent import IntentDetectionAgent
from agents.stats_agent import StatsAgent
from agents.player_stats_agent import PlayerStatsAgent
from agents.schedule_agent import ScheduleAgent
from agents.article_search_agent import ArticleSearchAgent
from agents.response_formatter_agent import ResponseFormatterAgent
from agents.live_game_agent import LiveGameAgent
from agents.standings_agent import StandingsAgent
from agents.injury_report_agent import InjuryReportAgent
from agents.player_trend_agent import PlayerTrendAgent
from agents.season_averages_agent import SeasonAveragesAgent
from agents.team_news_agent import TeamNewsAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BasketballChatbot:
    """Main chatbot orchestration engine"""
    
    def __init__(self):
        self.intent_agent = IntentDetectionAgent()
        self.stats_agent = StatsAgent()
        self.player_stats_agent = PlayerStatsAgent()
        self.schedule_agent = ScheduleAgent()
        self.article_agent = ArticleSearchAgent()
        self.live_game_agent = LiveGameAgent()
        self.standings_agent = StandingsAgent()
        self.injury_agent = InjuryReportAgent()
        self.trend_agent = PlayerTrendAgent()
        self.season_avg_agent = SeasonAveragesAgent()
        self.team_news_agent = TeamNewsAgent()
        self.formatter_agent = ResponseFormatterAgent()
    
    def process_question(self, question: str) -> str:
        """
        Process a user question and return a formatted answer
        
        Workflow:
        1. Detect intent
        2. Route to appropriate agent(s)
        3. Format response using LLM
        4. Return natural answer
        """
        try:
            # Step 1: Detect intent
            intent = self.intent_agent.detect_intent(question)
            logger.info(f"Detected intent: {intent}")
            
            # Step 2: Route to appropriate agent(s)
            intent_data = None
            article_data = None
            
            # Handle general/greeting questions first
            if intent == 'general':
                return self._handle_general_question(question)
            
            elif intent == 'match_stats':
                intent_data = self.stats_agent.process_query(question)
            
            elif intent == 'player_stats':
                intent_data = self.player_stats_agent.process_query(question)
            
            elif intent == 'schedule':
                intent_data = self.schedule_agent.process_query(question)
            
            elif intent == 'date_schedule':
                intent_data = self.schedule_agent.process_query(question)
            
            elif intent == 'live_game':
                intent_data = self.live_game_agent.process_query(question)
            
            elif intent == 'standings':
                intent_data = self.standings_agent.process_query(question)
            
            elif intent == 'injuries':
                intent_data = self.injury_agent.process_query(question)
            
            elif intent == 'player_trend':
                intent_data = self.trend_agent.process_query(question)
            
            elif intent == 'season_averages':
                # Try player_stats_agent first (has better query handling)
                # Fall back to season_avg_agent if needed
                intent_data = self.player_stats_agent.process_query(question)
                # Only fall back if player_stats_agent didn't return any intent_data structure
                # (e.g., returned None), not if it returned empty data
                if not intent_data:
                    intent_data = self.season_avg_agent.process_query(question)
            
            elif intent == 'team_news':
                intent_data = self.team_news_agent.process_query(question)
            
            elif intent == 'team_scoring_leader':
                # Handle who led the scoring queries
                intent_data = self.player_stats_agent.process_query(question)
            
            elif intent == 'articles':
                # Check if this is actually a standings query first
                # Only redirect if it's explicitly about standings/rankings, not just because a team is mentioned
                question_lower = question.lower()
                is_standings_query = any(word in question_lower for word in ['standings', 'ranking', 'rank', 'record', 'playoff', 'playoffs', 'play-in', 'playin', 'top', 'position', 'seed', 'conference'])
                
                # Only redirect to standings if it's explicitly about standings AND not asking about articles
                if is_standings_query and 'article' not in question_lower and 'say' not in question_lower:
                    # This is actually a standings query, not an article query
                    intent_data = self.standings_agent.process_query(question)
                else:
                    # For article queries, get article data
                    article_result = self.article_agent.process_query(question)
                    # Article agent returns data in 'data' field with 'combined_text'
                    if article_result.get('data') or article_result.get('combined_text'):
                        article_data = article_result
                        # Create a minimal intent_data so validation passes
                        intent_data = {
                            'type': 'articles',
                            'data': article_result.get('data', []),
                            'query': question
                        }
                    else:
                        intent_data = {
                            'type': 'articles',
                            'data': [],
                            'query': question,
                            'error': 'No articles found'
                        }
            
            elif intent == 'mixed':
                # Handle mixed queries - get both stats and articles
                # Try to determine primary intent
                question_lower = question.lower()
                
                # Check for article keywords first
                if any(phrase in question_lower for phrase in ['what does', 'what do', 'say about', 'says about', 'article', 'articles']):
                    article_result = self.article_agent.process_query(question)
                    if article_result.get('data') or article_result.get('combined_text'):
                        article_data = article_result
                        intent_data = {
                            'type': 'articles',
                            'data': article_result.get('data', []),
                            'query': question
                        }
                    else:
                        intent_data = {'type': 'articles', 'data': [], 'query': question}
                elif any(word in question_lower for word in ['schedule', 'nba schedule', 'fixtures', 'upcoming games']):
                    intent_data = self.schedule_agent.process_query(question)
                elif any(phrase in question_lower for phrase in ['win by', 'won by', 'winning by', 'lose by', 'lost by', 'losing by', 'defeated by', 'beat by']) and 'points' in question_lower:
                    # Point differential queries go to stats agent
                    intent_data = self.stats_agent.process_query(question)
                elif any(word in question_lower for word in ['points', 'rebounds', 'assists', 'blocks', 'steals']):
                    # Check for player stats keywords first (before general score/result)
                    intent_data = self.player_stats_agent.process_query(question)
                elif any(word in question_lower for word in ['yesterday', 'yesterday games', 'yesterday results']):
                    intent_data = self.stats_agent.process_query(question)
                elif any(word in question_lower for word in ['score', 'result', 'won', 'lost', 'win', 'lose', 'outcome', 'final score']) or ('did' in question_lower and ('win' in question_lower or 'lose' in question_lower)) or ('result of' in question_lower and ('last game' in question_lower or 'previous game' in question_lower)) or (any(team in question_lower for team in ['lakers', 'warriors', 'celtics', 'bucks', 'nuggets', 'suns', 'heat', 'mavericks', 'clippers', '76ers', 'cavaliers', 'knicks', 'hawks', 'thunder', 'timberwolves', 'kings', 'pelicans', 'grizzlies', 'raptors', 'nets', 'bulls', 'pistons', 'pacers', 'hornets', 'magic', 'wizards', 'rockets', 'spurs']) and ('last game' in question_lower or 'previous game' in question_lower or 'yesterday' in question_lower) and ('result' in question_lower or 'score' in question_lower)):
                    intent_data = self.stats_agent.process_query(question)
                elif any(word in question_lower for word in ['next', 'upcoming', 'when', 'today', 'tomorrow']):
                    intent_data = self.schedule_agent.process_query(question)
                elif any(word in question_lower for word in ['live', 'currently', 'in progress']):
                    intent_data = self.live_game_agent.process_query(question)
                elif any(word in question_lower for word in ['standings', 'ranking', 'rank', 'record', 'playoff', 'playoffs', 'play-in', 'playin', 'top', 'position']) or any(team in question_lower for team in ['thunder', 'lakers', 'warriors', 'celtics', 'nuggets', 'suns', 'heat', 'bucks', 'knicks', '76ers', 'cavaliers', 'hawks', 'magic', 'raptors', 'pistons', 'bulls', 'hornets', 'nets', 'pacers', 'wizards', 'rockets', 'spurs', 'timberwolves', 'kings', 'pelicans', 'grizzlies', 'mavericks', 'jazz', 'trail blazers', 'clippers']):
                    intent_data = self.standings_agent.process_query(question)
                elif any(word in question_lower for word in ['injury', 'injured']) and 'out of playoff' not in question_lower and 'out of playoffs' not in question_lower:
                    intent_data = self.injury_agent.process_query(question)
                elif any(word in question_lower for word in ['trend', 'recently', 'lately']):
                    intent_data = self.trend_agent.process_query(question)
                elif any(word in question_lower for word in ['season average', 'averages']):
                    intent_data = self.season_avg_agent.process_query(question)
                elif any(word in question_lower for word in ['news', 'update', 'breaking']):
                    intent_data = self.team_news_agent.process_query(question)
                else:
                    intent_data = self.stats_agent.process_query(question)
                
                # Also get article context if relevant
                if any(word in question_lower for word in ['analysis', 'opinion', 'explain']) and not article_data:
                    article_data = self.article_agent.process_query(question)
            
            # Step 3: Validate data before formatting
            # For article queries, check article_data instead of intent_data
            if intent_data and intent_data.get('type') == 'articles':
                # Articles are handled via article_data
                if article_data and (article_data.get('data') or article_data.get('combined_text')):
                    # Has article data, proceed
                    pass
                else:
                    return "I couldn't find any articles about that topic. Please try asking about a specific team, player, or game."
            
            elif intent_data:
                data = intent_data.get('data', [])
                source = intent_data.get('source', 'unknown')
                intent_type = intent_data.get('type', '')
                error = intent_data.get('error')
                
                # Check if there's an error message (even if data exists, error might be set)
                if error and not data:
                    logger.warning(f"Error returned for intent: {intent_type}, error: {error}")
                    return error
                
                # Check if data is empty or None (handle both dict and list)
                # CRITICAL: For date_schedule, let the formatter handle empty data
                # because it may need to check day after tomorrow
                if not data:
                    if intent_type not in ['triple_double_count', 'team_scoring_leader', 'date_schedule']:
                        # For other types, provide helpful message
                        logger.warning(f"No data returned for intent: {intent_type}, source: {source}")
                        # Provide helpful message based on query type
                        if 'schedule' in intent_type and intent_type != 'date_schedule':
                            return "I couldn't find upcoming game schedules at the moment. The NBA schedule may not be available yet, or games might have already been played. Please try asking about recent game results instead."
                        elif 'standings' in intent_type:
                            return "I couldn't retrieve current standings at the moment. Please try asking about specific team records or recent game results."
                        elif 'live' in intent_type:
                            return "I couldn't find any games currently in progress. There may not be any live games right now."
                        else:
                            # Use error message if available, otherwise generic message
                            if error:
                                return error
                            return "I couldn't find that information from available sources right now. Please try asking about a different game, player, or team, or rephrase your question."
                
                # For triple_double_count and similar, let formatter handle even with empty data
                # The formatter will use the error field if present
                
                # Handle single dict vs list - both are valid
                if isinstance(data, dict):
                    # Single item response (dict) - this is valid, continue
                    pass
                elif isinstance(data, list) and len(data) == 0:
                    if intent_type not in ['triple_double_count', 'team_scoring_leader', 'date_schedule']:
                        logger.warning(f"Empty data list for intent: {intent_type}")
                        if error:
                            return error
                        return "I couldn't find that specific information. Please try asking about a different game, player, or team."
            
            if not intent_data and not article_data:
                return "I couldn't find relevant information to answer your question. Could you rephrase it?"
            
            # Check if intent_data has pre-formatted response (from responder agent)
            if intent_data and intent_data.get('formatted_response'):
                logger.info("Using pre-formatted response from Responder agent")
                return intent_data['formatted_response']
            
            # Use formatter agent to create natural response
            # For article queries, pass article_data properly
            if intent_data and intent_data.get('type') == 'articles' and article_data:
                # Use article_data as the main data source
                response = self.formatter_agent.format_response(
                    {'type': 'articles', 'data': article_data.get('data', []), 'query': question},
                    article_data
                )
            else:
                response = self.formatter_agent.format_response(
                    intent_data or {'type': 'articles', 'data': []},
                    article_data
                )
            
            # Validate response is not empty
            if not response or len(response.strip()) == 0:
                return "I don't have that information in my database."
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            return f"I encountered an error while processing your question. Please try again."
    
    def _handle_general_question(self, question: str) -> str:
        """
        Handle general conversational questions like greetings and capability queries
        """
        question_lower = question.lower().strip()
        
        # Greetings
        if any(greeting in question_lower for greeting in ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']):
            return "Hello! 👋 I'm your Basketball AI assistant. I'm here to help you with all things NBA! I can answer questions about game scores, player statistics, schedules, standings, and more. What would you like to know?"
        
        # Capability questions
        if any(phrase in question_lower for phrase in [
            'what can you do', 'what do you do', 'what are you', 'who are you',
            'capabilities', 'features', 'what questions', 'what can i ask',
            'how can you help', 'what do you know', 'what information',
            'tell me about yourself', 'introduce yourself', 'help'
        ]):
            return """I'm a Basketball AI Chatbot specialized in NBA information! 🏀 Here's what I can help you with:

**Game Information:**
• Match scores and results
• Live game updates
• Game schedules (today, tomorrow, upcoming games)

**Player Statistics:**
• Individual player stats (points, rebounds, assists, etc.)
• Recent game performances
• Season averages and trends
• Triple-doubles and double-doubles

**Team Information:**
• Team standings and rankings
• Conference positions
• Team records and win/loss records
• Injury reports
• Team news and updates

**Analysis & Insights:**
• Game analysis and breakdowns
• Player performance analysis
• Team strategy discussions

Just ask me anything about NBA basketball, and I'll do my best to help! For example:
• "What was the score in the Lakers vs Warriors game?"
• "How many points did LeBron James score?"
• "When is the next Celtics game?"
• "Show me the current NBA standings"

What would you like to know?"""
        
        # Default response for other general questions
        return "I'm a Basketball AI assistant focused on NBA information. I can help you with game scores, player stats, schedules, standings, and more. What would you like to know about basketball?"


if __name__ == "__main__":
    # Test the chatbot
    chatbot = BasketballChatbot()
    
    test_questions = [
        "How many points did LeBron James score?",
        "When is the next Lakers game?",
        "What was the score in the Warriors vs Suns match?",
        "Show me Giannis' last game stats."
    ]
    
    for question in test_questions:
        print(f"\nQ: {question}")
        answer = chatbot.process_question(question)
        print(f"A: {answer}")

