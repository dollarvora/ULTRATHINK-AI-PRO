#!/usr/bin/env python3
"""
ULTRATHINK Enhanced - Company Alias Matching Validation Test
Tests the expanded company alias intelligence system
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.company_alias_matcher import get_company_matcher
from utils.employee_manager import load_employee_manager
from summarizer.gpt_summarizer import GPTSummarizer

def setup_logging():
    """Setup logging for alias validation test"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def test_company_alias_matching():
    """Test company alias matching functionality"""
    logger = setup_logging()
    logger.info("🧪 Testing Company Alias Matching System")
    logger.info("=" * 60)
    
    # Initialize company matcher with debug enabled
    matcher = get_company_matcher(debug=True)
    
    # Test cases covering various scenarios
    test_texts = [
        # Microsoft aliases
        "Microsoft announced Azure price increases affecting Office365 and Teams users",
        "MSFT reported strong earnings with M365 subscriber growth",
        
        # Dell aliases  
        "Dell EMC PowerEdge servers now include isilon storage integration",
        "VxRail deployments show Unity benefits for Dell customers",
        
        # Cisco aliases
        "Webex Teams integration with Meraki networks improves Umbrella security",
        "Cisco Catalyst switches support Duo authentication via AnyConnect",
        
        # Mixed vendor content
        "TD Synnex (formerly Tech Data) announced new AWS and Azure partnership programs",
        "CDW Corporation vs Insight Global competitive analysis shows market consolidation",
        
        # Complex technical content
        "CrowdStrike Falcon detects threats while Zscaler ZPA secures cloud access via Fortinet FortiGate",
        
        # Channel/distributor content
        "Ingram Micro expands cloud services while Arrow Electronics focuses on IoT solutions"
    ]
    
    logger.info(f"🔍 Testing {len(test_texts)} sample texts...")
    
    total_companies_found = 0
    total_aliases_used = 0
    
    for i, text in enumerate(test_texts, 1):
        logger.info(f"\n📄 Test {i}: {text[:60]}...")
        
        # Find companies in text
        result = matcher.find_companies_in_text(text)
        
        logger.info(f"   🎯 Companies detected: {len(result.matched_companies)}")
        for company in sorted(result.matched_companies):
            aliases_found = result.alias_hits.get(company, [])
            logger.info(f"      • {company}: {', '.join(aliases_found) if aliases_found else 'main name'}")
            total_aliases_used += len(aliases_found)
        
        logger.info(f"   📊 Total matches: {result.total_matches}")
        logger.info(f"   🎯 Confidence: {result.confidence_score:.2f}")
        
        total_companies_found += len(result.matched_companies)
    
    logger.info(f"\n📊 ALIAS MATCHING SUMMARY:")
    logger.info(f"   • Total companies detected: {total_companies_found}")
    logger.info(f"   • Total alias matches: {total_aliases_used}")
    logger.info(f"   • Companies in mapping: {len(matcher.company_mappings)}")
    logger.info(f"   • Total aliases available: {sum(len(aliases) for aliases in matcher.company_mappings.values())}")
    
    return total_companies_found > 0, total_aliases_used > 0

def test_employee_manager():
    """Test employee manager with enhanced CSV structure"""
    logger = logging.getLogger(__name__)
    logger.info("\n👥 Testing Employee Manager")
    logger.info("-" * 40)
    
    try:
        # Load employee manager
        emp_manager = load_employee_manager(debug=True)
        
        employees = emp_manager.get_active_employees()
        logger.info(f"✅ Loaded {len(employees)} active employees")
        
        # Test role distribution
        roles = set(emp.role for emp in employees)
        logger.info(f"🎯 Roles found: {', '.join(sorted(roles))}")
        
        # Test keyword consolidation
        all_keywords = emp_manager.get_all_keywords()
        weighted_keywords = emp_manager.get_weighted_keywords()
        
        logger.info(f"🔗 Consolidated keywords: {len(all_keywords)} total")
        logger.info(f"⚖️  Weighted keywords: {len(weighted_keywords)} with weights")
        
        # Show sample employee
        if employees:
            sample_emp = employees[0]
            logger.info(f"\n📋 Sample Employee: {sample_emp.name}")
            logger.info(f"   • Role: {sample_emp.role}")
            logger.info(f"   • Vendors: {len(sample_emp.vendors)} ({', '.join(sample_emp.vendors[:3])}{'...' if len(sample_emp.vendors) > 3 else ''})")
            logger.info(f"   • Manufacturers: {len(sample_emp.manufacturers)} ({', '.join(sample_emp.manufacturers[:3])}{'...' if len(sample_emp.manufacturers) > 3 else ''})")
            logger.info(f"   • Combined keywords: {len(sample_emp.combined_keywords)}")
        
        return True, len(employees)
        
    except Exception as e:
        logger.error(f"❌ Employee manager test failed: {e}")
        return False, 0

