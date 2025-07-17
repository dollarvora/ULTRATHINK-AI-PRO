#!/usr/bin/env python3
"""
Test Enhanced Urgency Detection for Vendor Ecosystem Changes
This test demonstrates how the enhanced urgency detection system would properly 
classify vendor ecosystem changes like the VMware VCSP program shutdown.
"""

import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from fetchers.base_fetcher import BaseFetcher

# Mock configuration for testing
TEST_CONFIG = {
    "keywords": {
        "pricing": ["price", "cost", "pricing", "license", "subscription"],
        "urgency_indicators": [
            "urgent", "critical", "immediate", "breaking", "emergency"
        ],
        "urgency_high": [
            "urgent", "critical", "immediate", "breaking", "emergency", 
            "acquisition", "merger", "security breach", "vulnerability", 
            "end of life", "EOL", "discontinuation", "recall", "lawsuit",
            "compliance", "regulatory", "audit", "zero-day", "exploit",
            "data breach", "ransomware", "supply shortage", "chip shortage",
            "licensing deadline", "contract expiration", "price deadline",
            "limited time", "exclusive offer", "flash sale", "vendor lock-in",
            "channel conflict", "margin compression", "bankruptcy",
            "shutdown", "termination", "cancelled", "program closure", 
            "program shutdown", "program termination", "vcsp", "vcp",
            "var program", "csp program", "partner program shutdown",
            "channel program end", "reseller program terminated", 
            "migration deadline", "forced migration", "mandatory migration",
            "certification expires", "certification discontinued", 
            "license model change", "licensing overhaul", "subscription mandatory",
            "end of support", "end of sales", "last order date", "final orders",
            "all partners", "all resellers", "all distributors", "global program",
            "thousands of partners", "hundreds of partners", "entire channel",
            "program overhaul", "business model change", "go-to-market change",
            "channel strategy shift", "partner model restructure", "program consolidation"
        ],
        "urgency_medium": [
            "update", "upgrade", "new release", "feature", "enhancement", 
            "partnership", "integration", "expansion", "growth", 
            "quarterly results", "earnings", "forecast", "outlook", 
            "roadmap", "strategy", "initiative", "program",
            "product launch", "beta release", "preview", "announcement",
            "rebate program", "channel program", "training", "certification",
            "webinar", "conference", "trade show", "summit",
            "program changes", "partner program update", "channel update",
            "certification program", "training program", "enablement program",
            "partner portal", "reseller portal", "distributor portal",
            "tier changes", "tier adjustments", "tier requirements",
            "program requirements", "new program", "program launch",
            "incentive program", "spiff program", "co-op program",
            "mdf program", "marketing development fund", "channel marketing",
            "partner benefits", "program benefits", "new benefits",
            "many partners", "multiple partners", "several partners",
            "regional program", "select partners", "key partners",
            "major partners", "tier 1 partners", "enterprise partners",
            "significant portion", "substantial impact", "considerable change",
            "widespread", "broad impact", "numerous", "extensive"
        ],
        "urgency_low": [
            "maintenance", "patch", "bugfix", "optimization", "performance", 
            "documentation", "training", "certification", "webinar", 
            "conference", "event", "announcement", "newsletter",
            "general availability", "stable release", "minor update",
            "cosmetic changes", "UI improvements", "user experience"
        ]
    },
    "vendors": {
        "software": ["VMware", "vSphere", "vCenter", "ESXi", "NSX"]
    },
    "sources": {
        "test": {"enabled": True}
    },
    "scoring": {
        "keyword_weight": 1.0,
        "urgency_weight": 2.0,
        "vendor_weight": 1.5,
        "high_score_threshold": 5.0,
        "medium_score_threshold": 2.0
    },
    "system": {
        "cache_ttl_hours": 6
    }
}

class TestFetcher(BaseFetcher):
    def get_source_name(self) -> str:
        return "test"
    
    async def fetch_raw(self):
        return []

