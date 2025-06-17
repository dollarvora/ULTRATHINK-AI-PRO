"""
Reddit Fetcher
Fetches pricing-related content from Reddit using PRAW
"""

import os
import asyncio
import praw
from datetime import datetime, timedelta
from typing import List, Dict, Any

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
        """Synchronous fetch method for Reddit"""
        reddit = self._get_reddit_client()
        all_posts = []

        # Calculate time threshold (last 7 days)
        time_threshold = datetime.now() - timedelta(days=7)

        for subreddit_name in self.source_config['subreddits']:
            try:
                self.logger.info(f"Fetching from r/{subreddit_name}")
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
