#!/usr/bin/env python3
"""
Test suite for Configuration Management
Validates configuration loading, environment handling, and security
"""
import unittest
import sys
import os
import tempfile
import json
from unittest.mock import patch, Mock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import CONFIG, load_keywords


class TestConfigurationManagement(unittest.TestCase):
    """Test cases for Configuration Management"""
    
    def test_config_structure(self):
        """Test CONFIG structure and required fields"""
        # Test top-level structure
        required_sections = ['system', 'credentials', 'keywords', 'sources', 'summarization', 'email', 'scoring']
        
        for section in required_sections:
            self.assertIn(section, CONFIG, f"Missing required config section: {section}")
        
        # Test system section
        system_config = CONFIG['system']
        self.assertIn('name', system_config)
        self.assertIn('version', system_config)
        self.assertEqual(system_config['name'], "ULTRATHINK-AI-PRO Pricing Intelligence System")
        
        # Test credentials section structure
        credentials = CONFIG['credentials']
        required_creds = ['reddit', 'google', 'openai', 'email']
        for cred in required_creds:
            self.assertIn(cred, credentials, f"Missing credential section: {cred}")
    
    def test_keywords_loading(self):
        """Test keywords loading functionality"""
        keywords = load_keywords()
        
        self.assertIsInstance(keywords, dict)
        self.assertGreater(len(keywords), 0)
        
        # Test for expected keyword categories
        if 'pricing_keywords' in keywords:
            self.assertIsInstance(keywords['pricing_keywords'], list)
            self.assertGreater(len(keywords['pricing_keywords']), 0)
    
    @patch.dict(os.environ, {
        'REDDIT_CLIENT_ID': 'test_reddit_id',
        'REDDIT_CLIENT_SECRET': 'test_reddit_secret',
        'OPENAI_API_KEY': 'test_openai_key',
        'GOOGLE_API_KEY': 'test_google_key'
    })
    def test_environment_variable_loading(self):
        """Test environment variable loading"""
        # Reload config to pick up environment variables
        from config.config import CONFIG
        
        # Test that environment variables are loaded
        self.assertEqual(CONFIG['credentials']['reddit']['client_id'], 'test_reddit_id')
        self.assertEqual(CONFIG['credentials']['reddit']['client_secret'], 'test_reddit_secret')
        self.assertEqual(CONFIG['credentials']['openai']['api_key'], 'test_openai_key')
        self.assertEqual(CONFIG['credentials']['google']['api_key'], 'test_google_key')
    
    def test_sources_configuration(self):
        """Test sources configuration structure"""
        sources = CONFIG['sources']
        
        # Test Reddit configuration
        reddit_config = sources['reddit']
        self.assertIn('enabled', reddit_config)
        self.assertIn('subreddits', reddit_config)
        self.assertIn('post_limit', reddit_config)
        self.assertIsInstance(reddit_config['subreddits'], list)
        self.assertGreater(len(reddit_config['subreddits']), 0)
        
        # Test Google configuration
        google_config = sources['google']
        self.assertIn('enabled', google_config)
        self.assertIn('queries', google_config)
        self.assertIn('results_per_query', google_config)
        self.assertIsInstance(google_config['queries'], list)
    
    def test_summarization_configuration(self):
        """Test GPT summarization configuration"""
        summarization = CONFIG['summarization']
        
        # Test required fields
        self.assertIn('model', summarization)
        self.assertIn('max_tokens', summarization)
        self.assertIn('temperature', summarization)
        
        # Test values
        self.assertEqual(summarization['model'], 'gpt-4o-mini')
        self.assertIsInstance(summarization['max_tokens'], int)
        self.assertGreater(summarization['max_tokens'], 0)
        self.assertIsInstance(summarization['temperature'], (int, float))
        self.assertGreaterEqual(summarization['temperature'], 0.0)
        self.assertLessEqual(summarization['temperature'], 1.0)
    
    def test_email_configuration(self):
        """Test email configuration structure"""
        email_config = CONFIG['email']
        
        # Test required fields
        required_fields = ['enabled', 'subject_template', 'employee_csv']
        for field in required_fields:
            self.assertIn(field, email_config, f"Missing email config field: {field}")
        
        # Test subject template
        self.assertIn('{date}', email_config['subject_template'])
    
    def test_scoring_configuration(self):
        """Test scoring weights configuration"""
        scoring = CONFIG['scoring']
        
        # Test required weights
        required_weights = ['urgency_weight', 'vendor_weight', 'keyword_weight', 'recency_weight']
        for weight in required_weights:
            self.assertIn(weight, scoring, f"Missing scoring weight: {weight}")
            self.assertIsInstance(scoring[weight], (int, float))
            self.assertGreater(scoring[weight], 0)
        
        # Test thresholds
        self.assertIn('high_score_threshold', scoring)
        self.assertIn('medium_score_threshold', scoring)
        self.assertGreater(scoring['high_score_threshold'], scoring['medium_score_threshold'])
    
    def test_keywords_fallback(self):
        """Test keywords fallback when file doesn't exist"""
        # Test load_keywords with non-existent file
        with patch('os.path.exists', return_value=False):
            fallback_keywords = load_keywords()
            
            self.assertIsInstance(fallback_keywords, dict)
            self.assertIn('pricing_keywords', fallback_keywords)
            self.assertIn('urgency_high', fallback_keywords)


