#!/usr/bin/env python3
"""
Test suite for HTML Generator
Validates HTML report generation, mobile responsiveness, and accessibility
"""
import unittest
import sys
import os
import tempfile
from datetime import datetime
from bs4 import BeautifulSoup

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from html_generator import EnhancedHTMLGenerator, generate_and_save_report


class TestEnhancedHTMLGenerator(unittest.TestCase):
    """Test cases for Enhanced HTML Generator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = EnhancedHTMLGenerator(debug=False)
        
        # Sample test data
        self.sample_insights = [
            "🔴 Microsoft Office 365 pricing increased 15% affecting enterprise customers",
            "🟡 VMware licensing changes driving migration to alternatives",
            "🟢 Dell server pricing remains stable despite supply chain pressures"
        ]
        
        self.sample_content = [
            {
                'title': 'Microsoft Pricing Update',
                'content': 'Enterprise licensing costs increasing',
                'url': 'https://example.com/microsoft',
                'date': '2024-06-15',
                'source': 'reddit',
                'score': 95
            },
            {
                'title': 'VMware Migration Analysis', 
                'content': 'Broadcom acquisition impacts',
                'url': 'https://example.com/vmware',
                'date': '2024-06-14',
                'source': 'google',
                'score': 87
            }
        ]
        
        self.sample_vendor_analysis = {
            'top_vendors': [('microsoft', 3), ('vmware', 2), ('dell', 1)],
            'total_vendors': 3,
            'vendor_mentions': {'microsoft': 3, 'vmware': 2, 'dell': 1}
        }
        
        self.sample_config = {
            'system': {'name': 'ULTRATHINK-AI-PRO', 'version': '3.1.0'}
        }
        
        self.sample_performance_metrics = {
            'summary': {
                'total_runtime': 45.2,
                'success_rate': 0.95,
                'total_api_calls': 8,
                'total_data_processed': 150
            }
        }
    
    def test_initialization(self):
        """Test generator initialization"""
        self.assertIsInstance(self.generator, EnhancedHTMLGenerator)
        self.assertEqual(self.generator.debug, False)
    
    def test_content_grouping_by_source(self):
        """Test content grouping by source"""
        grouped = self.generator._group_content_by_source(self.sample_content)
        
        self.assertIsInstance(grouped, dict)
        self.assertIn('reddit', grouped)
        self.assertIn('google', grouped)
        self.assertEqual(len(grouped['reddit']), 1)
        self.assertEqual(len(grouped['google']), 1)
    
    def test_insights_categorization(self):
        """Test insights categorization by priority"""
        categorized = self.generator._categorize_insights_by_priority(self.sample_insights)
        
        self.assertIsInstance(categorized, dict)
        self.assertIn('alpha', categorized)
        self.assertIn('beta', categorized)
        self.assertIn('gamma', categorized)
        
        # Check categorization logic
        self.assertEqual(len(categorized['alpha']), 1)  # 🔴 high priority
        self.assertEqual(len(categorized['beta']), 1)   # 🟡 medium priority
        self.assertEqual(len(categorized['gamma']), 1)  # 🟢 low priority
    
    def test_vendor_stats_generation(self):
        """Test vendor statistics generation"""
        vendor_stats = self.generator._generate_vendor_stats(self.sample_vendor_analysis, self.sample_content)
        
        self.assertIsInstance(vendor_stats, dict)
        self.assertIn('top_vendors', vendor_stats)
        self.assertIn('total_vendors', vendor_stats)
        self.assertIn('vendor_mentions', vendor_stats)
        
        # Should have processed vendors
        self.assertGreater(len(vendor_stats['top_vendors']), 0)
    
    def test_html_report_generation(self):
        """Test complete HTML report generation"""
        html_content = self.generator.generate_html_report(
            insights=self.sample_insights,
            all_content=self.sample_content,
            vendor_analysis=self.sample_vendor_analysis,
            config=self.sample_config,
            performance_metrics=self.sample_performance_metrics
        )
        
        self.assertIsInstance(html_content, str)
        self.assertGreater(len(html_content), 1000)  # Should be substantial
        
        # Parse HTML to validate structure
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Test basic HTML structure
        self.assertIsNotNone(soup.find('html'))
        self.assertIsNotNone(soup.find('head'))
        self.assertIsNotNone(soup.find('body'))
        
        # Test required meta tags (mobile responsiveness)
        viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
        self.assertIsNotNone(viewport_meta, "Missing viewport meta tag for mobile responsiveness")
        
        charset_meta = soup.find('meta', attrs={'charset': True})
        self.assertIsNotNone(charset_meta, "Missing charset meta tag")
        
        description_meta = soup.find('meta', attrs={'name': 'description'})
        self.assertIsNotNone(description_meta, "Missing description meta tag")
    
    def test_accessibility_features(self):
        """Test accessibility features in generated HTML"""
        html_content = self.generator.generate_html_report(
            insights=self.sample_insights,
            all_content=self.sample_content,
            vendor_analysis=self.sample_vendor_analysis,
            config=self.sample_config
        )
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Test semantic HTML elements
        self.assertIsNotNone(soup.find('main'), "Missing main element")
        self.assertIsNotNone(soup.find('header'), "Missing header element") 
        self.assertIsNotNone(soup.find('footer'), "Missing footer element")
        
        # Test ARIA labels and roles
        main_element = soup.find('main')
        self.assertEqual(main_element.get('role'), 'main')
        
        # Test heading hierarchy
        h1 = soup.find('h1')
        h2 = soup.find('h2')
        self.assertIsNotNone(h1, "Missing h1 element")
        self.assertIsNotNone(h2, "Missing h2 element")
        
        # Test visually hidden text for screen readers
        visually_hidden = soup.find(class_='visually-hidden')
        self.assertIsNotNone(visually_hidden, "Missing visually-hidden elements for screen readers")
        
        # Test time elements for dates
        time_elements = soup.find_all('time')
        self.assertGreater(len(time_elements), 0, "Missing time elements for dates")
    
    def test_mobile_responsive_css(self):
        """Test mobile responsive CSS in generated HTML"""
        html_content = self.generator.generate_html_report(
            insights=self.sample_insights,
            all_content=self.sample_content,
            vendor_analysis=self.sample_vendor_analysis,
            config=self.sample_config
        )
        
        # Test for mobile responsive CSS
        self.assertIn('@media (max-width: 768px)', html_content, "Missing tablet responsive CSS")
        self.assertIn('@media (max-width: 480px)', html_content, "Missing mobile responsive CSS")
        self.assertIn('@media print', html_content, "Missing print styles")
        
        # Test for accessibility CSS
        self.assertIn('@media (prefers-contrast: high)', html_content, "Missing high contrast CSS")
        self.assertIn('@media (prefers-reduced-motion', html_content, "Missing reduced motion CSS")
        
        # Test for responsive grid
        self.assertIn('grid-template-columns', html_content, "Missing responsive grid CSS")
        self.assertIn('auto-fit', html_content, "Missing auto-fit grid property")
    
    def test_insights_section_generation(self):
        """Test insights section HTML generation"""
        alpha_html = self.generator._generate_insights_section(
            [self.sample_insights[0]], 'alpha', 'Priority Alpha (High Impact)'
        )
        
        soup = BeautifulSoup(alpha_html, 'html.parser')
        
        # Test section structure
        section = soup.find('section')
        self.assertIsNotNone(section)
        self.assertIsNotNone(section.get('aria-labelledby'))
        
        # Test heading
        h3 = soup.find('h3')
        self.assertIsNotNone(h3)
        self.assertIsNotNone(h3.get('id'))
        
        # Test insight items
        insight_item = soup.find(class_='insight-item')
        self.assertIsNotNone(insight_item)
        self.assertEqual(insight_item.get('role'), 'article')
        
        # Test confidence badge
        confidence_badge = soup.find('span', attrs={'role': 'status'})
        self.assertIsNotNone(confidence_badge, "Missing confidence badge with role=status")
    
    def test_vendor_section_generation(self):
        """Test vendor section HTML generation"""
        vendor_html = self.generator._generate_vendor_section(self.sample_vendor_analysis)
        
        soup = BeautifulSoup(vendor_html, 'html.parser')
        
        # Test section structure
        section = soup.find('section')
        self.assertIsNotNone(section)
        self.assertIsNotNone(section.get('aria-labelledby'))
        
        # Test vendor badges
        vendor_badges = soup.find_all(class_='vendor-badge')
        self.assertGreater(len(vendor_badges), 0)
        
        # Test accessibility attributes
        for badge in vendor_badges:
            self.assertEqual(badge.get('role'), 'listitem')
            self.assertIsNotNone(badge.get('aria-label'))
    
    def test_sources_section_generation(self):
        """Test sources section HTML generation"""
        content_by_source = self.generator._group_content_by_source(self.sample_content)
        sources_html = self.generator._generate_sources_section(content_by_source)
        
        soup = BeautifulSoup(sources_html, 'html.parser')
        
        # Test section structure
        section = soup.find('section')
        self.assertIsNotNone(section)
        self.assertIsNotNone(section.get('aria-labelledby'))
        
        # Test source articles
        articles = soup.find_all('article')
        self.assertGreater(len(articles), 0)
        
        # Test links with proper attributes
        links = soup.find_all('a')
        for link in links:
            if link.get('href') and link.get('href') != '#':
                self.assertEqual(link.get('target'), '_blank')
                self.assertEqual(link.get('rel'), 'noopener noreferrer')
                self.assertIsNotNone(link.get('aria-label'))
    
    def test_performance_section_generation(self):
        """Test performance metrics section generation"""
        performance_html = self.generator._generate_performance_section(self.sample_performance_metrics)
        
        soup = BeautifulSoup(performance_html, 'html.parser')
        
        # Test section structure
        section = soup.find('section')
        self.assertIsNotNone(section)
        self.assertIsNotNone(section.get('aria-labelledby'))
        
        # Test metrics grid
        metrics_grid = soup.find(class_='metrics-grid')
        self.assertIsNotNone(metrics_grid)
        self.assertEqual(metrics_grid.get('role'), 'group')
        
        # Test individual metrics
        metrics = soup.find_all('div', attrs={'role': 'listitem'})
        self.assertEqual(len(metrics), 4)  # Should have 4 metrics
        
        # Test aria-labels on metrics
        for metric in metrics:
            spans = metric.find_all('span')
            if spans:
                self.assertIsNotNone(spans[0].get('aria-label'))
    
    def test_save_html_report(self):
        """Test saving HTML report to file"""
        html_content = self.generator.generate_html_report(
            insights=self.sample_insights,
            all_content=self.sample_content,
            vendor_analysis=self.sample_vendor_analysis,
            config=self.sample_config
        )
        
        # Use temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            saved_file = self.generator.save_html_report(html_content, temp_dir)
            
            # Test file was created
            self.assertTrue(os.path.exists(saved_file))
            
            # Test file content
            with open(saved_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            self.assertEqual(file_content, html_content)
            
            # Test filename format
            filename = os.path.basename(saved_file)
            self.assertTrue(filename.startswith('ultrathink_enhanced_'))
            self.assertTrue(filename.endswith('.html'))
    
    def test_empty_insights_handling(self):
        """Test handling of empty insights"""
        empty_html = self.generator._generate_insights_section([], 'alpha', 'Priority Alpha')
        
        soup = BeautifulSoup(empty_html, 'html.parser')
        
        # Should still have proper structure
        section = soup.find('section')
        self.assertIsNotNone(section)
        
        # Should have empty state message
        self.assertIn('No alpha priority insights', empty_html)
    
    def test_vendor_highlighting(self):
        """Test vendor name highlighting in text"""
        test_text = "Microsoft Azure and VMware vSphere pricing updates"
        highlighted = self.generator._highlight_vendors(test_text)
        
        # Should contain highlighted vendors
        self.assertIn('<span style="background-color: #ffeb3b', highlighted)
        self.assertIn('Microsoft', highlighted)
        
        # Original vendors should be preserved
        soup = BeautifulSoup(highlighted, 'html.parser')
        highlighted_spans = soup.find_all('span', style=True)
        self.assertGreater(len(highlighted_spans), 0)
    
    def test_confidence_assessment(self):
        """Test insight confidence assessment"""
        # High confidence (specific data)
        high_conf_insight = "Microsoft pricing increased 15% with $50M revenue impact"
        high_conf = self.generator._assess_insight_confidence(high_conf_insight)
        self.assertEqual(high_conf['level'], 'High Confidence')
        
        # Medium confidence (reported data)
        med_conf_insight = "Reports indicate VMware pricing changes affecting customers"
        med_conf = self.generator._assess_insight_confidence(med_conf_insight)
        self.assertEqual(med_conf['level'], 'Medium Confidence')
        
        # Default confidence
        default_insight = "General market information available"
        default_conf = self.generator._assess_insight_confidence(default_insight)
        self.assertEqual(default_conf['level'], 'Moderate Confidence')


class TestHTMLGeneratorIntegration(unittest.TestCase):
    """Integration tests for HTML Generator"""
    
    def test_generate_and_save_report_function(self):
        """Test the convenience function for generating and saving reports"""
        sample_insights = ["🔴 Test insight for integration testing"]
        sample_content = [{'title': 'Test', 'content': 'Test', 'source': 'test'}]
        sample_vendor_analysis = {'top_vendors': [], 'total_vendors': 0, 'vendor_mentions': {}}
        sample_config = {'system': {'name': 'ULTRATHINK-AI-PRO'}}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            saved_file = generate_and_save_report(
                insights=sample_insights,
                all_content=sample_content,
                vendor_analysis=sample_vendor_analysis,
                config=sample_config,
                output_dir=temp_dir
            )
            
            # Verify file exists and is valid HTML
            self.assertTrue(os.path.exists(saved_file))
            
            with open(saved_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic HTML validation
            soup = BeautifulSoup(content, 'html.parser')
            self.assertIsNotNone(soup.find('html'))
            self.assertIsNotNone(soup.find('head'))
            self.assertIsNotNone(soup.find('body'))
            
            # Test our improvements are present
            self.assertIsNotNone(soup.find('meta', attrs={'name': 'viewport'}))
            self.assertIsNotNone(soup.find('main'))
    
    def test_large_content_handling(self):
        """Test handling of large amounts of content"""
        # Generate large content set
        large_content = []
        for i in range(100):
            large_content.append({
                'title': f'Test Article {i}',
                'content': f'Content for test article {i} with various vendor mentions Microsoft VMware Dell.',
                'url': f'https://example.com/article-{i}',
                'date': '2024-06-15',
                'source': 'reddit' if i % 2 == 0 else 'google'
            })
        
        large_insights = [f"🔴 Test insight {i} for large scale testing" for i in range(20)]
        
        generator = EnhancedHTMLGenerator(debug=False)
        
        html_content = generator.generate_html_report(
            insights=large_insights,
            all_content=large_content,
            vendor_analysis={'top_vendors': [('microsoft', 50), ('vmware', 30)], 'total_vendors': 2, 'vendor_mentions': {}},
            config={'system': {'name': 'ULTRATHINK-AI-PRO'}}
        )
        
        # Should handle large content without errors
        self.assertIsInstance(html_content, str)
        self.assertGreater(len(html_content), 5000)
        
        # Should be valid HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        self.assertIsNotNone(soup.find('html'))


if __name__ == '__main__':
    # Create test suite
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestEnhancedHTMLGenerator))
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestHTMLGeneratorIntegration))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)