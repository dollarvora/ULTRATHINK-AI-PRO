"""
Reddit Fetcher
Fetches pricing-related content from Reddit using PRAW and snscrape
Dual fetching for broader coverage and redundancy
"""

import os
import asyncio
import praw
import hashlib
import subprocess
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from fetchers.base_fetcher import BaseFetcher


class RedditFetcher(BaseFetcher):
    """Fetches content from Reddit subreddits"""

    def get_source_name(self) -> str:
        return 'reddit'

    def _get_reddit_client(self) -> praw.Reddit:
        """Create authenticated Reddit client using environment variables"""
        return praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT", "ultrathink-script/1.0 (by u/your_username)")
        )
    
    def _is_quality_post(self, submission):
        """Filter out low-quality posts"""
        # Skip deleted/removed
        if submission.selftext in ['[removed]', '[deleted]']:
            return False
        
        # Skip low engagement posts
        if submission.score < 10 and submission.num_comments < 5:
            return False
            
        # Skip very old posts
        post_age = datetime.now() - datetime.fromtimestamp(submission.created_utc)
        if post_age.days > 30:
            return False
            
        return True

    async def fetch_raw(self) -> List[Dict[str, Any]]:
        """Fetch posts from configured subreddits"""
        # Reddit API is synchronous, so run in executor
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._fetch_sync)

    def _fetch_sync(self) -> List[Dict[str, Any]]:
        """Synchronous fetch method for Reddit using both PRAW and snscrape"""
        all_posts = []
        
        # Fetch using PRAW API
        api_posts = self._fetch_via_praw()
        all_posts.extend(api_posts)
        
        # Fetch using snscrape for broader coverage
        if self._is_snscrape_available():
            scrape_posts = self._fetch_via_snscrape()
            all_posts.extend(scrape_posts)
        
        # Deduplicate posts by ID
        deduplicated = self._deduplicate_posts(all_posts)
        
        self.logger.info(f"Reddit dual fetch: {len(api_posts)} API + {len(all_posts) - len(api_posts)} scraped → {len(deduplicated)} unique")
        
        return deduplicated
    
    def _fetch_via_praw(self) -> List[Dict[str, Any]]:
        """Fetch posts using Reddit API via PRAW"""
        reddit = self._get_reddit_client()
        all_posts = []

        # Calculate time threshold (last 7 days)
        time_threshold = datetime.now() - timedelta(days=7)

        for subreddit_name in self.source_config['subreddits']:
            try:
                self.logger.info(f"Fetching from r/{subreddit_name} via API")
                subreddit = reddit.subreddit(subreddit_name)

                # Fetch hot posts
                for submission in subreddit.hot(limit=self.source_config['post_limit']):
                    if self._is_quality_post(submission):
                        post_data = self._extract_post_data(submission)
                        if post_data['created_at'] > time_threshold:
                            all_posts.append(post_data)

                # Fetch new posts
                for submission in subreddit.new(limit=self.source_config['post_limit']):
                    if self._is_quality_post(submission):
                        post_data = self._extract_post_data(submission)
                        if post_data['created_at'] > time_threshold and \
                           post_data['id'] not in [p['id'] for p in all_posts]:
                            all_posts.append(post_data)

            except Exception as e:
                self.logger.error(f"Error fetching from r/{subreddit_name}: {e}")
                continue

        return all_posts
    
    def _is_snscrape_available(self) -> bool:
        """Check if snscrape is installed and available"""
        try:
            result = subprocess.run(['snscrape', '--version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.logger.debug("snscrape not available - using API only")
            return False
    
    def _fetch_via_snscrape(self) -> List[Dict[str, Any]]:
        """Fetch posts using snscrape for broader coverage"""
        all_posts = []
        time_threshold = datetime.now() - timedelta(days=7)
        
        for subreddit_name in self.source_config['subreddits']:
            try:
                self.logger.info(f"Fetching from r/{subreddit_name} via snscrape")
                
                # Build snscrape command
                since_date = time_threshold.strftime('%Y-%m-%d')
                cmd = [
                    'snscrape',
                    '--jsonl',
                    '--max-results', str(self.source_config['post_limit'] * 2),
                    f'reddit-subreddit:{subreddit_name} since:{since_date}'
                ]
                
                # Execute snscrape with timeout
                result = subprocess.run(cmd, 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=30)
                
                if result.returncode == 0 and result.stdout:
                    # Parse JSONL output
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            try:
                                post = json.loads(line)
                                post_data = self._extract_snscrape_data(post)
                                if self._is_quality_post_data(post_data):
                                    all_posts.append(post_data)
                            except json.JSONDecodeError:
                                continue
                
            except subprocess.TimeoutExpired:
                self.logger.warning(f"snscrape timeout for r/{subreddit_name}")
            except Exception as e:
                self.logger.error(f"snscrape error for r/{subreddit_name}: {e}")
        
        return all_posts
    
    def _extract_snscrape_data(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from snscrape JSON format"""
        return {
            'id': post.get('id', ''),
            'title': post.get('title', ''),
            'content': post.get('selftext', ''),
            'url': post.get('url', ''),
            'author': post.get('author', '[deleted]'),
            'subreddit': post.get('subreddit', ''),
            'score': post.get('score', 0),
            'num_comments': post.get('commentCount', 0),
            'created_at': datetime.fromisoformat(post.get('date', '').replace('Z', '+00:00')) if post.get('date') else datetime.now(),
            'top_comments': [],  # snscrape doesn't include comments
            'flair': post.get('flair', ''),
            'is_self': post.get('isSelf', True),
            'source_method': 'snscrape'
        }
    
    def _is_quality_post_data(self, post_data: Dict[str, Any]) -> bool:
        """Check if post data meets quality criteria"""
        # Skip deleted/removed
        if post_data.get('content') in ['[removed]', '[deleted]', None, '']:
            return False
        
        # Skip low engagement posts
        if post_data.get('score', 0) < 10 and post_data.get('num_comments', 0) < 5:
            return False
        
        # Skip very old posts
        post_age = datetime.now() - post_data.get('created_at', datetime.now())
        if post_age.days > 30:
            return False
        
        return True
    
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
        """Extract relevant data from a Reddit submission"""
        top_comments = []
        submission.comments.replace_more(limit=0)

        for comment in submission.comments[:self.source_config['comment_limit']]:
            if hasattr(comment, 'body') and comment.score > 5:
                top_comments.append({
                    'text': comment.body,
                    'score': comment.score,
                    'author': str(comment.author) if comment.author else '[deleted]'
                })

        return {
            'id': submission.id,
            'title': submission.title,
            'content': submission.selftext,
            'url': f"https://reddit.com{submission.permalink}",
            'author': str(submission.author) if submission.author else '[deleted]',
            'subreddit': submission.subreddit.display_name,
            'score': submission.score,
            'num_comments': submission.num_comments,
            'created_at': datetime.fromtimestamp(submission.created_utc),
            'top_comments': top_comments,
            'flair': submission.link_flair_text,
            'is_self': submission.is_self
        }
