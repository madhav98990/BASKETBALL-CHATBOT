"""
Response Formatter Agent - Formats responses using local LLM (Ollama)
Converts raw data into natural, conversational responses
"""
import logging
import requests
import json
from config import OLLAMA_BASE_URL, OLLAMA_MODEL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResponseFormatterAgent:
    """Formats responses using Ollama LLM"""
    
    def __init__(self):
        self.base_url = OLLAMA_BASE_URL
        self.model = OLLAMA_MODEL
    
    def format_response(self, intent_data: dict, article_data: dict = None) -> str:
        """
        Format response based on intent data and optional article data
        Uses fallback formatter for accuracy - only uses LLM for article-based queries
        """
        try:
            intent_type = intent_data.get('type', '') if intent_data else ''
            
            # For article queries, check article_data first
            if intent_type == 'articles' or article_data:
                # Articles might have data in article_data even if intent_data is empty
                if article_data and (article_data.get('data') or article_data.get('combined_text')):
                    pass  # Proceed with article formatting
                elif intent_data and intent_data.get('data'):
                    pass  # Proceed with article formatting
                else:
                    return "I couldn't find any articles about that topic. Please try asking about a specific team, player, or game."
            
            # For other queries, validate data
            elif not intent_data or not intent_data.get('data'):
                # Skip validation for types that handle errors in formatter
                if intent_type not in ['triple_double_count', 'team_scoring_leader']:
                    return "I don't have that information in my database."
            
            data = intent_data.get('data', []) if intent_data else []
            # For game_leader and team_scoring_leader, data can be a dict or list
            # Skip validation if it's one of these types (they handle errors in formatter)
            if intent_type != 'articles' and intent_type not in ['triple_double_count', 'team_scoring_leader', 'game_leader']:
                if isinstance(data, list) and len(data) == 0:
                    return "I don't have that information in my database."
            elif not data:  # Also check for None or empty dict
                return "I don't have that information in my database."
            
            # For database queries, use fallback formatter
            # This ensures we only use actual database data, no hallucinations
            if intent_type in ['match_stats', 'player_stats', 'schedule', 'date_schedule',
                              'live_game', 'standings', 'injuries', 'player_trend',
                              'season_averages', 'team_news', 'triple_double_count', 'team_scoring_leader']:
                return self._format_fallback(intent_data, article_data)
            
            # For article-based queries, use LLM but with strict validation
            if intent_type == 'articles' or article_data:
                context = self._build_context(intent_data, article_data)
                if not context or context.strip() == "":
                    logger.warning("No context found for article query")
                    return "I couldn't find any articles about that topic. Please try asking about a specific team, player, or game."
                
                # Build article-specific prompt
                # Use more context for better answers
                context_length = 4000 if len(context) > 4000 else len(context)
                # Clean context one more time before sending to LLM
                import re
                context_clean = context[:context_length]
                # Remove any remaining navigation patterns
                context_clean = re.sub(r'< >.*?\d+[hd]', '', context_clean, flags=re.IGNORECASE)
                context_clean = re.sub(r'[A-Z]{2,4}\s+\d+[hd]', '', context_clean)
                context_clean = re.sub(r'[A-Z][a-z]+\s+\d+[hd][A-Z]', '', context_clean)
                context_clean = re.sub(r'EmailPrint|Close|Joined ESPN|Follow on', '', context_clean)
                
                prompt = f"""You are a sports analyst. Answer the question using ONLY the information from the article text provided below.

STRICT RULES:
1. Use ONLY the information found in the article text
2. DO NOT add information not in the article
3. DO NOT list article titles or navigation elements
4. DO NOT mention sources unless asked
5. If the article doesn't mention the topic, say: "The articles don't mention that specific information."
6. Keep your answer concise (3-4 sentences)
7. Summarize the player's/team's performance in clear, factual sentences
8. Focus on actual game events, statistics, and quotes from the article

ARTICLE TEXT:
{context_clean[:4000]}

QUESTION: {intent_data.get('query', 'the question')}

ANSWER (3-4 sentences, factual only):"""
                
                try:
                    # Try Ollama with shorter timeout for faster fallback
                    response = self._call_ollama(prompt, timeout=10)  # 10 second timeout
                    if response and len(response.strip()) > 0:
                        return response.strip()
                    else:
                        # Fallback: extract relevant info directly
                        if article_data and article_data.get('combined_text'):
                            text = article_data['combined_text']
                            # Try to find relevant sentences
                            sentences = text.split('.')
                            relevant_sentences = []
                            query_lower = intent_data.get('query', '').lower()
                            key_terms = [term for term in query_lower.split() if len(term) > 3]
                            
                            for sentence in sentences:
                                sentence_lower = sentence.lower()
                                if any(term in sentence_lower for term in key_terms):
                                    relevant_sentences.append(sentence.strip())
                            
                            if relevant_sentences:
                                return "Based on the articles: " + ". ".join(relevant_sentences[:3]) + "."
                            return "Based on the articles: " + text[:500] + "..."
                        return "I couldn't find specific information about that in the articles."
                except Exception as e:
                    logger.error(f"Error calling Ollama for articles: {e}")
                    # Fallback: try to extract relevant info directly with better extraction
                    if article_data and article_data.get('combined_text'):
                        text = article_data['combined_text']
                        query_lower = intent_data.get('query', '').lower()
                        
                        # Clean query to extract key terms
                        query_clean = query_lower
                        for phrase in ['what does', 'what do', 'the articles', 'article', 'articles', 'say about', 'says about']:
                            query_clean = query_clean.replace(phrase, '')
                        query_clean = query_clean.replace('?', '').strip()
                        
                        # Extract key terms (longer terms are more important)
                        key_terms = [term for term in query_clean.split() if len(term) > 3]
                        
                        # Split into sentences and find relevant ones
                        # First, remove any remaining navigation patterns
                        import re
                        text = re.sub(r'< >.*?\d+[hd]', '', text, flags=re.IGNORECASE)
                        text = re.sub(r'[A-Z]{2,4}\s+\d+[hd]', '', text)
                        text = re.sub(r'[A-Z][a-z]+\s+\d+[hd][A-Z]', '', text)
                        
                        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 30]
                        relevant_sentences = []
                        
                        for sentence in sentences:
                            sentence_lower = sentence.lower()
                            # Skip if it looks like navigation
                            if re.search(r'^\s*[A-Z]{2,4}\s+\d+[hd]', sentence) or len(sentence) < 30:
                                continue
                            
                            # Skip incomplete sentences (missing ending punctuation)
                            if not re.search(r'[.!?]$', sentence.strip()):
                                continue
                            
                            # Count how many key terms are in this sentence
                            matches = sum(1 for term in key_terms if term in sentence_lower)
                            if matches > 0:
                                # Prioritize sentences with more matches
                                score = matches * 10
                                
                                # Bonus for sentences that mention the main subject (first key term, usually player/team name)
                                if key_terms and key_terms[0] in sentence_lower:
                                    score += 15
                                
                                # Bonus for performance-related words in performance queries
                                if 'performance' in query_lower:
                                    perf_words = ['scored', 'points', 'game', 'played', 'assists', 'rebounds', 'mvp', 'win']
                                    if any(word in sentence_lower for word in perf_words):
                                        score += 10
                                
                                # Slight bonus for longer sentences (but not too long)
                                if 50 < len(sentence) < 300:
                                    score += 2
                                
                                relevant_sentences.append((score, sentence))
                        
                        # Sort by relevance (more matches first) and take top sentences
                        relevant_sentences.sort(key=lambda x: x[0], reverse=True)
                        top_sentences = [s[1] for s in relevant_sentences[:6]]  # Get more sentences for better context
                        
                        if top_sentences:
                            # Remove duplicates (exact and near-duplicates)
                            unique_sentences = []
                            seen = set()
                            for sentence in top_sentences:
                                # Normalize sentence for comparison (first 80 chars)
                                key = sentence[:80].lower().strip()
                                if key not in seen and len(sentence.strip()) > 30:
                                    seen.add(key)
                                    unique_sentences.append(sentence)
                            
                            # Take up to 5 unique sentences
                            unique_sentences = unique_sentences[:5]
                            
                            if unique_sentences:
                                # Join sentences and clean up
                                answer = ". ".join(unique_sentences)
                                # Remove any remaining navigation junk
                                answer = re.sub(r'< >.*?\d+[hd]', '', answer, flags=re.IGNORECASE)
                                answer = re.sub(r'[A-Z]{2,4}\s+\d+[hd]', '', answer)
                                answer = re.sub(r'EmailPrint|Close|Joined ESPN', '', answer)
                                answer = re.sub(r'\s+', ' ', answer).strip()
                                
                                # Ensure answer is coherent (has proper sentence structure)
                                if len(answer) > 100 and '.' in answer:
                                    return "Based on the articles: " + answer + "."
                        
                        # Fallback: use first substantial paragraph
                        paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 100]
                        if paragraphs:
                            return "Based on the articles: " + paragraphs[0][:500] + "..."
                        
                        return "Based on the articles: " + text[:600] + "..."
                    return "I couldn't process the article information. Please try asking a different question."
            
            # Default to fallback
            return self._format_fallback(intent_data, article_data)
            
        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            # Fallback to simple formatting
            return self._format_fallback(intent_data, article_data)
    
    def _build_context(self, intent_data: dict, article_data: dict = None) -> str:
        """Build context string from data"""
        context_parts = []
        
        intent_type = intent_data.get('type', '')
        data = intent_data.get('data', [])
        
        # For article queries, prioritize article_data
        if intent_type == 'articles' and article_data:
            combined_text = article_data.get('combined_text', '')
            if combined_text:
                return combined_text
            # Fallback to data if no combined_text
            if data:
                combined_text = "\n\n".join([item.get('text', '') for item in data if isinstance(item, dict) and item.get('text')])
                if combined_text:
                    return combined_text
        
        if not data:
            return ""
        
        if intent_type == 'match_stats':
            context_parts.append("MATCH RESULTS (use only these exact results):\n")
            for match in data[:5]:  # Limit to 5 matches
                team1 = match.get('team1_name', '')
                team2 = match.get('team2_name', '')
                score1 = match.get('team1_score', 0)
                score2 = match.get('team2_score', 0)
                date = match.get('match_date', '')
                winner = match.get('winner', '')
                
                # Only add if we have valid data
                if team1 and team2 and score1 and score2 and date:
                    context_parts.append(f"{team1} vs {team2}: {score1}-{score2} (Winner: {winner}) on {date}")
        
        elif intent_type == 'player_stats':
            if isinstance(data, dict) and 'avg_points' in data:
                # Average stats
                context_parts.append(f"PLAYER AVERAGE STATS (use only these numbers):\n")
                avg_points = data.get('avg_points', 0)
                avg_rebounds = data.get('avg_rebounds', 0)
                avg_assists = data.get('avg_assists', 0)
                avg_steals = data.get('avg_steals', 0)
                avg_blocks = data.get('avg_blocks', 0)
                games = data.get('games_played', 0)
                if avg_points > 0:
                    context_parts.append(f"Average Points: {avg_points:.1f}")
                    context_parts.append(f"Average Rebounds: {avg_rebounds:.1f}")
                    context_parts.append(f"Average Assists: {avg_assists:.1f}")
                    context_parts.append(f"Average Steals: {avg_steals:.1f}")
                    context_parts.append(f"Average Blocks: {avg_blocks:.1f}")
                    context_parts.append(f"Games Played: {games}")
            elif isinstance(data, list) and data:
                # Recent stats
                context_parts.append("PLAYER STATISTICS (use only these exact stats):\n")
                for stat in data[:3]:
                    points = stat.get('points', 0)
                    rebounds = stat.get('rebounds', 0)
                    assists = stat.get('assists', 0)
                    steals = stat.get('steals', 0)
                    blocks = stat.get('blocks', 0)
                    date = stat.get('match_date', '')
                    team1 = stat.get('team1_name', '')
                    team2 = stat.get('team2_name', '')
                    if points > 0 and date:
                        context_parts.append(
                            f"Game on {date}: {team1} vs {team2} - "
                            f"{points} points, {rebounds} rebounds, {assists} assists"
                        )
        
        elif intent_type == 'schedule':
            context_parts.append("UPCOMING MATCHES (use only these exact dates and teams):\n")
            for match in data[:10]:
                team1 = match.get('team1_name', '')
                team2 = match.get('team2_name', '')
                date = match.get('match_date', '')
                venue = match.get('venue', '')
                
                # Only add if we have valid data
                if team1 and team2 and date:
                    if venue:
                        context_parts.append(f"{team1} vs {team2} on {date} at {venue}")
                    else:
                        context_parts.append(f"{team1} vs {team2} on {date}")
        
        # Add article context if available
        if article_data and article_data.get('combined_text'):
            context_parts.append("\nARTICLE CONTEXT:\n")
            context_parts.append(article_data['combined_text'][:2000])  # Limit length
        
        return "\n".join(context_parts)
    
    def _build_prompt(self, context: str, question: str) -> str:
        """Build prompt for LLM"""
        if not context or context.strip() == "":
            return "I don't have that information in my database."
        
        prompt = f"""Answer the user's question using ONLY the exact data provided. DO NOT add any information not in the context.

STRICT RULES:
1. Use ONLY the exact numbers, dates, team names, and venue names from the context
2. DO NOT change venue names (e.g., if context says "Crypto.com Arena", use that exact name)
3. DO NOT add descriptive words like "thrilling", "electric", "stunning" unless the context includes them
4. DO NOT mention dates, scores, or teams not in the context
5. If context doesn't answer the question, say: "I don't have that information in my database."
6. Keep answer to 1-2 sentences
7. Format: "Team1 vs Team2: Score1-Score2 on Date at Venue" (use exact venue name from context)

CONTEXT DATA (ONLY use this):
{context}

QUESTION: {question}

ANSWER (copy exact data from context only):"""
        return prompt
    
    def _call_ollama(self, prompt: str, timeout: int = 10) -> str:
        """Call Ollama API with configurable timeout"""
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Lower temperature = less creative, more factual
                    "top_p": 0.8,  # Lower top_p = more focused
                    "max_tokens": 200  # Shorter responses = less room for hallucination
                }
            }
            
            response = requests.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '').strip()
            
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            logger.warning(f"Ollama timeout/connection error: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            raise
    
    def _format_fallback(self, intent_data: dict, article_data: dict = None) -> str:
        """Fallback formatting - uses ONLY actual database data, no LLM hallucinations"""
        if not intent_data:
            return "I don't have that information in my database."
        
        intent_type = intent_data.get('type', '')
        data = intent_data.get('data', [])
        
        # Skip data validation for types that handle empty data with error messages
        # For game_leader and team_scoring_leader, data can be a dict or list, so check appropriately
        if intent_type not in ['triple_double_count', 'team_scoring_leader', 'game_leader']:
            if not data:
                return "I don't have that information in my database."
            elif isinstance(data, list) and len(data) == 0:
                return "I don't have that information in my database."
        
        if intent_type == 'match_stats' and data:
            # Handle "result of [team] last game" queries
            if intent_data.get('result_query'):
                if isinstance(data, list) and len(data) > 0:
                    game_result = data[0]
                    team = game_result.get('team_name', intent_data.get('team', '').title())
                    did_win = game_result.get('did_win', intent_data.get('did_win', False))
                    team_score = game_result.get('team_score', intent_data.get('team_score', 0))
                    opponent_score = game_result.get('opponent_score', intent_data.get('opponent_score', 0))
                    opponent_name = game_result.get('opponent_name', intent_data.get('opponent_name', ''))
                    game_date = game_result.get('game_date', intent_data.get('game_date', ''))
                else:
                    team = intent_data.get('team', '').title()
                    did_win = intent_data.get('did_win', False)
                    team_score = intent_data.get('team_score', 0)
                    opponent_score = intent_data.get('opponent_score', 0)
                    opponent_name = intent_data.get('opponent_name', '')
                    game_date = intent_data.get('game_date', '')
                
                # Format opponent name (expand abbreviation if needed)
                opponent_display = opponent_name
                if opponent_name and len(opponent_name) <= 5:
                    abbrev_map = {
                        'ORL': 'Orlando Magic', 'NYK': 'New York Knicks', 'LAL': 'Los Angeles Lakers',
                        'GSW': 'Golden State Warriors', 'BOS': 'Boston Celtics', 'MIL': 'Milwaukee Bucks',
                        'DEN': 'Denver Nuggets', 'PHX': 'Phoenix Suns', 'MIA': 'Miami Heat',
                        'DAL': 'Dallas Mavericks', 'LAC': 'LA Clippers', 'PHI': 'Philadelphia 76ers',
                        'CLE': 'Cleveland Cavaliers', 'ATL': 'Atlanta Hawks', 'OKC': 'Oklahoma City Thunder',
                        'MIN': 'Minnesota Timberwolves', 'SAC': 'Sacramento Kings', 'NOP': 'New Orleans Pelicans',
                        'MEM': 'Memphis Grizzlies', 'TOR': 'Toronto Raptors', 'BKN': 'Brooklyn Nets',
                        'CHI': 'Chicago Bulls', 'DET': 'Detroit Pistons', 'IND': 'Indiana Pacers',
                        'CHA': 'Charlotte Hornets', 'WSH': 'Washington Wizards', 'POR': 'Portland Trail Blazers',
                        'UTA': 'Utah Jazz', 'HOU': 'Houston Rockets', 'SAS': 'San Antonio Spurs'
                    }
                    opponent_display = abbrev_map.get(opponent_name, opponent_name)
                
                # Format date if available
                date_str = ''
                if game_date:
                    try:
                        from datetime import datetime
                        if ',' in game_date:
                            date_obj = datetime.strptime(game_date, '%b %d, %Y')
                        else:
                            date_obj = datetime.strptime(game_date[:10], '%Y-%m-%d')
                        date_str = f" on {date_obj.strftime('%B %d, %Y')}"
                    except:
                        date_str = f" on {game_date}"
                
                # Format the result
                if did_win:
                    return f"The {team} won their last game{date_str}. Final score: {team} {team_score}, {opponent_display} {opponent_score}."
                else:
                    return f"The {team} lost their last game{date_str}. Final score: {opponent_display} {opponent_score}, {team} {team_score}."
            
            # Handle "win by" queries (point differential for wins)
            elif intent_data.get('win_by_query'):
                if isinstance(data, list) and len(data) > 0:
                    game_result = data[0]
                    team = game_result.get('team_name', intent_data.get('team', '').title())
                    point_differential = intent_data.get('point_differential')
                    did_win = intent_data.get('did_win', game_result.get('did_win', False))
                    opponent_name = game_result.get('opponent_name', '')
                    game_date = game_result.get('game_date', '')
                    team_score = intent_data.get('team_score', game_result.get('team_score', 0))
                    opponent_score = intent_data.get('opponent_score', game_result.get('opponent_score', 0))
                else:
                    team = intent_data.get('team', '').title()
                    point_differential = intent_data.get('point_differential')
                    did_win = intent_data.get('did_win', False)
                    opponent_name = intent_data.get('opponent_name', '')
                    game_date = intent_data.get('game_date', '')
                    team_score = intent_data.get('team_score', 0)
                    opponent_score = intent_data.get('opponent_score', 0)
                
                # Format opponent name (expand abbreviation if needed)
                opponent_display = opponent_name
                if opponent_name and len(opponent_name) <= 5:
                    abbrev_map = {
                        'ORL': 'Orlando Magic', 'NYK': 'New York Knicks', 'LAL': 'Los Angeles Lakers',
                        'GSW': 'Golden State Warriors', 'BOS': 'Boston Celtics', 'MIL': 'Milwaukee Bucks',
                        'DEN': 'Denver Nuggets', 'PHX': 'Phoenix Suns', 'MIA': 'Miami Heat',
                        'DAL': 'Dallas Mavericks', 'LAC': 'LA Clippers', 'PHI': 'Philadelphia 76ers',
                        'CLE': 'Cleveland Cavaliers', 'ATL': 'Atlanta Hawks', 'OKC': 'Oklahoma City Thunder',
                        'MIN': 'Minnesota Timberwolves', 'SAC': 'Sacramento Kings', 'NOP': 'New Orleans Pelicans',
                        'MEM': 'Memphis Grizzlies', 'TOR': 'Toronto Raptors', 'BKN': 'Brooklyn Nets',
                        'CHI': 'Chicago Bulls', 'DET': 'Detroit Pistons', 'IND': 'Indiana Pacers',
                        'CHA': 'Charlotte Hornets', 'WSH': 'Washington Wizards', 'POR': 'Portland Trail Blazers',
                        'UTA': 'Utah Jazz', 'HOU': 'Houston Rockets', 'SAS': 'San Antonio Spurs'
                    }
                    opponent_display = abbrev_map.get(opponent_name, opponent_name)
                
                # Format date if available
                date_str = ''
                if game_date:
                    try:
                        from datetime import datetime
                        if ',' in game_date:
                            date_obj = datetime.strptime(game_date, '%b %d, %Y')
                        else:
                            date_obj = datetime.strptime(game_date[:10], '%Y-%m-%d')
                        date_str = f" on {date_obj.strftime('%B %d, %Y')}"
                    except:
                        date_str = f" on {game_date}"
                
                if not did_win:
                    return f"The {team} lost their most recent game{date_str}, so they didn't win. They were defeated by the {opponent_display} {opponent_score}-{team_score}."
                elif point_differential is not None:
                    return f"The {team} won by {point_differential} point{'s' if point_differential != 1 else ''} in their last matchup{date_str}. The final score was {team} {team_score}, {opponent_display} {opponent_score}."
                else:
                    return f"I couldn't determine the point differential for the {team}'s most recent game."
            
            # Handle "lose by" queries (point differential for losses)
            elif intent_data.get('lose_by_query'):
                if isinstance(data, list) and len(data) > 0:
                    game_result = data[0]
                    team = game_result.get('team_name', intent_data.get('team', '').title())
                    point_differential = intent_data.get('point_differential')
                    did_win = intent_data.get('did_win', game_result.get('did_win', False))
                    opponent_name = game_result.get('opponent_name', '')
                    game_date = game_result.get('game_date', '')
                    team_score = intent_data.get('team_score', game_result.get('team_score', 0))
                    opponent_score = intent_data.get('opponent_score', game_result.get('opponent_score', 0))
                else:
                    team = intent_data.get('team', '').title()
                    point_differential = intent_data.get('point_differential')
                    did_win = intent_data.get('did_win', False)
                    opponent_name = intent_data.get('opponent_name', '')
                    game_date = intent_data.get('game_date', '')
                    team_score = intent_data.get('team_score', 0)
                    opponent_score = intent_data.get('opponent_score', 0)
                
                # Format opponent name (expand abbreviation if needed)
                opponent_display = opponent_name
                if opponent_name and len(opponent_name) <= 5:
                    abbrev_map = {
                        'ORL': 'Orlando Magic', 'NYK': 'New York Knicks', 'LAL': 'Los Angeles Lakers',
                        'GSW': 'Golden State Warriors', 'BOS': 'Boston Celtics', 'MIL': 'Milwaukee Bucks',
                        'DEN': 'Denver Nuggets', 'PHX': 'Phoenix Suns', 'MIA': 'Miami Heat',
                        'DAL': 'Dallas Mavericks', 'LAC': 'LA Clippers', 'PHI': 'Philadelphia 76ers',
                        'CLE': 'Cleveland Cavaliers', 'ATL': 'Atlanta Hawks', 'OKC': 'Oklahoma City Thunder',
                        'MIN': 'Minnesota Timberwolves', 'SAC': 'Sacramento Kings', 'NOP': 'New Orleans Pelicans',
                        'MEM': 'Memphis Grizzlies', 'TOR': 'Toronto Raptors', 'BKN': 'Brooklyn Nets',
                        'CHI': 'Chicago Bulls', 'DET': 'Detroit Pistons', 'IND': 'Indiana Pacers',
                        'CHA': 'Charlotte Hornets', 'WSH': 'Washington Wizards', 'POR': 'Portland Trail Blazers',
                        'UTA': 'Utah Jazz', 'HOU': 'Houston Rockets', 'SAS': 'San Antonio Spurs'
                    }
                    opponent_display = abbrev_map.get(opponent_name, opponent_name)
                
                # Format date if available
                date_str = ''
                if game_date:
                    try:
                        from datetime import datetime
                        if ',' in game_date:
                            date_obj = datetime.strptime(game_date, '%b %d, %Y')
                        else:
                            date_obj = datetime.strptime(game_date[:10], '%Y-%m-%d')
                        date_str = f" on {date_obj.strftime('%B %d, %Y')}"
                    except:
                        date_str = f" on {game_date}"
                
                if did_win:
                    return f"The {team} won their most recent game{date_str}, so they didn't lose. They defeated the {opponent_display} {team_score}-{opponent_score}."
                elif point_differential is not None:
                    return f"The {team} lost by {point_differential} point{'s' if point_differential != 1 else ''} in their last matchup{date_str}. The final score was {opponent_display} {opponent_score}, {team} {team_score}."
                else:
                    return f"I couldn't determine the point differential for the {team}'s most recent game."
            
            # Handle "did [team] win" queries first
            elif intent_data.get('multiple_games_query'):
                # Handle multiple game results (e.g., "last 5 games")
                if isinstance(data, list) and len(data) > 0:
                    team = intent_data.get('team', '').title()
                    num_games = intent_data.get('num_games', len(data))
                    
                    results = []
                    wins = 0
                    losses = 0
                    
                    for game in data:
                        game_date = game.get('game_date', '')
                        team_score = game.get('team_score', 0)
                        opponent_score = game.get('opponent_score', 0)
                        opponent_name = game.get('opponent_name', '')
                        did_win = game.get('did_win', False)
                        
                        if did_win:
                            wins += 1
                        else:
                            losses += 1
                        
                        # Format date
                        date_str = ''
                        if game_date:
                            try:
                                from datetime import datetime
                                if ',' in game_date:
                                    date_obj = datetime.strptime(game_date, '%b %d, %Y')
                                else:
                                    date_obj = datetime.strptime(game_date[:10], '%Y-%m-%d')
                                date_str = date_obj.strftime('%b %d, %Y')
                            except:
                                date_str = game_date[:10] if len(game_date) >= 10 else game_date
                        
                        # Format opponent name
                        opponent_display = opponent_name
                        if opponent_name and len(opponent_name) <= 5:
                            abbrev_map = {
                                'ORL': 'Orlando Magic', 'NYK': 'New York Knicks', 'LAL': 'Los Angeles Lakers',
                                'GSW': 'Golden State Warriors', 'BOS': 'Boston Celtics', 'MIL': 'Milwaukee Bucks',
                                'DEN': 'Denver Nuggets', 'PHX': 'Phoenix Suns', 'MIA': 'Miami Heat',
                                'DAL': 'Dallas Mavericks', 'LAC': 'LA Clippers', 'PHI': 'Philadelphia 76ers',
                                'CLE': 'Cleveland Cavaliers', 'ATL': 'Atlanta Hawks', 'OKC': 'Oklahoma City Thunder',
                                'MIN': 'Minnesota Timberwolves', 'SAC': 'Sacramento Kings', 'NOP': 'New Orleans Pelicans',
                                'MEM': 'Memphis Grizzlies', 'TOR': 'Toronto Raptors', 'BKN': 'Brooklyn Nets',
                                'CHI': 'Chicago Bulls', 'DET': 'Detroit Pistons', 'IND': 'Indiana Pacers',
                                'CHA': 'Charlotte Hornets', 'WSH': 'Washington Wizards', 'POR': 'Portland Trail Blazers',
                                'UTA': 'Utah Jazz', 'HOU': 'Houston Rockets', 'SAS': 'San Antonio Spurs'
                            }
                            opponent_display = abbrev_map.get(opponent_name, opponent_name)
                        
                        # Format result with better readability
                        result_str = f"• {date_str}: {team} vs {opponent_display}\n  Final Score: {team_score}-{opponent_score} ({'Win' if did_win else 'Loss'})"
                        results.append(result_str)
                    
                    if results:
                        # Create formatted header with summary
                        header = f"📊 Last {num_games} Game Results for the {team}\n"
                        header += f"Record: {wins}-{losses}\n\n"
                        return header + "\n".join(results)
                    else:
                        return f"I couldn't retrieve game results for the {team}."
                else:
                    error_msg = intent_data.get('error', f"I couldn't retrieve game results for the {intent_data.get('team', 'team').title()}.")
                    return error_msg
            
            elif intent_data.get('win_query'):
                # Check for error message first (after all retries failed)
                if intent_data.get('error'):
                    return intent_data.get('error', "Live game data is temporarily unavailable. Please try again shortly.")
                
                # Get data from the game result (NBA API format)
                if isinstance(data, list) and len(data) > 0:
                    game_result = data[0]
                    did_win = game_result.get('did_win', intent_data.get('did_win', False))
                    # Use team_name from game_result if available, otherwise use team from intent_data
                    team = game_result.get('team_name', intent_data.get('team', '').title())
                    # Ensure full team name is used (e.g., "New York Knicks" not just "Knicks")
                    if team and len(team.split()) == 1:
                        # Single word team name, try to expand it
                        team_map = {
                            'Knicks': 'New York Knicks', 'Lakers': 'Los Angeles Lakers',
                            'Warriors': 'Golden State Warriors', 'Celtics': 'Boston Celtics',
                            'Bucks': 'Milwaukee Bucks', 'Nuggets': 'Denver Nuggets',
                            'Suns': 'Phoenix Suns', 'Heat': 'Miami Heat',
                            'Mavericks': 'Dallas Mavericks', 'Clippers': 'LA Clippers',
                            '76ers': 'Philadelphia 76ers', 'Cavaliers': 'Cleveland Cavaliers',
                            'Hawks': 'Atlanta Hawks', 'Thunder': 'Oklahoma City Thunder',
                            'Timberwolves': 'Minnesota Timberwolves', 'Kings': 'Sacramento Kings',
                            'Pelicans': 'New Orleans Pelicans', 'Grizzlies': 'Memphis Grizzlies',
                            'Raptors': 'Toronto Raptors', 'Nets': 'Brooklyn Nets',
                            'Bulls': 'Chicago Bulls', 'Pistons': 'Detroit Pistons',
                            'Pacers': 'Indiana Pacers', 'Hornets': 'Charlotte Hornets',
                            'Magic': 'Orlando Magic', 'Wizards': 'Washington Wizards',
                            'Trail Blazers': 'Portland Trail Blazers', 'Jazz': 'Utah Jazz',
                            'Rockets': 'Houston Rockets', 'Spurs': 'San Antonio Spurs'
                        }
                        team = team_map.get(team, team)
                    team_score = game_result.get('team_score', 0)
                    opponent_score = game_result.get('opponent_score', 0)
                    opponent_name = game_result.get('opponent_name', '')
                    game_date = game_result.get('game_date', '')
                else:
                    # Fallback to intent_data
                    did_win = intent_data.get('did_win', False)
                    team = intent_data.get('team', '').title()
                    # Expand single word team names
                    if team and len(team.split()) == 1:
                        team_map = {
                            'Knicks': 'New York Knicks', 'Lakers': 'Los Angeles Lakers',
                            'Warriors': 'Golden State Warriors', 'Celtics': 'Boston Celtics'
                        }
                        team = team_map.get(team, team)
                    team_score = intent_data.get('team_score', 0)
                    opponent_score = intent_data.get('opponent_score', 0)
                    opponent_name = intent_data.get('opponent_name', '')
                    game_date = intent_data.get('game_date', '')
                
                # Format opponent name (expand abbreviation if needed)
                opponent_display = opponent_name
                if opponent_name and len(opponent_name) <= 5:
                    # Map common abbreviations to full names
                    abbrev_map = {
                        'ORL': 'Orlando Magic', 'NYK': 'New York Knicks', 'LAL': 'Los Angeles Lakers',
                        'GSW': 'Golden State Warriors', 'BOS': 'Boston Celtics', 'MIL': 'Milwaukee Bucks',
                        'DEN': 'Denver Nuggets', 'PHX': 'Phoenix Suns', 'MIA': 'Miami Heat',
                        'DAL': 'Dallas Mavericks', 'LAC': 'LA Clippers', 'PHI': 'Philadelphia 76ers',
                        'CLE': 'Cleveland Cavaliers', 'ATL': 'Atlanta Hawks', 'OKC': 'Oklahoma City Thunder',
                        'MIN': 'Minnesota Timberwolves', 'SAC': 'Sacramento Kings', 'NOP': 'New Orleans Pelicans',
                        'MEM': 'Memphis Grizzlies', 'TOR': 'Toronto Raptors', 'BKN': 'Brooklyn Nets',
                        'CHI': 'Chicago Bulls', 'DET': 'Detroit Pistons', 'IND': 'Indiana Pacers',
                        'CHA': 'Charlotte Hornets', 'WSH': 'Washington Wizards', 'POR': 'Portland Trail Blazers',
                        'UTA': 'Utah Jazz', 'HOU': 'Houston Rockets', 'SAS': 'San Antonio Spurs'
                    }
                    opponent_display = abbrev_map.get(opponent_name, opponent_name)
                
                # Format date if available
                date_str = ''
                if game_date:
                    try:
                        from datetime import datetime
                        # Handle format like "DEC 13, 2025"
                        if ',' in game_date:
                            date_obj = datetime.strptime(game_date, '%b %d, %Y')
                        else:
                            date_obj = datetime.strptime(game_date[:10], '%Y-%m-%d')
                        date_str = f" on {date_obj.strftime('%B %d, %Y')}"
                    except:
                        date_str = f" on {game_date}"
                
                # Format response - use same format for ALL teams (not just Knicks)
                # Format: "Yes/No. The {Team} won/lost their most recent game against {opponent} with a final score of {team_score}–{opponent_score}."
                if did_win:
                    return f"Yes. The {team} won their most recent game against {opponent_display} with a final score of {team_score}–{opponent_score}."
                else:
                    return f"No. The {team} lost their most recent game against {opponent_display} with a final score of {team_score}–{opponent_score}."
            
            # Check if this is a specific team matchup query
            query_lower = intent_data.get('query', '').lower()
            is_specific_matchup = ('vs' in query_lower or 'versus' in query_lower) and len([w for w in ['warriors', 'suns', 'lakers', 'celtics', 'bucks', 'nuggets', 'heat', 'mavericks', 'clippers', '76ers', 'cavaliers', 'knicks', 'hawks', 'thunder', 'timberwolves', 'kings', 'pelicans', 'grizzlies', 'raptors', 'nets', 'bulls', 'pistons', 'pacers', 'hornets', 'magic', 'wizards', 'trail blazers', 'jazz', 'rockets', 'spurs'] if w in query_lower]) >= 2
            
            # Single match or specific matchup
            if len(data) == 1 or is_specific_matchup:
                match = data[0] if isinstance(data, list) else data
                team1 = match.get('team1_name', '')
                team2 = match.get('team2_name', '')
                score1 = match.get('team1_score', 0)
                score2 = match.get('team2_score', 0)
                winner = match.get('winner', '')
                date = match.get('match_date', '')
                
                if team1 and team2 and score1 is not None and score2 is not None:
                    if date:
                        return f"The {team1} vs {team2} game on {date} ended with a score of {team1} {score1} - {team2} {score2}. {winner} won the game."
                    else:
                        return f"The {team1} vs {team2} game ended with a score of {team1} {score1} - {team2} {score2}. {winner} won the game."
            
            # Handle multiple matches for "recent games" queries
            if len(data) > 1:
                results = []
                for match in data[:5]:  # Limit to 5 matches
                    team1 = match.get('team1_name', '')
                    team2 = match.get('team2_name', '')
                    score1 = match.get('team1_score', 0)
                    score2 = match.get('team2_score', 0)
                    date = match.get('match_date', '')
                    winner = match.get('winner', '')
                    
                    if team1 and team2 and score1 is not None and score2 is not None:
                        if date:
                            results.append(f"{team1} vs {team2}: {score1}-{score2} (Winner: {winner}) on {date}")
                        else:
                            results.append(f"{team1} vs {team2}: {score1}-{score2} (Winner: {winner})")
                
                if results:
                    return "Recent match results:\n" + "\n".join(results)
        
        elif intent_type == 'season_averages' and data:
            # Handle season averages
            # Data can be dict (single player) or list (from season_avg_agent)
            if isinstance(data, dict):
                player_name = intent_data.get('player_name', 'Player')
                avg_points = data.get('avg_points', 0) or 0
                avg_rebounds = data.get('avg_rebounds', 0) or 0
                avg_assists = data.get('avg_assists', 0) or 0
                avg_steals = data.get('avg_steals', 0) or 0
                avg_blocks = data.get('avg_blocks', 0) or 0
                games = data.get('games_played', 0) or 0
                
                if games > 0:
                    return f"{player_name}'s season averages: {avg_points:.1f} points, {avg_rebounds:.1f} rebounds, {avg_assists:.1f} assists, {avg_steals:.1f} steals, {avg_blocks:.1f} blocks per game over {games} games."
            elif isinstance(data, list) and len(data) > 0:
                # Handle list from season_avg_agent
                first_player = data[0]
                player_name = first_player.get('player_name', 'Player')
                avg_points = first_player.get('points_per_game', 0) or 0
                avg_rebounds = first_player.get('rebounds_per_game', 0) or 0
                avg_assists = first_player.get('assists_per_game', 0) or 0
                games = first_player.get('games_played', 0) or 0
                
                if games > 0:
                    return f"{player_name}'s season averages: {avg_points:.1f} points, {avg_rebounds:.1f} rebounds, {avg_assists:.1f} assists per game over {games} games."
        
        elif (intent_type == 'game_leader' or intent_type == 'team_scoring_leader') and data:
            # Handle game leader query (both 'game_leader' and 'team_scoring_leader' use same format)
            if isinstance(data, dict):
                player_name = data.get('player_name', 'Unknown')
                points = data.get('points', 0)
                rebounds = data.get('rebounds', 0)
                assists = data.get('assists', 0)
                # Get team from data first, then intent_data, then default
                team = data.get('team', intent_data.get('team', 'the team'))
                # Capitalize team name properly
                if team and team != 'the team':
                    team = team.title()
                date = data.get('game_date', data.get('match_date', ''))
                matchup = data.get('matchup', '')
                
                if date and matchup:
                    return f"{player_name} led the scoring for the {team} in their {matchup} game on {date} with {points} points, {rebounds} rebounds, and {assists} assists."
                elif date:
                    return f"{player_name} led the scoring for the {team} in their game on {date} with {points} points, {rebounds} rebounds, and {assists} assists."
                else:
                    return f"{player_name} led the scoring for the {team} with {points} points, {rebounds} rebounds, and {assists} assists."
            elif isinstance(data, list) and len(data) > 0:
                # Handle list of game leaders (shouldn't happen, but handle it)
                leader = data[0]
                if isinstance(leader, dict):
                    player_name = leader.get('player_name', 'Unknown')
                    points = leader.get('points', 0)
                    rebounds = leader.get('rebounds', 0)
                    assists = leader.get('assists', 0)
                    team = leader.get('team', intent_data.get('team', 'the team'))
                    if team and team != 'the team':
                        team = team.title()
                    date = leader.get('game_date', leader.get('match_date', ''))
                    matchup = leader.get('matchup', '')
                    
                    if date and matchup:
                        return f"{player_name} led the scoring for the {team} in their {matchup} game on {date} with {points} points, {rebounds} rebounds, and {assists} assists."
                    elif date:
                        return f"{player_name} led the scoring for the {team} in their game on {date} with {points} points, {rebounds} rebounds, and {assists} assists."
                    else:
                        return f"{player_name} led the scoring for the {team} with {points} points, {rebounds} rebounds, and {assists} assists."
        
        # Handle error case for game leader queries
        elif (intent_type == 'game_leader' or intent_type == 'team_scoring_leader'):
            error = intent_data.get('error', '')
            if error:
                return f"I couldn't find that information. {error}"
            return "I couldn't find the scoring leader for that team's latest game. Please try asking about a different team or game."
        
        elif intent_type == 'triple_double_count':
            # Handle triple-double count query
            if data and isinstance(data, dict):
                player_name = data.get('player_name', 'Player')
                count = data.get('count', 0)
                triple_doubles = data.get('triple_doubles', [])
                
                # Build response with count
                response = f"{player_name} has {count} triple-double{'s' if count != 1 else ''} this season."
                
                # Add details of each triple-double if available
                if triple_doubles and len(triple_doubles) > 0:
                    response += "\n\nTriple-double games:\n"
                    for i, td in enumerate(triple_doubles, 1):
                        date = td.get('date', 'N/A')
                        # Handle both formats: 'opponent' and 'matchup'
                        matchup = td.get('matchup') or td.get('opponent', 'Unknown')
                        pts = td.get('points', 0)
                        reb = td.get('rebounds', 0)
                        ast = td.get('assists', 0)
                        result = td.get('result', '')
                        
                        # Format: "1. Dec 01, 2025 DEN vs. DAL: 29pts, 20reb, 13ast (L)"
                        result_str = f" ({result})" if result else ""
                        response += f"{i}. {date} {matchup}: {pts}pts, {reb}reb, {ast}ast{result_str}\n"
                
                return response.strip()
            elif intent_data.get('error'):
                # Return the error message if available
                return intent_data.get('error')
            else:
                return "I couldn't find triple-double statistics for that player."
        
        elif intent_type == 'top_players':
            # Handle top players query
            # Check for error first
            if intent_data.get('error'):
                return intent_data.get('error', 'Unable to retrieve top players data.')
            
            # Check if data exists and is valid
            if not data or (isinstance(data, list) and len(data) == 0):
                stat_type = intent_data.get('stat', 'points')
                return f"I couldn't retrieve the top players in {stat_type} at this time. Please try again later."
            
            if isinstance(data, list) and data:
                stat_type = intent_data.get('stat', 'points')
                limit = intent_data.get('limit', 5)
                results = []
                
                # Format stat type name for display
                stat_display_map = {
                    'points': 'points per game',
                    'assists': 'assists per game',
                    'rebounds': 'rebounds per game',
                    'steals': 'steals per game',
                    'blocks': 'blocks per game',
                    'three_pointers_made': '3-pointers made',
                    'three_pointers_made_per_game': '3-pointers made per game',
                    'three_point_pct': '3-pointer percentage',
                    'field_goal_pct': 'field goal percentage',
                    'score': 'points per game',
                    'scoring': 'points per game'
                }
                stat_display = stat_display_map.get(stat_type, f'{stat_type} per game')
                
                for idx, player in enumerate(data[:limit], 1):
                    player_name = player.get('player_name', 'Unknown')
                    stat_value = player.get('stat_value', player.get(stat_type, 0))
                    team = player.get('team', '')
                    games_played = player.get('games_played', 0)
                    
                    # Format stat value
                    # For field goal percentage and 3-point percentage, convert from 0-1 range to percentage
                    if stat_type == 'field_goal_pct' or stat_type == 'three_point_pct':
                        if isinstance(stat_value, float):
                            # Convert from 0-1 to percentage (e.g., 0.625 -> 62.5%)
                            stat_value_str = f"{stat_value * 100:.1f}%"
                        else:
                            stat_value_str = f"{float(stat_value) * 100:.1f}%" if stat_value else "0.0%"
                    elif stat_type == 'three_pointers_made':
                        # For total 3-pointers made, show as integer (no decimals)
                        if isinstance(stat_value, float):
                            stat_value_str = f"{int(stat_value)}"
                        else:
                            stat_value_str = str(int(float(stat_value))) if stat_value else "0"
                    else:
                        # Round to 1 decimal for averages
                        if isinstance(stat_value, float):
                            stat_value_str = f"{stat_value:.1f}"
                        else:
                            stat_value_str = str(stat_value)
                    
                    # For points, assists, rebounds, steals, blocks, 3-pointers made, and field goal percentage queries, use standings-like compact vertical format
                    if stat_type == 'points' or stat_display == 'points per game':
                        # Standings-like format: Rank. Player Name (Team) - PPG (Games)
                        if team:
                            player_line = f"{idx}. {player_name} ({team}) - {stat_value_str} PPG"
                        else:
                            player_line = f"{idx}. {player_name} - {stat_value_str} PPG"
                        
                        if games_played > 0:
                            player_line += f" ({games_played} games)"
                        
                        results.append(player_line)
                    elif stat_type == 'assists' or stat_display == 'assists per game':
                        # Same compact format as points: Rank. Player Name (Team) - APG (Games)
                        # Only show assist stat, no additional stats
                        if team:
                            player_line = f"{idx}. {player_name} ({team}) - {stat_value_str} APG"
                        else:
                            player_line = f"{idx}. {player_name} - {stat_value_str} APG"
                        
                        if games_played > 0:
                            player_line += f" ({games_played} games)"
                        
                        results.append(player_line)
                    elif stat_type == 'rebounds' or stat_display == 'rebounds per game':
                        # Same compact format as points: Rank. Player Name (Team) - RPG (Games)
                        # Only show rebound stat, no additional stats
                        if team:
                            player_line = f"{idx}. {player_name} ({team}) - {stat_value_str} RPG"
                        else:
                            player_line = f"{idx}. {player_name} - {stat_value_str} RPG"
                        
                        if games_played > 0:
                            player_line += f" ({games_played} games)"
                        
                        results.append(player_line)
                    elif stat_type == 'steals' or stat_display == 'steals per game':
                        # Same compact format as points: Rank. Player Name (Team) - SPG (Games)
                        # Only show steal stat, no additional stats
                        if team:
                            player_line = f"{idx}. {player_name} ({team}) - {stat_value_str} SPG"
                        else:
                            player_line = f"{idx}. {player_name} - {stat_value_str} SPG"
                        
                        if games_played > 0:
                            player_line += f" ({games_played} games)"
                        
                        results.append(player_line)
                    elif stat_type == 'blocks' or stat_display == 'blocks per game':
                        # Same compact format as points: Rank. Player Name (Team) - BPG (Games)
                        # Only show block stat, no additional stats
                        if team:
                            player_line = f"{idx}. {player_name} ({team}) - {stat_value_str} BPG"
                        else:
                            player_line = f"{idx}. {player_name} - {stat_value_str} BPG"
                        
                        if games_played > 0:
                            player_line += f" ({games_played} games)"
                        
                        results.append(player_line)
                    elif stat_type == 'three_pointers_made' or stat_display == '3-pointers made':
                        # Same compact format as points: Rank. Player Name (Team) - 3PM (Games)
                        # Only show total 3-pointers made stat, no additional stats
                        if team:
                            player_line = f"{idx}. {player_name} ({team}) - {stat_value_str} 3PM"
                        else:
                            player_line = f"{idx}. {player_name} - {stat_value_str} 3PM"
                        
                        if games_played > 0:
                            player_line += f" ({games_played} games)"
                        
                        results.append(player_line)
                    elif stat_type == 'three_pointers_made_per_game' or stat_display == '3-pointers made per game':
                        # Same compact format as points: Rank. Player Name (Team) - 3PM (Games)
                        # Only show 3-pointers made per game stat, no additional stats
                        if team:
                            player_line = f"{idx}. {player_name} ({team}) - {stat_value_str} 3PM"
                        else:
                            player_line = f"{idx}. {player_name} - {stat_value_str} 3PM"
                        
                        if games_played > 0:
                            player_line += f" ({games_played} games)"
                        
                        results.append(player_line)
                    elif stat_type == 'three_point_pct' or stat_display == '3-pointer percentage':
                        # Same compact format as points: Rank. Player Name (Team) - X.X% 3PT% (Games games)
                        # Only show 3-pointer percentage, no additional stats
                        if team:
                            player_line = f"{idx}. {player_name} ({team}) - {stat_value_str} 3PT%"
                        else:
                            player_line = f"{idx}. {player_name} - {stat_value_str} 3PT%"
                        
                        if games_played > 0:
                            player_line += f" ({games_played} games)"
                        
                        results.append(player_line)
                    elif stat_type == 'field_goal_pct' or stat_display == 'field goal percentage':
                        # Same compact format as points: Rank. Player Name (Team) - FG% (Games)
                        # Only show field goal percentage, no additional stats
                        if team:
                            player_line = f"{idx}. {player_name} ({team}) - {stat_value_str} FG%"
                        else:
                            player_line = f"{idx}. {player_name} - {stat_value_str} FG%"
                        
                        if games_played > 0:
                            player_line += f" ({games_played} games)"
                        
                        results.append(player_line)
                    else:
                        # For other stats, use detailed vertical format
                        player_lines = []
                        
                        # Player name and team
                        if team:
                            player_lines.append(f"{idx}. {player_name} ({team})")
                        else:
                            player_lines.append(f"{idx}. {player_name}")
                        
                        # Main stat
                        player_lines.append(f"   {stat_display.capitalize()}: {stat_value_str}")
                        
                        # Get additional stats for non-points queries
                        points = player.get('points', 0)
                        rebounds = player.get('rebounds', 0)
                        assists = player.get('assists', 0)
                        steals = player.get('steals', 0)
                        blocks = player.get('blocks', 0)
                        fg_pct = player.get('field_goal_pct', 0)
                        
                        # Add other stats only for non-points queries
                        if points > 0 and stat_type != 'points':
                            player_lines.append(f"   Points: {points:.1f} PPG")
                        if rebounds > 0 and stat_type != 'rebounds':
                            player_lines.append(f"   Rebounds: {rebounds:.1f} RPG")
                        if assists > 0 and stat_type != 'assists':
                            player_lines.append(f"   Assists: {assists:.1f} APG")
                        if steals > 0 and stat_type != 'steals':
                            player_lines.append(f"   Steals: {steals:.1f} SPG")
                        if blocks > 0 and stat_type != 'blocks':
                            player_lines.append(f"   Blocks: {blocks:.1f} BPG")
                        if fg_pct > 0:
                            player_lines.append(f"   Field Goal %: {fg_pct*100:.1f}%")
                        
                        # Games played (always show if available)
                        if games_played > 0:
                            player_lines.append(f"   Games Played: {games_played}")
                        
                        # Join all lines for this player
                        results.append("\n".join(player_lines))
                
                if results:
                    return f"Top {len(results)} players in {stat_display}:\n\n" + "\n\n".join(results)
        
        elif intent_type == 'player_stats' and data:
            # Handle both list and single dict
            if isinstance(data, list) and data:
                stat = data[0]
            elif isinstance(data, dict):
                stat = data
            else:
                stat = {}
            
            points = stat.get('points', 0)
            rebounds = stat.get('rebounds', 0)
            assists = stat.get('assists', 0)
            steals = stat.get('steals', 0)
            blocks = stat.get('blocks', 0)
            date = stat.get('match_date', '')
            team1 = stat.get('team1_name', '')
            team2 = stat.get('team2_name', '')
            player_team = stat.get('player_team', '')
            player_name = intent_data.get('player_name', 'The player')
            
            # Check if query mentions specific game/team
            query_lower = intent_data.get('query', '').lower()
            has_team_context = any(team in query_lower for team in ['vs', 'versus', 'against', 'lakers', 'warriors', 'celtics', 'suns'])
            
            if points is not None and points >= 0:  # Allow 0 points
                stats_parts = []
                if points is not None:
                    stats_parts.append(f"{int(points)} points")
                if rebounds is not None and rebounds >= 0:
                    stats_parts.append(f"{int(rebounds)} rebounds")
                if assists is not None and assists >= 0:
                    stats_parts.append(f"{int(assists)} assists")
                if steals is not None and steals >= 0:
                    stats_parts.append(f"{int(steals)} steals")
                if blocks is not None and blocks >= 0:
                    stats_parts.append(f"{int(blocks)} blocks")
                
                stats_str = ', '.join(stats_parts) if stats_parts else "no stats recorded"
                
                # Format based on available context - prioritize showing opponent team correctly
                if date and team1 and team2:
                    # Determine which team is the opponent based on player's team
                    if player_team:
                        # Player is on one team, opponent is the other
                        if player_team.lower() == team1.lower():
                            opponent = team2
                        elif player_team.lower() == team2.lower():
                            opponent = team1
                        else:
                            opponent = team2 if team1.lower() == player_team.lower() else team1
                        
                        # If query asked for vs specific team, verify it matches
                        query_lower = intent_data.get('query', '').lower()
                        if 'vs' in query_lower or 'versus' in query_lower:
                            # Use the teams from the game
                            return f"{player_name} scored {stats_str} in the {team1} vs {team2} game on {date}."
                        else:
                            return f"{player_name} scored {stats_str} when {player_team} played {opponent} on {date}."
                    else:
                        return f"{player_name} scored {stats_str} in the {team1} vs {team2} game on {date}."
                elif date and (team1 or player_team):
                    return f"{player_name} scored {stats_str} in their game on {date}."
                elif date:
                    return f"{player_name} scored {stats_str} in their game on {date}."
                elif team1 and team2:
                    return f"{player_name} scored {stats_str} in the {team1} vs {team2} game."
                else:
                    return f"{player_name} scored {stats_str} in their last game."
            elif isinstance(data, dict) and 'avg_points' in data:
                avg_points = data.get('avg_points', 0)
                avg_rebounds = data.get('avg_rebounds', 0)
                avg_assists = data.get('avg_assists', 0)
                avg_steals = data.get('avg_steals', 0)
                avg_blocks = data.get('avg_blocks', 0)
                games = data.get('games_played', 0)
                player_name = intent_data.get('player_name', 'The player')
                
                if avg_points >= 0:  # Allow 0 average
                    return f"{player_name} is averaging {avg_points:.1f} points, {avg_rebounds:.1f} rebounds, {avg_assists:.1f} assists, {avg_steals:.1f} steals, and {avg_blocks:.1f} blocks per game over {games} games this season."
        
        # CRITICAL: Check for 'date_schedule' FIRST (before 'schedule')
        # This ensures tomorrow queries are formatted correctly
        # Handle date_schedule even with empty data to check day after tomorrow
        if intent_type == 'date_schedule':
            # Handle date-specific schedule queries (today, tomorrow, yesterday) - CHECK THIS FIRST
            # Get target date from intent_data
            target_date = intent_data.get('date', '')
            
            # Handle empty data - check if we need to look for day after tomorrow
            if not data:
                query_lower = intent_data.get('query', '').lower()
                
                # If query mentions tomorrow and we have no data, check day after tomorrow
                if 'tomorrow' in query_lower and 'day after' not in query_lower and target_date:
                    from datetime import date, timedelta, datetime
                    try:
                        tomorrow_date = date.today() + timedelta(days=1)
                        day_after_date = date.today() + timedelta(days=2)
                        
                        # Check if target_date is tomorrow
                        target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
                        if target_date_obj == tomorrow_date:
                            # No games for tomorrow - try to fetch day after tomorrow
                            logger.info(f"No games for tomorrow ({target_date}), checking day after tomorrow ({day_after_date})")
                            
                            # Try to get day after tomorrow's games from schedule agent
                            try:
                                from agents.schedule_agent import ScheduleAgent
                                schedule_agent = ScheduleAgent()
                                day_after_result = schedule_agent.process_query(f"nba schedule for {day_after_date.strftime('%Y-%m-%d')}")
                                
                                if day_after_result and day_after_result.get('data'):
                                    day_after_games = day_after_result.get('data', [])
                                    if day_after_games:
                                        # Filter to exact date
                                        day_after_str = day_after_date.strftime('%Y-%m-%d')
                                        filtered_games = []
                                        for game in day_after_games:
                                            game_date = game.get('match_date', '')
                                            game_date_part = game_date[:10] if len(game_date) >= 10 else game_date
                                            if game_date_part == day_after_str:
                                                filtered_games.append(game)
                                        
                                        if filtered_games:
                                            # Format day after tomorrow's games
                                            results = []
                                            for match in filtered_games:
                                                team1 = match.get('team1_name', match.get('team1_display', ''))
                                                team2 = match.get('team2_name', match.get('team2_display', ''))
                                                venue = match.get('venue', '')
                                                
                                                if team1 and team2:
                                                    if venue:
                                                        results.append(f"{team1} vs {team2} at {venue}")
                                                    else:
                                                        results.append(f"{team1} vs {team2}")
                                            
                                            if results:
                                                formatted_games = "\n".join([f"  • {game}" for game in results])
                                                return f"NBA Schedule for day after tomorrow (no games tomorrow):\n\n{formatted_games}"
                            except Exception as e:
                                logger.warning(f"Error checking day after tomorrow: {e}")
                            
                            # If we couldn't get day after tomorrow's games, return appropriate message
                            return f"There are no NBA games scheduled for tomorrow ({tomorrow_date.strftime('%B %d, %Y')})."
                    except Exception as e:
                        logger.warning(f"Error processing empty date_schedule: {e}")
                
                # For other date_schedule queries with no data, return appropriate message
                if target_date:
                    try:
                        from datetime import datetime, date, timedelta
                        date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
                        today = date.today()
                        tomorrow = today + timedelta(days=1)
                        day_after = today + timedelta(days=2)
                        
                        if date_obj == today:
                            date_str = "today"
                        elif date_obj == tomorrow:
                            date_str = "tomorrow"
                        elif date_obj == day_after:
                            date_str = "day after tomorrow"
                        elif date_obj == today - timedelta(days=1):
                            date_str = "yesterday"
                        else:
                            date_str = date_obj.strftime('%B %d, %Y')
                        
                        return f"There are no NBA games scheduled for {date_str} ({date_obj.strftime('%B %d, %Y')})."
                    except:
                        return f"There are no NBA games scheduled for the requested date."
                else:
                    return "I couldn't find any games for the requested date."
            
            # Filter games to only show those matching the target date
            if target_date:
                from datetime import datetime
                try:
                    # Parse target date
                    target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
                    # Filter data to only include games on the target date
                    filtered_data = []
                    for match in data:
                        match_date_str = match.get('match_date', '')
                        if match_date_str:
                            # Extract date part (first 10 characters: YYYY-MM-DD)
                            match_date_part = match_date_str[:10] if len(match_date_str) >= 10 else match_date_str
                            try:
                                match_date_obj = datetime.strptime(match_date_part, '%Y-%m-%d').date()
                                if match_date_obj == target_date_obj:
                                    filtered_data.append(match)
                            except:
                                # If date parsing fails, check if string matches
                                if match_date_part == target_date:
                                    filtered_data.append(match)
                    # Use filtered data instead of all data
                    data = filtered_data
                    logger.info(f"Filtered {len(data)} games for date {target_date}")
                except Exception as e:
                    logger.warning(f"Error filtering by date: {e}, showing all games")
            
            if len(data) > 1:
                results = []
                for match in data[:20]:  # Show up to 20 games (already filtered by date)
                    team1 = match.get('team1_name', match.get('team1_display', ''))
                    team2 = match.get('team2_name', match.get('team2_display', ''))
                    match_date = match.get('match_date', '')
                    venue = match.get('venue', '')
                    status = match.get('status', '')
                    team1_score = match.get('team1_score')
                    team2_score = match.get('team2_score')
                    
                    if team1 and team2:
                        game_time = match.get('game_time', '')
                        if status == 'completed' and team1_score is not None and team2_score is not None:
                            # Completed game - show score
                            results.append(f"{team1} vs {team2}: {team1_score}-{team2_score}")
                        elif status == 'live':
                            # Live game - show current score
                            score_text = f" {team1_score}-{team2_score}" if team1_score is not None and team2_score is not None else ""
                            results.append(f"{team1} vs {team2}{score_text} (Live)")
                        else:
                            # Upcoming game - include time if available
                            if game_time:
                                if venue:
                                    results.append(f"{team1} vs {team2} at {game_time} at {venue}")
                                else:
                                    results.append(f"{team1} vs {team2} at {game_time}")
                            else:
                                if venue:
                                    results.append(f"{team1} vs {team2} at {venue}")
                                else:
                                    results.append(f"{team1} vs {team2}")
                
                if results:
                    target_date = intent_data.get('date', '')
                    is_next_available = intent_data.get('is_next_available', False)
                    
                    # Format date nicely
                    try:
                        from datetime import datetime, date, timedelta
                        date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
                        today = date.today()
                        tomorrow = today + timedelta(days=1)
                        day_after = today + timedelta(days=2)
                        
                        if date_obj == today:
                            date_str = "today"
                        elif date_obj == tomorrow:
                            # If showing day after tomorrow's games when user asked for tomorrow
                            if is_next_available:
                                date_str = "day after tomorrow (no games tomorrow)"
                            else:
                                date_str = "tomorrow"
                        elif date_obj == day_after:
                            # If showing day after tomorrow's games when user asked for tomorrow
                            if is_next_available:
                                date_str = "day after tomorrow (no games tomorrow)"
                            else:
                                date_str = "day after tomorrow"
                        elif date_obj == today - timedelta(days=1):
                            date_str = "yesterday"
                        else:
                            date_str = date_obj.strftime('%B %d, %Y')
                            if is_next_available:
                                date_str = f"{date_str} (next available games)"
                    except:
                        date_str = target_date
                        if is_next_available:
                            date_str = f"{date_str} (next available games)"
                    
                    # Format with better spacing and structure
                    formatted_games = "\n".join([f"  • {game}" for game in results])
                    return f"NBA Schedule for {date_str}:\n\n{formatted_games}"
            
            # Single match on date
            match = data[0] if data else {}
            team1 = match.get('team1_name', match.get('team1_display', ''))
            team2 = match.get('team2_name', match.get('team2_display', ''))
            match_date = match.get('match_date', '')
            venue = match.get('venue', '')
            status = match.get('status', '')
            team1_score = match.get('team1_score')
            team2_score = match.get('team2_score')
            
            if team1 and team2:
                # Format date nicely
                target_date = intent_data.get('date', match_date)
                is_next_available = intent_data.get('is_next_available', False)
                try:
                    from datetime import datetime, date, timedelta
                    date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
                    today = date.today()
                    tomorrow = today + timedelta(days=1)
                    
                    if date_obj == today:
                        date_str = "today"
                    elif date_obj == tomorrow:
                        date_str = "tomorrow"
                    elif date_obj == today - timedelta(days=1):
                        date_str = "yesterday"
                    else:
                        date_str = date_obj.strftime('%B %d, %Y')
                    
                    # If showing next available day instead of tomorrow, indicate this
                    if is_next_available and date_obj != tomorrow:
                        date_str = f"{date_str} (next available game)"
                except:
                    date_str = target_date
                    if is_next_available:
                        date_str = f"{date_str} (next available game)"
                
                if status == 'completed' and team1_score is not None and team2_score is not None:
                    return f"On {date_str}, {team1} vs {team2}: {team1_score}-{team2_score}."
                elif venue:
                    return f"On {date_str}, {team1} vs {team2} at {venue}."
                else:
                    return f"On {date_str}, {team1} vs {team2}."
        
        elif intent_type == 'schedule' and data:
            # CRITICAL: Check if query mentions "tomorrow" - if so, filter to only tomorrow's games
            query_lower = intent_data.get('query', '').lower()
            if 'tomorrow' in query_lower and 'day after' not in query_lower:
                from datetime import date, timedelta
                tomorrow_date = date.today() + timedelta(days=1)
                tomorrow_str = tomorrow_date.strftime('%Y-%m-%d')
                
                # Filter data to only tomorrow's games
                filtered_data = []
                for game in data:
                    game_date = game.get('match_date', '')
                    game_date_part = game_date[:10] if len(game_date) >= 10 else game_date
                    if game_date_part == tomorrow_str:
                        filtered_data.append(game)
                
                if filtered_data:
                    # Use the filtered data and format as date_schedule
                    data = filtered_data
                    logger.info(f"CRITICAL: Filtered schedule to {len(filtered_data)} games for tomorrow")
                    
                    # Format as date_schedule response
                    results = []
                    for match in filtered_data:
                        team1 = match.get('team1_name', match.get('team1_display', ''))
                        team2 = match.get('team2_name', match.get('team2_display', ''))
                        venue = match.get('venue', '')
                        
                        if team1 and team2:
                            if venue:
                                results.append(f"{team1} vs {team2} at {venue}")
                            else:
                                results.append(f"{team1} vs {team2}")
                    
                    if results:
                        formatted_games = "\n".join([f"  • {game}" for game in results])
                        return f"NBA Schedule for tomorrow:\n\n{formatted_games}"
                    else:
                        return f"There are no NBA games scheduled for tomorrow ({tomorrow_date.strftime('%B %d, %Y')})."
                elif not filtered_data and data:
                    # No games for tomorrow, but we have games - check day after tomorrow
                    logger.warning(f"CRITICAL: Query mentions tomorrow but no games found for {tomorrow_str}, checking day after tomorrow")
                    day_after_date = date.today() + timedelta(days=2)
                    day_after_str = day_after_date.strftime('%Y-%m-%d')
                    
                    # Filter data to only day after tomorrow's games
                    filtered_day_after = []
                    for game in data:
                        game_date = game.get('match_date', '')
                        game_date_part = game_date[:10] if len(game_date) >= 10 else game_date
                        if game_date_part == day_after_str:
                            filtered_day_after.append(game)
                    
                    if filtered_day_after:
                        # Format as day after tomorrow's games
                        results = []
                        for match in filtered_day_after:
                            team1 = match.get('team1_name', match.get('team1_display', ''))
                            team2 = match.get('team2_name', match.get('team2_display', ''))
                            venue = match.get('venue', '')
                            
                            if team1 and team2:
                                if venue:
                                    results.append(f"{team1} vs {team2} at {venue}")
                                else:
                                    results.append(f"{team1} vs {team2}")
                        
                        if results:
                            formatted_games = "\n".join([f"  • {game}" for game in results])
                            return f"NBA Schedule for day after tomorrow (no games tomorrow):\n\n{formatted_games}"
                    
                    # No games for tomorrow or day after tomorrow
                    return f"There are no NBA games scheduled for tomorrow ({tomorrow_date.strftime('%B %d, %Y')})."
            
            # Check if this is a team-specific query
            is_team_query = 'lakers' in query_lower or 'next' in query_lower or any(team in query_lower for team in ['warriors', 'celtics', 'bucks', 'nuggets', 'suns'])
            
            # Get number of games requested (if specified)
            num_games = intent_data.get('num_games')
            if num_games is None:
                # Try to extract from query
                import re
                num_match = re.search(r'next\s+(\d+)\s+games?', query_lower)
                if num_match:
                    num_games = int(num_match.group(1))
            
            # Determine how many games to show
            limit = num_games if num_games is not None else (len(data) if len(data) <= 20 else 20)
            
            # Handle multiple upcoming matches
            if len(data) > 1:
                results = []
                for match in data[:limit]:  # Use the limit
                    team1 = match.get('team1_name', '')
                    team2 = match.get('team2_name', '')
                    date_str = match.get('match_date', '')
                    venue = match.get('venue', '')
                    
                    # Format date nicely
                    formatted_date = date_str
                    if date_str:
                        try:
                            from datetime import datetime
                            if len(date_str) >= 10:
                                date_obj = datetime.strptime(date_str[:10], '%Y-%m-%d')
                                formatted_date = date_obj.strftime('%b %d, %Y')
                        except:
                            pass  # Use original date string if parsing fails
                    
                    if team1 and team2 and date_str:
                        if venue:
                            results.append(f"{team1} vs {team2} on {formatted_date} at {venue}")
                        else:
                            results.append(f"{team1} vs {team2} on {formatted_date}")
                
                if results:
                    if is_team_query and len(data) == 1:
                        # For "next game" queries, just show the first one
                        return f"The next game is {results[0]}."
                    # Format with better spacing and structure
                    formatted_games = "\n".join([f"  • {game}" for game in results])
                    return f"Upcoming games:\n\n{formatted_games}"
            
            # Single upcoming match
            if data:
                match = data[0] if isinstance(data, list) else data
                team1 = match.get('team1_name', '')
                team2 = match.get('team2_name', '')
                date = match.get('match_date', '')
                venue = match.get('venue', '')
                
                if team1 and team2 and date:
                    if venue:
                        return f"The next game is {team1} vs {team2} on {date} at {venue}."
                    else:
                        return f"The next game is {team1} vs {team2} on {date}."
        
        elif intent_type == 'live_game' and data:
            # Handle live game queries
            if len(data) > 1:
                results = []
                for game in data[:5]:
                    team1 = game.get('team1_name', '')
                    team2 = game.get('team2_name', '')
                    score1 = game.get('team1_score', 0)
                    score2 = game.get('team2_score', 0)
                    quarter = game.get('quarter', 1)
                    time = game.get('time_remaining', '')
                    status = game.get('game_status', 'live')
                    
                    if team1 and team2:
                        if status == 'halftime':
                            results.append(f"{team1} {score1} - {score2} {team2} (Halftime)")
                        else:
                            results.append(f"{team1} {score1} - {score2} {team2} (Q{quarter}, {time})")
                
                if results:
                    return "Live games:\n" + "\n".join(results)
            
            # Single live game
            game = data[0] if data else {}
            team1 = game.get('team1_name', '')
            team2 = game.get('team2_name', '')
            score1 = game.get('team1_score', 0)
            score2 = game.get('team2_score', 0)
            quarter = game.get('quarter', 1)
            time = game.get('time_remaining', '')
            status = game.get('game_status', 'live')
            
            if team1 and team2:
                if status == 'halftime':
                    return f"Live: {team1} {score1} - {score2} {team2} (Halftime)"
                else:
                    return f"Live: {team1} {score1} - {score2} {team2} (Q{quarter}, {time})"
        
        elif intent_type == 'standings' and data:
            # Handle games behind queries (e.g., "How far behind first place are the Celtics?")
            if intent_data.get('games_behind_query'):
                team_data = data if isinstance(data, dict) else {}
                team_name = intent_data.get('team', '')
                games_back = intent_data.get('games_back', 0)
                team_rank = intent_data.get('rank', 0)
                first_place_team = intent_data.get('first_place_team', {})
                conference = intent_data.get('conference', '')
                
                # Format team name
                team_display = team_data.get('team_name', team_name.title())
                wins = team_data.get('wins', 0)
                losses = team_data.get('losses', 0)
                
                # Format first place team name
                first_place_name = first_place_team.get('team_name', 'the first place team') if first_place_team else 'first place'
                
                conference_name = f"{conference}ern Conference" if conference else "NBA"
                
                if games_back == 0:
                    return f"The {team_display} are currently in first place in the {conference_name} with a record of {wins}-{losses}."
                else:
                    games_back_str = f"{games_back:.1f}".rstrip('0').rstrip('.') if games_back % 1 != 0 else str(int(games_back))
                    return f"The {team_display} are {games_back_str} game{'s' if games_back != 1 else ''} behind first place ({first_place_name}) in the {conference_name}. They are currently ranked {team_rank}{'th' if team_rank > 3 else ('st' if team_rank == 1 else ('nd' if team_rank == 2 else 'rd'))} with a record of {wins}-{losses}."
            
            # Handle team position queries (e.g., "Are the Thunder still in the top 3?")
            elif intent_data.get('team_position_query'):
                team_data = data if isinstance(data, dict) else {}
                team_name = intent_data.get('team', '')
                target_position = intent_data.get('target_position', 0)
                actual_rank = intent_data.get('actual_rank', 0)
                is_in_top = intent_data.get('is_in_top', False)
                conference = intent_data.get('conference', '')
                
                # Format team name
                team_display = team_data.get('team_name', team_name.title())
                # Use data from intent_data first (validated), then fallback to team_data
                wins = intent_data.get('wins', team_data.get('wins', 0))
                losses = intent_data.get('losses', team_data.get('losses', 0))
                win_pct = intent_data.get('win_percentage', team_data.get('win_percentage', 0))
                if win_pct > 0:
                    win_pct_str = f"{win_pct:.3f}".lstrip('0') if win_pct < 1 else "1.000"
                else:
                    win_pct_str = "0.000"
                
                # Format ordinal for rank
                if actual_rank == 1:
                    rank_ordinal = "1st"
                elif actual_rank == 2:
                    rank_ordinal = "2nd"
                elif actual_rank == 3:
                    rank_ordinal = "3rd"
                else:
                    rank_ordinal = f"{actual_rank}th"
                
                conference_name = f"{conference}ern Conference" if conference else "NBA"
                
                if is_in_top:
                    return f"Yes, the {team_display} are currently in the top {target_position} of the {conference_name}. They are ranked {rank_ordinal} with a record of {wins}-{losses} ({win_pct_str} win percentage)."
                else:
                    return f"No, the {team_display} are not in the top {target_position} of the {conference_name}. They are currently ranked {rank_ordinal} with a record of {wins}-{losses} ({win_pct_str} win percentage)."
            
            # Handle playoff spots queries (teams ranked 1-6)
            elif intent_data.get('playoff'):
                if isinstance(data, dict) and 'east' in data and 'west' in data:
                    east_teams = data['east']
                    west_teams = data['west']
                    
                    results = []
                    results.append("Eastern Conference Playoff Teams (Top 6):\n\n")
                    for team in east_teams:
                        team_name = team.get('team_name', '')
                        rank = team.get('conference_rank', 0)
                        wins = team.get('wins', 0)
                        losses = team.get('losses', 0)
                        win_pct = team.get('win_percentage', 0)
                        if win_pct > 0:
                            win_pct_str = f"{win_pct:.3f}".lstrip('0') if win_pct < 1 else "1.000"
                        else:
                            win_pct_str = "0.000"
                        results.append(f"{rank}. {team_name}: {wins}-{losses} ({win_pct_str})\n\n")
                    
                    results.append("Western Conference Playoff Teams (Top 6):\n\n")
                    for team in west_teams:
                        team_name = team.get('team_name', '')
                        rank = team.get('conference_rank', 0)
                        wins = team.get('wins', 0)
                        losses = team.get('losses', 0)
                        win_pct = team.get('win_percentage', 0)
                        if win_pct > 0:
                            win_pct_str = f"{win_pct:.3f}".lstrip('0') if win_pct < 1 else "1.000"
                        else:
                            win_pct_str = "0.000"
                        results.append(f"{rank}. {team_name}: {wins}-{losses} ({win_pct_str})\n\n")
                    
                    return "".join(results).rstrip()
            
            # Handle out of playoffs queries (teams ranked 11-15)
            elif intent_data.get('out_of_playoffs'):
                if isinstance(data, dict) and 'east' in data and 'west' in data:
                    east_teams = data['east']
                    west_teams = data['west']
                    
                    results = []
                    results.append("Eastern Conference Teams Out of Playoffs:\n\n")
                    for team in east_teams:
                        team_name = team.get('team_name', '')
                        rank = team.get('conference_rank', 0)
                        wins = team.get('wins', 0)
                        losses = team.get('losses', 0)
                        win_pct = team.get('win_percentage', 0)
                        if win_pct > 0:
                            win_pct_str = f"{win_pct:.3f}".lstrip('0') if win_pct < 1 else "1.000"
                        else:
                            win_pct_str = "0.000"
                        results.append(f"{rank}. {team_name}: {wins}-{losses} ({win_pct_str})\n\n")
                    
                    results.append("Western Conference Teams Out of Playoffs:\n\n")
                    for team in west_teams:
                        team_name = team.get('team_name', '')
                        rank = team.get('conference_rank', 0)
                        wins = team.get('wins', 0)
                        losses = team.get('losses', 0)
                        win_pct = team.get('win_percentage', 0)
                        if win_pct > 0:
                            win_pct_str = f"{win_pct:.3f}".lstrip('0') if win_pct < 1 else "1.000"
                        else:
                            win_pct_str = "0.000"
                        results.append(f"{rank}. {team_name}: {wins}-{losses} ({win_pct_str})\n\n")
                    
                    return "".join(results).rstrip()
            
            # Handle play-in tournament queries
            elif intent_data.get('playin'):
                if isinstance(data, dict) and 'east' in data and 'west' in data:
                    east_teams = data['east']
                    west_teams = data['west']
                    
                    results = []
                    results.append("Eastern Conference Play-In Teams:\n\n")
                    for team in east_teams:
                        team_name = team.get('team_name', '')
                        rank = team.get('conference_rank', 0)
                        wins = team.get('wins', 0)
                        losses = team.get('losses', 0)
                        win_pct = team.get('win_percentage', 0)
                        if win_pct > 0:
                            win_pct_str = f"{win_pct:.3f}".lstrip('0') if win_pct < 1 else "1.000"
                        else:
                            win_pct_str = "0.000"
                        results.append(f"{rank}. {team_name}: {wins}-{losses} ({win_pct_str})\n\n")
                    
                    results.append("Western Conference Play-In Teams:\n\n")
                    for team in west_teams:
                        team_name = team.get('team_name', '')
                        rank = team.get('conference_rank', 0)
                        wins = team.get('wins', 0)
                        losses = team.get('losses', 0)
                        win_pct = team.get('win_percentage', 0)
                        if win_pct > 0:
                            win_pct_str = f"{win_pct:.3f}".lstrip('0') if win_pct < 1 else "1.000"
                        else:
                            win_pct_str = "0.000"
                        results.append(f"{rank}. {team_name}: {wins}-{losses} ({win_pct_str})\n\n")
                    
                    return "".join(results).rstrip()
            
            # Handle standings queries
            # Check if this is a seed query (single team result)
            seed = intent_data.get('seed')
            if seed and isinstance(data, list) and len(data) == 1:
                # This is a seed query - format as direct answer
                standing = data[0]
                team = standing.get('team_name', '')
                wins = standing.get('wins', 0)
                losses = standing.get('losses', 0)
                win_pct = standing.get('win_percentage', 0)
                conference = intent_data.get('conference', '')
                
                if team:
                    # Format win percentage
                    if win_pct > 0:
                        win_pct_str = f"{win_pct:.3f}".lstrip('0') if win_pct < 1 else "1.000"
                    else:
                        win_pct_str = "0.000"
                    
                    # Format ordinal suffix
                    if seed == 1:
                        ordinal = "1st"
                    elif seed == 2:
                        ordinal = "2nd"
                    elif seed == 3:
                        ordinal = "3rd"
                    else:
                        ordinal = f"{seed}th"
                    
                    conference_name = f"{conference}ern Conference" if conference else "NBA"
                    return f"The {ordinal} seed in the {conference_name} is {team} with a record of {wins}-{losses} ({win_pct_str} win percentage)."
            
            if isinstance(data, list) and len(data) > 0:
                results = []
                # Map team names to abbreviations
                team_abbrev_map = {
                    'Oklahoma City Thunder': 'OKC', 'Detroit Pistons': 'DET', 'Houston Rockets': 'HOU',
                    'New York Knicks': 'NY', 'San Antonio Spurs': 'SA', 'Denver Nuggets': 'DEN',
                    'Los Angeles Lakers': 'LAL', 'Philadelphia 76ers': 'PHI', 'Boston Celtics': 'BOS',
                    'Orlando Magic': 'ORL', 'Minnesota Timberwolves': 'MIN', 'Toronto Raptors': 'TOR',
                    'Cleveland Cavaliers': 'CLE', 'Phoenix Suns': 'PHX', 'Miami Heat': 'MIA',
                    'Atlanta Hawks': 'ATL', 'Golden State Warriors': 'GS', 'Memphis Grizzlies': 'MEM',
                    'Chicago Bulls': 'CHI', 'Milwaukee Bucks': 'MIL', 'Utah Jazz': 'UTAH',
                    'Dallas Mavericks': 'DAL', 'Portland Trail Blazers': 'POR', 'Charlotte Hornets': 'CHA',
                    'LA Clippers': 'LAC', 'Sacramento Kings': 'SAC', 'Brooklyn Nets': 'BKN',
                    'Indiana Pacers': 'IND', 'New Orleans Pelicans': 'NO', 'Washington Wizards': 'WSH'
                }
                
                # Filter by conference FIRST if specified
                conference = intent_data.get('conference', '') or intent_data.get('conference', None)
                filtered_data = data
                
                # If conference is specified, filter the data
                if conference:
                    conf_upper = str(conference).upper()
                    if conf_upper in ['EAST', 'WEST']:
                        filtered_data = []
                        for standing in data:
                            team_conf = str(standing.get('conference', '')).upper()
                            # Check if conference matches (handles "West" vs "Western Conference", "East" vs "Eastern Conference")
                            # Match if: "WEST" in "WESTERN CONFERENCE" or "WESTERN" starts with "WEST"
                            if conf_upper in team_conf or team_conf.startswith(conf_upper):
                                filtered_data.append(standing)
                        
                        # If no filtered data found, try alternative conference name formats
                        if not filtered_data:
                            # Try "Western" or "Eastern"
                            alt_conf = 'WESTERN' if conf_upper == 'WEST' else 'EASTERN'
                            for standing in data:
                                team_conf = str(standing.get('conference', '')).upper()
                                if alt_conf in team_conf:
                                    filtered_data.append(standing)
                        
                        # Log if filtering happened
                        if len(filtered_data) < len(data):
                            logger.info(f"Filtered standings: {len(data)} -> {len(filtered_data)} teams for {conference} conference")
                        elif len(filtered_data) == len(data) and len(data) > 15:
                            # If we still have all teams, the filtering didn't work - try harder
                            logger.warning(f"Conference filtering may have failed - still have {len(data)} teams")
                            # Try to identify conference by team names (fallback)
                            western_teams = ['LAL', 'GS', 'DEN', 'OKC', 'HOU', 'SA', 'DAL', 'POR', 'UTAH', 'LAC', 'SAC', 'MEM', 'MIN', 'NO']
                            eastern_teams = ['BOS', 'PHI', 'NYK', 'CLE', 'MIA', 'ORL', 'ATL', 'CHI', 'TOR', 'DET', 'IND', 'CHA', 'MIL', 'BKN', 'WSH']
                            
                            if conf_upper == 'WEST':
                                # Filter to teams that are likely Western
                                filtered_data = [s for s in data if any(team in str(s.get('team_name', '')).upper() for team in western_teams)]
                            elif conf_upper == 'EAST':
                                # Filter to teams that are likely Eastern
                                filtered_data = [s for s in data if any(team in str(s.get('team_name', '')).upper() for team in eastern_teams)]
                
                # Only build results from filtered_data if a conference is specified
                # If no conference, we'll build results separately for each conference
                if conference:
                    # Sort filtered data by win percentage (descending) to get proper ranking
                    filtered_data_sorted = sorted(filtered_data, key=lambda x: x.get('win_percentage', 0), reverse=True)
                    
                    # Show all teams in the filtered list, re-ranked starting from 1
                    for rank, standing in enumerate(filtered_data_sorted, 1):
                        team = standing.get('team_name', '')
                        wins = standing.get('wins', 0)
                        losses = standing.get('losses', 0)
                        win_pct = standing.get('win_percentage', 0)
                        games = standing.get('games_played', wins + losses)
                        streak = standing.get('streak', '')
                        
                        if team and games > 0:
                            # Convert team name to abbreviation if available
                            team_abbrev = team_abbrev_map.get(team, team)
                            # If team name is already an abbreviation (3-4 chars), use it as is
                            if len(team) <= 4 and team.isupper():
                                team_abbrev = team
                            
                            # Format win percentage
                            if win_pct > 0:
                                win_pct_str = f"{win_pct:.3f}".lstrip('0') if win_pct < 1 else "1.000"
                            else:
                                win_pct_str = "0.000"
                            
                            # Build result line matching user's format: "1. OKC: 25-2 (.926)"
                            result_line = f"{rank}. {team_abbrev}: {wins}-{losses} ({win_pct_str})"
                            if streak:
                                result_line += f" - {streak}"
                            result_line += "\n"
                            results.append(result_line)
                
                if results or not conference:
                    # If conference was specified but we still have all teams, try to detect from query
                    if not conference and len(filtered_data) == len(data) and len(data) > 15:
                        # Check if query mentions conference
                        query = intent_data.get('query', '')
                        if query:
                            query_lower = query.lower()
                            if 'western' in query_lower or ('west' in query_lower and 'western' not in query_lower):
                                conference = 'West'
                                # Re-filter with detected conference
                                western_teams = ['LAL', 'GS', 'DEN', 'OKC', 'HOU', 'SA', 'DAL', 'POR', 'UTAH', 'LAC', 'SAC', 'MEM', 'MIN', 'NO', 'PHX']
                                filtered_data = [s for s in data if any(team in str(s.get('team_name', '')).upper() for team in western_teams)]
                                # Rebuild results with filtered data
                                results = []
                                for standing in filtered_data:
                                    team = standing.get('team_name', '')
                                    wins = standing.get('wins', 0)
                                    losses = standing.get('losses', 0)
                                    rank = standing.get('conference_rank', 0)
                                    win_pct = standing.get('win_percentage', 0)
                                    
                                    if team and (wins + losses) > 0:
                                        team_abbrev = team_abbrev_map.get(team, team)
                                        if len(team) <= 4 and team.isupper():
                                            team_abbrev = team
                                        
                                        win_pct_str = f"{win_pct:.3f}".lstrip('0') if win_pct < 1 else "1.000"
                                        result_line = f"{rank}. {team_abbrev}: {wins}-{losses} ({win_pct_str})\n"
                                        results.append(result_line)
                            elif 'eastern' in query_lower or ('east' in query_lower and 'eastern' not in query_lower):
                                conference = 'East'
                    
                    if conference:
                        # Properly format conference name with blank line after title
                        if conference.upper() == 'EAST':
                            return f"Eastern Conference Standings:\n\n" + "".join(results).rstrip() + "\n"
                        elif conference.upper() == 'WEST':
                            return f"Western Conference Standings:\n\n" + "".join(results).rstrip() + "\n"
                        else:
                            return f"{conference} Conference Standings:\n\n" + "".join(results).rstrip() + "\n"
                    else:
                        # Show both conferences separately
                        # Use original data (not filtered_data) to ensure we have all teams
                        logger.info(f"Processing standings: {len(data)} teams total")
                        
                        # First, try to identify by conference field
                        east_teams = []
                        west_teams = []
                        unassigned_teams = []
                        
                        for r in data:
                            conf = str(r.get('conference', '')).upper()
                            team_name = str(r.get('team_name', '')).upper()
                            # Check for Eastern Conference
                            if 'EAST' in conf or 'EASTERN' in conf:
                                east_teams.append(r)
                            # Check for Western Conference
                            elif 'WEST' in conf or 'WESTERN' in conf:
                                west_teams.append(r)
                            else:
                                # Conference field is missing or empty - will use fallback
                                unassigned_teams.append(r)
                        
                        logger.info(f"Conference field matching: {len(east_teams)} East, {len(west_teams)} West, {len(unassigned_teams)} unassigned")
                        
                        # If conference field doesn't work or we don't have enough teams, use team abbreviations as fallback
                        if len(east_teams) < 10 or len(west_teams) < 10 or unassigned_teams:
                            # Fallback: identify by team abbreviations - clear and rebuild
                            east_teams = []
                            west_teams = []
                            
                            # Comprehensive team name/abbreviation mapping
                            western_team_abbrevs = ['LAL', 'LAKERS', 'GS', 'GOLDEN STATE', 'WARRIORS', 'DEN', 'NUGGETS', 'OKC', 'THUNDER', 'HOU', 'ROCKETS', 'SA', 'SAS', 'SPURS', 'DAL', 'MAVERICKS', 'POR', 'TRAIL BLAZERS', 'BLAZERS', 'UTAH', 'JAZZ', 'LAC', 'CLIPPERS', 'SAC', 'KINGS', 'MEM', 'GRIZZLIES', 'MIN', 'TIMBERWOLVES', 'WOLVES', 'NO', 'NOP', 'PELICANS', 'PHX', 'SUNS', 'LOS ANGELES', 'DENVER', 'OKLAHOMA CITY', 'HOUSTON', 'SAN ANTONIO', 'DALLAS', 'PORTLAND', 'LA CLIPPERS', 'SACRAMENTO', 'MEMPHIS', 'MINNESOTA', 'NEW ORLEANS', 'PHOENIX']
                            eastern_team_abbrevs = ['BOS', 'CELTICS', 'PHI', '76ERS', 'SIXERS', 'NYK', 'KNICKS', 'CLE', 'CAVALIERS', 'CAVS', 'MIA', 'HEAT', 'ORL', 'MAGIC', 'ATL', 'HAWKS', 'CHI', 'BULLS', 'TOR', 'RAPTORS', 'DET', 'PISTONS', 'IND', 'PACERS', 'CHA', 'HORNETS', 'MIL', 'BUCKS', 'BKN', 'NETS', 'WSH', 'WIZARDS', 'BOSTON', 'PHILADELPHIA', 'NEW YORK', 'CLEVELAND', 'MIAMI', 'ORLANDO', 'ATLANTA', 'CHICAGO', 'TORONTO', 'DETROIT', 'INDIANA', 'CHARLOTTE', 'MILWAUKEE', 'BROOKLYN', 'WASHINGTON']
                            
                            # Process ALL teams to ensure we get all of them (fallback always processes everything)
                            for standing in data:
                                team_name = str(standing.get('team_name', '')).upper()
                                # Skip if already assigned by conference field
                                if standing in east_teams or standing in west_teams:
                                    continue
                                
                                # Check if team matches Western conference
                                is_western = any(abbrev in team_name for abbrev in western_team_abbrevs)
                                # Check if team matches Eastern conference
                                is_eastern = any(abbrev in team_name for abbrev in eastern_team_abbrevs)
                                
                                if is_western and not is_eastern:
                                    west_teams.append(standing)
                                elif is_eastern and not is_western:
                                    east_teams.append(standing)
                                # If both match (shouldn't happen), prioritize by checking full names
                                elif is_western and is_eastern:
                                    # Use more specific checks
                                    if any(name in team_name for name in ['LAKERS', 'CLIPPERS', 'WARRIORS', 'KINGS', 'SUNS']):
                                        west_teams.append(standing)
                                    elif any(name in team_name for name in ['CELTICS', 'KNICKS', '76ERS', 'SIXERS']):
                                        east_teams.append(standing)
                            
                            logger.info(f"After fallback: {len(east_teams)} East, {len(west_teams)} West teams")
                        
                        if east_teams and west_teams:
                            # Sort each conference by win percentage (descending) to get proper ranking
                            east_teams_sorted = sorted(east_teams, key=lambda x: x.get('win_percentage', 0), reverse=True)
                            west_teams_sorted = sorted(west_teams, key=lambda x: x.get('win_percentage', 0), reverse=True)
                            
                            east_results = []
                            west_results = []
                            
                            # Rank Eastern Conference teams starting from 1
                            for rank, standing in enumerate(east_teams_sorted, 1):
                                team = standing.get('team_name', '')
                                wins = standing.get('wins', 0)
                                losses = standing.get('losses', 0)
                                win_pct = standing.get('win_percentage', 0)
                                games = standing.get('games_played', wins + losses)
                                streak = standing.get('streak', '')
                                
                                if team and games > 0:
                                    # Use team abbreviations
                                    team_abbrev = team_abbrev_map.get(team, team)
                                    if len(team) <= 4 and team.isupper():
                                        team_abbrev = team
                                    
                                    win_pct_str = f"{win_pct:.3f}".lstrip('0') if win_pct < 1 else "1.000"
                                    result_line = f"{rank}. {team_abbrev}: {wins}-{losses} ({win_pct_str})"
                                    if streak:
                                        result_line += f" - {streak}"
                                    result_line += "\n"
                                    east_results.append(result_line)
                            
                            # Rank Western Conference teams starting from 1
                            for rank, standing in enumerate(west_teams_sorted, 1):
                                team = standing.get('team_name', '')
                                wins = standing.get('wins', 0)
                                losses = standing.get('losses', 0)
                                win_pct = standing.get('win_percentage', 0)
                                games = standing.get('games_played', wins + losses)
                                streak = standing.get('streak', '')
                                
                                if team and games > 0:
                                    # Use team abbreviations
                                    team_abbrev = team_abbrev_map.get(team, team)
                                    if len(team) <= 4 and team.isupper():
                                        team_abbrev = team
                                    
                                    win_pct_str = f"{win_pct:.3f}".lstrip('0') if win_pct < 1 else "1.000"
                                    result_line = f"{rank}. {team_abbrev}: {wins}-{losses} ({win_pct_str})"
                                    if streak:
                                        result_line += f" - {streak}"
                                    result_line += "\n"
                                    west_results.append(result_line)
                            
                            east_str = "".join(east_results).rstrip()
                            west_str = "".join(west_results).rstrip()
                            return f"Eastern Conference Standings:\n\n{east_str}\n\nWestern Conference Standings:\n\n{west_str}\n"
                        else:
                            return "Current NBA Standings:\n\n" + "".join(results).rstrip()
            
            # Single team standing or single dict (including seed queries)
            standing = data[0] if isinstance(data, list) and data else (data if isinstance(data, dict) else {})
            team = standing.get('team_name', '')
            wins = standing.get('wins', 0)
            losses = standing.get('losses', 0)
            rank = standing.get('conference_rank', 0)
            win_pct = standing.get('win_percentage', 0)
            games = standing.get('games_played', wins + losses)
            seed = intent_data.get('seed')
            conference = intent_data.get('conference', '')
            
            if team and games > 0:
                # Format win percentage
                if win_pct > 0:
                    win_pct_str = f"{win_pct:.3f}".lstrip('0') if win_pct < 1 else "1.000"
                else:
                    win_pct_str = "0.000"
                
                # Handle seed queries specifically
                if seed:
                    conference_name = f"{conference}ern Conference" if conference else "NBA"
                    return f"The {seed}{'th' if seed > 3 else ('st' if seed == 1 else ('nd' if seed == 2 else 'rd'))} seed in the {conference_name} is {team} with a record of {wins}-{losses} ({win_pct_str} win percentage)."
                else:
                    win_pct_str = f"{win_pct:.1%}" if win_pct else f"{wins/(games):.1%}"
                    return f"{team} has a record of {wins}-{losses} ({win_pct_str} win percentage) and is ranked #{rank} in the conference."
        
        elif intent_type == 'injuries' and data:
            # Handle injury queries
            if len(data) > 1:
                results = []
                for injury in data[:10]:
                    player = injury.get('player_name', '')
                    team = injury.get('team_name', '')
                    injury_type = injury.get('injury_type', '')
                    status = injury.get('status', '')
                    
                    if player:
                        results.append(f"{player} ({team}): {injury_type} - {status}")
                
                if results:
                    team_name = intent_data.get('team', '')
                    if team_name:
                        return f"{team_name.title()} Injury Report:\n" + "\n".join(results)
                    else:
                        return "Injury Report:\n" + "\n".join(results)
            
            # Single injury
            injury = data[0] if data else {}
            player = injury.get('player_name', '')
            team = injury.get('team_name', '')
            injury_type = injury.get('injury_type', '')
            status = injury.get('status', '')
            expected_return = injury.get('expected_return', '')
            
            if player:
                result = f"{player} ({team}) is {status} with {injury_type}"
                if expected_return:
                    result += f". Expected return: {expected_return}"
                return result + "."
        
        elif intent_type == 'player_trend' and data:
            # Handle player trend queries
            trend_data = data.get('trend', {}) if isinstance(data, dict) else {}
            recent_games = data.get('recent_games', []) if isinstance(data, dict) else []
            season_avg = data.get('season_average', {}) if isinstance(data, dict) else {}
            
            if trend_data:
                player_name = intent_data.get('player_name', 'The player')
                points_trend = trend_data.get('points_trend', '')
                recent_avg = trend_data.get('recent_avg_points', 0)
                season_avg_points = trend_data.get('season_avg_points', 0)
                
                if points_trend == 'up':
                    return f"{player_name} is trending up! Recent average: {recent_avg:.1f} PPG vs season average: {season_avg_points:.1f} PPG"
                else:
                    return f"{player_name} is trending down. Recent average: {recent_avg:.1f} PPG vs season average: {season_avg_points:.1f} PPG"
            elif recent_games:
                player_name = intent_data.get('player_name', 'The player')
                return f"{player_name}'s recent performance: {len(recent_games)} games analyzed"
            else:
                return "I don't have trend data for this player."
        
        elif intent_type == 'season_averages' and data:
            # Handle season averages queries
            if len(data) > 1:
                results = []
                for avg in data[:10]:
                    player = avg.get('player_name', '')
                    points = avg.get('points_per_game', 0)
                    rebounds = avg.get('rebounds_per_game', 0)
                    assists = avg.get('assists_per_game', 0)
                    games = avg.get('games_played', 0)
                    
                    if player:
                        results.append(f"{player}: {points:.1f} PPG, {rebounds:.1f} RPG, {assists:.1f} APG ({games} games)")
                
                if results:
                    return "Season Averages:\n" + "\n".join(results)
            
            # Single player season average
            avg = data[0] if isinstance(data, list) and data else (data if isinstance(data, dict) else {})
            player = avg.get('player_name', '')
            points = avg.get('points_per_game', 0)
            rebounds = avg.get('rebounds_per_game', 0)
            assists = avg.get('assists_per_game', 0)
            games = avg.get('games_played', 0)
            
            if player:
                return f"{player} is averaging {points:.1f} points, {rebounds:.1f} rebounds, and {assists:.1f} assists per game over {games} games this season."
        
        elif intent_type == 'team_news' and data:
            # Handle team news queries
            if len(data) > 1:
                results = []
                for news in data[:5]:
                    headline = news.get('headline', '')
                    team = news.get('team_name', '')
                    date = news.get('published_date', '')
                    is_breaking = news.get('is_breaking', False)
                    
                    if headline:
                        prefix = "🔥 BREAKING: " if is_breaking else ""
                        results.append(f"{prefix}{headline} ({team}, {date})")
                
                if results:
                    return "Team News:\n" + "\n".join(results)
            
            # Single news item
            news = data[0] if data else {}
            headline = news.get('headline', '')
            team = news.get('team_name', '')
            content = news.get('content', '')
            date = news.get('published_date', '')
            
            if headline:
                result = f"{headline} ({team}, {date})"
                if content:
                    result += f"\n{content[:200]}..."
                return result
        
        # Handle articles in fallback
        if intent_type == 'articles' or article_data:
            if article_data and article_data.get('combined_text'):
                # Use article text directly, limit length
                article_text = article_data['combined_text'][:1500]
                if article_text.strip():
                    # Extract key points from article
                    sentences = article_text.split('.')
                    key_sentences = [s.strip() for s in sentences[:5] if len(s.strip()) > 20]
                    if key_sentences:
                        return '. '.join(key_sentences) + '.'
                    return article_text[:500] + '...' if len(article_text) > 500 else article_text
            
            if intent_type == 'articles' and isinstance(data, list) and len(data) > 0:
                # Format article search results
                results = []
                for article in data[:3]:  # Limit to 3 articles
                    text = article.get('text', '')
                    if text:
                        # Get first 200 chars of article
                        preview = text[:200].strip()
                        if preview:
                            results.append(preview + '...')
                
                if results:
                    return '\n\n'.join(results)
        
        return "I don't have that information in my database."

