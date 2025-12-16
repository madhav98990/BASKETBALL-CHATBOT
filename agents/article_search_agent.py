"""
Article Search Agent - Handles article-based queries
Searches Pinecone vector database for relevant articles
"""
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArticleSearchAgent:
    """Handles article search queries using Pinecone"""
    
    def __init__(self):
        self.vector_store = None
        self.initialized = False
        self.vector_store_available = False
    
    def _get_vector_store(self):
        """Lazy load vector store to avoid import errors at startup"""
        if self.vector_store is None:
            try:
                from embeddings.vector_store import VectorStore
                self.vector_store = VectorStore()
                self.vector_store_available = True
            except ImportError as e:
                logger.warning(f"Vector store not available: {e}. Article search will be disabled.")
                self.vector_store_available = False
        return self.vector_store
    
    def initialize(self):
        """Initialize vector store"""
        if not self.initialized:
            vector_store = self._get_vector_store()
            if not self.vector_store_available:
                logger.warning("Vector store not available. Cannot initialize article search.")
                return
            try:
                vector_store.initialize_model()
                vector_store.initialize_pinecone()
                self.initialized = True
            except Exception as e:
                logger.error(f"Error initializing vector store: {e}")
                raise
    
    def search_articles(self, query: str, top_k: int = 5) -> list:
        """Search for relevant articles - tries Pinecone first, falls back to file search"""
        # Try Pinecone vector search first
        if self.vector_store_available:
            if not self.initialized:
                try:
                    self.initialize()
                except Exception as e:
                    logger.warning(f"Could not initialize vector store: {e}, falling back to file search")
            
            if self.initialized:
                try:
                    results = self.vector_store.search(query, top_k=top_k)
                    if results:
                        logger.info(f"Found {len(results)} results from Pinecone")
                        return results
                except Exception as e:
                    logger.warning(f"Pinecone search failed: {e}, falling back to file search")
        
        # Fallback: Search articles directly from files
        logger.info("Searching articles from files as fallback")
        return self._search_articles_from_files(query, top_k)
    
    def _clean_article_content(self, content: str) -> str:
        """Clean article content by removing navigation junk, timestamps, and formatting"""
        import re
        
        if not content or len(content.strip()) < 50:
            return ""
        
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Find the actual article start - look for location markers, dates, or author bylines
        # Common patterns: "LAS VEGAS --", "Dec 13, 2025", author names followed by dates
        article_start_patterns = [
            r'[A-Z][A-Z\s]+\s*--\s+',  # Location markers like "LAS VEGAS --"
            r'\w+\s+\d{1,2},?\s+\d{4}',  # Date patterns like "Dec 13, 2025"
            r'EmailPrint',  # Often marks end of navigation
        ]
        
        article_start = -1
        for pattern in article_start_patterns:
            match = re.search(pattern, content)
            if match:
                # Check if there's substantial content after this pattern
                potential_start = match.end()
                # Look for a sentence or paragraph after the pattern
                remaining = content[potential_start:potential_start + 200]
                if len(remaining.strip()) > 50 and not re.search(r'^\s*[A-Z]{2,4}\s+\d+[hd]', remaining):
                    article_start = potential_start
                    break
        
        # If we found an article start, use content from there
        if article_start > 0:
            content = content[article_start:]
        
        # Remove common navigation patterns more aggressively
        navigation_patterns = [
            r'< >.*?\d+[hd]',  # Navigation items with timestamps
            r'[A-Z][a-z]+\'s\s+[A-Z][a-z]+\s+\d+[hd]',  # "Magic's Suggs 10h"
            r'[A-Z]{2,4}\s+\d+[hd]',  # "OKC 4h"
            r'[A-Z][a-z]+\s+\d+[hd]',  # "Orlando Magic10h"
            r'NBA Schedule.*?Washington Wizards',  # Schedule navigation
            r'Team Schedules.*?hidden',  # Team schedule navigation
            r'MATCHUPTIMETVtickets.*?Terms of Use',  # Schedule table
            r'All of ESPN[^.]*\.',  # "All of ESPN" navigation
            r'Sign Up Now|Watch Now|Subscribe Now',  # Subscription prompts
            r'Facebook|X/Twitter|Instagram|Snapchat|TikTok|YouTube|Google News',
            r'ESPN Deportes|Andscape|espnW|ESPNFC|X Games|SEC Network',
            r'Customize ESPN|Brian Windhorst|The Hoop Collective',
            r'Listen to|Spotify|Apple|Amazon|iHeartMedia|TuneIn|Latest episodes',
            r'EmailPrint|Close|Joined ESPN',
            r'Copyright.*?ESPN Sports Media Ltd',
            r'Terms of Use|Addendum to the Global Interest Based Ads',
            r'Follow him on Twitter|Follow on X',  # Social media links
        ]
        
        for pattern in navigation_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove article titles that are concatenated (often at start)
        # Pattern: TitleTextTeamNameTimeAuthor (e.g., "MVP' Brunson drops 40Orlando Magic10hVincent")
        content = re.sub(r'^[^.]*?[A-Z][a-z]+\s+\d+[hd][A-Z][a-z]+', '', content)
        
        # Split into lines and clean more aggressively
        lines = content.split('\n')
        cleaned_lines = []
        skip_navigation = True
        found_article_start = False
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped:
                if found_article_start:
                    cleaned_lines.append('')
                continue
            
            # Skip navigation lines
            if skip_navigation:
                # Check if this looks like navigation (article titles, timestamps, etc.)
                is_nav = False
                
                # Pattern: TitleTextTeamNameTimeAuthor
                if re.search(r'[A-Z][a-z]+\s+\d+[hd][A-Z]', line_stripped):
                    is_nav = True
                # Pattern: Short line with team abbrev and time
                elif len(line_stripped) < 100 and re.search(r'\b([A-Z]{2,4}|NBA|ESPN)\b.*\d+[hd]', line_stripped):
                    is_nav = True
                # Pattern: Just a title with time (no sentence structure)
                elif len(line_stripped) < 80 and re.search(r'\d+[hd]', line_stripped) and not re.search(r'[.!?]\s', line_stripped):
                    is_nav = True
                # Social media or navigation terms
                elif any(term in line_stripped for term in ['Listen to', 'Spotify', 'Apple', 'Sign Up', 'Watch Now', 'Follow on']):
                    is_nav = True
                
                if is_nav:
                    continue
                
                # Check if we've found the actual article content
                # Look for: location markers, dates, long sentences, or proper sentence structure
                if (re.search(r'--\s+[A-Z]', line_stripped) or  # Location marker
                    re.search(r'\d{1,2},?\s+\d{4}', line_stripped) or  # Date
                    re.search(r'[.!?]\s+[A-Z]', line_stripped) or  # Sentence structure
                    (len(line_stripped) > 150 and re.search(r'\b(the|a|an|is|are|was|were)\b', line_stripped, re.IGNORECASE))):  # Long sentence with common words
                    skip_navigation = False
                    found_article_start = True
                    # Skip if it's just a date/author line
                    if not re.search(r'^\w+\s+\w+.*\d{4}$', line_stripped):
                        cleaned_lines.append(line_stripped)
            else:
                # After navigation, skip remaining junk
                if any(junk in line_stripped for junk in ['All of ESPN', 'Sign Up', 'Watch Now', 'Facebook', 'Twitter', 'Follow on']):
                    continue
                # Skip very short lines that look like navigation
                if len(line_stripped) < 30 and re.search(r'\d+[hd]', line_stripped):
                    continue
                cleaned_lines.append(line_stripped)
        
        content = '\n'.join(cleaned_lines)
        
        # Remove repeated phrases (often from navigation)
        sentences = content.split('.')
        seen_sentences = set()
        unique_sentences = []
        for sentence in sentences:
            sentence_clean = sentence.strip()[:100]  # Use first 100 chars as key
            if sentence_clean and sentence_clean not in seen_sentences and len(sentence.strip()) > 20:
                seen_sentences.add(sentence_clean)
                unique_sentences.append(sentence.strip())
        
        content = '. '.join(unique_sentences)
        
        # Normalize whitespace
        content = re.sub(r'[ \t]+', ' ', content)
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(r'\.\s*\.', '.', content)  # Remove double periods
        
        return content.strip()
    
    def _extract_article_snippet(self, content: str, query_terms: list, match_positions: list, snippet_length: int = 1000) -> str:
        """Extract a clean, relevant snippet from article content"""
        import re
        
        # Clean content first
        cleaned = self._clean_article_content(content)
        if not cleaned or len(cleaned) < 100:
            return cleaned[:snippet_length] if cleaned else ""
        
        cleaned_lower = cleaned.lower()
        
        # Find the best match position in cleaned content
        best_pos = -1
        if query_terms:
            for term in query_terms:
                idx = cleaned_lower.find(term)
                if idx != -1 and (best_pos == -1 or idx < best_pos):
                    best_pos = idx
        
        if best_pos != -1 and best_pos < len(cleaned):
            # Extract snippet around match - ensure we get full sentences
            start = max(0, best_pos - 400)  # More context before
            end = min(len(cleaned), start + snippet_length)
            snippet = cleaned[start:end]
            
            # Try to start at sentence beginning (look for period-space or paragraph break)
            sentence_start = snippet.find('. ')
            if sentence_start > 100 and sentence_start < 400:
                snippet = snippet[sentence_start + 2:]
            else:
                # Try paragraph break
                para_start = snippet.find('\n\n')
                if para_start > 50 and para_start < 400:
                    snippet = snippet[para_start + 2:]
            
            # Try to end at sentence end
            sentence_end = snippet.rfind('. ')
            if sentence_end > snippet_length - 300:
                snippet = snippet[:sentence_end + 1]
            
            # Ensure snippet has meaningful content (not just navigation)
            if len(snippet.strip()) > 100 and not re.search(r'^\s*[A-Z]{2,4}\s+\d+[hd]', snippet):
                return snippet.strip()
        
        # Fallback: get first substantial paragraph(s) with proper sentences
        paragraphs = [p.strip() for p in cleaned.split('\n\n') if len(p.strip()) > 100]
        if paragraphs:
            # Combine first 2-3 paragraphs if they're short
            combined = paragraphs[0]
            for para in paragraphs[1:3]:
                if len(combined) < snippet_length - 200:
                    combined += " " + para
                else:
                    break
            return combined[:snippet_length]
        
        # Last resort: first substantial chunk with sentences
        sentences = [s.strip() for s in cleaned.split('.') if len(s.strip()) > 30]
        if sentences:
            combined = '. '.join(sentences[:5])  # First 5 sentences
            return combined[:snippet_length]
        
        return cleaned[:snippet_length]
    
    def _search_articles_from_files(self, query: str, top_k: int = 5) -> list:
        """Search articles directly from files using improved text matching"""
        import os
        import re
        from config import ARTICLES_DIR
        
        if not os.path.exists(ARTICLES_DIR):
            logger.warning(f"Articles directory not found: {ARTICLES_DIR}")
            return []
        
        query_lower = query.lower()
        
        # Clean query - remove common article query phrases
        query_clean = query_lower
        for phrase in ['what does', 'what do', 'the articles', 'article', 'articles', 'say about', 'says about', 'what']:
            query_clean = query_clean.replace(phrase, '')
        query_clean = query_clean.strip()
        
        # Remove question marks and punctuation
        query_clean = query_clean.replace('?', '').replace('.', '').replace(',', '').strip()
        
        # Extract key terms (remove stop words)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'about', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can'}
        query_terms = [term for term in query_clean.split() if term not in stop_words and len(term) > 2]
        
        # Detect question type for better matching
        question_type = 'general'
        if any(word in query_lower for word in ['loss', 'lost', 'losing', 'defeat', 'defeated', 'beat', 'beaten']):
            question_type = 'loss'
        elif any(word in query_lower for word in ['win', 'won', 'winning', 'victory', 'victorious']):
            question_type = 'win'
        elif any(word in query_lower for word in ['performance', 'perform', 'played', 'scored', 'points', 'stats', 'statistics']):
            question_type = 'performance'
        elif any(word in query_lower for word in ['injury', 'injured', 'hurt', 'out', 'sidelined', 'recovery']):
            question_type = 'injury'
        elif any(word in query_lower for word in ['trade', 'traded', 'deal', 'acquired', 'traded for']):
            question_type = 'trade'
        elif any(word in query_lower for word in ['mvp', 'most valuable', 'award', 'candidate']):
            question_type = 'award'
        
        # Extract phrases (2-word combinations) for better matching
        query_phrases = []
        if len(query_terms) >= 2:
            for i in range(len(query_terms) - 1):
                phrase = f"{query_terms[i]} {query_terms[i+1]}"
                query_phrases.append(phrase)
        
        # Add question-type specific terms to boost matching
        type_boost_terms = []
        if question_type == 'loss':
            type_boost_terms = ['loss', 'lost', 'losing', 'defeat', 'defeated', 'beat', 'beaten', 'struggled', 'fell']
        elif question_type == 'win':
            type_boost_terms = ['win', 'won', 'winning', 'victory', 'victorious', 'defeated', 'beat']
        elif question_type == 'performance':
            type_boost_terms = ['performance', 'scored', 'points', 'played', 'game', 'minutes', 'assists', 'rebounds']
        elif question_type == 'injury':
            type_boost_terms = ['injury', 'injured', 'out', 'sidelined', 'recovery', 'rehab', 'status']
        elif question_type == 'trade':
            type_boost_terms = ['trade', 'traded', 'deal', 'acquired', 'traded for', 'transaction']
        
        # Add type-specific terms to query terms if not already present
        for boost_term in type_boost_terms:
            if boost_term not in query_terms and boost_term not in query_lower:
                # Don't add if it's already in the query
                pass
        
        # If no meaningful terms after cleaning, use original query terms
        if not query_terms:
            query_terms = [term for term in query_lower.split() if len(term) > 2]
        
        results = []
        article_files = sorted([f for f in os.listdir(ARTICLES_DIR) if f.endswith('.txt')], reverse=True)  # Newest first
        
        logger.info(f"Searching {len(article_files)} article files for: {query} (key terms: {query_terms}, phrases: {query_phrases})")
        
        for filename in article_files[:300]:  # Search more files for better coverage
            filepath = os.path.join(ARTICLES_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if not content or len(content.strip()) < 100:
                        continue
                    
                    # Clean content first
                    cleaned_content = self._clean_article_content(content)
                    if len(cleaned_content) < 100:
                        continue
                    
                    content_lower = cleaned_content.lower()
                    
                    # Improved relevance scoring
                    score = 0
                    match_positions = []
                    matched_terms = set()
                    
                    # Score 1: Phrase matching (highest priority)
                    for phrase in query_phrases:
                        if phrase in content_lower:
                            score += 10  # High bonus for phrase matches
                            idx = content_lower.find(phrase)
                            if idx != -1:
                                match_positions.append(idx)
                            matched_terms.update(phrase.split())
                    
                    # Score 2: Individual term matching
                    for term in query_terms:
                        if term not in matched_terms:  # Don't double-count if already in phrase
                            count = content_lower.count(term)
                            if count > 0:
                                # Weight longer terms more (they're more specific)
                                weight = 3 if len(term) > 5 else 2 if len(term) > 4 else 1
                                score += count * weight
                                idx = content_lower.find(term)
                                if idx != -1:
                                    match_positions.append(idx)
                                matched_terms.add(term)
                    
                    # Score 3: Question-type specific matching
                    if question_type != 'general':
                        type_terms = {
                            'loss': ['loss', 'lost', 'losing', 'defeat', 'defeated', 'beat', 'struggled'],
                            'win': ['win', 'won', 'winning', 'victory', 'defeated', 'beat'],
                            'performance': ['scored', 'points', 'performance', 'played', 'game', 'minutes'],
                            'injury': ['injury', 'injured', 'out', 'sidelined', 'recovery'],
                            'trade': ['trade', 'traded', 'deal', 'acquired'],
                            'award': ['mvp', 'most valuable', 'award', 'candidate']
                        }
                        type_matches = sum(1 for term in type_terms.get(question_type, []) if term in content_lower)
                        if type_matches > 0:
                            score += type_matches * 2  # Bonus for type-specific matches
                    
                    # Score 4: Bonus for multiple terms matching
                    matched_count = len([t for t in query_terms if t in matched_terms or any(t in phrase for phrase in query_phrases if phrase in content_lower)])
                    if matched_count >= 2:
                        score *= 1.5
                    if matched_count == len(query_terms) and len(query_terms) > 1:
                        score *= 2  # All terms match - very relevant
                    
                    if score > 0:
                        # Extract clean snippet
                        snippet = self._extract_article_snippet(cleaned_content, query_terms, match_positions, snippet_length=1000)
                        
                        if snippet and len(snippet.strip()) > 100:  # Only add if meaningful content
                            results.append({
                                'text': snippet.strip(),
                                'filename': filename,
                                'score': score
                            })
            except Exception as e:
                logger.debug(f"Error reading {filename}: {e}")
                continue
        
        # Sort by relevance score and return top_k
        results.sort(key=lambda x: x['score'], reverse=True)
        logger.info(f"Found {len(results)} relevant articles from files")
        return results[:top_k]
    
    def process_query(self, question: str) -> dict:
        """Process an article-based query"""
        try:
            logger.info(f"Processing article query: {question}")
            results = self.search_articles(question, top_k=5)
            logger.info(f"Found {len(results)} article results")
            
            if not results:
                logger.warning("No article results found")
                return {
                    'type': 'articles',
                    'data': [],
                    'combined_text': '',
                    'query': question,
                    'error': 'No articles found'
                }
            
            # Combine relevant chunks and clean
            text_chunks = []
            for result in results:
                text = result.get('text', '').strip()
                if text and len(text) > 50:  # Only include meaningful chunks
                    # Additional cleaning for combined text
                    import re
                    # Remove any remaining navigation patterns
                    text = re.sub(r'< >.*?\d+[hd]', '', text, flags=re.IGNORECASE)
                    text = re.sub(r'[A-Z]{2,4}\s+\d+[hd]', '', text)
                    text = re.sub(r'EmailPrint|Close|Joined ESPN', '', text)
                    # Remove excessive whitespace
                    text = re.sub(r'\s+', ' ', text)
                    text = text.strip()
                    if text:
                        text_chunks.append(text)
            
            combined_text = "\n\n".join(text_chunks)
            
            if not combined_text or len(combined_text.strip()) < 100:
                logger.warning("No meaningful text content in article results")
                return {
                    'type': 'articles',
                    'data': [],
                    'combined_text': '',
                    'query': question,
                    'error': 'No article content found'
                }
            
            logger.info(f"Combined text length: {len(combined_text)}")
            return {
                'type': 'articles',
                'data': results,
                'combined_text': combined_text,
                'query': question
            }
        except Exception as e:
            logger.error(f"Error processing article query: {e}", exc_info=True)
            return {
                'type': 'articles',
                'data': [],
                'combined_text': '',
                'error': str(e),
                'query': question
            }

