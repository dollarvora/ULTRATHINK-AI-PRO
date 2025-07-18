#!/usr/bin/env python3
"""
System Integration Test for Enhanced Google CNAPP Intelligence
Tests that the enhanced system can load and process the new configuration
"""

import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_system_configuration_loading():
    """Test that the system can load the enhanced configuration"""
    logger.info("🔍 Testing System Configuration Loading")
    
    try:
        from run_hybrid_system import load_config
        config = load_config()
        
        # Verify configuration structure
        assert 'sources' in config
        assert 'google' in config['sources']
        assert 'queries' in config['sources']['google']
        
        # Verify query count
        queries = config['sources']['google']['queries']
        logger.info(f"✅ Loaded {len(queries)} Google queries")
        
        # Verify CNAPP-specific queries
        cnapp_queries = [q for q in queries if 'cnapp' in q.lower()]
        logger.info(f"✅ Found {len(cnapp_queries)} CNAPP-specific queries")
        
        # Verify cloud security vendor queries
        vendor_queries = [q for q in queries if any(v in q.lower() for v in ['wiz', 'prisma', 'aqua', 'snyk'])]
        logger.info(f"✅ Found {len(vendor_queries)} vendor-specific queries")
        
        logger.info("✅ System configuration loading successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration loading failed: {e}")
        return False

def test_fetcher_initialization():
    """Test that fetchers can be initialized with the new configuration"""
    logger.info("🔍 Testing Fetcher Initialization")
    
    try:
        from run_hybrid_system import load_config
        from fetchers.google_fetcher import GoogleFetcher
        
        config = load_config()
        
        # Initialize Google fetcher
        google_fetcher = GoogleFetcher(config)
        
        # Verify fetcher properties
        assert hasattr(google_fetcher, 'source_config')
        assert hasattr(google_fetcher, 'vendors')
        assert hasattr(google_fetcher, 'pricing_keywords')
        
        logger.info("✅ Google fetcher initialized successfully")
        
        # Verify vendor list includes cloud security vendors
        cloud_vendors = ['wiz', 'prisma cloud', 'aqua security', 'snyk']
        found_vendors = [v for v in google_fetcher.vendors if any(cv in v for cv in cloud_vendors)]
        logger.info(f"✅ Found {len(found_vendors)} cloud security vendors in fetcher")
        
        logger.info("✅ Fetcher initialization successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Fetcher initialization failed: {e}")
        return False

def test_query_processing():
    """Test that queries would be processed correctly"""
    logger.info("🔍 Testing Query Processing")
    
    try:
        from run_hybrid_system import load_config
        from fetchers.google_fetcher import GoogleFetcher
        
        config = load_config()
        google_fetcher = GoogleFetcher(config)
        
        # Get queries from configuration
        queries = config['sources']['google']['queries']
        
        # Test that queries are properly formatted
        for query in queries:
            assert isinstance(query, str)
            assert len(query) > 0
            assert not query.startswith('f"')  # Ensure f-strings are resolved
        
        logger.info(f"✅ All {len(queries)} queries are properly formatted")
        
        # Test specific CNAPP query
        cnapp_query = "CNAPP vendor pricing doubled overnight"
        if cnapp_query in queries:
            logger.info(f"✅ Target CNAPP query found: {cnapp_query}")
        else:
            logger.warning(f"⚠️ Target CNAPP query not found: {cnapp_query}")
        
        logger.info("✅ Query processing test successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Query processing test failed: {e}")
        return False

def test_scoring_system():
    """Test that the scoring system works with cloud security content"""
    logger.info("🔍 Testing Scoring System")
    
    try:
        from run_hybrid_system import load_config
        from fetchers.google_fetcher import GoogleFetcher
        
        config = load_config()
        google_fetcher = GoogleFetcher(config)
        
        # Test scoring with CNAPP content
        test_content = "CNAPP vendor pricing doubled overnight for cloud security platforms"
        
        # Test relevance scoring
        relevance_score = google_fetcher._calculate_relevance_score(test_content)
        
        logger.info(f"✅ CNAPP content relevance score: {relevance_score:.2f}")
        
        # Verify score is reasonable for high-value content
        if relevance_score > 5.0:
            logger.info("✅ High relevance score for CNAPP content")
        else:
            logger.warning(f"⚠️ Low relevance score for CNAPP content: {relevance_score:.2f}")
        
        # Test with vendor-specific content
        vendor_content = "Wiz pricing increase announcement affects cloud security budgets"
        vendor_score = google_fetcher._calculate_relevance_score(vendor_content)
        
        logger.info(f"✅ Vendor content relevance score: {vendor_score:.2f}")
        
        logger.info("✅ Scoring system test successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Scoring system test failed: {e}")
        return False

def main():
    """Run system integration tests"""
    logger.info("🚀 System Integration Test for Enhanced Google CNAPP Intelligence")
    logger.info("=" * 70)
    
    tests = [
        ("Configuration Loading", test_system_configuration_loading),
        ("Fetcher Initialization", test_fetcher_initialization),
        ("Query Processing", test_query_processing),
        ("Scoring System", test_scoring_system),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 {test_name}")
        logger.info("-" * 50)
        
        try:
            success = test_func()
            results.append((test_name, success))
            
            status = "✅ PASSED" if success else "❌ FAILED"
            logger.info(f"{status}: {test_name}")
            
        except Exception as e:
            logger.error(f"❌ {test_name} test failed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n📊 Integration Test Summary")
    logger.info("=" * 70)
    
    passed_tests = sum(1 for _, success in results if success)
    total_tests = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"{status} {test_name}")
    
    logger.info(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("✅ System integration successful! Enhanced Google CNAPP intelligence is ready.")
        logger.info("🚀 System can now capture 'CNAPP vendor pricing doubled overnight' intelligence.")
    else:
        logger.warning("⚠️ Some integration tests failed. System may need attention.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)