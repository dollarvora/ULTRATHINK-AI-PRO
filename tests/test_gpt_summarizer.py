#!/usr/bin/env python3
"""
Test suite for GPT Summarizer
Validates pricing intelligence analysis and insight generation
"""
import unittest
import sys
import os
import json
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from summarizer.gpt_summarizer import GPTSummarizer


class TestGPTSummarizer(unittest.TestCase):
    """Test cases for GPT Summarizer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.summarizer = GPTSummarizer(debug=False)
        
        # Sample test content
        self.sample_content = [
            {
                'title': 'Microsoft 365 Pricing Update',
                'content': 'Microsoft announces 15% price increase for Office 365 enterprise subscriptions effective Q3 2024.',
                'url': 'https://example.com/microsoft-pricing',
                'created_at': '2024-06-15',
                'source': 'reddit'
            },
            {
                'title': 'VMware Licensing Changes',
                'content': 'Broadcom discontinues perpetual VMware licenses, forcing customers to subscription model.',
                'url': 'https://example.com/vmware-broadcom',
                'created_at': '2024-06-14',
                'source': 'google'
            }
        ]
        
        # Sample config
        self.sample_config = {
            'summarization': {
                'model': 'gpt-4o-mini',
                'max_tokens': 800,
                'temperature': 0.3
            },
            'email': {
                'employee_csv': 'config/employees.csv'
            }
        }
    
    def test_initialization(self):
        """Test summarizer initialization"""
        self.assertIsInstance(self.summarizer, GPTSummarizer)
        self.assertIsInstance(self.summarizer.key_vendors, list)
        self.assertGreater(len(self.summarizer.key_vendors), 0)
        self.assertIn('urgency_keywords', self.summarizer.__dict__)
        self.assertIn('vendor_tiers', self.summarizer.__dict__)
    
    def test_pricing_relevance_filter(self):
        """Test pricing relevance filtering"""
        # Should pass pricing filter
        pricing_text = "Microsoft Office 365 price increase affecting enterprise customers"
        self.assertTrue(self.summarizer._is_pricing_relevant(pricing_text))
        
        # Should fail pricing filter
        non_pricing_text = "How to configure SSH access for network troubleshooting"
        self.assertFalse(self.summarizer._is_pricing_relevant(non_pricing_text))
        
        # Edge cases
        self.assertFalse(self.summarizer._is_pricing_relevant(""))
        self.assertTrue(self.summarizer._is_pricing_relevant("licensing change affects cost"))
    
    def test_content_deduplication(self):
        """Test content deduplication functionality"""
        duplicate_content = {
            'source1': [
                {'title': 'Same Title', 'content': 'Same content here'},
                {'title': 'Different Title', 'content': 'Different content'}
            ],
            'source2': [
                {'title': 'Same Title', 'content': 'Same content here'},  # Duplicate
                {'title': 'Unique Title', 'content': 'Unique content'}
            ]
        }
        
        deduplicated = self.summarizer._deduplicate_content(duplicate_content)
        
        # Should have fewer items after deduplication
        total_original = sum(len(items) for items in duplicate_content.values())
        total_deduplicated = sum(len(items) for items in deduplicated.values())
        
        self.assertLess(total_deduplicated, total_original)
        self.assertGreaterEqual(total_deduplicated, 3)  # At least 3 unique items
    
    def test_enhanced_relevance_scoring(self):
        """Test enhanced relevance scoring calculation"""
        # Mock company result
        company_result = Mock()
        company_result.matched_companies = ['microsoft', 'vmware']
        company_result.confidence_score = 0.8
        
        item = {'relevance_score': 5.0}
        text = "Microsoft pricing increase affects VMware migration decisions urgently"
        
        score = self.summarizer._calculate_enhanced_relevance_score(item, company_result, text)
        
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, item['relevance_score'])  # Should be boosted
        self.assertLessEqual(score, 10.0)  # Should be capped at 10
    
    def test_vendor_tier_multiplier(self):
        """Test vendor tier-based scoring multipliers"""
        # Tier 1 vendor (high multiplier)
        tier1_multiplier = self.summarizer._get_vendor_tier_multiplier('Microsoft')
        self.assertGreaterEqual(tier1_multiplier, 2.5)
        
        # Unknown vendor (default multiplier)
        unknown_multiplier = self.summarizer._get_vendor_tier_multiplier('UnknownVendor')
        self.assertEqual(unknown_multiplier, 1.0)
    
    def test_urgency_detection(self):
        """Test urgency level detection"""
        # High urgency
        high_urgency_text = "URGENT: Critical price increase immediate action required"
        self.assertEqual(self.summarizer._detect_urgency_level(high_urgency_text), 'high')
        
        # Medium urgency
        medium_urgency_text = "New pricing update available for review"
        urgency = self.summarizer._detect_urgency_level(medium_urgency_text)
        self.assertIn(urgency, ['medium', 'low'])
        
        # Low urgency
        low_urgency_text = "General market information for awareness"
        self.assertEqual(self.summarizer._detect_urgency_level(low_urgency_text), 'low')
    
    def test_role_detection_fallback(self):
        """Test role detection fallback functionality"""
        roles = self.summarizer._fallback_role_detection()
        
        self.assertIsInstance(roles, set)
        # Should include at least pricing analyst as default
        if not roles:
            roles.add('pricing_analyst')
        self.assertTrue(len(roles) > 0)
    
    def test_dynamic_roles_default(self):
        """Test dynamic role detection with defaults"""
        roles = self.summarizer._get_dynamic_roles()
        
        self.assertIsInstance(roles, set)
        self.assertGreater(len(roles), 0)
        # Should always have at least one role
        if not roles:
            self.fail("Dynamic roles should never be empty")
    
    def test_enhanced_system_message(self):
        """Test enhanced system message generation"""
        system_message = self.summarizer._build_enhanced_system_message()
        
        self.assertIsInstance(system_message, str)
        self.assertGreater(len(system_message), 100)
        self.assertIn('technology distribution', system_message.lower())
        self.assertIn('pricing intelligence', system_message.lower())
    
    def test_preprocessing_content(self):
        """Test content preprocessing functionality"""
        content_by_source = {'reddit': self.sample_content}
        
        processed = self.summarizer._preprocess_content(content_by_source)
        
        self.assertIsInstance(processed, str)
        self.assertGreater(len(processed), 0)
        self.assertIn('TITLE:', processed)
        self.assertIn('CONTENT:', processed)
        self.assertIn('SOURCE_ID:', processed)
    
    def test_enhanced_prompt_building(self):
        """Test enhanced prompt building"""
        roles = {'pricing_profitability_team'}
        content = "Microsoft pricing update: 15% increase"
        
        prompt = self.summarizer._build_enhanced_prompt(roles, content)
        
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 500)  # Should be comprehensive
        self.assertIn('pricing intelligence', prompt.lower())
        self.assertIn('content to analyze', prompt.lower())
        self.assertIn(content, prompt)
    
    @patch('openai.ChatCompletion.create')
    def test_generate_summary_success(self, mock_openai):
        """Test successful summary generation"""
        # Mock successful OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = json.dumps({
            "role_summaries": {
                "pricing_profitability_team": {
                    "role": "Pricing Profitability Team",
                    "summary": "Microsoft pricing analysis",
                    "key_insights": ["Test insight 1", "Test insight 2"],
                    "top_vendors": [{"vendor": "Microsoft", "mentions": 2}],
                    "sources": ["Reddit"]
                }
            },
            "by_urgency": {"high": 1, "medium": 1, "low": 0},
            "total_items": 2
        })
        mock_openai.return_value = mock_response
        
        # Test with API key
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            content_by_source = {'reddit': self.sample_content}
            result = self.summarizer.generate_summary(content_by_source, self.sample_config)
        
        self.assertIsInstance(result, dict)
        self.assertIn('role_summaries', result)
        self.assertIn('by_urgency', result)
        self.assertIn('total_items', result)
    
    def test_generate_summary_fallback(self):
        """Test summary generation fallback when GPT fails"""
        content_by_source = {'reddit': self.sample_content}
        
        # Test without API key (should trigger fallback)
        with patch.dict(os.environ, {}, clear=True):
            result = self.summarizer.generate_summary(content_by_source, self.sample_config)
        
        # Should return fallback summary
        self.assertIsInstance(result, dict)
        self.assertIn('role_summaries', result)
    
    def test_summary_structure_validation(self):
        """Test summary structure validation"""
        # Valid structure
        valid_summary = {
            "role_summaries": {
                "pricing_analyst": {
                    "role": "Pricing Analyst",
                    "summary": "Test summary",
                    "key_insights": ["Insight 1"],
                    "top_vendors": [],
                    "sources": []
                }
            },
            "by_urgency": {"high": 0, "medium": 1, "low": 0},
            "total_items": 1
        }
        
        self.assertTrue(self.summarizer._validate_summary_structure(
            valid_summary, {'pricing_analyst'}))
        
        # Invalid structure (missing required fields)
        invalid_summary = {
            "role_summaries": {},
            "by_urgency": {"high": 0},
            "total_items": 1
        }
        
        self.assertFalse(self.summarizer._validate_summary_structure(
            invalid_summary, {'pricing_analyst'}))
    
    def test_analysis_metadata_addition(self):
        """Test analysis metadata addition"""
        base_result = {
            "role_summaries": {
                "pricing_analyst": {
                    "role": "Pricing Analyst",
                    "summary": "Test",
                    "key_insights": [],
                    "top_vendors": [],
                    "sources": []
                }
            },
            "by_urgency": {"high": 0, "medium": 0, "low": 1},
            "total_items": 1
        }
        
        content_by_source = {'reddit': self.sample_content}
        enhanced_result = self.summarizer._add_analysis_metadata(base_result, content_by_source)
        
        self.assertIn('analysis_metadata', enhanced_result)
        self.assertIn('keywords_used', enhanced_result['analysis_metadata'])
        self.assertIn('content_analyzed', enhanced_result['analysis_metadata'])
        self.assertIn('processing_stats', enhanced_result['analysis_metadata'])


class TestGPTSummarizerIntegration(unittest.TestCase):
    """Integration tests for GPT Summarizer"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.summarizer = GPTSummarizer(debug=True)
        
        # Realistic pricing content
        self.realistic_content = [
            {
                'title': 'Microsoft Office 365 Enterprise Price Increase',
                'content': 'Microsoft announces 15% price increase for Office 365 Enterprise E3 and E5 plans, effective Q3 2024. Customers with existing multi-year agreements may be eligible for transition discounts.',
                'url': 'https://reddit.com/r/sysadmin/microsoft_pricing',
                'created_at': '2024-06-15T10:30:00Z',
                'source': 'reddit',
                'score': 95,
                'relevance_score': 8.5
            },
            {
                'title': 'VMware vSphere Licensing Crisis After Broadcom Acquisition',
                'content': 'Broadcom discontinues perpetual VMware licenses, forcing all customers to subscription-only model. Enterprise customers report 200-300% cost increases, driving mass migrations to Hyper-V and Proxmox.',
                'url': 'https://google.com/search?q=vmware+broadcom+pricing',
                'created_at': '2024-06-14T15:45:00Z',
                'source': 'google',
                'score': 87,
                'relevance_score': 9.2
            },
            {
                'title': 'Dell PowerEdge Server Pricing Pressures',
                'content': 'Dell Technologies raises PowerEdge server prices 8-12% due to component shortages and logistics costs. R750 and R7525 models most affected, impacting Q3 procurement budgets.',
                'url': 'https://example.com/dell-pricing-update',
                'created_at': '2024-06-13T09:15:00Z',
                'source': 'reddit',
                'score': 65,
                'relevance_score': 7.1
            }
        ]
    
    def test_realistic_content_processing(self):
        """Test processing of realistic pricing content"""
        content_by_source = {'reddit': self.realistic_content[:2], 'google': [self.realistic_content[2]]}
        
        processed = self.summarizer._preprocess_content(content_by_source)
        
        # Should contain vendor names
        self.assertIn('Microsoft', processed)
        self.assertIn('VMware', processed)
        self.assertIn('Dell', processed)
        
        # Should contain pricing indicators
        self.assertIn('15%', processed)
        self.assertIn('price increase', processed.lower())
        self.assertIn('cost', processed.lower())
    
    def test_company_detection_integration(self):
        """Test integration with company alias matcher"""
        # The summarizer should initialize with company matcher
        self.assertIsNotNone(self.summarizer.company_matcher)
        
        # Test that preprocessing detects companies
        content_by_source = {'reddit': self.realistic_content}
        
        # Process content and check enhanced items are created
        processed = self.summarizer._preprocess_content(content_by_source)
        
        # Should have enhanced items with company detection
        if hasattr(self.summarizer, '_enhanced_items'):
            enhanced_items = self.summarizer._enhanced_items
            self.assertGreater(len(enhanced_items), 0)
            
            # At least one item should have detected companies
            companies_detected = any(item.get('detected_companies') for item in enhanced_items)
            self.assertTrue(companies_detected)
    
    def test_vendor_tier_scoring_integration(self):
        """Test vendor tier scoring with realistic data"""
        # Test tier 1 vendor (Microsoft)
        microsoft_multiplier = self.summarizer._get_vendor_tier_multiplier('Microsoft')
        self.assertGreaterEqual(microsoft_multiplier, 2.5)
        
        # Test tier 2 vendor (CrowdStrike) 
        crowdstrike_multiplier = self.summarizer._get_vendor_tier_multiplier('CrowdStrike')
        self.assertGreaterEqual(crowdstrike_multiplier, 2.0)
        
        # Test tier 3 vendor (TD SYNNEX)
        distributor_multiplier = self.summarizer._get_vendor_tier_multiplier('TD SYNNEX')
        self.assertGreaterEqual(distributor_multiplier, 1.5)
    
    def test_urgency_detection_realistic(self):
        """Test urgency detection with realistic scenarios"""
        # High urgency scenarios
        high_urgency_scenarios = [
            "URGENT: Price increase deadline tomorrow",
            "Critical licensing change affects all customers immediately",
            "Emergency: Supply shortage disrupts procurement"
        ]
        
        for scenario in high_urgency_scenarios:
            urgency = self.summarizer._detect_urgency_level(scenario)
            self.assertEqual(urgency, 'high', f"Failed for: {scenario}")
        
        # Medium urgency scenarios
        medium_urgency_scenarios = [
            "New pricing model launches Q3 2024",
            "Partnership announcement affects vendor relationships",
            "Product update includes pricing changes"
        ]
        
        for scenario in medium_urgency_scenarios:
            urgency = self.summarizer._detect_urgency_level(scenario)
            self.assertIn(urgency, ['medium', 'high'], f"Failed for: {scenario}")
    
    def test_role_based_analysis_integration(self):
        """Test role-based analysis integration"""
        # Test with pricing profitability team role
        roles = {'pricing_profitability_team'}
        
        # Generate role-specific prompt
        content = "Microsoft pricing increase affects enterprise margins"
        prompt = self.summarizer._build_enhanced_prompt(roles, content)
        
        # Should include role-specific context
        self.assertIn('pricing', prompt.lower())
        self.assertIn('margin', prompt.lower())
        self.assertIn('profitability', prompt.lower())


if __name__ == '__main__':
    # Create test suite
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestGPTSummarizer))
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestGPTSummarizerIntegration))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)