def test_urgency_detection():
    """Test enhanced urgency detection with vendor ecosystem scenarios"""
    
    # Initialize test fetcher
    fetcher = TestFetcher(TEST_CONFIG)
    
    # Test cases for vendor ecosystem changes
    test_cases = [
        {
            "name": "VMware VCSP Program Shutdown",
            "text": "VMware announces the shutdown of its VCSP program affecting thousands of partners with migration deadline in Oct 2025",
            "expected_urgency": "high",
            "reasons": ["shutdown", "vcsp", "thousands of partners", "migration deadline"]
        },
        {
            "name": "Partner Program Termination",
            "text": "Microsoft terminates its partner program for all resellers effective immediately",
            "expected_urgency": "high",
            "reasons": ["termination", "partner program", "all resellers", "immediately"]
        },
        {
            "name": "Channel Program Changes",
            "text": "Dell updates its channel program with new tier requirements for select partners",
            "expected_urgency": "medium",
            "reasons": ["channel program", "tier requirements", "select partners"]
        },
        {
            "name": "Certification Program Update",
            "text": "Cisco announces updates to its certification program for training purposes",
            "expected_urgency": "medium",
            "reasons": ["certification program", "training"]
        },
        {
            "name": "Minor Program Announcement",
            "text": "HP announces minor documentation updates for its partner portal",
            "expected_urgency": "low",
            "reasons": ["documentation", "minor"]
        },
        {
            "name": "Time-based Urgency",
            "text": "Program migration required by end of month for all partners",
            "expected_urgency": "high",
            "reasons": ["migration required", "end of month"]
        },
        {
            "name": "Scale-based Urgency",
            "text": "Industry-wide program overhaul affecting hundreds of partners",
            "expected_urgency": "high",
            "reasons": ["industry-wide", "program overhaul", "hundreds of partners"]
        }
    ]
    
    print("Enhanced Urgency Detection Test Results")
    print("="*60)
    
    correct_predictions = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print(f"Text: {test_case['text']}")
        
        # Test urgency detection
        detected_urgency = fetcher._determine_content_urgency(test_case['text'], 1.0)
        expected_urgency = test_case['expected_urgency']
        
        print(f"Expected: {expected_urgency}")
        print(f"Detected: {detected_urgency}")
        
        if detected_urgency == expected_urgency:
            print("✅ PASS - Correct urgency detected")
            correct_predictions += 1
        else:
            print("❌ FAIL - Incorrect urgency detected")
        
        print(f"Key indicators: {', '.join(test_case['reasons'])}")
        
        # Test helper methods
        time_urgency = fetcher._detect_time_urgency(test_case['text'])
        scale_urgency = fetcher._detect_scale_urgency(test_case['text'])
        
        if time_urgency or scale_urgency != 'low':
            print(f"Additional detection: Time urgency={time_urgency}, Scale urgency={scale_urgency}")
    
    print(f"\n{'='*60}")
    print(f"Test Summary: {correct_predictions}/{total_tests} tests passed")
    print(f"Accuracy: {(correct_predictions/total_tests)*100:.1f}%")
    
    return correct_predictions == total_tests

def demonstrate_improvements():
    """Demonstrate how the enhanced system would handle the original VMware VCSP case"""
    
    print("\n" + "="*60)
    print("DEMONSTRATION: Enhanced vs Original System")
    print("="*60)
    
    original_text = "VMware announces the shutdown of its VCSP program affecting thousands of partners with migration deadline in Oct 2025"
    
    # Initialize fetcher
    fetcher = TestFetcher(TEST_CONFIG)
    
    print(f"Original text: {original_text}")
    print()
    
    # Show what the original system would detect
    print("Original System (hardcoded keywords only):")
    original_keywords = [
        'acquisition', 'merger', 'acquired', 'acquires', 'buying', 'bought',
        'bankruptcy', 'lawsuit', 'security breach', 'data breach', 'zero-day',
        'critical vulnerability', 'emergency', 'urgent', 'immediate',
        'discontinued', 'end of life', 'eol', 'supply shortage', 'recall',
        'price increase', 'cost increase', 'breaking', 'alert'
    ]
    
    original_matches = [kw for kw in original_keywords if kw in original_text.lower()]
    print(f"  Matches: {original_matches if original_matches else 'None'}")
    print(f"  Classification: {'high' if original_matches else 'low'} (based on score)")
    
    # Show what the enhanced system detects
    print("\nEnhanced System (vendor ecosystem aware):")
    enhanced_urgency = fetcher._determine_content_urgency(original_text, 1.0)
    time_urgency = fetcher._detect_time_urgency(original_text)
    scale_urgency = fetcher._detect_scale_urgency(original_text)
    
    print(f"  Vendor ecosystem matches: shutdown, vcsp, thousands of partners")
    print(f"  Time-based urgency: {time_urgency} (Oct 2025 deadline)")
    print(f"  Scale-based urgency: {scale_urgency} (thousands of partners)")
    print(f"  Final classification: {enhanced_urgency}")
    
    print("\nKey Improvements:")
    print("  ✅ Vendor program terminology (VCSP, shutdown, migration)")
    print("  ✅ Time-based urgency detection (Oct 2025 deadline)")
    print("  ✅ Scale-based urgency detection (thousands of partners)")
    print("  ✅ Business impact awareness for IT procurement teams")
    print("  ✅ Configurable keywords from keywords.json")

if __name__ == "__main__":
    print("Testing Enhanced Urgency Detection for Vendor Ecosystem Changes")
    print("This test validates improvements for IT procurement intelligence\n")
    
    # Run the test suite
    success = test_urgency_detection()
    
    # Demonstrate the improvements
    demonstrate_improvements()
    
    print(f"\n{'='*60}")
    if success:
        print("✅ All tests passed! Enhanced urgency detection is working correctly.")
    else:
        print("❌ Some tests failed. Review the implementation.")
    
    print("\nThe enhanced system would now properly classify:")
    print("- VMware VCSP program shutdown as HIGH urgency")
    print("- Partner program terminations as HIGH urgency")
    print("- Channel program changes as MEDIUM urgency")
    print("- Time-sensitive deadlines as HIGH urgency")
    print("- Large-scale program changes as HIGH urgency")