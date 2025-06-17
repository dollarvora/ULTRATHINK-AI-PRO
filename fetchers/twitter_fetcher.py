import os
import logging
import requests
from datetime import datetime, timedelta
from urllib.parse import quote

class TwitterFetcher:
    def __init__(self, config, test_mode=False):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.test_mode = test_mode
        self.token = os.getenv("TWITTER_BEARER_TOKEN")
        self.query = "#ITbudget"
        self.days = 7
        self.limit = 10

    async def fetch(self):
        if self.test_mode:
            self.logger.info("Using mock Twitter data...")
            return self._mock_data()

        self.logger.info(f"Fetching tweets from Twitter API for query: {self.query}")
        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        start_time = (datetime.utcnow() - timedelta(days=self.days)).isoformat("T") + "Z"
        encoded_query = quote(self.query)

        url = (
            f"https://api.twitter.com/2/tweets/search/recent"
            f"?query={encoded_query}"
            f"&tweet.fields=created_at,author_id"
            f"&max_results={self.limit}"
            f"&start_time={start_time}"
        )

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            tweets = response.json().get("data", [])

            return [
                {
                    "title": f"Tweet by user {tweet['author_id']}",
                    "content": tweet["text"],
                    "timestamp": tweet["created_at"],
                    "url": f"https://twitter.com/i/web/status/{tweet['id']}",
                }
                for tweet in tweets
            ]

        except Exception as e:
            self.logger.warning(f"Twitter API error: {e}")
            return []

    def _mock_data(self):
        return [{
            "title": "Mock tweet",
            "content": "This is a mock tweet for testing.",
            "timestamp": str(datetime.utcnow()),
            "url": "https://twitter.com/mock"
        }]
