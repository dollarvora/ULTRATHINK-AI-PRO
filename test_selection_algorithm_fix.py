#!/usr/bin/env python3
"""
ULTRATHINK Selection Algorithm Fix Validation
===========================================

PURPOSE:
Tests the selection algorithm fix to ensure high-relevance intelligence content
is properly prioritized over high-engagement but low-relevance content.

SPECIFIC TESTS:
1. High-relevance intelligence content should be selected over viral memes
2. Business-critical intelligence should override pure engagement metrics
3. Vendor-specific intelligence should be prioritized appropriately
4. MSP/Security intelligence should get proper scoring boosts

VALIDATION CRITERIA:
- High-relevance intelligence (8.0+ score) should rank above viral content
- Business-critical keywords should provide sufficient scoring boosts
- MSP context multipliers should be properly applied
- Partnership intelligence boosts should be functional

Author: ULTRATHINK Selection Algorithm Validation
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
from summarizer.gpt_summarizer_hybrid import HybridGPTSummarizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestFetcher(BaseFetcher):
    """Test fetcher for selection algorithm validation"""
    
    def get_source_name(self) -> str:
        return "test_selection"
    
    async def fetch_raw(self) -> List[Dict[str, Any]]:
        return []

class SelectionAlgorithmValidator:
    """Validates the selection algorithm fix for intelligence prioritization"""
    
    def __init__(self):
        self.config = get_config(secure=False)
        self.fetcher = TestFetcher(self.config, test_mode=True)
        self.summarizer = HybridGPTSummarizer()
        
    def create_mixed_content_test_data(self) -> List[Dict[str, Any]]:
        """Create mixed content with high-engagement/low-relevance and high-relevance/low-engagement"""
        return [
            # High-engagement but low-relevance content (viral memes, jokes)
            {
                'title': 'Hilarious IT meme goes viral',
                'content': 'This funny meme about turning IT off and on again has gone viral on social media. Everyone is sharing it and laughing about their IT experiences. Very relatable content for IT professionals.',
                'url': 'https://example.com/viral-meme',
                'score': 500,  # High Reddit score
                'num_comments': 200,  # High engagement
                'expected_relevance': 0.5,  # Very low relevance
                'content_type': 'viral_low_relevance'
            },
            {
                'title': 'Popular joke about Windows updates',
                'content': 'Another popular joke about Windows updates that everyone finds funny. Lots of upvotes and comments from people sharing their own Windows update horror stories.',
                'url': 'https://example.com/windows-joke',
                'score': 800,  # Very high Reddit score
                'num_comments': 350,  # Very high engagement
                'expected_relevance': 0.3,  # Very low relevance
                'content_type': 'viral_low_relevance'
            },
            
            # High-relevance but low-engagement intelligence content
            {
                'title': 'CNAPP vendor pricing doubled overnight for cloud security platforms',
                'content': 'Major CNAPP vendors including Prisma Cloud and Wiz have doubled their cloud security platform pricing overnight, indicating a significant cost increase for security platforms. Container security pricing has increased by 100% across the board.',
                'url': 'https://example.com/cnapp-pricing-intelligence',
                'score': 15,  # Low Reddit score
                'num_comments': 3,  # Low engagement
                'expected_relevance': 9.0,  # Very high relevance
                'content_type': 'high_relevance_intelligence'
            },
            {
                'title': 'Broadcom begins auditing organizations using VMware infrastructure',
                'content': 'Broadcom has begun conducting post-acquisition audits of organizations using VMware infrastructure, hinting at aggressive post-acquisition strategies. The company is auditing organizations and implementing license enforcement measures.',
                'url': 'https://example.com/broadcom-vmware-intelligence',
                'score': 8,  # Very low Reddit score
                'num_comments': 1,  # Very low engagement
                'expected_relevance': 9.5,  # Very high relevance
                'content_type': 'high_relevance_intelligence'
            },
            {
                'title': 'Microsoft business relationship changes may reflect broader cloud service shifts',
                'content': 'Microsoft\'s business relationship changes with key partners may reflect broader shifts in cloud service partnerships. The company is modifying its channel program and partner program structure, affecting thousands of partners globally.',
                'url': 'https://example.com/microsoft-partnership-intelligence',
                'score': 12,  # Low Reddit score
                'num_comments': 2,  # Low engagement
                'expected_relevance': 8.5,  # Very high relevance
                'content_type': 'high_relevance_intelligence'
            },
            
            # MSP content with moderate engagement
            {
                'title': 'What\'s your experience with Lenovo servers for MSP clients?',
                'content': 'Looking for feedback on Lenovo servers for our MSP clients. We\'re considering switching from Dell and want to hear about pricing, reliability, and support experiences from other MSPs.',
                'url': 'https://example.com/msp-lenovo-experience',
                'score': 45,  # Moderate Reddit score
                'num_comments': 12,  # Moderate engagement
                'expected_relevance': 7.0,  # High relevance with MSP boost
                'content_type': 'msp_intelligence'
            },
            {
                'title': 'Microsoft Defender makes me suffer - performance issues in MSP environment',
                'content': 'Microsoft Defender is causing performance issues across our MSP client base. Anyone else experiencing similar problems? Looking for alternatives or solutions.',
                'url': 'https://example.com/defender-msp-issues',
                'score': 35,  # Moderate Reddit score
                'num_comments': 8,  # Moderate engagement
                'expected_relevance': 6.5,  # High relevance with security boost
                'content_type': 'security_intelligence'
            },
            
            # Business-critical content with low engagement
            {
                'title': 'VMware partner program shutdown affects thousands of partners',
                'content': 'VMware is shutting down its partner program, affecting thousands of partners globally. Partners are being asked to migrate their clients to alternative solutions. This represents a major channel disruption.',
                'url': 'https://example.com/vmware-program-shutdown',
                'score': 20,  # Low Reddit score
                'num_comments': 5,  # Low engagement
                'expected_relevance': 8.0,  # Very high relevance (business critical)
                'content_type': 'business_critical_intelligence'
            }
        ]
    
    def test_scoring_system(self) -> Dict[str, Any]:
        """Test the scoring system on mixed content"""
        logger.info("🔍 Testing Enhanced Scoring System")
        logger.info("=" * 60)
        
        test_data = self.create_mixed_content_test_data()
        scoring_results = []
        
        for item in test_data:
            # Calculate actual relevance score
            text = f"{item['title']} {item['content']}"
            actual_score = self.fetcher._calculate_relevance_score(text)
            
            scoring_result = {
                'title': item['title'],
                'content_type': item['content_type'],
                'reddit_score': item['score'],
                'num_comments': item['num_comments'],
                'expected_relevance': item['expected_relevance'],
                'actual_relevance': actual_score,
                'score_difference': actual_score - item['expected_relevance'],
                'url': item['url']
            }
            scoring_results.append(scoring_result)
            
            # Log the result
            logger.info(f"📝 {item['title'][:50]}...")
            logger.info(f"  🎯 Type: {item['content_type']}")
            logger.info(f"  📊 Reddit: {item['score']}, Comments: {item['num_comments']}")
            logger.info(f"  🔍 Expected: {item['expected_relevance']:.1f}, Actual: {actual_score:.1f}")
            logger.info(f"  {'✅' if actual_score >= item['expected_relevance'] * 0.8 else '❌'} Score Match")
            logger.info("")
        
        return {
            'test_type': 'scoring_system',
            'results': scoring_results,
            'summary': self._analyze_scoring_results(scoring_results)
        }
    
    def test_selection_algorithm(self) -> Dict[str, Any]:
        """Test the selection algorithm with mixed content"""
        logger.info("🔍 Testing Selection Algorithm Fix")
        logger.info("=" * 60)
        
        test_data = self.create_mixed_content_test_data()
        
        # Convert to format expected by selection algorithm
        items_with_scores = []
        for item in test_data:
            text = f"{item['title']} {item['content']}"
            relevance_score = self.fetcher._calculate_relevance_score(text)
            
            processed_item = {
                'title': item['title'],
                'content': item['content'],
                'url': item['url'],
                'score': item['score'],
                'num_comments': item['num_comments'],
                'relevance_score': relevance_score,
                'content_type': item['content_type']
            }
            items_with_scores.append(processed_item)
        
        # Test selection algorithm
        selected_items = self.summarizer._select_items_with_engagement_override(items_with_scores, 50)
        
        # Analyze selection results
        selection_analysis = self._analyze_selection_results(selected_items, items_with_scores)
        
        logger.info("📊 Selection Algorithm Results:")
        logger.info(f"  📦 Total Items: {len(items_with_scores)}")
        logger.info(f"  ✅ Selected Items: {len(selected_items)}")
        logger.info(f"  🎯 High-Relevance Intelligence Selected: {selection_analysis['high_relevance_selected']}")
        logger.info(f"  🔥 Viral Low-Relevance Selected: {selection_analysis['viral_low_relevance_selected']}")
        logger.info(f"  💼 Business-Critical Selected: {selection_analysis['business_critical_selected']}")
        logger.info(f"  🏢 MSP Intelligence Selected: {selection_analysis['msp_intelligence_selected']}")
        
        return {
            'test_type': 'selection_algorithm',
            'selected_items': selected_items,
            'analysis': selection_analysis
        }
    
    def test_prioritization_logic(self) -> Dict[str, Any]:
        """Test that intelligence content is properly prioritized"""
        logger.info("🔍 Testing Intelligence Prioritization Logic")
        logger.info("=" * 60)
        
        test_data = self.create_mixed_content_test_data()
        
        # Calculate hybrid scores for each item
        prioritization_results = []
        for item in test_data:
            text = f"{item['title']} {item['content']}"
            relevance_score = self.fetcher._calculate_relevance_score(text)
            
            # Calculate hybrid score (similar to selection algorithm)
            engagement_score = item['score'] + item['num_comments']
            normalized_engagement = min(engagement_score / 50.0, 10.0)
            hybrid_score = (relevance_score * 0.7) + (normalized_engagement * 0.3)
            
            prioritization_result = {
                'title': item['title'],
                'content_type': item['content_type'],
                'relevance_score': relevance_score,
                'engagement_score': engagement_score,
                'normalized_engagement': normalized_engagement,
                'hybrid_score': hybrid_score,
                'should_be_prioritized': item['content_type'] in ['high_relevance_intelligence', 'business_critical_intelligence']
            }
            prioritization_results.append(prioritization_result)
        
        # Sort by hybrid score
        prioritization_results.sort(key=lambda x: x['hybrid_score'], reverse=True)
        
        # Analyze prioritization
        prioritization_analysis = self._analyze_prioritization_results(prioritization_results)
        
        logger.info("📊 Prioritization Results:")
        for i, result in enumerate(prioritization_results[:5], 1):
            logger.info(f"  {i}. {result['title'][:50]}...")
            logger.info(f"     🎯 Type: {result['content_type']}")
            logger.info(f"     📊 Hybrid: {result['hybrid_score']:.1f} (R:{result['relevance_score']:.1f}, E:{result['normalized_engagement']:.1f})")
        
        return {
            'test_type': 'prioritization_logic',
            'results': prioritization_results,
            'analysis': prioritization_analysis
        }
    
    def _analyze_scoring_results(self, scoring_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze scoring system results"""
        intelligence_items = [r for r in scoring_results if 'intelligence' in r['content_type']]
        viral_items = [r for r in scoring_results if 'viral' in r['content_type']]
        
        avg_intelligence_score = sum(r['actual_relevance'] for r in intelligence_items) / len(intelligence_items)
        avg_viral_score = sum(r['actual_relevance'] for r in viral_items) / len(viral_items)
        
        return {
            'intelligence_items': len(intelligence_items),
            'viral_items': len(viral_items),
            'avg_intelligence_score': avg_intelligence_score,
            'avg_viral_score': avg_viral_score,
            'scoring_fix_working': avg_intelligence_score > avg_viral_score * 5  # Intelligence should score much higher
        }
    
    def _analyze_selection_results(self, selected_items: List[Dict[str, Any]], all_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze selection algorithm results"""
        # Count types in selected items
        high_relevance_selected = len([item for item in selected_items if item.get('content_type') == 'high_relevance_intelligence'])
        viral_low_relevance_selected = len([item for item in selected_items if item.get('content_type') == 'viral_low_relevance'])
        business_critical_selected = len([item for item in selected_items if item.get('content_type') == 'business_critical_intelligence'])
        msp_intelligence_selected = len([item for item in selected_items if item.get('content_type') == 'msp_intelligence'])
        
        # Count types in all items
        total_high_relevance = len([item for item in all_items if item.get('content_type') == 'high_relevance_intelligence'])
        total_viral_low_relevance = len([item for item in all_items if item.get('content_type') == 'viral_low_relevance'])
        
        return {
            'high_relevance_selected': high_relevance_selected,
            'viral_low_relevance_selected': viral_low_relevance_selected,
            'business_critical_selected': business_critical_selected,
            'msp_intelligence_selected': msp_intelligence_selected,
            'total_high_relevance': total_high_relevance,
            'total_viral_low_relevance': total_viral_low_relevance,
            'selection_fix_working': high_relevance_selected > viral_low_relevance_selected
        }
    
    def _analyze_prioritization_results(self, prioritization_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze prioritization logic results"""
        # Check if intelligence content is in top positions
        top_5 = prioritization_results[:5]
        intelligence_in_top_5 = len([r for r in top_5 if r['should_be_prioritized']])
        
        # Check if viral content is properly de-prioritized
        viral_positions = [i for i, r in enumerate(prioritization_results) if r['content_type'] == 'viral_low_relevance']
        avg_viral_position = sum(viral_positions) / len(viral_positions) if viral_positions else 0
        
        return {
            'intelligence_in_top_5': intelligence_in_top_5,
            'total_top_5_slots': 5,
            'avg_viral_position': avg_viral_position,
            'total_items': len(prioritization_results),
            'prioritization_fix_working': intelligence_in_top_5 >= 3 and avg_viral_position > 3
        }
    
    def run_comprehensive_selection_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation of selection algorithm fix"""
        logger.info("🚀 ULTRATHINK Selection Algorithm Fix Validation")
        logger.info("=" * 60)
        logger.info("Testing enhanced selection algorithm against mixed content scenarios:")
        logger.info("1. High-relevance intelligence vs viral low-relevance content")
        logger.info("2. Business-critical intelligence prioritization")
        logger.info("3. MSP and security intelligence scoring boosts")
        logger.info("4. Hybrid scoring system effectiveness")
        logger.info("=" * 60)
        
        validation_results = {
            'validation_timestamp': datetime.now().isoformat(),
            'test_results': {},
            'summary': {},
            'recommendations': []
        }
        
        # Test 1: Scoring System
        scoring_test = self.test_scoring_system()
        validation_results['test_results']['scoring_system'] = scoring_test
        
        # Test 2: Selection Algorithm
        selection_test = self.test_selection_algorithm()
        validation_results['test_results']['selection_algorithm'] = selection_test
        
        # Test 3: Prioritization Logic
        prioritization_test = self.test_prioritization_logic()
        validation_results['test_results']['prioritization_logic'] = prioritization_test
        
        # Generate overall summary
        validation_results['summary'] = self._generate_validation_summary(validation_results['test_results'])
        
        # Generate recommendations
        validation_results['recommendations'] = self._generate_recommendations(validation_results['summary'])
        
        return validation_results
    
    def _generate_validation_summary(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate validation summary"""
        scoring_working = test_results['scoring_system']['summary']['scoring_fix_working']
        selection_working = test_results['selection_algorithm']['analysis']['selection_fix_working']
        prioritization_working = test_results['prioritization_logic']['analysis']['prioritization_fix_working']
        
        return {
            'scoring_system_working': scoring_working,
            'selection_algorithm_working': selection_working,
            'prioritization_logic_working': prioritization_working,
            'overall_fix_working': scoring_working and selection_working and prioritization_working,
            'tests_passed': sum([scoring_working, selection_working, prioritization_working]),
            'total_tests': 3
        }
    
    def _generate_recommendations(self, summary: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        if not summary['scoring_system_working']:
            recommendations.append("Enhance relevance scoring multipliers for intelligence content")
        
        if not summary['selection_algorithm_working']:
            recommendations.append("Adjust selection algorithm to better prioritize high-relevance content")
        
        if not summary['prioritization_logic_working']:
            recommendations.append("Review hybrid scoring weights to ensure intelligence content ranks appropriately")
        
        if summary['overall_fix_working']:
            recommendations.append("Selection algorithm fix is working correctly - intelligence content properly prioritized")
        
        return recommendations
    
    def save_validation_results(self, results: Dict[str, Any]) -> None:
        """Save validation results to file"""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"selection_algorithm_validation_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\n💾 Selection algorithm validation results saved to: {output_file}")

def main():
    """Main validation function"""
    try:
        # Initialize validator
        validator = SelectionAlgorithmValidator()
        
        # Run comprehensive validation
        results = validator.run_comprehensive_selection_validation()
        
        # Save results
        validator.save_validation_results(results)
        
        # Log final results
        logger.info("\n📋 SELECTION ALGORITHM VALIDATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"📊 Scoring System: {'✅ WORKING' if results['summary']['scoring_system_working'] else '❌ NEEDS FIX'}")
        logger.info(f"🔄 Selection Algorithm: {'✅ WORKING' if results['summary']['selection_algorithm_working'] else '❌ NEEDS FIX'}")
        logger.info(f"🎯 Prioritization Logic: {'✅ WORKING' if results['summary']['prioritization_logic_working'] else '❌ NEEDS FIX'}")
        logger.info(f"🎉 Overall Fix Status: {'✅ WORKING' if results['summary']['overall_fix_working'] else '❌ NEEDS FIX'}")
        
        # Return exit code based on validation results
        if results['summary']['overall_fix_working']:
            logger.info("\n🎉 SELECTION ALGORITHM FIX VALIDATED SUCCESSFULLY!")
            return 0
        else:
            logger.error("\n❌ SELECTION ALGORITHM FIX VALIDATION FAILED")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Selection algorithm validation failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())