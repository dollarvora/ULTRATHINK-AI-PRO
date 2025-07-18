#!/usr/bin/env python3
"""
Google CNAPP Intelligence Validation Test
Tests that the new Google queries can capture the specific CNAPP pricing intelligence that was previously missed
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_cnapp_pricing_doubled_query_matching():
    """Test that queries specifically target 'CNAPP vendor pricing doubled overnight' intelligence"""
    logger.info("🔍 Testing CNAPP Pricing Doubled Query Matching")
    
    from run_hybrid_system import load_config
    config = load_config()
    
    # Get Google queries
    queries = config['sources']['google']['queries']
    
    # Target intelligence we want to capture
    target_intelligence = "CNAPP vendor pricing doubled overnight"
    
    # Find queries that would match this type of intelligence
    matching_queries = []
    
    for query in queries:
        query_lower = query.lower()
        target_lower = target_intelligence.lower()
        
        # Check if query contains key terms from target intelligence
        key_terms = ['cnapp', 'vendor', 'pricing', 'doubled', 'overnight']
        matches = sum(1 for term in key_terms if term in query_lower)
        
        if matches >= 2:  # At least 2 key terms match
            matching_queries.append((query, matches))
    
    # Sort by number of matches
    matching_queries.sort(key=lambda x: x[1], reverse=True)
    
    logger.info(f"🎯 Found {len(matching_queries)} queries that could capture CNAPP pricing doubled intelligence:")
    for query, matches in matching_queries:
        logger.info(f"  📍 {query} (matches: {matches}/5)")
    
    # Check if we have the specific query
    specific_query = "CNAPP vendor pricing doubled overnight"
    has_specific_query = any(specific_query.lower() in query.lower() for query in queries)
    
    logger.info(f"🔍 Has specific query: {'✅' if has_specific_query else '❌'}")
    
    return len(matching_queries) >= 3, len(matching_queries)

def test_cloud_security_coverage():
    """Test comprehensive cloud security pricing coverage"""
    logger.info("🔍 Testing Cloud Security Coverage")
    
    from run_hybrid_system import load_config
    config = load_config()
    
    # Get Google queries
    queries = config['sources']['google']['queries']
    
    # Define comprehensive cloud security categories
    security_categories = {
        'CNAPP': ['cnapp', 'cloud native application protection platform'],
        'CSPM': ['cspm', 'cloud security posture management'],
        'CWPP': ['cwpp', 'cloud workload protection'],
        'CIEM': ['ciem', 'cloud infrastructure entitlement management'],
        'DevSecOps': ['devsecops', 'shift-left security'],
        'Container Security': ['container security', 'kubernetes security'],
        'Runtime Security': ['runtime security', 'vulnerability management'],
        'Cloud Security Platform': ['cloud security platform', 'cloud security pricing']
    }
    
    # Check coverage for each category
    category_coverage = {}
    
    for category, terms in security_categories.items():
        matching_queries = []
        
        for query in queries:
            query_lower = query.lower()
            if any(term in query_lower for term in terms):
                matching_queries.append(query)
        
        category_coverage[category] = len(matching_queries)
        
        logger.info(f"📊 {category}: {len(matching_queries)} queries")
        for query in matching_queries:
            logger.info(f"  ✅ {query}")
    
    # Calculate overall coverage
    total_categories = len(security_categories)
    covered_categories = sum(1 for count in category_coverage.values() if count > 0)
    coverage_percentage = (covered_categories / total_categories) * 100
    
    logger.info(f"🎯 Overall Coverage: {coverage_percentage:.1f}% ({covered_categories}/{total_categories})")
    
    return coverage_percentage >= 75.0, coverage_percentage

def test_vendor_specific_intelligence():
    """Test vendor-specific pricing intelligence capture"""
    logger.info("🔍 Testing Vendor-Specific Intelligence")
    
    from run_hybrid_system import load_config
    config = load_config()
    
    # Get Google queries
    queries = config['sources']['google']['queries']
    
    # Major cloud security vendors
    vendors = [
        'Wiz', 'Prisma Cloud', 'Aqua Security', 'Snyk', 'Lacework', 'Orca Security',
        'CrowdStrike', 'Palo Alto Networks', 'Zscaler', 'SentinelOne'
    ]
    
    # Pricing intelligence terms
    pricing_terms = ['pricing', 'price', 'cost', 'increase', 'change', 'overhaul', 'doubled']
    
    # Check vendor-specific pricing queries
    vendor_queries = {}
    
    for vendor in vendors:
        matching_queries = []
        
        for query in queries:
            query_lower = query.lower()
            vendor_lower = vendor.lower()
            
            # Check if query contains vendor and pricing terms
            if vendor_lower in query_lower and any(term in query_lower for term in pricing_terms):
                matching_queries.append(query)
        
        vendor_queries[vendor] = matching_queries
        
        if matching_queries:
            logger.info(f"🏢 {vendor}: {len(matching_queries)} queries")
            for query in matching_queries:
                logger.info(f"  💰 {query}")
        else:
            logger.info(f"🏢 {vendor}: No specific queries")
    
    # Calculate vendor coverage
    covered_vendors = sum(1 for queries in vendor_queries.values() if queries)
    vendor_coverage = (covered_vendors / len(vendors)) * 100
    
    logger.info(f"🎯 Vendor Coverage: {vendor_coverage:.1f}% ({covered_vendors}/{len(vendors)})")
    
    return vendor_coverage >= 60.0, vendor_coverage

def test_pricing_intelligence_terms():
    """Test that queries contain comprehensive pricing intelligence terms"""
    logger.info("🔍 Testing Pricing Intelligence Terms")
    
    from run_hybrid_system import load_config
    config = load_config()
    
    # Get Google queries
    queries = config['sources']['google']['queries']
    
    # Critical pricing intelligence terms
    pricing_terms = {
        'price_changes': ['increase', 'change', 'overhaul', 'doubled', 'adjustment'],
        'pricing_models': ['pricing', 'cost', 'subscription', 'license', 'fee'],
        'market_impact': ['announcement', 'update', 'policy', 'strategy', 'model'],
        'urgency_indicators': ['overnight', 'sudden', 'immediate', 'urgent', 'breaking']
    }
    
    # Analyze term coverage
    term_coverage = {}
    
    for category, terms in pricing_terms.items():
        matching_queries = []
        
        for query in queries:
            query_lower = query.lower()
            if any(term in query_lower for term in terms):
                matching_queries.append(query)
        
        term_coverage[category] = len(matching_queries)
        
        logger.info(f"📊 {category}: {len(matching_queries)} queries")
        
        # Show sample queries for each category
        for i, query in enumerate(matching_queries[:3]):  # Show first 3
            logger.info(f"  📍 {query}")
        
        if len(matching_queries) > 3:
            logger.info(f"  ... and {len(matching_queries) - 3} more")
    
    # Calculate overall term coverage
    total_categories = len(pricing_terms)
    covered_categories = sum(1 for count in term_coverage.values() if count > 0)
    coverage_percentage = (covered_categories / total_categories) * 100
    
    logger.info(f"🎯 Pricing Term Coverage: {coverage_percentage:.1f}% ({covered_categories}/{total_categories})")
    
    return coverage_percentage >= 75.0, coverage_percentage

def simulate_cnapp_intelligence_matching():
    """Simulate how the new queries would match actual CNAPP intelligence"""
    logger.info("🔍 Simulating CNAPP Intelligence Matching")
    
    from run_hybrid_system import load_config
    config = load_config()
    
    # Simulate realistic CNAPP intelligence scenarios
    intelligence_scenarios = [
        "CNAPP vendor pricing doubled overnight for cloud security platforms",
        "Wiz announces major pricing increase for cloud security platform",
        "Prisma Cloud pricing overhaul impacts enterprise security budgets",
        "Container security pricing sees unprecedented increases across vendors",
        "CSPM pricing changes affect cloud security posture management costs",
        "Aqua Security increases pricing for cloud workload protection platform",
        "DevSecOps pricing models shift as security shifts left",
        "Lacework pricing adjustment for cloud security posture management",
        "Snyk pricing change affects container security implementations",
        "CWPP pricing increase hits cloud workload protection budgets"
    ]
    
    # Get Google queries
    queries = config['sources']['google']['queries']
    
    # Test how many scenarios would be captured
    captured_scenarios = 0
    
    for scenario in intelligence_scenarios:
        scenario_lower = scenario.lower()
        matching_queries = []
        
        for query in queries:
            query_lower = query.lower()
            
            # Extract key terms from both scenario and query
            scenario_terms = set(scenario_lower.split())
            query_terms = set(query_lower.split())
            
            # Calculate term overlap
            overlap = len(scenario_terms & query_terms)
            
            if overlap >= 2:  # At least 2 terms overlap
                matching_queries.append((query, overlap))
        
        if matching_queries:
            captured_scenarios += 1
            # Sort by overlap score
            matching_queries.sort(key=lambda x: x[1], reverse=True)
            logger.info(f"✅ Scenario: {scenario}")
            logger.info(f"   Best match: {matching_queries[0][0]} (overlap: {matching_queries[0][1]})")
        else:
            logger.info(f"❌ Scenario: {scenario}")
    
    capture_rate = (captured_scenarios / len(intelligence_scenarios)) * 100
    logger.info(f"🎯 Intelligence Capture Rate: {capture_rate:.1f}% ({captured_scenarios}/{len(intelligence_scenarios)})")
    
    return capture_rate >= 70.0, capture_rate

def main():
    """Run comprehensive CNAPP intelligence validation"""
    logger.info("🚀 Google CNAPP Intelligence Validation Test")
    logger.info("=" * 60)
    logger.info("Mission: Validate that new Google queries can capture CNAPP pricing intelligence")
    logger.info("Target: Successfully collect 'CNAPP vendor pricing doubled overnight' intelligence")
    logger.info("")
    
    tests = [
        ("CNAPP Pricing Doubled Query Matching", test_cnapp_pricing_doubled_query_matching),
        ("Cloud Security Coverage", test_cloud_security_coverage),
        ("Vendor-Specific Intelligence", test_vendor_specific_intelligence),
        ("Pricing Intelligence Terms", test_pricing_intelligence_terms),
        ("CNAPP Intelligence Matching Simulation", simulate_cnapp_intelligence_matching),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 {test_name}")
        logger.info("-" * 50)
        
        try:
            passed, score = test_func()
            results.append((test_name, passed, score))
            
            status = "✅ PASSED" if passed else "❌ FAILED"
            logger.info(f"{status}: {test_name} - Score: {score:.1f}")
            
        except Exception as e:
            logger.error(f"❌ {test_name} test failed: {e}")
            results.append((test_name, False, 0.0))
    
    # Summary
    logger.info("\n📊 Validation Summary")
    logger.info("=" * 60)
    
    passed_tests = sum(1 for _, passed, _ in results if passed)
    total_tests = len(results)
    overall_score = sum(score for _, passed, score in results if passed) / total_tests
    
    for test_name, passed, score in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{status} {test_name}: {score:.1f}")
    
    logger.info(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
    logger.info(f"📈 Average Score: {overall_score:.1f}")
    
    if passed_tests == total_tests:
        logger.info("✅ Mission Accomplished: Google queries can capture CNAPP pricing intelligence!")
        logger.info("🚀 Previously missed 'CNAPP vendor pricing doubled overnight' intelligence will now be captured")
    else:
        logger.warning("⚠️ Some validation tests failed. Review query configuration.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)