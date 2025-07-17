#!/usr/bin/env python3
"""
End-to-end test to verify VCSP detection works completely
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(__file__))

from run_hybrid_system import load_config, fetch_content, analyze_content
from fetchers.reddit_fetcher import RedditFetcher

async def test_complete_pipeline():
    """Test the complete pipeline with VCSP-like content"""
    
    print("🧪 END-TO-END PIPELINE TEST")
    print("=" * 50)
    
    # 1. Test Configuration Loading
    print("📋 Step 1: Testing Configuration...")
    config = load_config()
    
    # 2. Test Fetcher Creation
    print("🔧 Step 2: Testing Fetcher...")
    fetcher = RedditFetcher(config)
    
    # 3. Test VCSP Content Scoring
    print("🎯 Step 3: Testing VCSP Content Scoring...")
    vcsp_content = {
        'title': 'VMware by Broadcom VCSP program is closing',
        'content': 'Thousands of partners are asked to shutdown business and migrate their clients smoothly to competition.',
        'score': 153,
        'num_comments': 56,
        'created_at': '2025-07-16T10:00:00',
        'url': 'https://reddit.com/r/sysadmin/test',
        'author': 'test_user',
        'subreddit': 'sysadmin'
    }
    
    # Simulate processing this content
    text = f"{vcsp_content['title']} {vcsp_content['content']}"
    relevance_score = fetcher._calculate_relevance_score(text)
    
    print(f"📈 VCSP Relevance Score: {relevance_score}")
    
    # 4. Test Selection Logic
    print("🔍 Step 4: Testing Selection Logic...")
    mock_items = [vcsp_content]
    selected = fetcher._select_items_with_engagement_override(mock_items, 20)
    
    print(f"✅ Items selected: {len(selected)}")
    if len(selected) > 0:
        print(f"📄 Selected item title: {selected[0]['title'][:50]}...")
    
    # 5. Test GPT Summarizer Integration
    print("🤖 Step 5: Testing GPT Summarizer...")
    try:
        from summarizer.gpt_summarizer_hybrid import HybridGPTSummarizer
        summarizer = HybridGPTSummarizer(debug=True)
        
        # Test confidence calculation
        insight_text = "VMware by Broadcom VCSP program is closing [reddit_1]"
        source_ids = ["reddit_1"]
        confidence = summarizer._calculate_insight_confidence(insight_text, source_ids)
        
        print(f"🎯 Confidence calculation:")
        print(f"   Score: {confidence['confidence_score']}")
        print(f"   Level: {confidence['confidence_level']}")
        print(f"   Percentage: {confidence['confidence_percentage']}%")
        print(f"   Factors: {confidence['confidence_factors']}")
        
    except Exception as e:
        print(f"❌ GPT Summarizer test failed: {e}")
    
    # 6. Overall Assessment
    print("\n📊 OVERALL ASSESSMENT:")
    
    success_criteria = [
        ("Keywords loaded", len(fetcher.urgency_keywords) >= 40),
        ("VCSP scores highly", relevance_score >= 15.0),
        ("Content gets selected", len(selected) > 0),
        ("Confidence calculation works", 'confidence_score' in confidence if 'confidence' in locals() else False)
    ]
    
    all_passed = True
    for criterion, passed in success_criteria:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}: {criterion}")
        if not passed:
            all_passed = False
    
    print(f"\n🎯 FINAL RESULT: {'✅ ALL SYSTEMS GO!' if all_passed else '❌ ISSUES DETECTED'}")
    
    return all_passed

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(test_complete_pipeline())
    sys.exit(0 if result else 1)