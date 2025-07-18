#!/usr/bin/env python3
"""
Test Enhanced Scoring System
Validates that MSP and security content gets proper scoring boosts
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from fetchers.base_fetcher import BaseFetcher
from run_hybrid_system import load_config
import json

class TestFetcher(BaseFetcher):
    """Test implementation of BaseFetcher to test scoring system"""
    
    def get_source_name(self):
        return "test"
    
    async def fetch_raw(self):
        return []

def test_enhanced_scoring():
    print("🧪 ENHANCED SCORING SYSTEM TEST")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    
    # Create a test fetcher
    fetcher = TestFetcher(config)
    
    # Test the Lenovo content from cache
    lenovo_text = """What's your experience with Lenovo (servers + storage)? 
Being pushed quite heavily at our MSP from the higher ups because apparently the profits are better. 
I get it. We're in this business to make money. I have some commercial experience and I want us to do well. 
But I have zero hands on experience with Lenovo Servers + Storage so from the tech side I'm anxious."""
    
    # Test the Microsoft Defender content from cache
    defender_text = """MS Defender makes me suffer and I have no clue what to do
I'm the sole IT admin for a small company (~50 users). Our main product is a software we develop inhouse and sell to customers.
Last year, we had to make a rather quick switch to Microsoft Defender due to an emergency – meaning we're now fully in the Microsoft Cloud ecosystem (Intune, Entra, etc.)."""
    
    print("🔍 Testing Lenovo Content:")
    print(f"   Text: '{lenovo_text[:80]}...'")
    lenovo_score = fetcher._calculate_relevance_score(lenovo_text)
    print(f"   💰 Enhanced Score: {lenovo_score:.1f}")
    
    print()
    print("🔍 Testing Microsoft Defender Content:")
    print(f"   Text: '{defender_text[:80]}...'")
    defender_score = fetcher._calculate_relevance_score(defender_text)
    print(f"   💰 Enhanced Score: {defender_score:.1f}")
    
    print()
    print("📊 SCORING ANALYSIS:")
    print(f"   Lenovo servers: {lenovo_score:.1f} (Should be ≥ 3.0 for Tier 1)")
    print(f"   Microsoft Defender: {defender_score:.1f} (Should be ≥ 2.0 for Tier 2)")
    
    # Test if they would be included in tiered selection
    print()
    print("🎯 TIERED INCLUSION TEST:")
    
    # Test Lenovo (should be Tier 1)
    if lenovo_score >= 3.0:
        print("   ✅ Lenovo: Tier 1 (High confidence) - INCLUDED")
    elif lenovo_score >= 2.0:
        print("   ✅ Lenovo: Tier 2 (Medium confidence) - INCLUDED if MSP/security pattern")
    else:
        print("   ❌ Lenovo: Below Tier 2 threshold - EXCLUDED")
    
    # Test Defender (should be Tier 2)
    if defender_score >= 3.0:
        print("   ✅ Microsoft Defender: Tier 1 (High confidence) - INCLUDED")
    elif defender_score >= 2.0:
        print("   ✅ Microsoft Defender: Tier 2 (Medium confidence) - INCLUDED if MSP/security pattern")
    else:
        print("   ❌ Microsoft Defender: Below Tier 2 threshold - EXCLUDED")
    
    print()
    print("🚀 ENHANCEMENT VALIDATION:")
    
    # Check if enhancements are working
    if lenovo_score >= 3.0 and defender_score >= 2.0:
        print("   ✅ SUCCESS: Enhanced scoring is working correctly!")
        print("   ✅ MSP and security content will now be included in reports")
        print("   ✅ Tiered relevance thresholds are effective")
        return True
    else:
        print("   ❌ NEEDS IMPROVEMENT: Enhanced scoring not sufficient")
        print("   ❌ Some valuable content may still be filtered out")
        return False

if __name__ == "__main__":
    success = test_enhanced_scoring()
    
    if success:
        print("\n🎉 ENHANCED SCORING SYSTEM: WORKING! 🎉")
        exit(0)
    else:
        print("\n🔧 ENHANCED SCORING SYSTEM: NEEDS REFINEMENT 🔧")
        exit(1)