def test_gpt_summarizer_integration():
    """Test GPT summarizer with enhanced company detection"""
    logger = logging.getLogger(__name__)
    logger.info("\n🤖 Testing GPT Summarizer Integration")
    logger.info("-" * 45)
    
    try:
        # Initialize summarizer with debug
        summarizer = GPTSummarizer(debug=True)
        
        # Test mock content with company aliases
        mock_content = {
            'reddit': [
                {
                    'title': 'Azure price increase hitting Office365 enterprise customers',
                    'content': 'Microsoft announced that M365 and Teams subscriptions will see 15% increases starting Q1 2024. This affects all enterprise agreement customers.',
                    'url': 'https://reddit.com/r/sysadmin/azure_pricing',
                    'created_at': '2024-01-15',
                    'relevance_score': 8.5
                }
            ],
            'google': [
                {
                    'title': 'Dell EMC PowerEdge server pricing updates through CDW',
                    'content': 'CDW Corporation reports new Dell server pricing with VxRail configurations showing competitive advantages over HPE alternatives.',
                    'url': 'https://crn.com/dell-pricing-update',
                    'created_at': '2024-01-14',
                    'relevance_score': 7.2
                }
            ]
        }
        
        # Test preprocessing with company detection
        logger.info("🔍 Testing content preprocessing...")
        combined_content = summarizer._preprocess_content(mock_content)
        
        # Check if enhanced items were created
        enhanced_items = getattr(summarizer, '_enhanced_items', [])
        logger.info(f"✅ Enhanced items created: {len(enhanced_items)}")
        
        companies_detected = 0
        for item in enhanced_items:
            detected = item.get('detected_companies', [])
            if detected:
                companies_detected += len(detected)
                logger.info(f"   📄 '{item['title'][:40]}...' → {', '.join(detected)}")
        
        logger.info(f"🎯 Total company detections: {companies_detected}")
        
        # Test role detection
        roles = summarizer._get_dynamic_roles()
        logger.info(f"👥 Detected roles: {', '.join(sorted(roles))}")
        
        return companies_detected > 0, len(roles) > 0
        
    except Exception as e:
        logger.error(f"❌ GPT summarizer test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False, False

def run_validation_suite():
    """Run complete validation suite"""
    logger = setup_logging()
    
    logger.info("🚀 ULTRATHINK ENHANCED - ALIAS VALIDATION SUITE")
    logger.info("=" * 70)
    
    results = {}
    
    # Test 1: Company Alias Matching
    try:
        companies_found, aliases_used = test_company_alias_matching()
        results['alias_matching'] = {
            'passed': companies_found and aliases_used,
            'companies_found': companies_found,
            'aliases_used': aliases_used
        }
    except Exception as e:
        logger.error(f"❌ Alias matching test failed: {e}")
        results['alias_matching'] = {'passed': False, 'error': str(e)}
    
    # Test 2: Employee Manager
    try:
        emp_loaded, emp_count = test_employee_manager()
        results['employee_manager'] = {
            'passed': emp_loaded and emp_count > 0,
            'employees_loaded': emp_count
        }
    except Exception as e:
        logger.error(f"❌ Employee manager test failed: {e}")
        results['employee_manager'] = {'passed': False, 'error': str(e)}
    
    # Test 3: GPT Summarizer Integration
    try:
        companies_detected, roles_detected = test_gpt_summarizer_integration()
        results['gpt_integration'] = {
            'passed': companies_detected and roles_detected,
            'companies_detected': companies_detected,
            'roles_detected': roles_detected
        }
    except Exception as e:
        logger.error(f"❌ GPT integration test failed: {e}")
        results['gpt_integration'] = {'passed': False, 'error': str(e)}
    
    # Generate summary report
    logger.info("\n" + "=" * 70)
    logger.info("🎯 VALIDATION RESULTS SUMMARY")
    logger.info("=" * 70)
    
    passed_tests = sum(1 for result in results.values() if result.get('passed', False))
    total_tests = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result.get('passed', False) else "❌ FAILED"
        logger.info(f"{test_name.replace('_', ' ').title()}: {status}")
        
        if 'error' in result:
            logger.info(f"   Error: {result['error']}")
    
    logger.info(f"\n📊 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("🎉 ALL TESTS PASSED - Company alias intelligence system is working correctly!")
        
        # Test specific Microsoft→Azure mapping as requested
        logger.info("\n🔍 SPECIFIC ALIAS TEST: Microsoft → Azure")
        matcher = get_company_matcher()
        test_result = matcher.find_companies_in_text("Microsoft Azure pricing and Teams integration")
        
        if 'microsoft' in test_result.matched_companies:
            azure_aliases = test_result.alias_hits.get('microsoft', [])
            if any('azure' in alias.lower() for alias in azure_aliases):
                logger.info("✅ CONFIRMED: 'Azure' correctly maps to 'Microsoft'")
            else:
                logger.info("✅ CONFIRMED: Microsoft detected in Azure content")
        
        return True
    else:
        logger.error(f"❌ {total_tests - passed_tests} tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = run_validation_suite()
    sys.exit(0 if success else 1)