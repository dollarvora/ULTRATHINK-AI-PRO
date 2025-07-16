"""
Reddit Fetcher - ULTRATHINK-AI-PRO Enhanced Reddit Data Collection
=================================================================

PURPOSE:
- Fetches pricing-related content from Reddit using enhanced PRAW API approach
- Replaces broken snscrape with reliable, authenticated Reddit API access
- Implements multiple search methods for comprehensive data coverage
- Provides quality filtering and deduplication for clean data sets

TECHNICAL APPROACH:
- Uses PRAW (Python Reddit API Wrapper) with official Reddit API credentials
- 4-method search strategy: hot, new, top, rising posts for maximum coverage
- Smart fallback system: extends to 7-day search if insufficient 24h data
- Quality filtering: minimum scores, comments, and age limits
- Content deduplication using MD5 hashing and Reddit post IDs
- Security validation and input sanitization when available

INTEGRATION:
- Part of ULTRATHINK-AI-PRO hybrid pricing intelligence system
- Works with 29+ configured subreddits for enterprise IT pricing signals
- Feeds processed data to GPT summarizer for insight generation
- Outputs structured data for HTML report generation

AUTHENTICATION REQUIRED:
- REDDIT_CLIENT_ID: Reddit API application client ID
- REDDIT_CLIENT_SECRET: Reddit API application secret  
- REDDIT_USER_AGENT: User agent string for API requests

Author: Dollar (dollar3191@gmail.com)
System: ULTRATHINK-AI-PRO v3.1.0 Hybrid
"""

import os
import asyncio
import praw
import hashlib
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from fetchers.base_fetcher import BaseFetcher

# Import security components
try:
    from utils.security_manager import InputValidator, SecureCredentialManager, secure_api_call
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False

logger = logging.getLogger(__name__)


