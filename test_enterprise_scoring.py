#!/usr/bin/env python3
"""
Test the enhanced enterprise scoring system
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from run_hybrid_system import load_config
from fetchers.reddit_fetcher import RedditFetcher

def test_enterprise_scoring():
    """Test enterprise keyword categories"""
    
    print("🎯 TESTING ENTERPRISE SCORING CATEGORIES")
    print("=" * 50)
    
    # Load config and create fetcher
    config = load_config()
    fetcher = RedditFetcher(config)
    
    # Test cases for different categories
    test_cases = [
        {
            "name": "Price Point Intelligence",
            "text": "Looking at enterprise tier pricing for $100K+ deal with volume discount and annual commitment",
            "expected_categories": ["price_point_intelligence"]
        },
        {
            "name": "Competitive Displacement",
            "text": "Company is switching from VMware to Microsoft, migration project underway to replace existing platform",
            "expected_categories": ["competitive_displacement"]
        },
        {
            "name": "Financial Impact",
            "text": "Budget freeze announced, need to cut opex and reduce total cost of ownership for IT procurement",
            "expected_categories": ["financial_impact"]
        },
        {
            "name": "Industry Vertical",
            "text": "Healthcare IT implementation for hospital technology and medical devices across health systems",
            "expected_categories": ["industry_verticals"]
        },
        {
            "name": "Economic Conditions",
            "text": "Recession impact on technology spending, inflation affecting supply chain and budget cuts",
            "expected_categories": ["economic_conditions"]
        },
        {
            "name": "Technology Trends",
            "text": "AI pricing models for machine learning costs, cloud migration to AWS with SaaS pricing strategy",
            "expected_categories": ["technology_trends"]
        },
        {
            "name": "Multi-Category",
            "text": "Enterprise tier $500K+ budget for competitive win switching from Oracle with healthcare IT focus during recession",
            "expected_categories": ["price_point_intelligence", "competitive_displacement", "financial_impact", "industry_verticals", "economic_conditions"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"   Text: {test_case['text'][:80]}...")
        
        score = fetcher._calculate_relevance_score(test_case['text'])
        print(f"   Score: {score:.1f}")
        
        # Check specific category keywords
        print(f"   Expected: {', '.join(test_case['expected_categories'])}")
    
    print(f"\n🎯 DETAILED KEYWORD ANALYSIS:")
    
    # Test VCSP with enhanced scoring
    vcsp_text = "VMware by Broadcom VCSP program is closing with $50M+ budget impact affecting enterprise tier customers"
    print(f"\n📊 VCSP Enhanced Test:")
    print(f"   Text: {vcsp_text}")
    
    score = fetcher._calculate_relevance_score(vcsp_text)
    print(f"   Total Score: {score:.1f}")
    
    # Manual keyword checks
    for category in ['price_point_intelligence', 'financial_impact', 'competitive_displacement']:
        keywords = config['keywords'].get(category, [])
        matches = [kw for kw in keywords if kw.lower() in vcsp_text.lower()]
        print(f"   {category}: {len(matches)} matches - {matches[:3] if matches else 'None'}")

if __name__ == "__main__":
    test_enterprise_scoring()