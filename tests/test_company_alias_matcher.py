#!/usr/bin/env python3
"""
Test suite for Company Alias Matcher
Validates vendor detection and alias matching functionality
"""
import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.company_alias_matcher import CompanyAliasMatcher, get_company_matcher, AliasMatchResult


class TestCompanyAliasMatcher(unittest.TestCase):
    """Test cases for Company Alias Matcher"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.matcher = CompanyAliasMatcher(debug=False)
    
    def test_initialization(self):
        """Test matcher initialization"""
        self.assertIsInstance(self.matcher, CompanyAliasMatcher)
        self.assertGreater(len(self.matcher.company_mappings), 0)
        self.assertGreater(len(self.matcher.reverse_mappings), 0)
        self.assertGreater(len(self.matcher.compiled_patterns), 0)
    
    def test_company_detection_exact_match(self):
        """Test exact company name detection"""
        text = "Microsoft Azure pricing increased by 15% this quarter"
        result = self.matcher.find_companies_in_text(text)
        
        self.assertIsInstance(result, AliasMatchResult)
        self.assertIn('microsoft', result.matched_companies)
        self.assertGreater(result.total_matches, 0)
        self.assertGreater(result.confidence_score, 0)
    
    def test_company_detection_alias_match(self):
        """Test alias-based company detection"""
        text = "Our vSphere infrastructure needs upgrading due to VMware licensing changes"
        result = self.matcher.find_companies_in_text(text)
        
        self.assertIn('vmware', result.matched_companies)
        self.assertIn('vmware', result.alias_hits)
        self.assertGreater(len(result.alias_hits['vmware']), 0)
    
    def test_multiple_vendor_detection(self):
        """Test detection of multiple vendors in single text"""
        text = "Comparing AWS Lambda costs vs Azure Functions and Google Cloud Functions"
        result = self.matcher.find_companies_in_text(text)
        
        expected_vendors = {'aws', 'microsoft', 'google cloud'}
        detected_vendors = result.matched_companies
        
        # Should detect at least 2 of the 3 vendors
        self.assertGreaterEqual(len(detected_vendors.intersection(expected_vendors)), 2)
    
    def test_case_insensitive_matching(self):
        """Test case insensitive vendor detection"""
        text_lower = "crowdstrike falcon endpoint protection"
        text_upper = "CROWDSTRIKE FALCON ENDPOINT PROTECTION" 
        text_mixed = "CrowdStrike Falcon Endpoint Protection"
        
        result_lower = self.matcher.find_companies_in_text(text_lower)
        result_upper = self.matcher.find_companies_in_text(text_upper)
        result_mixed = self.matcher.find_companies_in_text(text_mixed)
        
        self.assertIn('crowdstrike', result_lower.matched_companies)
        self.assertIn('crowdstrike', result_upper.matched_companies)
        self.assertIn('crowdstrike', result_mixed.matched_companies)
    
    def test_normalize_company_name(self):
        """Test company name normalization"""
        # Test exact name
        self.assertEqual(self.matcher.normalize_company_name('microsoft'), 'microsoft')
        
        # Test alias normalization
        self.assertEqual(self.matcher.normalize_company_name('azure'), 'microsoft')
        self.assertEqual(self.matcher.normalize_company_name('vsphere'), 'vmware')
        
        # Test unknown company
        self.assertIsNone(self.matcher.normalize_company_name('unknown_vendor'))
    
    def test_get_all_aliases(self):
        """Test retrieving aliases for companies"""
        microsoft_aliases = self.matcher.get_all_aliases_for_company('microsoft')
        self.assertIsInstance(microsoft_aliases, list)
        self.assertIn('azure', microsoft_aliases)
        
        # Test with alias as input
        vmware_aliases = self.matcher.get_all_aliases_for_company('vsphere')
        self.assertIsInstance(vmware_aliases, list)
        self.assertGreater(len(vmware_aliases), 0)
    
    def test_expand_keyword_list(self):
        """Test keyword list expansion with aliases"""
        keywords = ['microsoft', 'vmware']
        expanded = self.matcher.expand_keyword_list(keywords)
        
        self.assertIn('microsoft', expanded)
        self.assertIn('vmware', expanded)
        self.assertIn('azure', expanded)  # Microsoft alias
        self.assertIn('vsphere', expanded)  # VMware alias
        
        # Should have more keywords than input
        self.assertGreater(len(expanded), len(keywords))
    
    def test_company_relevance_scoring(self):
        """Test relevance scoring for specific companies"""
        text = "Microsoft Office 365 and Azure pricing updates affecting enterprise customers"
        target_companies = ['microsoft', 'vmware', 'cisco']
        
        scores = self.matcher.get_company_relevance_score(text, target_companies)
        
        self.assertIn('microsoft', scores)
        self.assertGreater(scores['microsoft'], 0)  # Should have high relevance
        self.assertEqual(scores['vmware'], 0)  # Should be zero (not mentioned)
        self.assertEqual(scores['cisco'], 0)  # Should be zero (not mentioned)
    
    def test_empty_text_handling(self):
        """Test handling of empty or invalid text"""
        result_empty = self.matcher.find_companies_in_text("")
        result_none = self.matcher.find_companies_in_text(None)
        
        self.assertEqual(len(result_empty.matched_companies), 0)
        self.assertEqual(len(result_none.matched_companies), 0)
        self.assertEqual(result_empty.total_matches, 0)
        self.assertEqual(result_none.total_matches, 0)
    
    def test_confidence_scoring(self):
        """Test confidence scoring mechanism"""
        # High confidence: multiple mentions with specific details
        high_confidence_text = "Microsoft Azure pricing increased 15% affecting Office 365 Enterprise customers"
        high_result = self.matcher.find_companies_in_text(high_confidence_text)
        
        # Low confidence: single mention
        low_confidence_text = "Microsoft mentioned in brief"
        low_result = self.matcher.find_companies_in_text(low_confidence_text)
        
        self.assertGreater(high_result.confidence_score, low_result.confidence_score)
    
    def test_global_matcher_instance(self):
        """Test global matcher instance functionality"""
        global_matcher = get_company_matcher()
        self.assertIsInstance(global_matcher, CompanyAliasMatcher)
        
        # Should return same instance on subsequent calls
        global_matcher2 = get_company_matcher()
        self.assertIs(global_matcher, global_matcher2)
    
    def test_debug_stats_generation(self):
        """Test debug statistics generation"""
        # Generate some matches first
        test_texts = [
            "Microsoft Azure pricing update",
            "VMware vSphere licensing changes",
            "Cisco networking equipment costs"
        ]
        
        for text in test_texts:
            self.matcher.find_companies_in_text(text)
        
        stats = self.matcher.get_debug_stats()
        
        self.assertIn('total_companies', stats)
        self.assertIn('total_aliases', stats)
        self.assertIn('match_stats', stats)
        self.assertIn('top_aliases', stats)
        self.assertGreater(stats['total_companies'], 0)
        self.assertGreater(stats['total_aliases'], 0)


class TestCompanyAliasMatcherIntegration(unittest.TestCase):
    """Integration tests for Company Alias Matcher"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.matcher = get_company_matcher(debug=True)
    
    def test_real_world_pricing_text(self):
        """Test with realistic pricing intelligence text"""
        pricing_text = """
        Microsoft announces 15% price increase for Office 365 Enterprise plans 
        effective Q3 2024. Meanwhile, VMware customers report 300% cost increases 
        following Broadcom acquisition, forcing migrations to Proxmox and 
        Hyper-V alternatives. AWS EC2 instances see regional pricing adjustments, 
        while CrowdStrike Falcon platform adds new EDR capabilities with 
        premium pricing tiers.
        """
        
        result = self.matcher.find_companies_in_text(pricing_text)
        
        # Should detect multiple major vendors
        expected_vendors = {'microsoft', 'vmware', 'aws', 'crowdstrike'}
        detected_vendors = result.matched_companies
        
        # Should detect at least 3 of the 4 vendors
        overlap = detected_vendors.intersection(expected_vendors)
        self.assertGreaterEqual(len(overlap), 3, 
                              f"Expected at least 3 vendors, detected: {detected_vendors}")
        
        # Should have high confidence due to specific pricing details
        self.assertGreater(result.confidence_score, 0.5)
    
    def test_distributor_detection(self):
        """Test detection of IT distributors and resellers"""
        distributor_text = """
        TD SYNNEX reports strong quarterly results driven by enterprise security 
        sales. Ingram Micro expands cloud marketplace offerings, while CDW 
        focuses on digital transformation services. SHI International wins 
        major federal contract for Microsoft Enterprise Agreement.
        """
        
        result = self.matcher.find_companies_in_text(distributor_text)
        
        expected_distributors = {'td synnex', 'ingram micro', 'cdw', 'shi'}
        detected_companies = result.matched_companies
        
        # Should detect at least 2 distributors
        overlap = detected_companies.intersection(expected_distributors)
        self.assertGreaterEqual(len(overlap), 2,
                              f"Expected distributors, detected: {detected_companies}")


if __name__ == '__main__':
    # Create test suite
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestCompanyAliasMatcher))
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestCompanyAliasMatcherIntegration))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)