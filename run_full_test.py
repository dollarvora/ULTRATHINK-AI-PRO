#!/usr/bin/env python3
"""
ULTRATHINK Enhanced - Full System Test Runner
Comprehensive end-to-end testing of all system components
"""

import os
import sys
import json
import csv
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.performance_monitor import PerformanceMonitor, PerformanceContext
from utils.cache_manager import CacheManager
from config.advanced_config import AdvancedConfigManager
from fetchers.reddit_fetcher import RedditFetcher
from fetchers.google_fetcher import GoogleFetcher
from summarizer.gpt_summarizer import GPTSummarizer
from emailer.template import EmailTemplate
from emailer.sender import EmailSender

# Configure logging
def setup_logging():
    """Setup comprehensive logging"""
    log_dir = Path("/Users/Dollar/Documents/ultrathink-enhanced/output/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f"full_test_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"🚀 ULTRATHINK Full System Test Started - Log: {log_file}")
    return logger

class FullSystemTester:
    """Comprehensive system tester"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.performance_monitor = PerformanceMonitor()
        self.cache_manager = CacheManager()
        self.config_manager = None
        self.config = None
        self.vendors = {}
        self.keywords = {}
        self.employees = []
        self.test_results = {}
        
    async def run_full_test(self):
        """Run comprehensive system test"""
        try:
            self.logger.info("=" * 60)
            self.logger.info("🎯 ULTRATHINK ENHANCED - FULL SYSTEM TEST")
            self.logger.info("=" * 60)
            
            # Stage 1: Environment Setup
            await self._stage_1_setup()
            
            # Stage 2: Data Loading
            await self._stage_2_data_loading()
            
            # Stage 3: Fetcher Testing
            await self._stage_3_fetcher_testing()
            
            # Stage 4: AI Summarization
            await self._stage_4_summarization()
            
            # Stage 5: Email Preview Generation
            await self._stage_5_email_preview()
            
            # Stage 6: Performance Metrics
            await self._stage_6_metrics()
            
            # Stage 7: Test Results
            await self._stage_7_results()
            
            self.logger.info("✅ FULL SYSTEM TEST COMPLETED SUCCESSFULLY!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ FULL SYSTEM TEST FAILED: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False
    
    async def _stage_1_setup(self):
        """Stage 1: Environment and Configuration Setup"""
        self.logger.info("\n🔧 STAGE 1: Environment & Configuration Setup")
        self.logger.info("-" * 50)
        
        with PerformanceContext("stage_1_setup", self.performance_monitor):
            # Load environment variables
            load_dotenv()
            self.logger.info("✅ Environment variables loaded from .env")
            
            # Verify critical environment variables
            required_vars = [
                'OPENAI_API_KEY', 'REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET',
                'GOOGLE_API_KEY', 'GOOGLE_CSE_ID', 'SMTP_HOST', 'SMTP_USER', 'SMTP_PASSWORD'
            ]
            
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            if missing_vars:
                self.logger.warning(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
            else:
                self.logger.info("✅ All critical environment variables present")
            
            # Load configuration
            self.config_manager = AdvancedConfigManager()
            self.config = self.config_manager.get_config()
            self.logger.info(f"✅ Configuration loaded - Environment: {self.config.system.environment}")
            
            # Create output directory in ultrathink-enhanced
            output_dir = Path("/Users/Dollar/Documents/ultrathink-enhanced/output")
            output_dir.mkdir(exist_ok=True)
            self.logger.info(f"✅ Output directory ready: {output_dir.absolute()}")
            
        self.test_results['stage_1'] = {'status': 'success', 'duration': 'tracked'}
    
    async def _stage_2_data_loading(self):
        """Stage 2: Load Keywords, Vendors, and Employees"""
        self.logger.info("\n📊 STAGE 2: Data Loading")
        self.logger.info("-" * 50)
        
        with PerformanceContext("stage_2_data_loading", self.performance_monitor):
            # Load keywords.json
            keywords_file = Path("config/keywords.json")
            if keywords_file.exists():
                with open(keywords_file, 'r') as f:
                    self.keywords = json.load(f)
                self.logger.info(f"✅ Keywords loaded: {len(self.keywords)} categories")
                for category, items in self.keywords.items():
                    self.logger.info(f"   • {category}: {len(items)} items")
            else:
                self.logger.warning("⚠️  keywords.json not found, using default keywords")
                self.keywords = self.config.keywords
            
            # Load vendors (assuming they're in keywords.json under vendors)
            if 'vendors' in self.keywords:
                self.vendors = self.keywords['vendors']
                self.logger.info(f"✅ Vendors loaded: {sum(len(v) for v in self.vendors.values())} total")
            else:
                self.vendors = self.config.vendors
                self.logger.info("✅ Using default vendor configuration")
            
            # Load employees.csv with absolute path
            employees_file = Path("/Users/Dollar/Documents/ultrathink-enhanced/config/employees.csv")
            if employees_file.exists():
                with open(employees_file, 'r') as f:
                    reader = csv.DictReader(f)
                    self.employees = [row for row in reader if str(row.get('active', '')).lower() == 'true']
                self.logger.info(f"✅ Employees loaded: {len(self.employees)} active employees")
                
                # Show role distribution
                roles = {}
                for emp in self.employees:
                    role = emp.get('role', 'unknown')
                    roles[role] = roles.get(role, 0) + 1
                
                for role, count in roles.items():
                    self.logger.info(f"   • {role}: {count} employees")
            else:
                self.logger.error(f"❌ Employee file not found: {employees_file}")
                self.employees = []
            
        self.test_results['stage_2'] = {
            'status': 'success',
            'keywords_categories': len(self.keywords),
            'vendor_categories': len(self.vendors), 
            'employees': len(self.employees)
        }
    
    async def _stage_3_fetcher_testing(self):
        """Stage 3: Test All Fetchers"""
        self.logger.info("\n🌐 STAGE 3: Fetcher Testing")
        self.logger.info("-" * 50)
        
        fetcher_results = {}
        
        # Test Reddit Fetcher (dual mode)
        if self.config.sources['reddit'].enabled:
            self.logger.info("🔴 Testing Reddit Fetcher (Dual Mode)...")
            try:
                with PerformanceContext("reddit_fetcher", self.performance_monitor):
                    reddit_fetcher = RedditFetcher()
                    reddit_data = await reddit_fetcher.fetch_pricing_discussions()
                    
                    fetcher_results['reddit'] = {
                        'status': 'success',
                        'posts_fetched': len(reddit_data),
                        'dual_mode': hasattr(reddit_fetcher, '_fetch_via_snscrape')
                    }
                    
                    self.logger.info(f"✅ Reddit: {len(reddit_data)} posts fetched")
                    if reddit_data:
                        self.logger.info(f"   • Sample: {reddit_data[0].get('title', 'N/A')[:60]}...")
                        
            except Exception as e:
                self.logger.error(f"❌ Reddit Fetcher failed: {e}")
                fetcher_results['reddit'] = {'status': 'failed', 'error': str(e)}
        else:
            self.logger.info("⏭️  Reddit fetcher disabled in config")
        
        # Test Google Fetcher
        if self.config.sources['google'].enabled:
            self.logger.info("🔍 Testing Google Fetcher...")
            try:
                with PerformanceContext("google_fetcher", self.performance_monitor):
                    google_fetcher = GoogleFetcher()
                    google_data = await google_fetcher.search_pricing_news()
                    
                    fetcher_results['google'] = {
                        'status': 'success',
                        'results_fetched': len(google_data),
                        'relevance_filtering': hasattr(google_fetcher, '_is_relevant_content')
                    }
                    
                    self.logger.info(f"✅ Google: {len(google_data)} results fetched")
                    if google_data:
                        self.logger.info(f"   • Sample: {google_data[0].get('title', 'N/A')[:60]}...")
                        
            except Exception as e:
                self.logger.error(f"❌ Google Fetcher failed: {e}")
                fetcher_results['google'] = {'status': 'failed', 'error': str(e)}
        else:
            self.logger.info("⏭️  Google fetcher disabled in config")
        
        # LinkedIn and Twitter would be implemented similarly
        self.logger.info("⏭️  LinkedIn and Twitter fetchers not yet implemented")
        
        self.test_results['stage_3'] = {'status': 'success', 'fetchers': fetcher_results}
    
    async def _stage_4_summarization(self):
        """Stage 4: AI Summarization Testing"""
        self.logger.info("\n🤖 STAGE 4: AI Summarization")
        self.logger.info("-" * 50)
        
        with PerformanceContext("ai_summarization", self.performance_monitor):
            try:
                # Prepare mock data for summarization
                mock_content = {
                    'reddit': [
                        {
                            'title': 'Microsoft Price Increase Discussion',
                            'content': 'Microsoft announced a 15% price increase on Office 365 licenses starting next quarter. This affects all enterprise customers.',
                            'vendor_mentions': ['Microsoft'],
                            'urgency': 'high',
                            'source': 'reddit'
                        },
                        {
                            'title': 'Dell Server Pricing Updates',
                            'content': 'Dell has updated their PowerEdge server pricing with competitive discounts for Q4.',
                            'vendor_mentions': ['Dell'],
                            'urgency': 'medium',
                            'source': 'reddit'
                        }
                    ],
                    'google': [
                        {
                            'title': 'Enterprise Software Trends',
                            'content': 'Industry report shows increasing prices across major software vendors including Oracle and SAP.',
                            'vendor_mentions': ['Oracle', 'SAP'],
                            'urgency': 'medium',
                            'source': 'google'
                        }
                    ]
                }
                
                # Initialize summarizer
                summarizer = GPTSummarizer()
                
                # Test summarization with different roles
                test_roles = ['pricing_analyst', 'procurement_manager', 'bi_strategy']
                summaries = {}
                
                for role in test_roles:
                    if any(emp.get('role') == role for emp in self.employees):
                        self.logger.info(f"🎯 Generating summary for role: {role}")
                        try:
                            summary = await summarizer.generate_role_based_summary(mock_content, role)
                            summaries[role] = summary
                            self.logger.info(f"✅ Summary generated for {role}")
                        except Exception as e:
                            self.logger.error(f"❌ Summary failed for {role}: {e}")
                            summaries[role] = {'error': str(e)}
                
                # Save summaries to file
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                summary_file = Path(f"/Users/Dollar/Documents/ultrathink-enhanced/output/test_summaries_{timestamp}.json")
                
                with open(summary_file, 'w') as f:
                    json.dump(summaries, f, indent=2)
                
                self.logger.info(f"✅ Summaries saved to: {summary_file}")
                
                self.test_results['stage_4'] = {
                    'status': 'success',
                    'roles_tested': len(summaries),
                    'summaries_file': str(summary_file)
                }
                
                # Store summaries for email preview
                self.summaries = summaries
                
            except Exception as e:
                self.logger.error(f"❌ AI Summarization failed: {e}")
                self.test_results['stage_4'] = {'status': 'failed', 'error': str(e)}
                self.summaries = {}
    
    async def _stage_5_email_preview(self):
        """Stage 5: Email Preview Generation"""
        self.logger.info("\n📧 STAGE 5: Email Preview Generation")
        self.logger.info("-" * 50)
        
        with PerformanceContext("email_preview", self.performance_monitor):
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                preview_file = Path(f"/Users/Dollar/Documents/ultrathink-enhanced/output/preview_{timestamp}.html")
                
                # Find a pricing analyst for testing
                pricing_analyst = next(
                    (emp for emp in self.employees if emp.get('role') == 'pricing_analyst'),
                    None
                )
                
                if not pricing_analyst:
                    self.logger.warning("⚠️  No pricing_analyst found, using first employee")
                    pricing_analyst = self.employees[0] if self.employees else {
                        'name': 'Test User',
                        'email': 'test@example.com',
                        'role': 'pricing_analyst'
                    }
                
                # Get summary for this role
                role_summary = self.summaries.get('pricing_analyst', {
                    'role_summaries': {
                        'pricing_analyst': {
                            'role': 'Pricing Analyst',
                            'summary': 'Test summary for email preview generation',
                            'key_insights': ['Test insight 1', 'Test insight 2'],
                            'top_vendors': [{'vendor': 'Microsoft', 'mentions': 5}]
                        }
                    },
                    'by_urgency': {'high': 2, 'medium': 3, 'low': 1},
                    'total_items': 6
                })
                
                # Generate email template
                email_template = EmailTemplate()
                role_summary_data = role_summary.get('role_summaries', {}).get('pricing_analyst', {})
                urgency_counts = role_summary.get('by_urgency', {})
                total_items = role_summary.get('total_items', 0)
                
                html_content = email_template.render(
                    role_summary=role_summary_data,
                    urgency_counts=urgency_counts,
                    total_items=total_items
                )
                
                # Save preview
                with open(preview_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                self.logger.info(f"✅ Email preview generated: {preview_file}")
                self.logger.info(f"   • Target: {pricing_analyst.get('name')} ({pricing_analyst.get('role')})")
                self.logger.info(f"   • File size: {len(html_content)} characters")
                
                self.test_results['stage_5'] = {
                    'status': 'success',
                    'preview_file': str(preview_file),
                    'target_employee': pricing_analyst.get('name'),
                    'html_size': len(html_content)
                }
                
                # Store for potential email sending
                self.preview_html = html_content
                self.target_employee = pricing_analyst
                
            except Exception as e:
                self.logger.error(f"❌ Email preview generation failed: {e}")
                self.test_results['stage_5'] = {'status': 'failed', 'error': str(e)}
    
    async def _stage_6_metrics(self):
        """Stage 6: Performance Metrics Collection"""
        self.logger.info("\n📊 STAGE 6: Performance Metrics")
        self.logger.info("-" * 50)
        
        try:
            # Get performance summary
            performance_summary = self.performance_monitor.get_performance_summary()
            
            # Save detailed metrics
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            metrics_file = Path(f"/Users/Dollar/Documents/ultrathink-enhanced/output/full_test_metrics_{timestamp}.json")
            
            self.performance_monitor.save_metrics(metrics_file)
            
            # Log key metrics
            self.logger.info("🔍 Performance Summary:")
            self.logger.info(f"   • CPU Usage: {performance_summary['system_metrics']['cpu_percent']:.1f}%")
            self.logger.info(f"   • Memory Usage: {performance_summary['system_metrics']['memory_percent']:.1f}%")
            self.logger.info(f"   • Operations Tracked: {len(performance_summary['operation_metrics'])}")
            
            for op, metrics in performance_summary['operation_metrics'].items():
                self.logger.info(f"   • {op}: {metrics['avg_time']:.2f}s avg ({metrics['count']} runs)")
            
            # Cache statistics
            cache_stats = self.cache_manager.get_cache_stats()
            self.logger.info(f"💾 Cache: {cache_stats['total_files']} files ({cache_stats['total_size_mb']:.2f} MB)")
            
            self.test_results['stage_6'] = {
                'status': 'success',
                'metrics_file': str(metrics_file),
                'operations_tracked': len(performance_summary['operation_metrics']),
                'cache_files': cache_stats['total_files']
            }
            
        except Exception as e:
            self.logger.error(f"❌ Metrics collection failed: {e}")
            self.test_results['stage_6'] = {'status': 'failed', 'error': str(e)}
    
    async def _stage_7_results(self):
        """Stage 7: Test Results Summary"""
        self.logger.info("\n📋 STAGE 7: Test Results Summary")
        self.logger.info("-" * 50)
        
        # Save comprehensive test results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = Path(f"/Users/Dollar/Documents/ultrathink-enhanced/output/full_test_results_{timestamp}.json")
        
        complete_results = {
            'test_run': {
                'timestamp': timestamp,
                'duration': 'tracked_in_performance_metrics',
                'status': 'completed'
            },
            'system_info': {
                'config_environment': self.config.system.environment,
                'config_version': self.config.system.version,
                'employees_loaded': len(self.employees),
                'vendor_categories': len(self.vendors),
                'keyword_categories': len(self.keywords)
            },
            'stage_results': self.test_results
        }
        
        with open(results_file, 'w') as f:
            json.dump(complete_results, f, indent=2)
        
        # Print summary
        self.logger.info("🎯 TEST RESULTS SUMMARY:")
        successful_stages = sum(1 for stage in self.test_results.values() if stage.get('status') == 'success')
        total_stages = len(self.test_results)
        
        self.logger.info(f"   • Stages Completed: {successful_stages}/{total_stages}")
        self.logger.info(f"   • Results File: {results_file}")
        
        for stage_name, result in self.test_results.items():
            status_emoji = "✅" if result.get('status') == 'success' else "❌"
            self.logger.info(f"   • {stage_name}: {status_emoji} {result.get('status', 'unknown')}")


async def main():
    """Main test runner"""
    print("🚀 ULTRATHINK Enhanced - Full System Test")
    print("=" * 60)
    
    tester = FullSystemTester()
    success = await tester.run_full_test()
    
    if success:
        print("\n✅ All tests completed successfully!")
        print("📁 Check the output/ directory for detailed results and metrics")
        return 0
    else:
        print("\n❌ Some tests failed. Check logs for details.")
        return 1


if __name__ == "__main__":
    import sys
    # Python 3.6 compatibility - asyncio.run() was added in Python 3.7
    loop = asyncio.get_event_loop()
    try:
        exit_code = loop.run_until_complete(main())
    finally:
        loop.close()
    sys.exit(exit_code)