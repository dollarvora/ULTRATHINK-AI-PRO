#!/usr/bin/env python3
"""
Quick test to verify scoring fix is working
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from run_hybrid_system import load_config
from fetchers.reddit_fetcher import RedditFetcher

def test_scoring():
    """Test that scoring algorithm can load keywords correctly"""
    
    # Load config
    config = load_config()
    
    print("🔧 Testing Scoring Algorithm Fix")
    print("=" * 40)
    
    # Create fetcher
    fetcher = RedditFetcher(config)
    
    # Test keyword loading
    print(f"📊 Pricing keywords loaded: {len(fetcher.keywords)}")
    print(f"🚨 Urgency keywords loaded: {len(fetcher.urgency_keywords)}")
    print(f"🏢 Vendors loaded: {len(fetcher.vendors)}")
    
    if len(fetcher.keywords) > 0:
        print(f"✅ Sample pricing keywords: {fetcher.keywords[:5]}")
    else:
        print("❌ No pricing keywords loaded!")
        
    if len(fetcher.urgency_keywords) > 0:
        print(f"✅ Sample urgency keywords: {fetcher.urgency_keywords[:5]}")
    else:
        print("❌ No urgency keywords loaded!")
        
    if len(fetcher.vendors) > 0:
        print(f"✅ Sample vendors: {fetcher.vendors[:5]}")
    else:
        print("❌ No vendors loaded!")
    
    # Test VCSP scoring
    print("\n🎯 Testing VCSP Post Scoring:")
    vcsp_text = "VMware by Broadcom VCSP program is closing. Thousands of partners are asked to shutdown business and migrate their clients smoothly to competition."
    score = fetcher._calculate_relevance_score(vcsp_text)
    print(f"📈 VCSP post score: {score}")
    
    if score > 0:
        print("✅ Scoring is working!")
        return True
    else:
        print("❌ Scoring still broken!")
        return False

if __name__ == "__main__":
    success = test_scoring()
    sys.exit(0 if success else 1)