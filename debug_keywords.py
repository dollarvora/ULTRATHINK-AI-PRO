#!/usr/bin/env python3
"""
Debug what keywords are actually loaded
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from run_hybrid_system import load_config

def debug_keywords():
    """Debug what keywords are in the config"""
    
    config = load_config()
    
    print("🔧 Debugging Keyword Loading")
    print("=" * 40)
    
    print("📊 Config structure:")
    print(f"- config['keywords'] keys: {list(config['keywords'].keys())}")
    
    if 'pricing' in config['keywords']:
        print(f"- pricing keywords: {config['keywords']['pricing']}")
    
    if 'urgency_indicators' in config['keywords']:
        print(f"- urgency_indicators: {config['keywords']['urgency_indicators']}")
    
    if 'vendors' in config:
        print(f"- vendors structure: {type(config['vendors'])}")
        if isinstance(config['vendors'], dict):
            print(f"- vendor categories: {list(config['vendors'].keys())}")
    
    # Test VCSP keywords specifically
    vcsp_text = "vmware by broadcom vcsp program is closing thousands of partners asked to shutdown migrate clients smoothly"
    
    print(f"\n🎯 Testing VCSP text: '{vcsp_text[:50]}...'")
    
    # Check for pricing keywords
    pricing_matches = []
    for kw in config['keywords'].get('pricing', []):
        if kw.lower() in vcsp_text:
            pricing_matches.append(kw)
    
    # Check for urgency keywords
    urgency_matches = []
    for kw in config['keywords'].get('urgency_indicators', []):
        if kw.lower() in vcsp_text:
            urgency_matches.append(kw)
    
    print(f"💰 Pricing keyword matches: {pricing_matches}")
    print(f"🚨 Urgency keyword matches: {urgency_matches}")
    
    # Check business critical keywords we added
    business_critical = [
        'program shutdown', 'program closure', 'partner program', 'vcsp', 'vcp',
        'channel program', 'reseller program', 'distributor program', 'var program',
        'csp program', 'certification program', 'program discontinuation',
        'migrate clients', 'migrate their clients', 'smoothly migrate',
        'migrate to competition', 'migrate to competitors', 'client migration',
        'business shutdown', 'shutdown business', 'asked to shutdown',
        'program is closing', 'program closing', 'thousands of partners',
        'broadcom', 'vmware by broadcom'
    ]
    
    critical_matches = []
    for kw in business_critical:
        if kw.lower() in vcsp_text:
            critical_matches.append(kw)
    
    print(f"⚠️ Business critical matches: {critical_matches}")

if __name__ == "__main__":
    debug_keywords()