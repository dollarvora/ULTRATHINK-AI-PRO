#!/usr/bin/env python3
"""
ULTRATHINK Intelligence Validation Test Suite
============================================

PURPOSE:
Tests the enhanced ULTRATHINK system against the three critical intelligence cases:
1. CNAPP Intelligence (target: 8.0+ scoring)
2. Broadcom/VMware Intelligence (target: 7.0+ scoring)  
3. Microsoft Partnership Intelligence (target: 8.0+ scoring)

VALIDATION APPROACH:
- Creates realistic test content for each intelligence type
- Tests against actual scoring algorithms in BaseFetcher
- Verifies enhanced keyword detection and scoring multipliers
- Confirms all intelligence gaps are resolved
- Tests integration and regression scenarios

Author: ULTRATHINK Intelligence Validation System
Version: 3.1.0
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import the enhanced scoring system
from config.config import get_config
from fetchers.base_fetcher import BaseFetcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestFetcher(BaseFetcher):
    """Test fetcher for validation"""
    
    def get_source_name(self) -> str:
        return "test_validation"
    
    async def fetch_raw(self) -> List[Dict[str, Any]]:
        return []

class IntelligenceValidationSuite:
    """Comprehensive validation suite for critical intelligence types"""
    
    def __init__(self):
        self.config = get_config(secure=False)
        self.fetcher = TestFetcher(self.config, test_mode=True)
        self.results = {
            'cnapp_intelligence': [],
            'broadcom_vmware_intelligence': [],
            'microsoft_partnership_intelligence': [],
            'integration_test': [],
            'regression_test': []
        }
        
    def create_cnapp_test_content(self) -> List[Dict[str, str]]:
        """Create realistic CNAPP intelligence test content"""
        return [
            {
                'title': 'CNAPP vendor pricing doubled overnight for cloud security platforms',
                'content': 'Major CNAPP vendors including Prisma Cloud and Wiz have doubled their cloud security platform pricing overnight, indicating a significant cost increase for security platforms. Container security pricing has increased by 100% across the board, with Kubernetes security pricing following suit. This represents a major shift in cloud native application protection platform costs.',
                'url': 'https://example.com/cnapp-pricing-increase',
                'expected_score': 9.0
            },
            {
                'title': 'Cloud workload protection pricing sees dramatic increase',
                'content': 'CWPP pricing has seen unprecedented increases as cloud workload protection platform vendors adjust their pricing models. DevSecOps pricing and shift-left security pricing have both increased significantly, with runtime security pricing following the same trend. This affects all cloud native security implementations.',
                'url': 'https://example.com/cwpp-pricing-increase',
                'expected_score': 8.5
            },
            {
                'title': 'Container security cost increase affects enterprise deployments',
                'content': 'Container image scanning pricing and container vulnerability scanning costs have increased substantially. Kubernetes security solutions are seeing similar price adjustments, making cloud native security more expensive for enterprises. API security pricing has also doubled in many cases.',
                'url': 'https://example.com/container-security-costs',
                'expected_score': 8.0
            },
            {
                'title': 'CSPM and CIEM pricing overhaul hits enterprises',
                'content': 'Cloud security posture management (CSPM) and cloud infrastructure entitlement management (CIEM) pricing has been overhauled, with significant cost increases across major vendors. Compliance management pricing and policy as code costs have also increased dramatically.',
                'url': 'https://example.com/cspm-ciem-pricing',
                'expected_score': 7.5
            }
        ]
    
    def create_broadcom_vmware_test_content(self) -> List[Dict[str, str]]:
        """Create realistic Broadcom/VMware intelligence test content"""
        return [
            {
                'title': 'Broadcom begins auditing organizations using VMware infrastructure',
                'content': 'Broadcom has begun conducting post-acquisition audits of organizations using VMware infrastructure, hinting at aggressive post-acquisition strategies. The company is auditing organizations and implementing license enforcement measures as part of their acquisition monetization strategy. This affects thousands of VMware customers globally.',
                'url': 'https://example.com/broadcom-vmware-audit',
                'expected_score': 9.0
            },
            {
                'title': 'VMware by Broadcom licensing overhaul creates compliance challenges',
                'content': 'Following the acquisition, Broadcom has implemented a licensing overhaul for VMware products, creating compliance challenges for enterprises. License enforcement and compliance audits are being conducted across the customer base. Organizations are facing mandatory migration to new licensing models.',
                'url': 'https://example.com/vmware-licensing-overhaul',
                'expected_score': 8.5
            },
            {
                'title': 'Post-acquisition monetization strategy affects partner programs',
                'content': 'Broadcom\'s post-acquisition monetization strategy is affecting VMware partner programs, with many facing program consolidation or shutdown. Partner program restructuring is underway as part of the acquisition integration process. This creates significant channel disruption.',
                'url': 'https://example.com/vmware-partner-program-changes',
                'expected_score': 8.0
            },
            {
                'title': 'VMware compliance review reveals licensing gaps',
                'content': 'Recent VMware compliance reviews and license audits have revealed significant licensing gaps in enterprise deployments. Broadcom is conducting comprehensive compliance audits as part of their acquisition integration strategy. This affects enterprise customers with complex VMware deployments.',
                'url': 'https://example.com/vmware-compliance-review',
                'expected_score': 7.5
            }
        ]
    
    def create_microsoft_partnership_test_content(self) -> List[Dict[str, str]]:
        """Create realistic Microsoft partnership intelligence test content"""
        return [
            {
                'title': 'Microsoft business relationship changes may reflect broader cloud service shifts',
                'content': 'Microsoft\'s business relationship changes with key partners may reflect broader shifts in cloud service partnerships. The company is modifying its channel program and partner program structure, affecting thousands of partners globally. These partnership changes indicate strategic shifts in go-to-market approaches.',
                'url': 'https://example.com/microsoft-partnership-changes',
                'expected_score': 8.5
            },
            {
                'title': 'Microsoft partner program restructure affects channel partners',
                'content': 'Microsoft is restructuring its partner program, affecting channel partners across multiple tiers. The Microsoft Partner Network (MPN) is undergoing significant changes, with new competency requirements and certification program updates. This affects cloud solution providers (CSPs) and managed service providers globally.',
                'url': 'https://example.com/microsoft-partner-restructure',
                'expected_score': 8.0
            },
            {
                'title': 'Azure partner program modifications create new opportunities',
                'content': 'Microsoft has announced modifications to its Azure partner program, creating new opportunities for cloud solution providers. The changes include updates to partner tier requirements and certification programs. Azure Expert MSP designations are being reviewed as part of the program changes.',
                'url': 'https://example.com/azure-partner-program-changes',
                'expected_score': 7.5
            },
            {
                'title': 'Microsoft channel strategy shift impacts resellers',
                'content': 'Microsoft\'s channel strategy shift is impacting resellers and distributors globally. The company is modifying its go-to-market approach and partner relationship model. This includes changes to the Cloud Solution Provider (CSP) program and partner benefits structure.',
                'url': 'https://example.com/microsoft-channel-strategy',
                'expected_score': 7.0
            }
        ]
    
    def create_integration_test_content(self) -> List[Dict[str, str]]:
        """Create content that combines all three intelligence types"""
        return [
            {
                'title': 'Enterprise security transformation drives costs across CNAPP, VMware, and Microsoft platforms',
                'content': 'Enterprise security transformation is driving significant cost increases across CNAPP platforms, VMware infrastructure, and Microsoft cloud services. CNAPP vendor pricing has doubled for cloud security platforms, while Broadcom begins auditing VMware organizations as part of post-acquisition strategy. Microsoft partnership changes are creating additional complexity for managed service providers dealing with these transitions.',
                'url': 'https://example.com/enterprise-security-transformation',
                'expected_score': 9.5
            },
            {
                'title': 'Cloud security market disruption affects vendor relationships',
                'content': 'Cloud security market disruption from CNAPP pricing increases, VMware licensing changes, and Microsoft partnership modifications is creating significant vendor relationship challenges. Container security costs have increased while Broadcom licensing overhaul affects VMware deployments. Microsoft channel strategy shifts are compounding these challenges for enterprises.',
                'url': 'https://example.com/cloud-security-market-disruption',
                'expected_score': 9.0
            }
        ]
    
    def create_regression_test_content(self) -> List[Dict[str, str]]:
        """Create non-intelligence content to ensure no regression"""
        return [
            {
                'title': 'Regular software update released',
                'content': 'A regular software update has been released with bug fixes and minor improvements. This maintenance release includes performance optimizations and documentation updates. No pricing changes or major feature additions are included.',
                'url': 'https://example.com/regular-update',
                'expected_score': 1.0
            },
            {
                'title': 'Company announces new office location',
                'content': 'Technology company announces new office location in downtown area. The expansion will accommodate growing workforce and provide better access to public transportation. No impact on product pricing or partner programs.',
                'url': 'https://example.com/office-announcement',
                'expected_score': 0.5
            },
            {
                'title': 'Employee recognition program launched',
                'content': 'New employee recognition program launched to celebrate outstanding contributions. The program includes quarterly awards and team building activities. This is an internal initiative with no external impact.',
                'url': 'https://example.com/employee-recognition',
                'expected_score': 0.0
            }
        ]
    
    def test_intelligence_type(self, intelligence_type: str, test_content: List[Dict[str, str]]) -> Dict[str, Any]:
        """Test a specific intelligence type"""
        logger.info(f"\n🔍 Testing {intelligence_type.upper()} Intelligence Detection")
        logger.info("=" * 60)
        
        results = {
            'intelligence_type': intelligence_type,
            'test_results': [],
            'summary': {
                'total_tests': len(test_content),
                'passed': 0,
                'failed': 0,
                'average_score': 0.0,
                'target_met': False
            }
        }
        
        # Set target scores based on intelligence type
        if intelligence_type == 'cnapp_intelligence':
            target_score = 8.0
        elif intelligence_type == 'broadcom_vmware_intelligence':
            target_score = 7.0
        elif intelligence_type == 'microsoft_partnership_intelligence':
            target_score = 8.0
        else:
            target_score = 7.0
        
        total_score = 0.0
        
        for i, content in enumerate(test_content, 1):
            # Test the scoring system
            text = f"{content['title']} {content['content']}"
            actual_score = self.fetcher._calculate_relevance_score(text)
            expected_score = content['expected_score']
            
            # Determine if test passed
            test_passed = actual_score >= target_score
            
            test_result = {
                'test_number': i,
                'title': content['title'][:80] + "..." if len(content['title']) > 80 else content['title'],
                'expected_score': expected_score,
                'actual_score': actual_score,
                'target_score': target_score,
                'passed': test_passed,
                'url': content['url']
            }
            
            results['test_results'].append(test_result)
            
            if test_passed:
                results['summary']['passed'] += 1
                status = "✅ PASSED"
            else:
                results['summary']['failed'] += 1
                status = "❌ FAILED"
            
            total_score += actual_score
            
            logger.info(f"Test {i}: {status}")
            logger.info(f"  📝 Content: {content['title'][:60]}...")
            logger.info(f"  🎯 Target: {target_score:.1f}+ | Actual: {actual_score:.1f} | Expected: {expected_score:.1f}")
            logger.info(f"  🔗 URL: {content['url']}")
            logger.info("")
        
        # Calculate summary statistics
        results['summary']['average_score'] = total_score / len(test_content)
        results['summary']['target_met'] = results['summary']['average_score'] >= target_score
        
        # Log summary
        logger.info(f"📊 {intelligence_type.upper()} INTELLIGENCE SUMMARY:")
        logger.info(f"  ✅ Tests Passed: {results['summary']['passed']}/{results['summary']['total_tests']}")
        logger.info(f"  ❌ Tests Failed: {results['summary']['failed']}/{results['summary']['total_tests']}")
        logger.info(f"  📈 Average Score: {results['summary']['average_score']:.1f}")
        logger.info(f"  🎯 Target Met: {'YES' if results['summary']['target_met'] else 'NO'} (target: {target_score:.1f}+)")
        
        return results
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation of all intelligence types"""
        logger.info("🚀 ULTRATHINK Intelligence Validation Suite")
        logger.info("=" * 60)
        logger.info("Testing enhanced system against three critical intelligence cases:")
        logger.info("1. CNAPP Intelligence (target: 8.0+ scoring)")
        logger.info("2. Broadcom/VMware Intelligence (target: 7.0+ scoring)")
        logger.info("3. Microsoft Partnership Intelligence (target: 8.0+ scoring)")
        logger.info("=" * 60)
        
        # Test 1: CNAPP Intelligence
        cnapp_content = self.create_cnapp_test_content()
        cnapp_results = self.test_intelligence_type('cnapp_intelligence', cnapp_content)
        self.results['cnapp_intelligence'] = cnapp_results
        
        # Test 2: Broadcom/VMware Intelligence
        broadcom_content = self.create_broadcom_vmware_test_content()
        broadcom_results = self.test_intelligence_type('broadcom_vmware_intelligence', broadcom_content)
        self.results['broadcom_vmware_intelligence'] = broadcom_results
        
        # Test 3: Microsoft Partnership Intelligence
        microsoft_content = self.create_microsoft_partnership_test_content()
        microsoft_results = self.test_intelligence_type('microsoft_partnership_intelligence', microsoft_content)
        self.results['microsoft_partnership_intelligence'] = microsoft_results
        
        # Test 4: Integration Test
        logger.info("\n🔄 Integration Test - Combined Intelligence Types")
        logger.info("=" * 60)
        integration_content = self.create_integration_test_content()
        integration_results = self.test_intelligence_type('integration_test', integration_content)
        self.results['integration_test'] = integration_results
        
        # Test 5: Regression Test
        logger.info("\n🔙 Regression Test - Non-Intelligence Content")
        logger.info("=" * 60)
        regression_content = self.create_regression_test_content()
        regression_results = self.test_intelligence_type('regression_test', regression_content)
        self.results['regression_test'] = regression_results
        
        return self.generate_final_report()
    
    def generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        logger.info("\n📋 COMPREHENSIVE VALIDATION REPORT")
        logger.info("=" * 60)
        
        # Overall summary
        total_tests = 0
        total_passed = 0
        total_failed = 0
        intelligence_gaps_resolved = 0
        
        report = {
            'validation_timestamp': datetime.now().isoformat(),
            'system_version': '3.1.0',
            'intelligence_types_tested': 5,
            'detailed_results': self.results,
            'summary': {},
            'recommendations': []
        }
        
        # Analyze each intelligence type
        for intelligence_type, results in self.results.items():
            total_tests += results['summary']['total_tests']
            total_passed += results['summary']['passed']
            total_failed += results['summary']['failed']
            
            # Check if intelligence gaps are resolved
            if intelligence_type in ['cnapp_intelligence', 'broadcom_vmware_intelligence', 'microsoft_partnership_intelligence']:
                if results['summary']['target_met']:
                    intelligence_gaps_resolved += 1
                    status = "✅ RESOLVED"
                else:
                    status = "❌ NOT RESOLVED"
                
                logger.info(f"{intelligence_type.upper()}: {status}")
                logger.info(f"  📊 Score: {results['summary']['average_score']:.1f}")
                logger.info(f"  🎯 Target: {'MET' if results['summary']['target_met'] else 'NOT MET'}")
                logger.info(f"  ✅ Passed: {results['summary']['passed']}/{results['summary']['total_tests']}")
            else:
                logger.info(f"{intelligence_type.upper()}: {results['summary']['average_score']:.1f} avg score")
        
        # Overall assessment
        report['summary'] = {
            'total_tests': total_tests,
            'total_passed': total_passed,
            'total_failed': total_failed,
            'pass_rate': (total_passed / total_tests) * 100 if total_tests > 0 else 0,
            'intelligence_gaps_resolved': intelligence_gaps_resolved,
            'critical_intelligence_types': 3,
            'system_validation': 'PASSED' if intelligence_gaps_resolved == 3 else 'FAILED'
        }
        
        # Final verdict
        logger.info("\n🎯 FINAL VALIDATION RESULTS")
        logger.info("=" * 60)
        logger.info(f"📊 Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {total_passed}")
        logger.info(f"❌ Failed: {total_failed}")
        logger.info(f"📈 Pass Rate: {report['summary']['pass_rate']:.1f}%")
        logger.info(f"🔧 Intelligence Gaps Resolved: {intelligence_gaps_resolved}/3")
        logger.info(f"🎯 System Validation: {report['summary']['system_validation']}")
        
        # Recommendations
        if intelligence_gaps_resolved < 3:
            logger.info("\n⚠️  RECOMMENDATIONS:")
            if not self.results['cnapp_intelligence']['summary']['target_met']:
                report['recommendations'].append("Enhance CNAPP intelligence keywords and scoring multipliers")
            if not self.results['broadcom_vmware_intelligence']['summary']['target_met']:
                report['recommendations'].append("Strengthen Broadcom/VMware M&A intelligence detection")
            if not self.results['microsoft_partnership_intelligence']['summary']['target_met']:
                report['recommendations'].append("Improve Microsoft partnership intelligence scoring")
        else:
            logger.info("\n✅ All critical intelligence gaps have been resolved!")
            report['recommendations'].append("System is performing optimally for all intelligence types")
        
        return report
    
    def save_results(self, results: Dict[str, Any]) -> None:
        """Save validation results to file"""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"intelligence_validation_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\n💾 Validation results saved to: {output_file}")

def main():
    """Main validation function"""
    try:
        # Initialize validation suite
        validator = IntelligenceValidationSuite()
        
        # Run comprehensive validation
        results = validator.run_comprehensive_validation()
        
        # Save results
        validator.save_results(results)
        
        # Return exit code based on validation results
        if results['summary']['system_validation'] == 'PASSED':
            logger.info("\n🎉 VALIDATION COMPLETED SUCCESSFULLY!")
            return 0
        else:
            logger.error("\n❌ VALIDATION FAILED - Intelligence gaps remain")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Validation suite failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())