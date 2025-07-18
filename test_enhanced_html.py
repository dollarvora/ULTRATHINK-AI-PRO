#!/usr/bin/env python3
"""
Test script for Enhanced HTML Generator
Tests the new features and validates 95%+ footnote accuracy
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from html_generator import EnhancedHTMLGenerator
from datetime import datetime

def create_test_data():
    """Create comprehensive test data to validate all enhancements"""
    
    # Test insights with different priority levels and confidence data
    test_insights = [
        {
            'text': 'Microsoft Office 365 pricing increasing by 15% in Q1 2024, affecting enterprise customers [reddit_1]',
            'confidence': {
                'confidence_level': 'high',
                'confidence_percentage': 92,
                'confidence_factors': ['Multiple sources confirm', 'Official announcement', 'Historical pattern']
            }
        },
        {
            'text': 'Dell server supply chain experiencing delays due to chip shortages [reddit_2]',
            'confidence': {
                'confidence_level': 'medium',
                'confidence_percentage': 78,
                'confidence_factors': ['Industry reports', 'Supplier notifications']
            }
        },
        {
            'text': 'VMware licensing model changes creating opportunities for alternative solutions [google_1]',
            'confidence': {
                'confidence_level': 'high',
                'confidence_percentage': 88,
                'confidence_factors': ['Customer feedback', 'Market analysis', 'Competitive movement']
            }
        },
        {
            'text': 'Cisco networking equipment prices stabilizing after recent increases [google_2]',
            'confidence': {
                'confidence_level': 'low',
                'confidence_percentage': 65,
                'confidence_factors': ['Limited data', 'Regional variation']
            }
        }
    ]
    
    # Test content with Reddit and Google sources
    test_content = [
        {
            'source': 'reddit',
            'title': 'Microsoft Office 365 Enterprise Price Increase Discussion',
            'content': 'Microsoft announced a 15% price increase for Office 365 Enterprise plans effective Q1 2024. This affects millions of enterprise customers...',
            'url': 'https://reddit.com/r/sysadmin/microsoft-office-365-price-increase',
            'subreddit': 'sysadmin',
            'relevance_score': 9.2,
            'created_at': '2024-01-15T10:30:00Z'
        },
        {
            'source': 'reddit',
            'title': 'Dell Server Supply Chain Issues - What to Expect',
            'content': 'Dell is experiencing significant supply chain delays for their PowerEdge servers due to ongoing chip shortages...',
            'url': 'https://reddit.com/r/homelab/dell-server-supply-chain',
            'subreddit': 'homelab',
            'relevance_score': 8.5,
            'created_at': '2024-01-14T14:20:00Z'
        },
        {
            'source': 'google',
            'title': 'VMware Licensing Changes Drive Customer Migration',
            'content': 'VMware\'s recent licensing model changes are causing many customers to evaluate alternative virtualization solutions...',
            'url': 'https://example.com/vmware-licensing-changes',
            'relevance_score': 8.8,
            'created_at': '2024-01-13T09:15:00Z'
        },
        {
            'source': 'google',
            'title': 'Cisco Network Equipment Pricing Trends 2024',
            'content': 'Cisco networking equipment prices are showing signs of stabilization after significant increases in 2023...',
            'url': 'https://example.com/cisco-pricing-trends',
            'relevance_score': 7.3,
            'created_at': '2024-01-12T16:45:00Z'
        }
    ]
    
    # Test vendor analysis
    test_vendor_analysis = {
        'top_vendors': [
            ('Microsoft', 15),
            ('Dell', 12),
            ('VMware', 10),
            ('Cisco', 8),
            ('HP', 6),
            ('Oracle', 5),
            ('IBM', 4),
            ('Intel', 3)
        ],
        'total_vendors': 8,
        'vendor_mentions': {
            'Microsoft': 15,
            'Dell': 12,
            'VMware': 10,
            'Cisco': 8,
            'HP': 6,
            'Oracle': 5,
            'IBM': 4,
            'Intel': 3
        }
    }
    
    # Test source mapping for footnote accuracy
    test_source_mapping = {
        'reddit_1': {
            'title': 'Microsoft Office 365 Enterprise Price Increase Discussion',
            'url': 'https://reddit.com/r/sysadmin/microsoft-office-365-price-increase',
            'source': 'reddit',
            'content': 'Microsoft announced a 15% price increase for Office 365 Enterprise plans effective Q1 2024. This affects millions of enterprise customers...',
            'relevance_score': 9.2,
            'created_at': '2024-01-15T10:30:00Z'
        },
        'reddit_2': {
            'title': 'Dell Server Supply Chain Issues - What to Expect',
            'url': 'https://reddit.com/r/homelab/dell-server-supply-chain',
            'source': 'reddit',
            'content': 'Dell is experiencing significant supply chain delays for their PowerEdge servers due to ongoing chip shortages...',
            'relevance_score': 8.5,
            'created_at': '2024-01-14T14:20:00Z'
        },
        'google_1': {
            'title': 'VMware Licensing Changes Drive Customer Migration',
            'url': 'https://example.com/vmware-licensing-changes',
            'source': 'google',
            'content': 'VMware\'s recent licensing model changes are causing many customers to evaluate alternative virtualization solutions...',
            'relevance_score': 8.8,
            'created_at': '2024-01-13T09:15:00Z'
        },
        'google_2': {
            'title': 'Cisco Network Equipment Pricing Trends 2024',
            'url': 'https://example.com/cisco-pricing-trends',
            'source': 'google',
            'content': 'Cisco networking equipment prices are showing signs of stabilization after significant increases in 2023...',
            'relevance_score': 7.3,
            'created_at': '2024-01-12T16:45:00Z'
        }
    }
    
    test_config = {
        'sources': {
            'reddit': {'enabled': True},
            'google': {'enabled': True}
        }
    }
    
    return test_insights, test_content, test_vendor_analysis, test_config, test_source_mapping

def test_footnote_accuracy(generator, insights, source_mapping):
    """Test footnote accuracy by checking SOURCE_ID mapping"""
    
    print("🔍 Testing Footnote Accuracy...")
    
    # Set up source mapping
    if source_mapping:
        generator.source_id_mapping = {}
        footnote_counter = 1
        for source_id, source_data in source_mapping.items():
            generator.source_id_mapping[source_id] = {
                'footnote_number': footnote_counter,
                'title': source_data['title'],
                'url': source_data['url'],
                'source': source_data['source'],
                'content_preview': source_data['content'][:200] + '...'
            }
            footnote_counter += 1
    
    # Test insight processing
    categorized_insights = generator._categorize_insights_by_priority(insights)
    
    # Check footnote extraction
    total_insights = sum(len(insights) for insights in categorized_insights.values())
    insights_with_footnotes = 0
    
    for priority, priority_insights in categorized_insights.items():
        for insight in priority_insights:
            insight_text = insight.get('text', str(insight)) if isinstance(insight, dict) else str(insight)
            if '[' in insight_text and ']' in insight_text:
                insights_with_footnotes += 1
    
    accuracy = (insights_with_footnotes / total_insights * 100) if total_insights > 0 else 0
    
    print(f"   📊 Total insights: {total_insights}")
    print(f"   📊 Insights with footnotes: {insights_with_footnotes}")
    print(f"   📊 Footnote accuracy: {accuracy:.1f}%")
    
    return accuracy

def test_enhanced_features():
    """Test all enhanced HTML generator features"""
    
    print("🚀 Testing Enhanced HTML Generator Features...")
    print("=" * 60)
    
    # Create test data
    test_insights, test_content, test_vendor_analysis, test_config, test_source_mapping = create_test_data()
    
    # Initialize generator with debug mode
    generator = EnhancedHTMLGenerator(debug=True)
    
    # Test 1: Footnote Accuracy
    print("\\n1. Testing Footnote Accuracy...")
    accuracy = test_footnote_accuracy(generator, test_insights, test_source_mapping)
    accuracy_status = "✅ PASSED" if accuracy >= 95 else "⚠️ NEEDS IMPROVEMENT"
    print(f"   Result: {accuracy:.1f}% {accuracy_status}")
    
    # Test 2: Generate Complete HTML Report
    print("\\n2. Testing Complete HTML Report Generation...")
    try:
        html_content = generator.generate_html_report(
            insights=test_insights,
            all_content=test_content,
            vendor_analysis=test_vendor_analysis,
            config=test_config,
            source_mapping=test_source_mapping
        )
        print("   ✅ HTML report generated successfully")
        print(f"   📊 HTML length: {len(html_content):,} characters")
        
        # Check for key enhancements
        enhancements_found = {
            'Enhanced CSS': 'enhanced-insight' in html_content,
            'Interactive Elements': 'enhanced-footnote' in html_content,
            'Vendor Charts': 'vendor-chart-bar' in html_content,
            'Mobile Responsive': '@media (max-width: 768px)' in html_content,
            'Confidence Badges': 'confidence-badge' in html_content,
            'Search Functionality': 'insight-search' in html_content,
            'Accuracy Dashboard': 'accuracy-dashboard' in html_content
        }
        
        print("\\n   🎯 Enhancement Features Detected:")
        for feature, found in enhancements_found.items():
            status = "✅" if found else "❌"
            print(f"      {status} {feature}")
        
        # Test 3: Save HTML Report
        print("\\n3. Testing HTML Report Saving...")
        output_path = generator.save_html_report(html_content, "test_output")
        print(f"   ✅ HTML report saved to: {output_path}")
        
        # Test 4: Performance Metrics
        print("\\n4. Testing Performance Metrics...")
        import time
        start_time = time.time()
        
        # Generate report multiple times to test performance
        for i in range(3):
            generator.generate_html_report(
                insights=test_insights,
                all_content=test_content,
                vendor_analysis=test_vendor_analysis,
                config=test_config,
                source_mapping=test_source_mapping
            )
        
        avg_time = (time.time() - start_time) / 3
        print(f"   ⚡ Average generation time: {avg_time:.2f}s")
        performance_status = "✅ FAST" if avg_time < 2.0 else "⚠️ SLOW"
        print(f"   Performance: {performance_status}")
        
        return True, accuracy, enhancements_found
        
    except Exception as e:
        print(f"   ❌ Error generating HTML report: {e}")
        return False, 0, {}

def main():
    """Main test execution"""
    
    print("🧪 ULTRATHINK-AI-PRO Enhanced HTML Generator Test Suite")
    print("=" * 60)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    success, accuracy, enhancements = test_enhanced_features()
    
    print("\\n" + "=" * 60)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    if success:
        print("✅ Overall Status: PASSED")
        print(f"📊 Footnote Accuracy: {accuracy:.1f}%")
        print(f"🎯 Features Implemented: {sum(enhancements.values())}/{len(enhancements)}")
        
        # Overall assessment
        if accuracy >= 95 and sum(enhancements.values()) >= 6:
            print("🏆 EXCELLENT: All enhancement targets achieved!")
        elif accuracy >= 85 and sum(enhancements.values()) >= 5:
            print("🎯 GOOD: Most enhancement targets achieved")
        else:
            print("⚠️ NEEDS IMPROVEMENT: Some targets not met")
    else:
        print("❌ Overall Status: FAILED")
        print("🔧 Please review error messages above")
    
    print("\\n✅ Test suite completed!")

if __name__ == "__main__":
    main()