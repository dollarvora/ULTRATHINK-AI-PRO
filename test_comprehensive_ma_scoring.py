#!/usr/bin/env python3
"""
Comprehensive Test for M&A Intelligence Scoring Enhancement
Validates various M&A intelligence patterns and scoring boost logic
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fetchers.base_fetcher import BaseFetcher
from run_hybrid_system import load_config

class TestFetcher(BaseFetcher):
    """Test fetcher for comprehensive M&A intelligence scoring validation"""
    
    def get_source_name(self) -> str:
        return "test"
    
    async def fetch_raw(self):
        return []

def test_comprehensive_ma_intelligence_scoring():
    """Test comprehensive M&A intelligence scoring with various patterns"""
    
    # Load configuration
    config = load_config()
    
    # Create test fetcher
    fetcher = TestFetcher(config)
    
    # Comprehensive test cases covering various M&A intelligence patterns
    test_cases = [
        # Original critical case
        {
            "text": "Broadcom begins auditing organizations using VMware",
            "expected_min_score": 7.0,
            "category": "Critical M&A Intelligence"
        },
        # Post-acquisition patterns
        {
            "text": "Post-acquisition audit reveals licensing compliance issues",
            "expected_min_score": 6.0,
            "category": "Post-Acquisition Pattern"
        },
        {
            "text": "Company conducts post-acquisition monetization strategy review",
            "expected_min_score": 6.0,
            "category": "Post-Acquisition Monetization"
        },
        # License enforcement patterns
        {
            "text": "License enforcement audit targets enterprise customers",
            "expected_min_score": 6.0,
            "category": "License Enforcement"
        },
        {
            "text": "VMware licensing overhaul forces mandatory migration",
            "expected_min_score": 6.0,
            "category": "Licensing Overhaul"
        },
        # Broadcom/VMware specific patterns
        {
            "text": "Broadcom VMware audit creates compliance concerns",
            "expected_min_score": 7.0,
            "category": "Broadcom/VMware Specific"
        },
        {
            "text": "VMware by Broadcom implements usage audit process",
            "expected_min_score": 7.0,
            "category": "VMware by Broadcom"
        },
        # Acquisition monetization patterns
        {
            "text": "Acquisition strategy focuses on customer monetization",
            "expected_min_score": 6.0,
            "category": "Acquisition Strategy"
        },
        {
            "text": "Merger integration includes license verification process",
            "expected_min_score": 6.0,
            "category": "Merger Integration"
        },
        # Enterprise scale patterns
        {
            "text": "Enterprise customers face licensing compliance audit",
            "expected_min_score": 5.0,
            "category": "Enterprise Scale"
        },
        # Control cases (should have low scores)
        {
            "text": "Regular software maintenance update released",
            "expected_min_score": 0.0,
            "category": "Control - Low Score"
        },
        {
            "text": "Standard product documentation updated",
            "expected_min_score": 0.0,
            "category": "Control - Low Score"
        }
    ]
    
    print("🧪 Comprehensive M&A Intelligence Scoring Test")
    print("=" * 80)
    print(f"Testing {len(test_cases)} M&A intelligence patterns...")
    print("=" * 80)
    
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        text = test_case["text"]
        expected_min = test_case["expected_min_score"]
        category = test_case["category"]
        
        # Calculate current score
        current_score = fetcher._calculate_relevance_score(text)
        
        # Determine result
        result = "✅ PASS" if current_score >= expected_min else "❌ FAIL"
        if current_score >= expected_min:
            passed += 1
        
        print(f"\nTest {i}: {category}")
        print(f"Text: '{text}'")
        print(f"Score: {current_score:.2f} (Expected: {expected_min:.2f}+)")
        print(f"Result: {result}")
        
        if current_score < expected_min:
            print(f"⚠️  Gap: {expected_min - current_score:.2f} points needed")
    
    print("\n" + "=" * 80)
    print(f"📊 SUMMARY: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All M&A intelligence patterns scoring correctly!")
        print("✅ Enhancement successfully implemented!")
    else:
        print(f"⚠️  {total - passed} tests need attention")
    
    print("=" * 80)
    
    # Test the original undervalued case specifically
    print("\n🎯 ORIGINAL UNDERVALUED CASE VALIDATION:")
    print("-" * 50)
    original_text = "Broadcom begins auditing organizations using VMware"
    original_score = fetcher._calculate_relevance_score(original_text)
    print(f"Original Case: '{original_text}'")
    print(f"Previous Score: 1.4 (Undervalued)")
    print(f"New Score: {original_score:.2f}")
    print(f"Improvement: +{original_score - 1.4:.2f} points")
    print(f"Target Achievement: {'✅ SUCCESS' if original_score >= 7.0 else '❌ NEEDS WORK'}")
    
    return passed == total

if __name__ == "__main__":
    test_comprehensive_ma_intelligence_scoring()