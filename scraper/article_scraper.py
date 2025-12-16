"""
Optimized Article Scraper Module
Scrapes basketball articles from RSS feeds using async/await for high performance
"""
import os
import asyncio
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
from tqdm import tqdm
import logging
import re
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse
import time
from datetime import datetime, timedelta
import feedparser

import sys
# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    RSS_FEEDS, 
    ARTICLES_DIR,
    MAX_CONCURRENT_REQUESTS,
    REQUEST_TIMEOUT,
    RATE_LIMIT_DELAY,
    MAX_RETRIES,
    MIN_ARTICLE_LENGTH
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArticleScraper:
    """Optimized async article scraper with NBA-specific filtering"""
    
    def __init__(self, articles_dir=ARTICLES_DIR, max_articles=1000):
        self.articles_dir = articles_dir
        self.max_articles = max_articles
        self.scraped_urls = set()
        self.article_count = 0
        self.failed_urls = []
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        
        # Create articles directory
        os.makedirs(self.articles_dir, exist_ok=True)
        
        # NBA keyword lists for filtering
        self.nba_teams = [
            'lakers', 'warriors', 'celtics', 'bucks', 'nuggets', 'suns', 'heat',
            'mavericks', 'clippers', '76ers', 'sixers', 'cavaliers', 'cavs', 'knicks', 
            'hawks', 'thunder', 'timberwolves', 'wolves', 'kings', 'pelicans', 
            'grizzlies', 'raptors', 'nets', 'bulls', 'pistons', 'pacers', 'hornets',
            'magic', 'wizards', 'rockets', 'spurs', 'jazz', 'trail blazers', 'blazers',
            'lakers', 'warriors', 'celtics', 'bucks', 'nuggets', 'suns', 'heat'
        ]
        
        # Common NBA player names (star players)
        self.nba_players = [
            'lebron', 'james', 'curry', 'durant', 'giannis', 'antetokounmpo', 'jokic',
            'doncic', 'tatum', 'butler', 'booker', 'lillard', 'morant', 'edwards',
            'holmgren', 'wembanyama', 'embiid', 'leonard', 'george', 'harden',
            'westbrook', 'paul', 'irving', 'ad', 'davis', 'towns', 'gobert',
            'mitchell', 'fox', 'sga', 'gilgeous-alexander', 'brown', 'holmgren',
            'banchero', 'cunningham', 'ball', 'lamelo', 'zion', 'williamson'
        ]
        
        # NBA-specific terms
        self.nba_terms = [
            'nba', 'national basketball association', 'playoffs', 'regular season',
            'nba finals', 'all-star', 'all star', 'mvp', 'rookie of the year',
            'defensive player', 'sixth man', 'nba draft', 'free agency', 'trade deadline',
            'conference finals', 'nba championship', 'nba game', 'nba matchup',
            'nba standings', 'nba schedule', 'nba stats', 'nba news', 'nba rumors'
        ]
        
        # Exclusion terms (non-NBA sports)
        self.exclusion_terms = [
            'college basketball', 'ncaa', 'march madness', 'college football',
            'nfl', 'super bowl', 'nhl', 'stanley cup', 'mlb', 'world series',
            'soccer', 'premier league', 'champions league', 'mls', 'fifa',
            'tennis', 'golf', 'pga', 'olympics', 'college sports', 'high school',
            'euroleague', 'fib', 'international basketball', 'wnba'  # WNBA is separate
        ]
        
        # Compile regex patterns once for performance
        self.ad_patterns = [
            re.compile(r'Subscribe.*?newsletter', re.IGNORECASE),
            re.compile(r'Click here.*?more', re.IGNORECASE),
            re.compile(r'Advertisement', re.IGNORECASE),
            re.compile(r'Ad\s+', re.IGNORECASE),
            re.compile(r'Cookie.*?policy', re.IGNORECASE),
            re.compile(r'Privacy.*?policy', re.IGNORECASE),
            re.compile(r'Terms.*?service', re.IGNORECASE),
            re.compile(r'Follow us on.*?', re.IGNORECASE),
            re.compile(r'Share this.*?', re.IGNORECASE),
            re.compile(r'Related:.*?', re.IGNORECASE),
        ]
        self.url_pattern = re.compile(r'http\S+')
        self.email_pattern = re.compile(r'\S+@\S+')
        
        # Compile NBA keyword patterns for faster matching
        self.nba_keyword_pattern = re.compile(
            r'\b(' + '|'.join(self.nba_teams + self.nba_players + self.nba_terms) + r')\b',
            re.IGNORECASE
        )
        self.exclusion_pattern = re.compile(
            r'\b(' + '|'.join(self.exclusion_terms) + r')\b',
            re.IGNORECASE
        )
    
    def is_nba_relevant(self, text: str, min_keywords: int = 2) -> Tuple[bool, int]:
        """
        Check if text is NBA-relevant
        Returns (is_relevant, keyword_count)
        """
        if not text:
            return False, 0
        
        text_lower = text.lower()
        
        # Check for exclusion terms first
        exclusion_matches = len(self.exclusion_pattern.findall(text_lower))
        if exclusion_matches > 0:
            # If exclusion terms are prominent, reject
            nba_matches = len(self.nba_keyword_pattern.findall(text_lower))
            if exclusion_matches >= nba_matches:
                return False, 0
        
        # Count NBA keywords
        keyword_count = len(self.nba_keyword_pattern.findall(text_lower))
        
        # Must have minimum number of NBA keywords
        is_relevant = keyword_count >= min_keywords
        
        return is_relevant, keyword_count
    
    def parse_published_date(self, date_str: str, entry=None) -> Optional[datetime]:
        """Parse published date from various formats"""
        # First try to use feedparser's parsed date if entry is provided
        if entry and hasattr(entry, 'published_parsed') and entry.published_parsed:
            try:
                return datetime(*entry.published_parsed[:6])
            except:
                pass
        
        if not date_str:
            return None
        
        # Try common date formats
        date_formats = [
            '%a, %d %b %Y %H:%M:%S %z',
            '%a, %d %b %Y %H:%M:%S %Z',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%d %b %Y',
            '%B %d, %Y',
            '%b %d, %Y',
        ]
        
        for fmt in date_formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed
            except:
                continue
        
        return None
    
    def get_article_age_days(self, published_date: Optional[datetime]) -> Optional[int]:
        """Get age of article in days, None if date is invalid"""
        if not published_date:
            return None
        try:
            return (datetime.now() - published_date.replace(tzinfo=None)).days
        except:
            return None
    
    def calculate_quality_score(
        self, 
        content: str, 
        title: str, 
        published_date: Optional[datetime]
    ) -> float:
        """
        Calculate quality score for an article
        Higher score = better quality
        """
        score = 0.0
        
        # NBA relevance (0-40 points)
        title_relevant, title_keywords = self.is_nba_relevant(title, min_keywords=1)
        content_relevant, content_keywords = self.is_nba_relevant(content, min_keywords=2)
        
        if not content_relevant:
            return 0.0  # Must be NBA-relevant
        
        score += min(20, title_keywords * 5)  # Title keywords
        score += min(20, content_keywords * 2)  # Content keywords
        
        # Date recency (0-30 points)
        age_days = self.get_article_age_days(published_date)
        if age_days is not None:
            if age_days <= 7:
                score += 30
            elif age_days <= 30:
                score += 25
            elif age_days <= 60:
                score += 20
            elif age_days <= 90:
                score += 15
            elif age_days <= 180:
                score += 10
            elif age_days <= 365:
                score += 5
            # Older than 1 year gets 0 points
        else:
            # No date, give moderate score
            score += 10
        
        # Content quality (0-30 points)
        content_length = len(content)
        if content_length >= 1000:
            score += 30
        elif content_length >= 500:
            score += 20
        elif content_length >= 300:
            score += 15
        elif content_length >= 200:
            score += 10
        
        # Team/player mentions bonus (0-10 points)
        team_mentions = sum(1 for team in self.nba_teams if team in content.lower())
        player_mentions = sum(1 for player in self.nba_players if player in content.lower())
        score += min(10, (team_mentions + player_mentions) * 2)
        
        return score
    
    def get_existing_articles(self) -> Dict[int, str]:
        """Get list of already scraped articles to enable resume"""
        existing = {}
        if not os.path.exists(self.articles_dir):
            return existing
        
        for filename in os.listdir(self.articles_dir):
            if filename.startswith('article_') and filename.endswith('.txt'):
                try:
                    # Extract article number from filename
                    num = int(filename.replace('article_', '').replace('.txt', ''))
                    existing[num] = filename
                except ValueError:
                    continue
        
        return existing
    
    def get_next_article_number(self) -> int:
        """Get the next article number to use"""
        existing = self.get_existing_articles()
        if existing:
            return max(existing.keys()) + 1
        return 0
    
    def clean_text(self, text: str) -> str:
        """Clean article text by removing ads, garbage, and extra whitespace"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common ad patterns (using pre-compiled patterns)
        for pattern in self.ad_patterns:
            text = pattern.sub('', text)
        
        # Remove URLs
        text = self.url_pattern.sub('', text)
        
        # Remove email addresses
        text = self.email_pattern.sub('', text)
        
        # Remove very short lines (likely navigation/ads)
        lines = text.split('\n')
        cleaned_lines = [line.strip() for line in lines if len(line.strip()) > 20]
        
        return ' '.join(cleaned_lines).strip()
    
    async def extract_article_content_async(
        self, 
        session: aiohttp.ClientSession, 
        url: str
    ) -> Optional[str]:
        """Extract article content from URL using async requests with improved extraction"""
        async with self.semaphore:  # Limit concurrent requests
            for attempt in range(MAX_RETRIES):
                try:
                    # Use aiohttp for async requests with better headers
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Cache-Control': 'max-age=0',
                    }
                    
                    async with session.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True) as response:
                        # Handle redirects and different status codes
                        if response.status == 404:
                            return None  # Fast-fail for 404
                        
                        # For 403, try with different headers
                        if response.status == 403:
                            if attempt == 0:
                                # Try with different user agent
                                headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                                continue
                            return None
                        
                        if response.status not in [200, 301, 302]:
                            if attempt < MAX_RETRIES - 1:
                                await asyncio.sleep(1)
                                continue
                            return None
                        
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Remove unwanted elements
                        for element in soup(["script", "style", "nav", "footer", "header", "aside", 
                                           "iframe", "noscript", "form", "button", "input"]):
                            element.decompose()
                        
                        # Try multiple strategies to find main content (improved)
                        content = None
                        content_candidates = []
                        
                        # Strategy 1: Look for article tag
                        article_tag = soup.find('article')
                        if article_tag:
                            text = article_tag.get_text()
                            if len(text) > MIN_ARTICLE_LENGTH:
                                content_candidates.append((len(text), text))
                        
                        # Strategy 2: Look for main tag
                        main_tag = soup.find('main')
                        if main_tag:
                            text = main_tag.get_text()
                            if len(text) > MIN_ARTICLE_LENGTH:
                                content_candidates.append((len(text), text))
                        
                        # Strategy 3: Look for common content div classes (expanded)
                        content_selectors = [
                            {'class': re.compile(r'content|article|post|entry|story|text|body', re.IGNORECASE)},
                            {'class': re.compile(r'main-content|article-content|post-content', re.IGNORECASE)},
                            {'id': re.compile(r'content|article|post|main', re.IGNORECASE)},
                            {'itemprop': 'articleBody'},
                            {'role': 'article'},
                        ]
                        
                        for selector in content_selectors:
                            divs = soup.find_all('div', selector)
                            for div in divs:
                                text = div.get_text()
                                if len(text) > MIN_ARTICLE_LENGTH:
                                    content_candidates.append((len(text), text))
                        
                        # Strategy 4: Look for paragraph-heavy sections
                        all_divs = soup.find_all('div')
                        for div in all_divs:
                            paragraphs = div.find_all('p')
                            if len(paragraphs) >= 3:  # At least 3 paragraphs
                                text = div.get_text()
                                if len(text) > MIN_ARTICLE_LENGTH:
                                    content_candidates.append((len(text), text))
                        
                        # Strategy 5: Fallback to body (but filter out navigation)
                        if not content_candidates:
                            body = soup.find('body')
                            if body:
                                # Remove navigation elements
                                for nav in body.find_all(['nav', 'header', 'footer', 'aside']):
                                    nav.decompose()
                                text = body.get_text()
                                if len(text) > MIN_ARTICLE_LENGTH:
                                    content_candidates.append((len(text), text))
                        
                        # Select the best candidate (longest, but not too long)
                        if content_candidates:
                            # Sort by length, prefer medium-length content (not too short, not too long)
                            content_candidates.sort(key=lambda x: x[0], reverse=True)
                            # Take the longest, but if it's extremely long, might be the whole page
                            # Prefer content between 500-10000 chars
                            best_content = None
                            for length, text in content_candidates:
                                if 500 <= length <= 10000:
                                    best_content = text
                                    break
                            # If no ideal length found, use the longest
                            if not best_content and content_candidates:
                                best_content = content_candidates[0][1]
                            
                            content = best_content
                        
                        if not content:
                            return None
                        
                        # Clean the content
                        cleaned_content = self.clean_text(content)
                        
                        # Ensure minimum length
                        if len(cleaned_content) < MIN_ARTICLE_LENGTH:
                            return None
                        
                        # Validate NBA relevance
                        is_relevant, keyword_count = self.is_nba_relevant(cleaned_content, min_keywords=2)
                        if not is_relevant:
                            logger.debug(f"Article rejected: Not NBA-relevant (keywords: {keyword_count})")
                            return None
                        
                        # Filter out non-NBA sections from mixed articles
                        # Split into paragraphs and keep only NBA-relevant ones
                        paragraphs = cleaned_content.split('. ')
                        nba_paragraphs = []
                        for para in paragraphs:
                            if len(para.strip()) > 50:  # Skip very short fragments
                                para_relevant, _ = self.is_nba_relevant(para, min_keywords=1)
                                if para_relevant:
                                    nba_paragraphs.append(para)
                        
                        # If we filtered out too much, keep original
                        if len(nba_paragraphs) < len(paragraphs) * 0.3:
                            # Less than 30% passed filter, might be too aggressive
                            # Keep original but ensure it's NBA-relevant
                            if keyword_count >= 3:
                                filtered_content = cleaned_content
                            else:
                                return None
                        else:
                            # Reconstruct with NBA-relevant paragraphs
                            filtered_content = '. '.join(nba_paragraphs)
                            if len(filtered_content) < MIN_ARTICLE_LENGTH:
                                # If filtering removed too much, use original if it's good enough
                                if keyword_count >= 4:
                                    filtered_content = cleaned_content
                                else:
                                    return None
                        
                        # Small delay to avoid overwhelming servers
                        await asyncio.sleep(RATE_LIMIT_DELAY)
                        return filtered_content
                        
                except asyncio.TimeoutError:
                    if attempt < MAX_RETRIES - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    return None
                except Exception as e:
                    if attempt < MAX_RETRIES - 1:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    logger.debug(f"Failed to extract {url}: {e}")
                    return None
            
            return None
    
    async def save_article_async(self, content: str, article_num: int) -> bool:
        """Save article content to file asynchronously"""
        filename = f"article_{article_num}.txt"
        filepath = os.path.join(self.articles_dir, filename)
        
        try:
            async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                await f.write(content)
            return True
        except Exception as e:
            logger.error(f"Error saving article {article_num}: {e}")
            return False
    
    def get_rss_entries(self) -> List[Dict]:
        """Fetch all entries from RSS feeds with NBA filtering and date prioritization"""
        all_entries = []
        
        for feed_url in RSS_FEEDS:
            try:
                logger.info(f"Fetching RSS feed: {feed_url}")
                feed = feedparser.parse(feed_url)
                
                if feed.bozo:
                    logger.warning(f"Feed parsing error for {feed_url}: {feed.bozo_exception}")
                    continue
                
                feed_count = 0
                for entry in feed.entries:
                    if not hasattr(entry, 'link'):
                        continue
                    
                    title = getattr(entry, 'title', 'Untitled')
                    published_str = getattr(entry, 'published', '')
                    
                    # Filter by title - must be NBA-relevant
                    is_relevant, _ = self.is_nba_relevant(title, min_keywords=1)
                    if not is_relevant:
                        continue
                    
                    # Parse published date (use entry object for better parsing)
                    published_date = self.parse_published_date(published_str, entry)
                    
                    # Skip articles older than 1 year (unless highly relevant)
                    age_days = self.get_article_age_days(published_date)
                    if age_days is not None and age_days > 365:
                        # Still allow if title has strong NBA keywords
                        title_keywords = len(self.nba_keyword_pattern.findall(title.lower()))
                        if title_keywords < 3:
                            continue
                    
                    all_entries.append({
                        'url': entry.link,
                        'title': title,
                        'published': published_str,
                        'published_date': published_date
                    })
                    feed_count += 1
                
                logger.info(f"Found {feed_count} NBA-relevant entries in {feed_url} (from {len(feed.entries)} total)")
                
            except Exception as e:
                logger.error(f"Error fetching feed {feed_url}: {e}")
                continue
        
        # Remove duplicates
        seen_urls = set()
        unique_entries = []
        for entry in all_entries:
            if entry['url'] not in seen_urls:
                seen_urls.add(entry['url'])
                unique_entries.append(entry)
        
        # Sort by date (newest first) for prioritization
        unique_entries.sort(
            key=lambda x: x.get('published_date') or datetime(1970, 1, 1),
            reverse=True
        )
        
        logger.info(f"Total unique NBA-relevant entries from RSS feeds: {len(unique_entries)}")
        return unique_entries
    
    async def scrape_article_listing_page(
        self,
        session: aiohttp.ClientSession,
        base_url: str,
        max_pages: int = 20
    ) -> List[str]:
        """Scrape article listing pages to find more article URLs"""
        article_urls = []
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            
            # Try the base URL first
            try:
                async with session.get(base_url, headers=headers, timeout=REQUEST_TIMEOUT) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Find article links (common patterns) - filter for NBA
                        links = soup.find_all('a', href=True)
                        for link in links:
                            href = link.get('href', '')
                            text = link.get_text()
                            
                            # Must contain NBA-related keywords in URL or text
                            href_lower = href.lower()
                            text_lower = text.lower()
                            
                            # Check if NBA-relevant
                            is_nba_url = any(keyword in href_lower for keyword in 
                                           ['/nba/', '/basketball', 'nba-', 'basketball'])
                            is_nba_text, _ = self.is_nba_relevant(text, min_keywords=1)
                            
                            if href and (is_nba_url or is_nba_text or 
                                        any(keyword in href_lower for keyword in 
                                           ['article', 'news', 'story', 'post', '/20'])):
                                # Make absolute URL
                                if href.startswith('/'):
                                    from urllib.parse import urljoin
                                    href = urljoin(base_url, href)
                                elif not href.startswith('http'):
                                    href = f"{base_url}/{href.lstrip('/')}"
                                
                                if href not in article_urls and base_url in href:
                                    article_urls.append(href)
            except Exception:
                pass
            
            # Try pagination
            for page in range(1, max_pages + 1):
                try:
                    # Try common pagination patterns
                    page_urls = [
                        f"{base_url}?page={page}",
                        f"{base_url}/page/{page}",
                        f"{base_url}/p/{page}",
                        f"{base_url}/archive/page/{page}",
                    ]
                    
                    for page_url in page_urls:
                        try:
                            async with session.get(page_url, headers=headers, timeout=REQUEST_TIMEOUT) as response:
                                if response.status == 200:
                                    html = await response.text()
                                    soup = BeautifulSoup(html, 'html.parser')
                                    
                                    # Find article links - filter for NBA
                                    links = soup.find_all('a', href=True)
                                    found_new = False
                                    for link in links:
                                        href = link.get('href', '')
                                        text = link.get_text()
                                        
                                        if not href:
                                            continue
                                        
                                        href_lower = href.lower()
                                        # Must be NBA-related
                                        is_nba_url = any(keyword in href_lower for keyword in 
                                                       ['/nba/', '/basketball', 'nba-', 'basketball'])
                                        is_nba_text, _ = self.is_nba_relevant(text, min_keywords=1)
                                        
                                        if is_nba_url or is_nba_text or any(keyword in href_lower for keyword in 
                                                       ['article', 'news', 'story', 'post', '/20']):
                                            if href.startswith('/'):
                                                from urllib.parse import urljoin
                                                href = urljoin(base_url, href)
                                            elif not href.startswith('http'):
                                                href = f"{base_url}/{href.lstrip('/')}"
                                            
                                            if href not in article_urls and base_url in href:
                                                article_urls.append(href)
                                                found_new = True
                                    
                                    if not found_new:
                                        break  # No more articles on this page
                                    
                                    await asyncio.sleep(0.3)  # Rate limit
                                    break  # Found a working page pattern
                        except Exception:
                            continue
                except Exception:
                    continue
                    
        except Exception as e:
            logger.debug(f"Error scraping listing page {base_url}: {e}")
        
        return article_urls[:100]  # Limit per site
    
    async def scrape_single_article(
        self,
        session: aiohttp.ClientSession,
        entry: Dict,
        article_num: int
    ) -> bool:
        """Scrape a single article and save it with quality scoring"""
        url = entry['url']
        
        # Skip if already scraped
        if url in self.scraped_urls:
            return False
        
        # Extract content
        content = await self.extract_article_content_async(session, url)
        
        if content:
            # Calculate quality score
            title = entry.get('title', '')
            published_date = entry.get('published_date')
            quality_score = self.calculate_quality_score(content, title, published_date)
            
            # Minimum quality threshold (adjust as needed)
            MIN_QUALITY_SCORE = 30.0
            
            if quality_score < MIN_QUALITY_SCORE:
                logger.debug(f"Article rejected: Quality score too low ({quality_score:.1f} < {MIN_QUALITY_SCORE})")
                self.failed_urls.append(url)
                return False
            
            # Save article
            if await self.save_article_async(content, article_num):
                self.scraped_urls.add(url)
                self.article_count += 1
                logger.debug(f"Article saved: {article_num} (score: {quality_score:.1f})")
                return True
            else:
                self.failed_urls.append(url)
        else:
            self.failed_urls.append(url)
        
        return False
    
    async def scrape_articles_async(self):
        """Main async scraping function with enhanced URL collection"""
        logger.info("Starting optimized article scraping for 1000 articles...")
        start_time = time.time()
        
        # Get all RSS entries
        entries = self.get_rss_entries()
        
        # If we don't have enough URLs, try to get more from article listing pages
        if len(entries) < self.max_articles:
            logger.info(f"Only {len(entries)} URLs from RSS. Attempting to find more from article listing pages...")
            
            # Try to scrape article listing pages from major sites
            listing_sites = [
                'https://www.talkbasket.net',
                'https://www.hoopsrumors.com',
                'https://basketball.realgm.com',
                'https://www.clutchpoints.com/nba',
                'https://www.cbssports.com/nba',
                'https://www.espn.com/nba',
            ]
            
            connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT_REQUESTS * 2)
            timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
            
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                listing_tasks = [self.scrape_article_listing_page(session, site) for site in listing_sites]
                listing_results = await asyncio.gather(*listing_tasks, return_exceptions=True)
                
                for urls in listing_results:
                    if isinstance(urls, list):
                        for url in urls:
                            if url not in [e['url'] for e in entries]:
                                entries.append({
                                    'url': url,
                                    'title': 'Untitled',
                                    'published': ''
                                })
        
        if not entries:
            logger.error("No RSS entries found from RSS feeds")
            return 0
        
        # Get starting article number (resume capability)
        start_num = self.get_next_article_number()
        logger.info(f"Starting from article number: {start_num}")
        logger.info(f"Total URLs collected: {len(entries)}")
        
        # Limit to max_articles, but get more URLs to account for failures
        # We need ~3-4x URLs to get 1000 good articles (many will fail)
        entries = entries[:self.max_articles * 4]  # Get 4x URLs to account for failures
        logger.info(f"Scraping up to {self.max_articles} articles from {len(entries)} URLs with {MAX_CONCURRENT_REQUESTS} concurrent requests...")
        
        # Create aiohttp session with connection pooling
        connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT_REQUESTS * 2)
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # Create tasks for all articles
            tasks = []
            article_num = start_num
            
            for entry in entries:
                if self.article_count >= self.max_articles:
                    break
                
                task = self.scrape_single_article(session, entry, article_num)
                tasks.append(task)
                article_num += 1
            
            # Process with progress updates
            results = []
            completed = 0
            for coro in asyncio.as_completed(tasks):
                result = await coro
                results.append(result)
                completed += 1
                if completed % 20 == 0 or completed == len(tasks):
                    success_so_far = sum(1 for r in results if r)
                    logger.info(f"Progress: {completed}/{len(tasks)} processed | {success_so_far} articles saved | Target: {self.max_articles}")
                    
                    # If we've reached target, we can stop early
                    if success_so_far >= self.max_articles:
                        logger.info(f"Reached target of {self.max_articles} articles!")
                        break
        
        elapsed_time = time.time() - start_time
        success_count = sum(1 for r in results if r)
        
        logger.info(f"Scraping complete!")
        logger.info(f"  Time elapsed: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
        logger.info(f"  Articles saved: {success_count}")
        logger.info(f"  Failed URLs: {len(self.failed_urls)}")
        if elapsed_time > 0:
            logger.info(f"  Average speed: {success_count/elapsed_time:.2f} articles/second")
        
        return success_count
    
    def scrape_articles(self):
        """Synchronous wrapper for async scraping"""
        return asyncio.run(self.scrape_articles_async())


if __name__ == "__main__":
    scraper = ArticleScraper(max_articles=1000)
    result = scraper.scrape_articles()
    if result < 1000:
        logger.warning(f"Only scraped {result} articles. Run the scraper again later to get more as new articles are published.")
    else:
        logger.info(f"Successfully scraped {result} articles!")
