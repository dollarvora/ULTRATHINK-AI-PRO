#!/usr/bin/env python3
"""
ULTRATHINK Enhanced - Simple Test Email Sender
Sends a real email directly using SMTP without complex dependencies
"""

import os
import sys
import smtplib
import logging
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger(__name__)

def send_simple_test_email():
    """Send test email directly using SMTP"""
    logger = setup_logging()
    
    logger.info("📧 ULTRATHINK - Direct Email Test")
    logger.info("=" * 50)
    
    try:
        # Load environment variables
        load_dotenv("/Users/Dollar/Documents/ultrathink-enhanced/.env")
        logger.info("✅ Environment variables loaded")
        
        # Get SMTP settings from environment
        smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_user = os.getenv('SMTP_USER')
        smtp_password = os.getenv('SMTP_PASSWORD')
        from_email = os.getenv('FROM_EMAIL', f'ULTRATHINK <{smtp_user}>')
        
        if not all([smtp_user, smtp_password]):
            logger.error("❌ Missing SMTP credentials in environment variables")
            return False
        
        logger.info(f"📤 SMTP Config: {smtp_host}:{smtp_port} from {smtp_user}")
        
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
        
        # Recipient details
        to_email = "dollarvora@icloud.com"
        to_name = "John Smith"
        role = "pricing_analyst"
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"[ULTRATHINK TEST] Pricing Intelligence Digest - {datetime.now().strftime('%Y-%m-%d')}"
        msg['From'] = from_email
        msg['To'] = f"{to_name} <{to_email}>"
        
        # Add tracking pixel to HTML
        tracking_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        tracking_pixel = f'<img src="https://track.ultrathink.com/pixel.gif?id={tracking_id}&email={to_email}" width="1" height="1" style="display:none;" />'
        html_with_tracking = html_content.replace('</body>', f'{tracking_pixel}</body>')
        
        # Create plain text version
        text_content = f"""
ULTRATHINK Pricing Intelligence Digest
{datetime.now().strftime('%B %d, %Y')}

Hello {to_name},

This is a test email from the ULTRATHINK Pricing Intelligence System.

Role: {role}
Focus: Strategic pricing analysis and margin optimization

This email contains your personalized pricing intelligence digest with:
- Vendor activity analysis
- Market trend insights  
- Role-specific recommendations
- Urgency-based alerts

To view the full formatted digest, please enable HTML in your email client.

Best regards,
ULTRATHINK System

---
This is a test email. The system is now configured and ready for live data processing.
        """
        
        # Attach both parts
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_with_tracking, 'html'))
        
        # Send the email
        logger.info(f"📤 Sending email to: {to_email}")
        logger.info(f"🎯 Recipient: {to_name} ({role})")
        
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(smtp_user, to_email, text)
            
        logger.info("✅ TEST EMAIL SENT SUCCESSFULLY!")
        logger.info(f"📧 Delivered to: {to_email}")
        logger.info("🔍 Please check your email inbox for the ULTRATHINK digest")
        logger.info("🎯 Email contains role-specific pricing analyst insights")
        logger.info(f"📊 Tracking ID: {tracking_id}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Email sending failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = send_simple_test_email()
    sys.exit(0 if success else 1)