#!/usr/bin/env python3
"""
Test script for M&A Intelligence Scoring Enhancement
Validates the undervalued Broadcom/VMware audit intelligence
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fetchers.base_fetcher import BaseFetcher
from run_hybrid_system import load_config

class TestFetcher(BaseFetcher):
    """Test fetcher for M&A intelligence scoring validation"""
    
    def get_source_name(self) -> str:
        return "test"
    
    async def fetch_raw(self):
        return []

def test_ma_intelligence_scoring():
    """Test M&A intelligence scoring with the undervalued example"""
    
    # Load configuration
    config = load_config()
    
    # Create test fetcher
    fetcher = TestFetcher(config)
    
    # Test cases - including the undervalued Broadcom/VMware case
    test_cases = [
        {
            "text": "Broadcom begins auditing organizations using VMware",
            "expected_min_score": 7.0,
            "description": "Critical M&A intelligence - post-acquisition audit"
        },
        {
            "text": "VMware by Broadcom license enforcement audit customers",
            "expected_min_score": 8.0,
            "description": "M&A intelligence - license enforcement"
        },
        {
            "text": "Post-acquisition audit by Broadcom VMware customers",
            "expected_min_score": 7.0,
            "description": "M&A intelligence - post-acquisition pattern"
        },
        {
            "text": "Acquisition monetization strategy audit customers",
            "expected_min_score": 6.0,
            "description": "M&A intelligence - acquisition monetization"
        },
        {
            "text": "Regular software update announcement",
            "expected_min_score": 0.0,
            "description": "Non-M&A content - should have low score"
        }
    ]
    
    print("🧪 M&A Intelligence Scoring Test")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        text = test_case["text"]
        expected_min = test_case["expected_min_score"]
        description = test_case["description"]
        
        # Calculate current score
        current_score = fetcher._calculate_relevance_score(text)
        
        # Determine result
        result = "✅ PASS" if current_score >= expected_min else "❌ FAIL"
        
        print(f"\nTest {i}: {description}")
        print(f"Text: '{text}'")
        print(f"Current Score: {current_score:.2f}")
        print(f"Expected Min: {expected_min:.2f}")
        print(f"Result: {result}")
        
        if current_score < expected_min:
            print(f"⚠️  Score Gap: {expected_min - current_score:.2f} points needed")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_ma_intelligence_scoring()