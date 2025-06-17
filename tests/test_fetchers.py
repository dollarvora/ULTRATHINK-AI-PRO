"""
Tests for content fetchers
"""

import pytest
import asyncio
import json
from pathlib import Path
from datetime import datetime

from fetchers.reddit_fetcher import RedditFetcher
from fetchers.twitter_fetcher import TwitterFetcher
from fetchers.linkedin_fetcher import LinkedInFetcher
from fetchers.google_fetcher import GoogleFetcher


@pytest.fixture
def test_config():
    """Load test configuration"""
    with open('config/config.json', 'r') as f:
        config = json.load(f)
    
    # Add mock credentials
    config['credentials'] = {
        'reddit': {
            'client_id': 'test_id',
            'client_secret': 'test_secret',
            'user_agent': 'ULTRATHINK/test'
        },
        'google': {
            'api_key': 'test_key',
            'cse_id': 'test_cse'
        },
        'openai': {
            'api_key': 'test_key'
        },
        'email': {
            'smtp_host': 'localhost',
            'smtp_port': 1025,
            'smtp_user': 'test@example.com',
            'smtp_password': 'test',
            'from_email': 'test@example.com'
        }
    }
    
    return config


class TestRedditFetcher:
    """Test Reddit fetcher"""
    
    @pytest.mark.asyncio
    async def test_fetch_with_mock_data(self, test_config):
        """Test fetching with mock data"""
        fetcher = RedditFetcher(test_config, test_mode=True)
        results = await fetcher.fetch()
        
        assert isinstance(results, list)
        assert len(results) > 0
        
        # Check first item structure
        item = results[0]
        assert 'id' in item
        assert 'title' in item
        assert 'relevance_score' in item
        assert 'urgency' in item
        assert 'source' in item
        assert item['source'] == 'reddit'
    
    def test_relevance_scoring(self, test_config):
        """Test relevance scoring algorithm"""
        fetcher = RedditFetcher(test_config, test_mode=True)
        
        # Test with high-relevance text
        text = "Microsoft announces 15% price increase for Azure enterprise subscriptions"
        score = fetcher._calculate_relevance_score(text)
        assert score > 0
        
        # Test with low-relevance text
        text = "Just a random post about nothing important"
        score = fetcher._calculate_relevance_score(text)
        assert score == 0


class TestTwitterFetcher:
    """Test Twitter fetcher"""
    
    @pytest.mark.asyncio
    async def test_fetch_with_mock_data(self, test_config):
        """Test fetching with mock data"""
        fetcher = TwitterFetcher(test_config, test_mode=True)
        results = await fetcher.fetch()
        
        assert isinstance(results, list)
        assert len(results) > 0
        
        # Check tweet structure
        tweet = results[0]
        assert 'id' in tweet
        assert 'text' in tweet
        assert 'author' in tweet
        assert 'created_at' in tweet


class TestLinkedInFetcher:
    """Test LinkedIn fetcher"""
    
    @pytest.mark.asyncio
    async def test_fetch_with_mock_data(self, test_config):
        """Test fetching with mock data"""
        fetcher = LinkedInFetcher(test_config, test_mode=True)
        results = await fetcher.fetch()
        
        assert isinstance(results, list)
        assert len(results) > 0
        
        # Check post structure
        post = results[0]
        assert 'id' in post
        assert 'text' in post
        assert 'company' in post


class TestGoogleFetcher:
    """Test Google fetcher"""
    
    @pytest.mark.asyncio
    async def test_fetch_with_mock_data(self, test_config):
        """Test fetching with mock data"""
        fetcher = GoogleFetcher(test_config, test_mode=True)
        results = await fetcher.fetch()
        
        assert isinstance(results, list)
        assert len(results) > 0
        
        # Check article structure
        article = results[0]
        assert 'id' in article
        assert 'title' in article
        assert 'url' in article
        assert 'domain' in article