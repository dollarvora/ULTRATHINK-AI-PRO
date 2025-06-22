#!/usr/bin/env python3
"""
ULTRATHINK Enhanced - Send Test Email
Sends a real email using the generated preview to dollarvora@icloud.com
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger(__name__)

def send_test_email():
    """Send test email with the latest preview"""
    logger = setup_logging()
    
    logger.info("📧 ULTRATHINK - Sending Test Email")
    logger.info("=" * 50)
    
    try:
        # Load environment variables
        load_dotenv()
        logger.info("✅ Environment variables loaded")
        
        # Find the latest preview file
        output_dir = Path("/Users/Dollar/Documents/ultrathink-enhanced/output")
        preview_files = list(output_dir.glob("preview_*.html"))
        
        if not preview_files:
            logger.error("❌ No preview files found in output directory")
            return False
        
        # Get the most recent preview file
        latest_preview = max(preview_files, key=lambda p: p.stat().st_mtime)
        logger.info(f"📄 Using preview file: {latest_preview.name}")
        
        # Read the HTML content
        with open(latest_preview, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        logger.info(f"📊 HTML content size: {len(html_content)} characters")
        
        # Import and use the email sender
        from emailer.sender import EmailSender
        from config.advanced_config import AdvancedConfigManager
        
        # Initialize email sender with config in dictionary format
        config_manager = AdvancedConfigManager()
        pydantic_config = config_manager.get_config()
        
        # Convert Pydantic model to dictionary format expected by EmailSender
        config = {
            'email': {
                'tracking_enabled': pydantic_config.email.tracking_enabled,
                'tracking_server': pydantic_config.email.tracking_server,
                'employee_csv': "/Users/Dollar/Documents/ultrathink-enhanced/config/employees.csv"
            }
        }
        
        email_sender = EmailSender(config)
        
        # Prepare email data
        test_employee = {
            'name': 'John Smith',
            'email': 'dollarvora@icloud.com',
            'role': 'pricing_analyst'
        }
        
        # Send the email
        logger.info(f"📤 Sending test email to: {test_employee['email']}")
        logger.info(f"🎯 Recipient: {test_employee['name']} ({test_employee['role']})")
        
        success = email_sender.send_email(
            to_email=test_employee['email'],
            to_name=test_employee['name'],
            subject=f"[ULTRATHINK TEST] Pricing Intelligence Digest - {datetime.now().strftime('%Y-%m-%d')}",
            html_content=html_content
        )
        
        if success:
            logger.info("✅ TEST EMAIL SENT SUCCESSFULLY!")
            logger.info(f"📧 Delivered to: {test_employee['email']}")
            logger.info("🔍 Please check your email inbox for the ULTRATHINK digest")
            logger.info("🎯 Email contains role-specific pricing analyst insights")
            return True
        else:
            logger.error("❌ Failed to send test email")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test email failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = send_test_email()
    sys.exit(0 if success else 1)