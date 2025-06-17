"""
Tests for GPT summarizer
"""

import pytest
import json
from unittest.mock import Mock, patch

from summarizer.gpt_summarizer import GPTSummarizer


@pytest.fixture
def test_config():
    """Load test configuration"""
    with open('config/config.json', 'r') as f:
        config = json.load(f)
    
    config['credentials'] = {
        'openai': {'api_key': 'test_key'}
    }
    
    return config


@pytest.fixture
def sample_content():
    """Sample content for testing"""
    return {
        'reddit': [
            {
                'id': 'test1',
                'title': 'Microsoft price increase',
                'content': 'Azure prices going up 15%',
                'relevance_score': 8.5,
                'urgency': 'high',
                'source': 'reddit'
            }
        ],
        'twitter': [
            {
                'id': 'test2',
                'text': 'CrowdStrike announces new pricing model',
                'relevance_score': 6.0,
                'urgency': 'medium',
                'source': 'twitter'
            }
        ],
        'timestamp': '2024-01-15T10:00:00'
    }


class TestGPTSummarizer:
    """Test GPT summarizer"""
    
    def test_group_by_urgency(self, test_config, sample_content):
        """Test urgency grouping"""
        summarizer = GPTSummarizer(test_config)
        
        all_items = []
        for source, items in sample_content.items():
            if source != 'timestamp':
                all_items.extend(items)
        
        groups = summarizer._group_by_urgency(all_items)
        
        assert 'high' in groups
        assert 'medium' in groups
        assert len(groups['high']) == 1
        assert len(groups['medium']) == 1
    
    @patch('openai.OpenAI')
    def test_generate_summaries(self, mock_openai, test_config, sample_content):
        """Test summary generation"""
        # Mock OpenAI response
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test summary"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        summarizer = GPTSummarizer(test_config)
        summaries = summarizer.generate_summaries(sample_content)
        
        assert 'role_summaries' in summaries
        assert 'pricing_analyst' in summaries['role_summaries']
        assert summaries['total_items'] == 2
    
    def test_vendor_extraction(self, test_config):
        """Test vendor name extraction"""
        summarizer = GPTSummarizer(test_config)
        
        text = "Microsoft announces new Azure pricing"
        vendor = summarizer._extract_vendor(text)
        assert vendor == "Microsoft"
        
        text = "Random text without vendors"
        vendor = summarizer._extract_vendor(text)
        assert vendor is None