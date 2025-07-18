#!/usr/bin/env python3
"""
Comprehensive validation script for Enhanced Vendor Intelligence System
Tests 95% accuracy target for company/vendor identification
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.company_alias_matcher import CompanyAliasMatcher
from typing import Dict, List, Tuple
import json

def test_vendor_intelligence_accuracy():
    """Test comprehensive vendor intelligence accuracy"""
    
    # Initialize enhanced matcher
    matcher = CompanyAliasMatcher(debug=True)
    
    # Test scenarios with expected results
    test_scenarios = [
        # 2024-2025 Emerging Vendors
        {
            "text": "Anthropic's Claude AI competes with OpenAI's ChatGPT and GPT-4 models",
            "expected_vendors": {"anthropic", "openai"},
            "category": "AI/ML Vendors"
        },
        {
            "text": "Wiz cloud security platform acquired by Google for $32 billion",
            "expected_vendors": {"wiz", "google cloud"},
            "category": "Cybersecurity Acquisitions"
        },
        {
            "text": "NVIDIA H100 GPUs power CoreWeave's AI cloud infrastructure",
            "expected_vendors": {"nvidia", "coreweave"},
            "category": "AI Infrastructure"
        },
        {
            "text": "Sophos acquired Secureworks for $859 million to expand XDR capabilities",
            "expected_vendors": {"sophos", "secureworks"},
            "category": "Security M&A"
        },
        {
            "text": "ServiceNow acquired Moveworks for $2.85 billion to enhance AI automation",
            "expected_vendors": {"servicenow", "moveworks"},
            "category": "Enterprise AI"
        },
        
        # Traditional Vendors with M&A Context
        {
            "text": "Microsoft Office 365 pricing increased 15% affecting Enterprise customers",
            "expected_vendors": {"microsoft"},
            "category": "Traditional SaaS"
        },
        {
            "text": "VMware vSphere licensing costs surge following Broadcom acquisition",
            "expected_vendors": {"vmware", "broadcom"},
            "category": "Infrastructure M&A"
        },
        {
            "text": "CrowdStrike Falcon EDR platform adds new threat detection capabilities",
            "expected_vendors": {"crowdstrike"},
            "category": "Cybersecurity"
        },
        {
            "text": "AWS EC2 instances see regional pricing adjustments across availability zones",
            "expected_vendors": {"aws"},
            "category": "Cloud Infrastructure"
        },
        {
            "text": "Cisco Meraki wireless solutions integrate with Umbrella cloud security",
            "expected_vendors": {"cisco"},
            "category": "Network Security"
        },
        
        # Distributors and Channel Partners
        {
            "text": "TD Synnex reports strong quarterly results from Tech Data integration",
            "expected_vendors": {"td synnex"},
            "category": "IT Distribution"
        },
        {
            "text": "Ingram Micro expands cloud marketplace with new vendor partnerships",
            "expected_vendors": {"ingram micro"},
            "category": "Cloud Distribution"
        },
        {
            "text": "CDW Government wins major federal contract for Microsoft Enterprise Agreement",
            "expected_vendors": {"cdw", "microsoft"},
            "category": "Government Channel"
        },
        {
            "text": "SHI International partners with Jamf for enterprise mobile device management",
            "expected_vendors": {"shi", "jamf"},
            "category": "Enterprise Mobility"
        },
        
        # Storage and Infrastructure
        {
            "text": "Pure Storage FlashArray performance improvements announced at Pure//Accelerate",
            "expected_vendors": {"pure storage"},
            "category": "Enterprise Storage"
        },
        {
            "text": "Lenovo acquiring Infinidat for $1.6 billion to expand storage portfolio",
            "expected_vendors": {"lenovo", "infinidat"},
            "category": "Storage M&A"
        },
        {
            "text": "Nutanix Cloud Platform integrates with HPE GreenLake edge services",
            "expected_vendors": {"nutanix", "hpe"},
            "category": "Hybrid Cloud"
        },
        {
            "text": "NetApp ONTAP cloud storage supports AWS, Azure, and Google Cloud",
            "expected_vendors": {"netapp", "aws", "microsoft", "google cloud"},
            "category": "Multi-Cloud Storage"
        },
        
        # Security and Compliance
        {
            "text": "Zscaler Zero Trust Exchange platform adds new DLP capabilities",
            "expected_vendors": {"zscaler"},
            "category": "Zero Trust Security"
        },
        {
            "text": "Okta Identity Cloud integrates with Microsoft Azure Active Directory",
            "expected_vendors": {"okta", "microsoft"},
            "category": "Identity Management"
        },
        {
            "text": "Splunk Enterprise Security correlates threat intelligence from multiple sources",
            "expected_vendors": {"splunk"},
            "category": "Security Analytics"
        },
        
        # Complex Multi-Vendor Scenarios
        {
            "text": "Enterprise customers migrate from VMware vSphere to Microsoft Hyper-V following Broadcom acquisition pricing changes",
            "expected_vendors": {"vmware", "microsoft", "broadcom"},
            "category": "Migration Scenario"
        },
        {
            "text": "Cisco Catalyst switches integrate with Fortinet FortiGate firewalls and CrowdStrike Falcon endpoints",
            "expected_vendors": {"cisco", "fortinet", "crowdstrike"},
            "category": "Multi-Vendor Security"
        },
        {
            "text": "Oracle Cloud Infrastructure competes with AWS and Microsoft Azure for enterprise workloads",
            "expected_vendors": {"oracle", "aws", "microsoft"},
            "category": "Cloud Competition"
        }
    ]
    
    # Run tests and collect results
    results = []
    total_tests = 0
    total_correct = 0
    
    print("🔍 VENDOR INTELLIGENCE ACCURACY VALIDATION")
    print("=" * 60)
    
    for scenario in test_scenarios:
        total_tests += 1
        text = scenario["text"]
        expected = scenario["expected_vendors"]
        category = scenario["category"]
        
        # Run detection
        result = matcher.find_companies_in_text(text)
        detected = result.matched_companies
        
        # Calculate accuracy
        intersection = detected.intersection(expected)
        precision = len(intersection) / len(detected) if detected else 0
        recall = len(intersection) / len(expected) if expected else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Determine if test passed (high recall is most important for vendor intelligence)
        test_passed = recall >= 0.8  # 80% recall threshold
        if test_passed:
            total_correct += 1
        
        # Store result
        test_result = {
            "category": category,
            "text_preview": text[:80] + "..." if len(text) > 80 else text,
            "expected": sorted(expected),
            "detected": sorted(detected),
            "intersection": sorted(intersection),
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "confidence": result.confidence_score,
            "passed": test_passed,
            "acquisition_mappings": result.acquisition_mappings
        }
        results.append(test_result)
        
        # Print result
        status = "✅ PASS" if test_passed else "❌ FAIL"
        print(f"{status} {category}")
        print(f"   Expected: {expected}")
        print(f"   Detected: {detected}")
        print(f"   Recall: {recall:.1%}, Precision: {precision:.1%}, F1: {f1_score:.1%}")
        print(f"   Confidence: {result.confidence_score:.1%}")
        if result.acquisition_mappings:
            print(f"   M&A Intel: {result.acquisition_mappings}")
        print()
    
    # Calculate overall accuracy
    overall_accuracy = total_correct / total_tests
    
    print("📊 OVERALL RESULTS")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Tests Passed: {total_correct}")
    print(f"Overall Accuracy: {overall_accuracy:.1%}")
    
    # Category analysis
    category_results = {}
    for result in results:
        category = result["category"]
        if category not in category_results:
            category_results[category] = {"passed": 0, "total": 0}
        category_results[category]["total"] += 1
        if result["passed"]:
            category_results[category]["passed"] += 1
    
    print("\n🏷️ CATEGORY ANALYSIS")
    print("=" * 60)
    for category, stats in sorted(category_results.items()):
        accuracy = stats["passed"] / stats["total"]
        print(f"{category}: {accuracy:.1%} ({stats['passed']}/{stats['total']})")
    
    # Database statistics
    print("\n📈 DATABASE STATISTICS")
    print("=" * 60)
    print(f"Total Companies: {len(matcher.company_mappings)}")
    print(f"Total Aliases: {sum(len(aliases) for aliases in matcher.company_mappings.values())}")
    print(f"Acquisition Mappings: {len(matcher.acquisition_mappings)}")
    
    # Top performing categories
    avg_f1_by_category = {}
    for result in results:
        category = result["category"]
        if category not in avg_f1_by_category:
            avg_f1_by_category[category] = []
        avg_f1_by_category[category].append(result["f1_score"])
    
    print("\n🏆 TOP PERFORMING CATEGORIES (by F1 Score)")
    print("=" * 60)
    for category, f1_scores in sorted(avg_f1_by_category.items(), 
                                     key=lambda x: sum(x[1])/len(x[1]), reverse=True):
        avg_f1 = sum(f1_scores) / len(f1_scores)
        print(f"{category}: {avg_f1:.1%}")
    
    # Success criteria
    print("\n🎯 SUCCESS CRITERIA")
    print("=" * 60)
    print(f"Target Accuracy: 95%")
    print(f"Achieved Accuracy: {overall_accuracy:.1%}")
    
    if overall_accuracy >= 0.95:
        print("🎉 SUCCESS: 95% accuracy target achieved!")
    elif overall_accuracy >= 0.90:
        print("🔶 GOOD: 90%+ accuracy achieved, approaching target")
    elif overall_accuracy >= 0.85:
        print("🔸 ACCEPTABLE: 85%+ accuracy achieved, needs improvement")
    else:
        print("🔴 NEEDS WORK: Below 85% accuracy, requires optimization")
    
    # Save detailed results
    with open("vendor_intelligence_validation_results.json", "w") as f:
        json.dump({
            "overall_accuracy": overall_accuracy,
            "total_tests": total_tests,
            "total_correct": total_correct,
            "category_results": category_results,
            "detailed_results": results,
            "database_stats": {
                "total_companies": len(matcher.company_mappings),
                "total_aliases": sum(len(aliases) for aliases in matcher.company_mappings.values()),
                "acquisition_mappings": len(matcher.acquisition_mappings)
            }
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: vendor_intelligence_validation_results.json")
    
    return overall_accuracy >= 0.95

if __name__ == "__main__":
    success = test_vendor_intelligence_accuracy()
    sys.exit(0 if success else 1)