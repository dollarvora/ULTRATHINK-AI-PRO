#!/usr/bin/env python3
"""
Test the selection algorithm fix for ULTRATHINK-AI-PRO
Validates that high relevance pricing intelligence beats high engagement generic content
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from summarizer.gpt_summarizer_hybrid import HybridGPTSummarizer

def test_lenovo_vs_nvidia_selection():
    """Test the exact scenario: Lenovo servers (10.0 relevance) vs Nvidia CEO (1.5 relevance)"""
    
    print("🧪 SELECTION ALGORITHM FIX TEST")
    print("=" * 60)
    print("Testing: Lenovo servers (10.0 relevance) vs Nvidia CEO (1.5 relevance)")
    print("")
    
    # Create test data that mimics the exact scenario
    test_items = [
        {
            "title": "Nvidia CEO Jensen Huang sells another $37 million worth of stock",
            "content": "CEO stock sale news content",
            "score": 287,  # High Reddit upvotes
            "num_comments": 29,  # High engagement
            "relevance_score": 1.5,  # LOW relevance for pricing intelligence
            "url": "https://reddit.com/r/nvidia_stock"
        },
        {
            "title": "What's your experience with Lenovo (servers + storage)?",
            "content": "MSPs discussing Lenovo servers and storage solutions, profit margins, procurement decisions",
            "score": 5,  # Low Reddit upvotes
            "num_comments": 8,  # Low engagement
            "relevance_score": 10.0,  # HIGH relevance for pricing intelligence
            "url": "https://reddit.com/r/msp"
        },
        {
            "title": "Microsoft Defender adoption in small businesses",
            "content": "Small businesses adopting Microsoft Defender, pricing discussions, enterprise security",
            "score": 15,  # Medium Reddit upvotes
            "num_comments": 12,  # Medium engagement
            "relevance_score": 9.5,  # HIGH relevance for pricing intelligence
            "url": "https://reddit.com/r/smallbusiness"
        },
        {
            "title": "AI has its place, but it can be junk food for an IT Professional",
            "content": "General IT discussion about AI",
            "score": 129,  # High Reddit upvotes
            "num_comments": 156,  # Very high engagement
            "relevance_score": 1.0,  # LOW relevance for pricing intelligence
            "url": "https://reddit.com/r/sysadmin"
        }
    ]
    
    # Test the fixed selection algorithm
    summarizer = HybridGPTSummarizer(debug=True)
    
    print("🔍 BEFORE FIX (Expected behavior):")
    print("   - Nvidia CEO would be selected first (high engagement)")
    print("   - Lenovo servers would be filtered out (low engagement)")
    print("   - Result: Pricing intelligence missed!")
    print("")
    
    print("🛠️ TESTING FIXED ALGORITHM:")
    selected_items = summarizer._select_items_with_engagement_override(test_items, 4)
    
    print("")
    print("🎯 SELECTION RESULTS:")
    
    # Check if Lenovo made it into selection
    lenovo_selected = any("lenovo" in item.get('title', '').lower() for item in selected_items)
    nvidia_selected = any("nvidia" in item.get('title', '').lower() for item in selected_items)
    microsoft_selected = any("microsoft" in item.get('title', '').lower() for item in selected_items)
    
    print(f"   ✅ Lenovo servers selected: {lenovo_selected}")
    print(f"   ✅ Microsoft Defender selected: {microsoft_selected}")
    print(f"   ⚠️  Nvidia CEO selected: {nvidia_selected}")
    
    # Analyze selection order
    print("")
    print("📊 SELECTION ORDER ANALYSIS:")
    for i, item in enumerate(selected_items):
        title = item.get('title', '')[:50]
        relevance = item.get('relevance_score', 0)
        engagement = item.get('score', 0) + item.get('num_comments', 0)
        print(f"   {i+1}. {title}... (Relevance: {relevance:.1f}, Engagement: {engagement})")
    
    # Test results
    print("")
    print("🧪 FIX VALIDATION:")
    
    success = True
    
    # Test 1: High relevance pricing intelligence should be selected
    if not lenovo_selected:
        print("   ❌ FAIL: Lenovo servers (10.0 relevance) not selected")
        success = False
    else:
        print("   ✅ PASS: Lenovo servers (10.0 relevance) selected")
    
    if not microsoft_selected:
        print("   ❌ FAIL: Microsoft Defender (9.5 relevance) not selected")
        success = False
    else:
        print("   ✅ PASS: Microsoft Defender (9.5 relevance) selected")
    
    # Test 2: High relevance should beat high engagement
    if selected_items:
        first_item_relevance = selected_items[0].get('relevance_score', 0)
        if first_item_relevance >= 7.0:
            print("   ✅ PASS: High relevance item selected first")
        else:
            print(f"   ❌ FAIL: Low relevance item selected first (relevance: {first_item_relevance:.1f})")
            success = False
    
    # Test 3: Pricing intelligence should be prioritized over generic content
    pricing_count = sum(1 for item in selected_items if item.get('relevance_score', 0) >= 7.0)
    generic_count = sum(1 for item in selected_items if item.get('relevance_score', 0) < 3.0)
    
    if pricing_count > generic_count:
        print(f"   ✅ PASS: More pricing intelligence ({pricing_count}) than generic content ({generic_count})")
    else:
        print(f"   ❌ FAIL: More generic content ({generic_count}) than pricing intelligence ({pricing_count})")
        success = False
    
    print("")
    if success:
        print("🎉 SUCCESS: Selection algorithm fix working correctly!")
        print("   - High relevance pricing intelligence is now prioritized")
        print("   - Lenovo servers (10.0) beats Nvidia CEO (1.5)")
        print("   - System will capture the insights that matter for pricing teams")
    else:
        print("❌ FAILURE: Selection algorithm fix needs more work")
        print("   - High relevance items still being filtered out")
        print("   - Generic content still beating pricing intelligence")
    
    return success

if __name__ == "__main__":
    success = test_lenovo_vs_nvidia_selection()
    
    if success:
        print("\n🚀 ULTRATHINK-AI-PRO SELECTION ALGORITHM: FIXED! 🚀")
        exit(0)
    else:
        print("\n🔧 ULTRATHINK-AI-PRO SELECTION ALGORITHM: NEEDS MORE WORK 🔧")
        exit(1)