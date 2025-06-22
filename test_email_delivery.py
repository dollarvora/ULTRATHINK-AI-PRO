#!/usr/bin/env python3
"""
ULTRATHINK Enhanced - Email Delivery End-to-End Test
Simulates complete email sending process with validation and tracking
"""

import os
import sys
import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.advanced_config import AdvancedConfigManager
from emailer.sender import EmailSender
from config.utils import is_valid_email

def setup_logging():
    """Setup logging for email delivery test"""
    log_dir = Path("output/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f"email_delivery_test_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"📧 ULTRATHINK Email Delivery Test Started - Log: {log_file}")
    return logger

def find_pricing_analyst(employees_file: Path, logger) -> dict:
    """Find an active pricing analyst from employees.csv"""
    try:
        if not employees_file.exists():
            logger.warning(f"⚠️  Employee file not found: {employees_file}")
            return None
        
        with open(employees_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if (row.get('active', '').lower() == 'true' and 
                    row.get('role', '').lower() == 'pricing_analyst'):
                    
                    # Validate email
                    email = row.get('email', '').strip()
                    if is_valid_email(email):
                        logger.info(f"✅ Found pricing analyst: {row.get('name')} ({email})")
                        return {
                            'name': row.get('name'),
                            'email': email,
                            'role': row.get('role'),
                            'keywords': row.get('keywords', '')
                        }
                    else:
                        logger.warning(f"⚠️  Invalid email for {row.get('name')}: {email}")
        
        logger.warning("⚠️  No valid pricing analyst found in employees.csv")
        return None
        
    except Exception as e:
        logger.error(f"❌ Error reading employees file: {e}")
        return None

def create_test_summary_data():
    """Create realistic test summary data"""
    return {
        'role_summaries': {
            'pricing_analyst': {
                'role': 'Pricing Analyst',
                'focus': 'Strategic pricing analysis and competitive intelligence',
                'summary': 'Critical week for pricing intelligence with Microsoft announcing significant Office 365 increases and Dell responding with aggressive server discounts. Market dynamics indicate a shift toward consumption-based pricing models across enterprise software.',
                'key_insights': [
                    '🔴 Microsoft Office 365 +15% price increase effective Q1 2024',
                    '🟢 Dell PowerEdge R750: 20% Q4 discount opportunity window',
                    '⚠️ Cisco DNA licensing model changes impacting enterprise renewals',
                    '📈 HPE GreenLake adoption driving 12% consumption pricing uptick',
                    '🔄 Oracle cloud pricing restructure affecting multi-year contracts'
                ],
                'top_vendors': [
                    {'vendor': 'Microsoft', 'mentions': 12, 'trend': '+15%', 'urgency': 'high'},
                    {'vendor': 'Dell', 'mentions': 8, 'trend': '-20%', 'urgency': 'medium'},
                    {'vendor': 'Cisco', 'mentions': 6, 'trend': 'Model Change', 'urgency': 'high'},
                    {'vendor': 'HPE', 'mentions': 5, 'trend': '+12%', 'urgency': 'medium'},
                    {'vendor': 'Oracle', 'mentions': 4, 'trend': 'Restructure', 'urgency': 'medium'}
                ],
                'sources': {'reddit': 18, 'google': 9, 'linkedin': 3}
            }
        },
        'by_urgency': {'high': 5, 'medium': 12, 'low': 8},
        'total_items': 25,
        'analysis_metadata': {
            'keywords_used': {
                'key_vendors': ['Microsoft', 'Dell', 'Cisco', 'HPE', 'Oracle'],
                'urgency_high': ['price increase', 'acquisition', 'security breach', 'licensing change'],
                'urgency_medium': ['discount', 'promotion', 'update', 'restructure'],
                'pricing_keywords': ['cost', 'price', 'pricing', 'discount', 'margin', 'licensing']
            },
            'content_analyzed': [
                {
                    'title': 'Microsoft Office 365 Enterprise Price Increase - Starting January 2024',
                    'content_preview': 'Microsoft announced a 15% price increase across Office 365 Enterprise plans, citing enhanced AI capabilities and security features...',
                    'source': 'reddit',
                    'urgency': 'high',
                    'relevance_score': 9.5,
                    'url': 'https://reddit.com/r/sysadmin/microsoft_pricing',
                    'created_at': datetime.now().strftime('%Y-%m-%d')
                },
                {
                    'title': 'Dell PowerEdge R750 Deep Discounts Through Q4',
                    'content_preview': 'Dell is offering significant discounts on PowerEdge R750 servers as part of their Q4 inventory clearance...',
                    'source': 'google',
                    'urgency': 'medium',
                    'relevance_score': 8.3,
                    'url': 'https://dell.com/poweredge-q4-deals',
                    'created_at': datetime.now().strftime('%Y-%m-%d')
                }
            ],
            'processing_stats': {
                'total_items_processed': 25,
                'sources_processed': ['reddit', 'google', 'linkedin'],
                'deduplication_applied': True,
                'urgency_detection_enabled': True,
                'vendor_detection_enabled': True
            }
        }
    }

def main():
    """Main email delivery test function"""
    logger = setup_logging()
    
    try:
        logger.info("=" * 60)
        logger.info("📧 ULTRATHINK EMAIL DELIVERY END-TO-END TEST")
        logger.info("=" * 60)
        
        # Load environment variables
        load_dotenv()
        logger.info("✅ Environment variables loaded from .env")
        
        # Load configuration
        config_manager = AdvancedConfigManager()
        config = config_manager.get_config()
        logger.info(f"✅ Configuration loaded - Environment: {config.system.environment}")
        
        # Verify email configuration
        email_config = config.email
        logger.info(f"📧 Email Configuration:")
        logger.info(f"   • Enabled: {email_config.enabled}")
        logger.info(f"   • Tracking: {email_config.tracking_enabled}")
        logger.info(f"   • Tracking Server: {email_config.tracking_server}")
        logger.info(f"   • Employee CSV: {email_config.employee_csv}")
        
        # Find pricing analyst
        employees_file = Path(email_config.employee_csv)
        pricing_analyst = find_pricing_analyst(employees_file, logger)
        
        if not pricing_analyst:
            # Create mock pricing analyst for testing
            logger.info("🤖 Creating mock pricing analyst for testing")
            pricing_analyst = {
                'name': 'Test Pricing Analyst',
                'email': 'test@example.com',
                'role': 'pricing_analyst',
                'keywords': 'microsoft, dell, pricing, discounts, enterprise'
            }
        
        # Create test summary data
        logger.info("📊 Generating test summary data...")
        summary_data = create_test_summary_data()
        
        # Save test data for reference
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        test_data_file = Path(f"output/email_test_data_{timestamp}.json")
        with open(test_data_file, 'w') as f:
            json.dump({
                'target_employee': pricing_analyst,
                'summary_data': summary_data,
                'test_timestamp': timestamp
            }, f, indent=2)
        logger.info(f"📄 Test data saved to: {test_data_file}")
        
        # Initialize email sender
        logger.info("🔧 Initializing email sender...")
        email_sender = EmailSender(config.dict())
        
        # Validate email before proceeding
        target_email = pricing_analyst['email']
        if not is_valid_email(target_email):
            logger.error(f"❌ Invalid email format: {target_email}")
            return 1
        
        logger.info(f"✅ Email validation passed for: {target_email}")
        
        # Generate preview first
        logger.info("🎨 Generating email preview...")
        preview_file = Path(f"output/email_delivery_preview_{timestamp}.html")
        email_sender.save_preview(summary_data, preview_file)
        logger.info(f"✅ Preview generated: {preview_file}")
        
        # Send test email
        logger.info("📤 Sending test email...")
        logger.info(f"   • Target: {pricing_analyst['name']} ({pricing_analyst['email']})")
        logger.info(f"   • Role: {pricing_analyst['role']}")
        logger.info(f"   • Keywords: {pricing_analyst.get('keywords', 'None')}")
        
        success = email_sender.send_test_email(target_email, summary_data)
        
        # Log final results
        logger.info("=" * 60)
        logger.info("📋 EMAIL DELIVERY TEST RESULTS")
        logger.info("=" * 60)
        
        if success:
            logger.info("✅ EMAIL DELIVERY SUCCESSFUL!")
            logger.info(f"   • Recipient: {pricing_analyst['name']} ({target_email})")
            logger.info(f"   • Email validation: PASSED")
            logger.info(f"   • Tracking pixel: {'EMBEDDED' if email_sender.tracking_enabled else 'DISABLED'}")
            logger.info(f"   • SMTP delivery: SUCCESS")
            logger.info(f"   • Preview file: {preview_file}")
            logger.info(f"   • Test data: {test_data_file}")
            
            # Create success report
            success_report = {
                'test_timestamp': timestamp,
                'status': 'SUCCESS',
                'recipient': pricing_analyst,
                'email_features': {
                    'tracking_enabled': email_sender.tracking_enabled,
                    'email_validation': True,
                    'smtp_delivery': True,
                    'html_template': True,
                    'role_based_content': True
                },
                'files_generated': {
                    'preview': str(preview_file),
                    'test_data': str(test_data_file)
                }
            }
            
            report_file = Path(f"output/email_delivery_report_{timestamp}.json")
            with open(report_file, 'w') as f:
                json.dump(success_report, f, indent=2)
            
            logger.info(f"📄 Success report saved: {report_file}")
            return 0
            
        else:
            logger.error("❌ EMAIL DELIVERY FAILED!")
            logger.error(f"   • Check SMTP configuration and credentials")
            logger.error(f"   • Verify email address: {target_email}")
            logger.error(f"   • Review logs for detailed error information")
            
            # Create failure report
            failure_report = {
                'test_timestamp': timestamp,
                'status': 'FAILED',
                'target_email': target_email,
                'possible_causes': [
                    'SMTP configuration error',
                    'Invalid email credentials',
                    'Network connectivity issue',
                    'Email server rejection'
                ]
            }
            
            report_file = Path(f"output/email_delivery_failure_{timestamp}.json")
            with open(report_file, 'w') as f:
                json.dump(failure_report, f, indent=2)
            
            logger.error(f"📄 Failure report saved: {report_file}")
            return 1
    
    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())