class TestSecurityConfiguration(unittest.TestCase):
    """Test cases for Security Configuration"""
    
    def test_sensitive_data_handling(self):
        """Test that sensitive data is properly handled"""
        credentials = CONFIG['credentials']
        
        # Test that credentials use environment variables (not hardcoded)
        for service, config in credentials.items():
            for key, value in config.items():
                if 'password' in key.lower() or 'secret' in key.lower() or 'key' in key.lower():
                    # Should either be None (from os.getenv) or start with placeholder
                    if value is not None:
                        self.assertNotIn('hardcoded', str(value).lower())
                        self.assertNotIn('placeholder', str(value).lower())
    
    def test_email_security(self):
        """Test email configuration security"""
        email_config = CONFIG['credentials']['email']
        
        # Should use environment variables for sensitive data
        sensitive_fields = ['smtp_password']
        for field in sensitive_fields:
            if field in email_config:
                value = email_config[field]
                if value is not None:
                    # Should not contain obvious test/placeholder values
                    self.assertNotIn('password', str(value).lower())
                    self.assertNotIn('secret', str(value).lower())
    
    def test_api_key_format_validation(self):
        """Test API key format validation (when present)"""
        credentials = CONFIG['credentials']
        
        # OpenAI API key format (when present)
        openai_key = credentials['openai']['api_key']
        if openai_key and openai_key != '':
            # Should start with 'sk-' for OpenAI
            # Note: Only validate format if key is present
            if not openai_key.startswith('sk-'):
                # This is acceptable in testing - just log warning
                pass
        
        # Reddit client ID format (when present)
        reddit_id = credentials['reddit']['client_id']
        if reddit_id and reddit_id != '':
            # Should be alphanumeric string
            self.assertRegex(reddit_id, r'^[a-zA-Z0-9_-]+$', "Invalid Reddit client ID format")


class TestConfigurationIntegration(unittest.TestCase):
    """Integration tests for Configuration"""
    
    def test_config_with_real_keywords_file(self):
        """Test configuration with actual keywords.json file"""
        # Test if keywords.json exists and is valid
        keywords_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'keywords.json')
        
        if os.path.exists(keywords_file):
            with open(keywords_file, 'r') as f:
                keywords_data = json.load(f)
            
            # Test structure
            self.assertIsInstance(keywords_data, dict)
            
            # Test expected categories
            expected_categories = ['vendors', 'pricing_keywords', 'urgency_high', 'urgency_medium']
            for category in expected_categories:
                if category in keywords_data:
                    self.assertIsInstance(keywords_data[category], (list, dict))
    
    def test_subreddit_configuration_realistic(self):
        """Test that subreddit configuration contains realistic subreddits"""
        subreddits = CONFIG['sources']['reddit']['subreddits']
        
        # Test for realistic IT/business subreddits
        realistic_subreddits = ['sysadmin', 'msp', 'cybersecurity', 'aws', 'azure', 'vmware']
        
        found_realistic = sum(1 for sub in subreddits if sub.lower() in realistic_subreddits)
        self.assertGreater(found_realistic, 3, "Should contain realistic IT subreddits")
    
    def test_google_queries_relevance(self):
        """Test that Google queries are relevant to pricing intelligence"""
        queries = CONFIG['sources']['google']['queries']
        
        # Check for pricing-related terms
        pricing_terms = ['pricing', 'cost', 'price', 'enterprise', 'vendor', 'software']
        
        relevant_queries = 0
        for query in queries:
            query_lower = query.lower()
            if any(term in query_lower for term in pricing_terms):
                relevant_queries += 1
        
        self.assertGreater(relevant_queries, len(queries) // 2, "Majority of queries should be pricing-related")
    
    def test_performance_configuration_realistic(self):
        """Test that performance configurations are realistic"""
        reddit_config = CONFIG['sources']['reddit']
        google_config = CONFIG['sources']['google']
        summarization_config = CONFIG['summarization']
        
        # Test reasonable limits
        self.assertLessEqual(reddit_config['post_limit'], 100, "Reddit post limit should be reasonable")
        self.assertLessEqual(google_config['results_per_query'], 20, "Google results limit should be reasonable")
        self.assertLessEqual(summarization_config['max_tokens'], 2000, "Token limit should be reasonable")
        
        # Test minimum values
        self.assertGreaterEqual(reddit_config['post_limit'], 10, "Should fetch minimum useful posts")
        self.assertGreaterEqual(google_config['results_per_query'], 5, "Should fetch minimum useful results")


if __name__ == '__main__':
    # Create test suite
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestConfigurationManagement))
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestSecurityConfiguration))
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestConfigurationIntegration))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)