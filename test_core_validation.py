#!/usr/bin/env python3
"""
ULTRATHINK Enhanced - Core Validation Test (No OpenAI required)
Tests company alias matching and employee management without GPT integration
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def setup_logging():
    """Setup logging for validation test"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def test_company_alias_matching():
    """Test company alias matching functionality"""
    logger = setup_logging()
    logger.info("🧪 Testing Company Alias Matching System")
    logger.info("=" * 60)
    
    try:
        from utils.company_alias_matcher import get_company_matcher
        
        # Initialize company matcher with debug enabled
        matcher = get_company_matcher(debug=False)
        
        logger.info(f"✅ Company matcher initialized with {len(matcher.company_mappings)} companies")
        logger.info(f"📊 Total aliases: {sum(len(aliases) for aliases in matcher.company_mappings.values())}")
        
        # Test specific Microsoft → Azure mapping as requested
        test_texts = [
            "Microsoft announced Azure price increases affecting Office365 users",
            "Teams integration with M365 shows strong adoption",
            "Dell PowerEdge servers with VMware vSphere deployment",
            "Cisco Meraki and Umbrella security integration",
            "TD Synnex (formerly Tech Data) AWS partnership"
        ]
        
        logger.info(f"\n🔍 Testing {len(test_texts)} sample texts for alias detection:")
        
        total_detections = 0
        microsoft_azure_test_passed = False
        
        for i, text in enumerate(test_texts, 1):
            logger.info(f"\n📄 Test {i}: {text}")
            
            # Find companies in text
            result = matcher.find_companies_in_text(text)
            
            logger.info(f"   🎯 Companies detected: {', '.join(sorted(result.matched_companies)) if result.matched_companies else 'None'}")
            
            for company in sorted(result.matched_companies):
                aliases_found = result.alias_hits.get(company, [])
                logger.info(f"      • {company}: {', '.join(aliases_found) if aliases_found else 'main name used'}")
                
                # Check for Microsoft→Azure mapping
                if company == 'microsoft' and any('azure' in alias.lower() for alias in aliases_found):
                    microsoft_azure_test_passed = True
                    logger.info(f"      ✅ CONFIRMED: Azure alias correctly mapped to Microsoft")
            
            total_detections += len(result.matched_companies)
            logger.info(f"   📊 Confidence: {result.confidence_score:.2f}")
        
        logger.info(f"\n📊 ALIAS MATCHING SUMMARY:")
        logger.info(f"   • Total company detections: {total_detections}")
        logger.info(f"   • Microsoft→Azure mapping: {'✅ PASSED' if microsoft_azure_test_passed else '❌ FAILED'}")
        
        return total_detections > 0 and microsoft_azure_test_passed
        
    except Exception as e:
        logger.error(f"❌ Company alias matching failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_employee_manager():
    """Test employee manager with enhanced CSV structure"""
    logger = logging.getLogger(__name__)
    logger.info("\n👥 Testing Employee Manager")
    logger.info("-" * 40)
    
    try:
        from utils.employee_manager import load_employee_manager
        
        # Load employee manager with absolute path
        csv_path = "/Users/Dollar/Documents/ultrathink-enhanced/config/employees.csv"
        emp_manager = load_employee_manager(csv_path, debug=False)
        
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
        
        # Find John Smith specifically for testing
        john_smith = emp_manager.get_employee_by_email('dollarvora@icloud.com')
        if john_smith and john_smith.name == 'John Smith':
            logger.info(f"\n📋 John Smith Analysis:")
            logger.info(f"   • Role: {john_smith.role}")
            logger.info(f"   • Vendors: {john_smith.vendors}")
            logger.info(f"   • Manufacturers: {john_smith.manufacturers}")
            logger.info(f"   • Distributors: {john_smith.distributors}")
            logger.info(f"   • Topics: {john_smith.topics}")
            logger.info(f"   • Combined keywords: {len(john_smith.combined_keywords)} total")
            logger.info(f"   • Sample keywords: {', '.join(john_smith.combined_keywords[:10])}...")
            
            # Test alias expansion
            original_count = len(john_smith.vendors + john_smith.manufacturers + john_smith.distributors + john_smith.topics)
            expanded_count = len(john_smith.combined_keywords)
            expansion_ratio = expanded_count / original_count if original_count > 0 else 0
            
            logger.info(f"   • Expansion: {original_count} → {expanded_count} (ratio: {expansion_ratio:.2f}x)")
            
            # Check if microsoft→azure expansion happened
            has_microsoft = 'microsoft' in john_smith.combined_keywords
            has_azure = 'azure' in john_smith.combined_keywords
            
            logger.info(f"   • Microsoft expansion test: microsoft={has_microsoft}, azure={has_azure}")
            
            if has_microsoft and has_azure:
                logger.info("   ✅ CONFIRMED: Microsoft aliases (including Azure) expanded correctly")
                return True, len(employees), True
            else:
                logger.warning("   ⚠️  Microsoft alias expansion may not be working as expected")
                return True, len(employees), False
        else:
            logger.warning("   ⚠️  John Smith not found in employee data")
            return True, len(employees), False
        
    except Exception as e:
        logger.error(f"❌ Employee manager test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False, 0, False

def test_role_context_system():
    """Test role-specific context configuration"""
    logger = logging.getLogger(__name__)
    logger.info("\n🎯 Testing Role Context System")
    logger.info("-" * 35)
    
    try:
        from utils.employee_manager import load_employee_manager
        
        csv_path = "/Users/Dollar/Documents/ultrathink-enhanced/config/employees.csv"
        emp_manager = load_employee_manager(csv_path)
        
        # Test role contexts for known roles
        test_roles = ['pricing_analyst', 'procurement_manager', 'bi_strategy', 'unknown_role']
        
        for role in test_roles:
            context = emp_manager.get_role_context(role)
            logger.info(f"🎭 {role}:")
            logger.info(f"   • Focus: {context['focus']}")
            logger.info(f"   • Style: {context['output_style']}")
            logger.info(f"   • Metrics: {', '.join(context['key_metrics'])}")
        
        # Specifically test John Smith's role context
        john_context = emp_manager.get_role_context('pricing_analyst')
        logger.info(f"\n📊 John Smith (pricing_analyst) will receive summaries focused on:")
        logger.info(f"   • {john_context['focus']}")
        logger.info(f"   • Output style: {john_context['output_style']}")
        logger.info(f"   • Key metrics: {', '.join(john_context['key_metrics'])}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Role context test failed: {e}")
        return False

def run_core_validation():
    """Run core validation without GPT integration"""
    logger = setup_logging()
    
    logger.info("🚀 ULTRATHINK ENHANCED - CORE VALIDATION SUITE")
    logger.info("=" * 70)
    
    results = {}
    
    # Test 1: Company Alias Matching
    try:
        alias_success = test_company_alias_matching()
        results['alias_matching'] = {'passed': alias_success}
    except Exception as e:
        logger.error(f"❌ Alias matching test failed: {e}")
        results['alias_matching'] = {'passed': False, 'error': str(e)}
    
    # Test 2: Employee Manager
    try:
        emp_loaded, emp_count, alias_expansion = test_employee_manager()
        results['employee_manager'] = {
            'passed': emp_loaded and emp_count > 0 and alias_expansion,
            'employees_loaded': emp_count,
            'alias_expansion_working': alias_expansion
        }
    except Exception as e:
        logger.error(f"❌ Employee manager test failed: {e}")
        results['employee_manager'] = {'passed': False, 'error': str(e)}
    
    # Test 3: Role Context System
    try:
        role_context_success = test_role_context_system()
        results['role_context'] = {'passed': role_context_success}
    except Exception as e:
        logger.error(f"❌ Role context test failed: {e}")
        results['role_context'] = {'passed': False, 'error': str(e)}
    
    # Generate summary report
    logger.info("\n" + "=" * 70)
    logger.info("🎯 CORE VALIDATION RESULTS")
    logger.info("=" * 70)
    
    passed_tests = sum(1 for result in results.values() if result.get('passed', False))
    total_tests = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result.get('passed', False) else "❌ FAILED"
        logger.info(f"{test_name.replace('_', ' ').title()}: {status}")
        
        if 'error' in result:
            logger.info(f"   Error: {result['error']}")
        
        # Additional details
        if test_name == 'employee_manager':
            logger.info(f"   Employees loaded: {result.get('employees_loaded', 0)}")
            logger.info(f"   Alias expansion: {'✅' if result.get('alias_expansion_working') else '❌'}")
    
    logger.info(f"\n📊 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("🎉 ALL CORE TESTS PASSED!")
        logger.info("\n🔍 KEY CONFIRMATIONS:")
        logger.info("✅ CSV parsing with structured vendor/manufacturer/distributor/topics")
        logger.info("✅ Company alias matching (Microsoft → Azure, etc.)")
        logger.info("✅ Employee keyword consolidation and expansion")
        logger.info("✅ Role-specific context configuration")
        logger.info("✅ John Smith (pricing_analyst) ready for margin-focused summaries")
        
        logger.info("\n📧 Ready for email delivery to: dollarvora@icloud.com")
        logger.info("🎯 Summary will be role-specific for pricing_analyst with vendor-aware content")
        
        return True
    else:
        logger.error(f"❌ {total_tests - passed_tests} tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = run_core_validation()
    sys.exit(0 if success else 1)