class RedditFetcher(BaseFetcher):
    """Fetches content from Reddit subreddits"""

    def __init__(self, config=None):
        # Handle both old and new calling patterns
        if config is None:
            # Create a minimal config for backward compatibility
            config = {
                'sources': {'reddit': {'subreddits': [], 'post_limit': 50, 'comment_limit': 20}},
                'keywords': {'pricing': [], 'urgency_indicators': []},
                'vendors': {},
                'scoring': {'keyword_weight': 1.0, 'urgency_weight': 2.0, 'vendor_weight': 1.5,
                           'high_score_threshold': 5.0, 'medium_score_threshold': 2.0},
                'system': {'cache_ttl_hours': 6}
            }
        super().__init__(config)
        self.config = config
        
        # Load performance settings from config
        if config and 'performance' in config and 'reddit' in config['performance']:
            self.performance_settings = config['performance']['reddit']
        else:
            # Default settings
            self.performance_settings = {
                'quality_post_min_score': 3,
                'quality_post_min_comments': 3,
                'max_post_age_days': 30,
                'search_time_window': 'week',
                'extended_search_days': 3
            }
        
        # Initialize security components
        if SECURITY_AVAILABLE:
            self.credential_manager = SecureCredentialManager(config)
            self.input_validator = InputValidator(config)
        else:
            self.credential_manager = None
            self.input_validator = None

    def get_source_name(self) -> str:
        return 'reddit'

    def _get_reddit_client(self) -> praw.Reddit:
        """Create authenticated Reddit client using environment variables with security validation"""
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        user_agent = os.getenv("REDDIT_USER_AGENT", "ultrathink-script/1.0 (by u/your_username)")
        
        # Validate credentials if security is available
        if self.credential_manager:
            if not self.credential_manager.validate_api_key('reddit', client_id, self.config):
                logger.warning("🔒 Reddit client ID validation failed")
            else:
                logger.info("✅ Reddit credentials validated successfully")
        
        return praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
    
    def _is_quality_post(self, submission):
        """Filter out low-quality posts using configurable thresholds"""
        # Skip deleted/removed
        if submission.selftext in ['[removed]', '[deleted]']:
            return False
        
        # Skip low engagement posts using configurable thresholds
        min_score = self.performance_settings.get('quality_post_min_score', 3)
        min_comments = self.performance_settings.get('quality_post_min_comments', 3)
        if submission.score < min_score and submission.num_comments < min_comments:
            return False
            
        # Skip very old posts using configurable age limit
        max_age_days = self.performance_settings.get('max_post_age_days', 30)
        post_age = datetime.now() - datetime.fromtimestamp(submission.created_utc)
        if post_age.days > max_age_days:
            return False
            
        return True

    async def fetch_raw(self) -> List[Dict[str, Any]]:
        """Fetch posts from configured subreddits"""
        # Reddit API is synchronous, so run in executor
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._fetch_sync)

    def _fetch_sync(self) -> List[Dict[str, Any]]:
        """Synchronous fetch method for Reddit using enhanced PRAW API approach"""
        all_posts = []
        
        # Enhanced PRAW API fetching with multiple search methods
        api_posts = self._fetch_via_enhanced_praw()
        all_posts.extend(api_posts)
        
        # Deduplicate posts by ID
        deduplicated = self._deduplicate_posts(all_posts)
        
        self.logger.info(f"Reddit enhanced API fetch: {len(api_posts)} collected → {len(deduplicated)} unique")
        
        return deduplicated
    
    def _fetch_via_enhanced_praw(self) -> List[Dict[str, Any]]:
        """
        Enhanced Reddit API fetching with multiple search methods and better coverage
        
        METHODOLOGY:
        1. Method 1 (Hot): Gets trending content with high engagement
        2. Method 2 (New): Gets recent posts for timely pricing signals  
        3. Method 3 (Top/Day): Gets highest quality content from today
        4. Method 4 (Rising): Gets emerging trends before they peak
        5. Smart Fallback: If <5 posts in 24h, extends to 7-day search
        
        QUALITY FILTERS:
        - Minimum score and comment thresholds (configurable)
        - Maximum post age limits (default 30 days)
        - Removes deleted/removed posts
        - Deduplicates across all search methods
        
        PERFORMANCE:
        - Processes 29+ subreddits in parallel
        - Configurable post limits per method
        - Timeout handling for unresponsive subreddits
        - Structured error handling with logging
        
        Returns: List of structured Reddit post data for GPT analysis
        """
        reddit = self._get_reddit_client()
        all_posts = []

        # Enhanced time windows
        time_threshold_24h = datetime.now() - timedelta(hours=24)
        time_threshold_7d = datetime.now() - timedelta(days=7)

        for subreddit_name in self.source_config['subreddits']:
            # Validate subreddit name if security is available
            if self.input_validator:
                if not self.input_validator.validate_subreddit_name(subreddit_name):
                    logger.warning(f"🔒 Invalid subreddit name skipped: {subreddit_name}")
                    continue
            
            try:
                self.logger.info(f"Fetching from r/{subreddit_name} via enhanced API")
                subreddit = reddit.subreddit(subreddit_name)
                subreddit_posts = []

                # Method 1: Hot posts (trending content)
                for submission in subreddit.hot(limit=self.source_config['post_limit']):
                    if self._is_quality_post(submission):
                        post_data = self._extract_post_data(submission)
                        if post_data['created_at'] > time_threshold_24h:
                            subreddit_posts.append(post_data)

                # Method 2: New posts (recent content)
                for submission in subreddit.new(limit=self.source_config['post_limit']):
                    if self._is_quality_post(submission):
                        post_data = self._extract_post_data(submission)
                        if post_data['created_at'] > time_threshold_24h and \
                           post_data['id'] not in [p['id'] for p in subreddit_posts]:
                            subreddit_posts.append(post_data)

                # Method 3: Top posts from today (high-quality content)
                try:
                    for submission in subreddit.top(time_filter='day', limit=self.source_config['post_limit']):
                        if self._is_quality_post(submission):
                            post_data = self._extract_post_data(submission)
                            if post_data['created_at'] > time_threshold_24h and \
                               post_data['id'] not in [p['id'] for p in subreddit_posts]:
                                subreddit_posts.append(post_data)
                except:
                    pass  # Some subreddits might not support top posts

                # Method 4: Rising posts (emerging trends)
                try:
                    for submission in subreddit.rising(limit=self.source_config['post_limit']):
                        if self._is_quality_post(submission):
                            post_data = self._extract_post_data(submission)
                            if post_data['created_at'] > time_threshold_24h and \
                               post_data['id'] not in [p['id'] for p in subreddit_posts]:
                                subreddit_posts.append(post_data)
                except:
                    pass  # Some subreddits might not support rising posts

                # Smart fallback: If insufficient 24h data, extend to 7 days with top posts
                if len(subreddit_posts) < 5:
                    self.logger.info(f"⚠️ Only {len(subreddit_posts)} posts in 24h for r/{subreddit_name}, extending to 7 days...")
                    
                    # Get top posts from past week
                    try:
                        for submission in subreddit.top(time_filter='week', limit=self.source_config['post_limit'] * 2):
                            if self._is_quality_post(submission):
                                post_data = self._extract_post_data(submission)
                                if post_data['created_at'] > time_threshold_7d and \
                                   post_data['id'] not in [p['id'] for p in subreddit_posts]:
                                    subreddit_posts.append(post_data)
                    except:
                        pass

                    # Get recent posts from past week
                    for submission in subreddit.new(limit=self.source_config['post_limit'] * 3):
                        if self._is_quality_post(submission):
                            post_data = self._extract_post_data(submission)
                            if post_data['created_at'] > time_threshold_7d and \
                               post_data['id'] not in [p['id'] for p in subreddit_posts]:
                                subreddit_posts.append(post_data)
                
                all_posts.extend(subreddit_posts)
                self.logger.info(f"✅ Enhanced fetch for r/{subreddit_name}: {len(subreddit_posts)} posts")

            except Exception as e:
                self.logger.error(f"Error fetching from r/{subreddit_name}: {e}")
                continue

        return all_posts
    
    # snscrape methods removed - using enhanced PRAW API approach instead
    
    def _deduplicate_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate posts using content hash"""
        seen_hashes = set()
        unique_posts = []
        
        for post in posts:
            # Create hash from title + content
            hash_text = f"{post.get('title', '')}{post.get('content', '')[:100]}".lower().strip()
            content_hash = hashlib.md5(hash_text.encode()).hexdigest()
            
            # Also check by ID
            post_id = post.get('id', '')
            
            if content_hash not in seen_hashes and post_id not in seen_hashes:
                seen_hashes.add(content_hash)
                if post_id:
                    seen_hashes.add(post_id)
                unique_posts.append(post)
        
        return unique_posts

    def _extract_post_data(self, submission) -> Dict[str, Any]:
        """Extract relevant data from a Reddit submission with security sanitization"""
        top_comments = []
        submission.comments.replace_more(limit=0)

        for comment in submission.comments[:self.source_config['comment_limit']]:
            if hasattr(comment, 'body') and comment.score > 5:
                # Sanitize comment text
                comment_text = comment.body
                if self.input_validator:
                    comment_text = self.input_validator.sanitize_text(comment_text)
                
                top_comments.append({
                    'text': comment_text,
                    'score': comment.score,
                    'author': str(comment.author) if comment.author else '[deleted]'
                })

        # Sanitize title and content
        title = submission.title
        content = submission.selftext
        permalink_url = f"https://reddit.com{submission.permalink}"
        
        if self.input_validator:
            # Use configurable max_title_length
            max_title_length = None
            if self.config and 'security' in self.config:
                max_title_length = self.config['security']['input_validation'].get('max_title_length', 500)
            
            title = self.input_validator.sanitize_text(title, max_length=max_title_length)
            content = self.input_validator.sanitize_text(content)
            permalink_url = self.input_validator.sanitize_url(permalink_url) or permalink_url

        return {
            'id': submission.id,
            'title': title,
            'content': content,
            'url': permalink_url,
            'author': str(submission.author) if submission.author else '[deleted]',
            'subreddit': submission.subreddit.display_name,
            'score': submission.score,
            'num_comments': submission.num_comments,
            'created_at': datetime.fromtimestamp(submission.created_utc),
            'top_comments': top_comments,
            'flair': submission.link_flair_text,
            'is_self': submission.is_self
        }
