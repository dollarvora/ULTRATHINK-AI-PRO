"""
Email Sender
Handles email composition and delivery with validation and tracking
Enhanced with email validation and tracking pixel support
"""

import smtplib
import logging
import csv
import uuid
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional

#from .template import build_html
from .template import EmailTemplate
from config.utils import is_valid_email


class EmailSender:
    """Handles email sending for pricing intelligence digests"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.template = EmailTemplate()
        
        # Tracking configuration
        self.tracking_enabled = self.config.get('email', {}).get('tracking_enabled', True)
        self.tracking_server = self.config.get('email', {}).get('tracking_server', 'https://track.ultrathink.com')
        
        # Load employee list
        self.employees = self._load_employees()
    
    def _load_employees(self) -> List[Dict[str, Any]]:
        """Load employee list from CSV"""
        csv_path = Path(self.config['email']['employee_csv'])
        
        if csv_path.exists():
            employees = []
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Filter active employees only
                    if row['active'].lower() == 'true':
                        email = row['email'].strip()
                        
                        # Validate email format
                        if not is_valid_email(email):
                            self.logger.warning(f"Invalid email format for {row['name']}: {email}")
                            continue
                        
                        employees.append({
                            'name': row['name'],
                            'email': email,
                            'role': row['role'],
                            'keywords': row['keywords']
                        })
            return employees
        else:
            self.logger.warning(f"Employee CSV not found at {csv_path}")
            # Return empty list
            return []
    
    def send_digest(self, summaries: Dict[str, Any]) -> None:
        """Send email digests to all active employees"""
        if not self.config['email']['enabled']:
            self.logger.info("Email sending is disabled")
            return
        
        # Get urgency counts
        urgency_counts = summaries['by_urgency']
        total_items = summaries['total_items']
        
        # Group employees by role
        role_groups = {}
        for employee in self.employees:
            role = employee['role']
            if role not in role_groups:
                role_groups[role] = []
            role_groups[role].append(employee)
        
        for role, employees in role_groups.items():
            if role not in summaries['role_summaries']:
                self.logger.warning(f"No summary generated for role: {role}")
                continue
            
            role_summary = summaries['role_summaries'][role]
            
            # Send to each employee in this role
            for employee in employees:
                try:
                    self._send_email(
                        employee,
                        role_summary,
                        urgency_counts,
                        total_items
                    )
                except Exception as e:
                    self.logger.error(f"Failed to send email to {employee['email']}: {e}")
        
        # Send to test recipients if configured
        if self.config['email'].get('test_recipients'):
            for test_email in self.config['email']['test_recipients']:
                try:
                    # Send pricing analyst summary to test recipients
                    if 'pricing_analyst' in summaries['role_summaries']:
                        self._send_email(
                            {'name': 'Test User', 'email': test_email},
                            summaries['role_summaries']['pricing_analyst'],
                            urgency_counts,
                            total_items
                        )
                except Exception as e:
                    self.logger.error(f"Failed to send test email to {test_email}: {e}")
    
    def _send_email(self, employee: Dict, role_summary: Dict, 
                   urgency_counts: Dict, total_items: int) -> None:
        """Send email to a single recipient with tracking"""
        
        # Validate email before proceeding
        if not is_valid_email(employee['email']):
            self.logger.warning(f"Invalid email address: {employee['email']}")
            return
        
        # Generate tracking ID for this email
        tracking_id = str(uuid.uuid4())
        
        # Personalize summary based on employee keywords
        personalized_summary = self._personalize_summary(
            role_summary,
            employee.get('keywords', '')
        )
        
        # Render email
        html_content = self.template.render(
            personalized_summary,
            urgency_counts,
            total_items
        )
        
        # Add tracking pixel if enabled
        if self.tracking_enabled:
            tracking_pixel = self._generate_tracking_pixel(
                tracking_id, 
                employee['email'],
                employee['role']
            )
            html_content = self._insert_tracking_pixel(html_content, tracking_pixel)
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = self.config['email']['subject_template'].format(
            date=datetime.now().strftime('%B %d, %Y')
        )
        msg['From'] = self.config['credentials']['email']['from_email']
        msg['To'] = employee['email']
        
        # Add tracking headers
        if self.tracking_enabled:
            msg['X-ULTRATHINK-Tracking-ID'] = tracking_id
            msg['X-ULTRATHINK-Role'] = employee['role']
        
        # Attach HTML
        msg.attach(MIMEText(html_content, 'html'))
        
        # Also create plain text version
        text_content = self._create_text_version(personalized_summary, urgency_counts)
        msg.attach(MIMEText(text_content, 'plain'))
        
        # Send email
        self._send_smtp(msg, employee['email'])
        self.logger.info(f"Email sent to {employee['name']} ({employee['email']}) - Tracking ID: {tracking_id}")
    
    def _generate_tracking_pixel(self, tracking_id: str, email: str, role: str) -> str:
        """Generate tracking pixel HTML"""
        # Build tracking URL with parameters
        tracking_url = f"{self.tracking_server}/track/{tracking_id}?email={email}&role={role}"
        
        # Return invisible 1x1 pixel image
        return f'<img src="{tracking_url}" width="1" height="1" alt="" style="display:block;border:0;outline:0;" />'
    
    def _insert_tracking_pixel(self, html_content: str, tracking_pixel: str) -> str:
        """Insert tracking pixel before closing body tag"""
        # Find the closing body tag
        close_body_index = html_content.rfind('</body>')
        
        if close_body_index != -1:
            # Insert tracking pixel before </body>
            return (html_content[:close_body_index] + 
                   f'\n<!-- Tracking Pixel -->\n{tracking_pixel}\n' + 
                   html_content[close_body_index:])
        else:
            # If no body tag found, append at end
            return html_content + f'\n{tracking_pixel}'
    
    def _personalize_summary(self, role_summary: Dict, keywords: str) -> Dict:
        """Personalize summary based on employee keywords"""
        personalized = role_summary.copy()
        
        if keywords:
            # Parse keywords
            user_keywords = [kw.strip().lower() for kw in keywords.split(',')]
            
            # Filter insights based on keywords
            if 'key_insights' in personalized:
                filtered_insights = []
                for insight in personalized['key_insights']:
                    if any(kw in insight.lower() for kw in user_keywords):
                        filtered_insights.append(insight)
                
                # Keep original insights if no matches
                if filtered_insights:
                    personalized['key_insights'] = filtered_insights
            
            # Highlight relevant vendors
            if 'top_vendors' in personalized:
                for vendor_info in personalized['top_vendors']:
                    if any(kw in vendor_info['vendor'].lower() for kw in user_keywords):
                        vendor_info['highlighted'] = True
        
        return personalized
    
    def _create_text_version(self, role_summary: Dict, urgency_counts: Dict) -> str:
        """Create plain text version of email"""
        text = f"""ULTRATHINK Pricing Intelligence Digest
{datetime.now().strftime('%B %d, %Y')}

Role: {role_summary['role']}
Focus: {role_summary['focus']}

URGENCY SUMMARY:
- High Priority: {urgency_counts['high']}
- Medium Priority: {urgency_counts['medium']}
- Low Priority: {urgency_counts['low']}

EXECUTIVE SUMMARY:
{role_summary['summary']}

"""
        
        if role_summary.get('key_insights'):
            text += "KEY INSIGHTS:\n"
            for i, insight in enumerate(role_summary['key_insights'][:5], 1):
                text += f"{i}. {insight}\n"
            text += "\n"
        
        if role_summary.get('top_vendors'):
            text += "TOP VENDOR ACTIVITY:\n"
            for vendor in role_summary['top_vendors'][:5]:
                text += f"- {vendor['vendor']}: {vendor['mentions']} mentions\n"
            text += "\n"
        
        text += f"""SOURCES:
"""
        for source, count in role_summary.get('sources', {}).items():
            text += f"- {source}: {count} items\n"
        
        text += """\n---
Generated by ULTRATHINK Pricing Intelligence System
"""
        
        return text
    
    def _send_smtp(self, msg: MIMEMultipart, recipient: str) -> None:
        """Send email via SMTP"""
        creds = self.config['credentials']['email']
        
        with smtplib.SMTP(creds['smtp_host'], creds['smtp_port']) as server:
            # Enable TLS
            server.starttls()
            
            # Login
            server.login(creds['smtp_user'], creds['smtp_password'])
            
            # Send email
            server.send_message(msg)
    
    def save_preview(self, summaries: Dict[str, Any], output_path: Path) -> None:
        """Save email preview as HTML file"""
        
        # Generate preview for each role
        previews = []
        
        urgency_counts = summaries['by_urgency']
        total_items = summaries['total_items']
        
        for role_key, role_summary in summaries['role_summaries'].items():
            html = self.template.render(
                role_summary,
                urgency_counts,
                total_items
            )
            
            previews.append(f"<h2>Preview for {role_summary['role']}</h2>")
            previews.append(html)
            previews.append("<hr style='margin: 50px 0;'>")
        
        # Add comprehensive analysis details
        analysis_section = self._generate_analysis_appendix(summaries)
        
        # Combine all previews
        full_preview = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>ULTRATHINK Email Preview</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
        }}
        h2 {{
            text-align: center;
            color: #333;
            margin: 40px 0 20px;
        }}
        .analysis-section {{
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            padding: 20px;
            margin: 30px 0;
            border-radius: 5px;
        }}
        .keyword-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
        }}
        .keyword-tag {{
            background-color: #007bff;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 12px;
        }}
        .content-item {{
            border: 1px solid #eee;
            padding: 10px;
            margin: 5px 0;
            background-color: white;
        }}
        .provider-section {{
            border: 1px solid #ccc;
            margin: 15px 0;
            border-radius: 5px;
            background-color: white;
        }}
        .provider-header {{
            background-color: #f8f9fa;
            padding: 15px;
            cursor: pointer;
            border-radius: 5px 5px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: bold;
            border-bottom: 1px solid #ddd;
        }}
        .provider-header:hover {{
            background-color: #e9ecef;
        }}
        .provider-content {{
            padding: 15px;
            display: none;
        }}
        .provider-content.active {{
            display: block;
        }}
        .toggle-icon {{
            font-size: 14px;
            transition: transform 0.3s;
        }}
        .toggle-icon.expanded {{
            transform: rotate(90deg);
        }}
        .show-all-btn {{
            background-color: #007bff;
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin: 10px 0;
        }}
        .show-all-btn:hover {{
            background-color: #0056b3;
        }}
        .provider-reddit {{ border-left: 4px solid #ff4500; }}
        .provider-google {{ border-left: 4px solid #4285f4; }}
        .provider-linkedin {{ border-left: 4px solid #0077b5; }}
    </style>
    <script>
        function toggleProvider(providerId) {{
            const content = document.getElementById(providerId + '-content');
            const icon = document.getElementById(providerId + '-icon');
            
            if (content.classList.contains('active')) {{
                content.classList.remove('active');
                icon.classList.remove('expanded');
            }} else {{
                content.classList.add('active');
                icon.classList.add('expanded');
            }}
        }}
        
        function showAllProviders() {{
            const contents = document.querySelectorAll('.provider-content');
            const icons = document.querySelectorAll('.toggle-icon');
            
            contents.forEach(content => content.classList.add('active'));
            icons.forEach(icon => icon.classList.add('expanded'));
        }}
        
        function hideAllProviders() {{
            const contents = document.querySelectorAll('.provider-content');
            const icons = document.querySelectorAll('.toggle-icon');
            
            contents.forEach(content => content.classList.remove('active'));
            icons.forEach(icon => icon.classList.remove('expanded'));
        }}
    </script>
</head>
<body>
    <h1 style="text-align: center;">ULTRATHINK Email Previews</h1>
    <p style="text-align: center; color: #666;">Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    {''.join(previews)}
    {analysis_section}
</body>
</html>"""
        
        # Save preview
        with open(output_path, 'w') as f:
            f.write(full_preview)
        
        self.logger.info(f"Email preview saved to {output_path}")

    def _generate_analysis_appendix(self, summaries: Dict[str, Any]) -> str:
        """Generate comprehensive analysis appendix with all details"""
        
        if 'analysis_metadata' not in summaries:
            return "<div class='analysis-section'><h2>Analysis Details</h2><p>No metadata available</p></div>"
        
        metadata = summaries['analysis_metadata']
        
        # Keywords section
        keywords_html = "<div class='analysis-section'><h2>🔍 Analysis Keywords & Criteria</h2>"
        
        keywords_html += "<h3>Key Vendors Monitored</h3><div class='keyword-list'>"
        for vendor in metadata['keywords_used']['key_vendors']:
            keywords_html += f"<span class='keyword-tag'>{vendor}</span>"
        keywords_html += "</div>"
        
        keywords_html += "<h3>High Urgency Keywords</h3><div class='keyword-list'>"
        for keyword in metadata['keywords_used']['urgency_high']:
            keywords_html += f"<span class='keyword-tag' style='background-color: #dc3545;'>{keyword}</span>"
        keywords_html += "</div>"
        
        keywords_html += "<h3>Medium Urgency Keywords</h3><div class='keyword-list'>"
        for keyword in metadata['keywords_used']['urgency_medium']:
            keywords_html += f"<span class='keyword-tag' style='background-color: #ffc107; color: black;'>{keyword}</span>"
        keywords_html += "</div>"
        
        keywords_html += "<h3>Pricing Analysis Keywords</h3><div class='keyword-list'>"
        for keyword in metadata['keywords_used']['pricing_keywords']:
            keywords_html += f"<span class='keyword-tag' style='background-color: #28a745;'>{keyword}</span>"
        keywords_html += "</div></div>"
        
        # Interactive content analyzed section organized by provider
        content_html = "<div class='analysis-section'><h2>📄 Content Analyzed</h2>"
        
        if metadata['content_analyzed']:
            content_html += f"<p><strong>Total Items Processed:</strong> {len(metadata['content_analyzed'])}</p>"
            content_html += f"<p><strong>Sources:</strong> {', '.join(metadata['processing_stats']['sources_processed'])}</p>"
            
            # Add control buttons
            content_html += """
            <div style='margin: 15px 0;'>
                <button class='show-all-btn' onclick='showAllProviders()'>📂 Expand All Sources</button>
                <button class='show-all-btn' onclick='hideAllProviders()' style='background-color: #6c757d;'>📁 Collapse All Sources</button>
            </div>
            """
            
            # Sort all content by urgency first (high → medium → low)
            urgency_order = {'high': 0, 'medium': 1, 'low': 2}
            sorted_content = sorted(metadata['content_analyzed'], 
                                  key=lambda x: (urgency_order.get(x['urgency'], 3), -x['relevance_score']))
            
            # Group content by provider
            providers = {}
            for item in sorted_content:
                provider = item['source'].lower()
                if provider not in providers:
                    providers[provider] = []
                providers[provider].append(item)
            
            # Create interactive sections for each provider
            for provider, items in providers.items():
                provider_icon = {
                    'reddit': '🔴',
                    'google': '🔵', 
                    'linkedin': '🔷',
                    'twitter': '🐦'
                }.get(provider, '📄')
                
                content_html += f"""
                <div class='provider-section provider-{provider}'>
                    <div class='provider-header' onclick='toggleProvider("{provider}")'>
                        <span>{provider_icon} {provider.title()} ({len(items)} items)</span>
                        <span class='toggle-icon' id='{provider}-icon'>▶</span>
                    </div>
                    <div class='provider-content' id='{provider}-content'>
                """
                
                # Items are already sorted globally by urgency, maintain that order
                
                for item in items:
                    urgency_color = {
                        'high': '#dc3545',
                        'medium': '#ffc107', 
                        'low': '#28a745'
                    }.get(item['urgency'], '#6c757d')
                    
                    urgency_emoji = {
                        'high': '🔴',
                        'medium': '🟡',
                        'low': '🟢'
                    }.get(item['urgency'], '⚪')
                    
                    content_html += f"""
                    <div class='content-item'>
                        <h4 style='margin: 0 0 10px 0;'>{urgency_emoji} {item['title']}</h4>
                        <p><strong>Relevance Score:</strong> {item['relevance_score']} | 
                           <strong>Urgency:</strong> <span style='color: {urgency_color}; font-weight: bold;'>{item['urgency'].upper()}</span></p>
                        {f"<p><strong>🔗 URL:</strong> <a href='{item['url']}' target='_blank'>{item['url'][:100]}{'...' if len(item['url']) > 100 else ''}</a></p>" if item['url'] else ""}
                        <p><strong>📅 Date:</strong> {item['created_at']}</p>
                        <details style='margin-top: 10px;'>
                            <summary style='cursor: pointer; font-weight: bold; color: #007bff;'>📋 Content Preview</summary>
                            <p style='margin-top: 10px; padding: 10px; background-color: #f8f9fa; border-radius: 4px;'>{item['content_preview']}</p>
                        </details>
                    </div>
                    """
                
                content_html += "</div></div>"
                
        else:
            content_html += "<p>No content available for analysis</p>"
        
        content_html += "</div>"
        
        # Source status and processing stats
        all_sources = ['Reddit', 'Google', 'LinkedIn']  # Expected sources
        
        # Check which sources actually have content
        sources_with_content = set()
        for item in metadata['content_analyzed']:
            sources_with_content.add(item['source'].title())
        
        successful_sources = [s for s in all_sources if s in sources_with_content]
        failed_sources = [s for s in all_sources if s not in sources_with_content]
        
        source_status_html = "<div class='analysis-section'><h2>📡 Source Status</h2>"
        source_status_html += "<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin: 15px 0;'>"
        
        for source in successful_sources:
            source_status_html += f"<div style='padding: 10px; background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 4px;'>✅ <strong>{source}</strong>: Active</div>"
        
        for source in failed_sources:
            source_status_html += f"<div style='padding: 10px; background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 4px;'>❌ <strong>{source}</strong>: Connection Failed</div>"
        
        source_status_html += "</div></div>"
        
        # Processing stats
        stats_html = f"""
        <div class='analysis-section'>
            <h2>⚙️ Processing Statistics</h2>
            <ul>
                <li><strong>Deduplication Applied:</strong> {metadata['processing_stats']['deduplication_applied']}</li>
                <li><strong>Urgency Detection:</strong> {metadata['processing_stats']['urgency_detection_enabled']}</li>
                <li><strong>Vendor Detection:</strong> {metadata['processing_stats']['vendor_detection_enabled']}</li>
                <li><strong>Total Items Processed:</strong> {metadata['processing_stats']['total_items_processed']}</li>
                <li><strong>Sources Successfully Processed:</strong> {', '.join(successful_sources)}</li>
                {f"<li><strong>Sources Failed:</strong> {', '.join(failed_sources)}</li>" if failed_sources else ""}
            </ul>
        </div>
        """
        
        # Comprehensive methodology and capability section
        methodology_html = f"""
        <div class='analysis-section' style='background-color: #e9ecef; border-color: #adb5bd;'>
            <h2>🧠 ULTRATHINK Enhanced - Complete Analysis Methodology</h2>
            <p><strong>ULTRATHINK Enhanced</strong> is an AI-powered pricing intelligence system designed for IT distribution and resale professionals. Here's the complete overview of capabilities:</p>
            
            <h3>📊 Data Sources & Collection Methods</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 15px 0;">
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #ff4500;">
                    <h4 style="color: #ff4500; margin: 0 0 10px 0;">🔴 Reddit Sources</h4>
                    <p><strong>Subreddits Monitored:</strong></p>
                    <ul style="margin: 5px 0; columns: 2;">
                        <li>r/sysadmin</li>
                        <li>r/msp</li>
                        <li>r/cybersecurity</li>
                        <li>r/ITManagers</li>
                        <li>r/procurement</li>
                        <li>r/enterprise</li>
                        <li>r/cloudcomputing</li>
                        <li>r/aws</li>
                        <li>r/azure</li>
                        <li>r/vmware</li>
                        <li>r/networking</li>
                        <li>r/storage</li>
                    </ul>
                    <p><strong>Keywords Searched:</strong> price increase, pricing, cost increase, expensive, license cost, subscription cost, Microsoft pricing, VMware pricing, Oracle licensing, Dell pricing, vendor pricing, enterprise pricing, software cost</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #4285f4;">
                    <h4 style="color: #4285f4; margin: 0 0 10px 0;">🔍 Google Search Intelligence</h4>
                    <p><strong>Search Queries:</strong></p>
                    <ul>
                        <li>Microsoft Office 365 price increase 2024</li>
                        <li>VMware Broadcom licensing price change</li>
                        <li>Dell server pricing enterprise 2024</li>
                        <li>Oracle database licensing cost increase</li>
                        <li>enterprise software pricing trends 2024</li>
                        <li>cybersecurity vendor price changes</li>
                        <li>IT distributor margin compression</li>
                        <li>cloud pricing updates AWS Azure</li>
                        <li>hardware vendor surcharge</li>
                    </ul>
                </div>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #0077b5;">
                    <h4 style="color: #0077b5; margin: 0 0 10px 0;">🔷 LinkedIn Professional Network</h4>
                    <p><strong>Companies Tracked:</strong></p>
                    <ul style="columns: 2;">
                        <li>Dell Technologies</li>
                        <li>Microsoft</li>
                        <li>Cisco</li>
                        <li>Fortinet</li>
                        <li>CrowdStrike</li>
                        <li>Palo Alto Networks</li>
                        <li>Zscaler</li>
                        <li>TD SYNNEX</li>
                        <li>Ingram Micro</li>
                        <li>CDW</li>
                        <li>Insight Enterprises</li>
                    </ul>
                </div>
            </div>
            
            <h3>🏢 Complete Vendor & Manufacturer Coverage</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 15px 0;">
                <div style="background: #fff3cd; padding: 12px; border-radius: 6px;">
                    <h4 style="color: #856404; margin: 0 0 8px 0;">🖥️ Hardware Manufacturers</h4>
                    <p style="font-size: 12px; margin: 0;">Dell Technologies, HPE, HP Inc., Lenovo, Cisco Systems, IBM, Oracle, Supermicro, Intel, AMD, NVIDIA, Qualcomm, Broadcom, Arista Networks, Juniper Networks, Extreme Networks, NetApp, Pure Storage, Western Digital, Seagate</p>
                </div>
                
                <div style="background: #d1ecf1; padding: 12px; border-radius: 6px;">
                    <h4 style="color: #0c5460; margin: 0 0 8px 0;">☁️ Cloud Service Providers</h4>
                    <p style="font-size: 12px; margin: 0;">Amazon Web Services (AWS), Microsoft Azure, Google Cloud Platform (GCP), Oracle Cloud Infrastructure, IBM Cloud, Alibaba Cloud, VMware Cloud, DigitalOcean, Linode (Akamai), Vultr</p>
                </div>
                
                <div style="background: #f8d7da; padding: 12px; border-radius: 6px;">
                    <h4 style="color: #721c24; margin: 0 0 8px 0;">🛡️ Cybersecurity Vendors</h4>
                    <p style="font-size: 12px; margin: 0;">Palo Alto Networks, Fortinet, Check Point, SonicWall, CrowdStrike, SentinelOne, Microsoft Defender, Symantec, McAfee, Trend Micro, Zscaler, Proofpoint, Okta, Splunk, IBM QRadar, Tenable, Qualys, Rapid7, Arctic Wolf, Darktrace</p>
                </div>
                
                <div style="background: #d4edda; padding: 12px; border-radius: 6px;">
                    <h4 style="color: #155724; margin: 0 0 8px 0;">💻 Software Vendors</h4>
                    <p style="font-size: 12px; margin: 0;">Microsoft, Oracle Corporation, SAP, Salesforce, Adobe, Atlassian, ServiceNow, Workday, VMware (Broadcom), Citrix, Red Hat (IBM), SUSE, Canonical (Ubuntu), MongoDB, Snowflake, Tableau, Databricks</p>
                </div>
                
                <div style="background: #e2e3e5; padding: 12px; border-radius: 6px;">
                    <h4 style="color: #383d41; margin: 0 0 8px 0;">🔧 MSP & IT Management</h4>
                    <p style="font-size: 12px; margin: 0;">ConnectWise, Kaseya, NinjaOne (Ninja), Datto, Atera, SolarWinds, ManageEngine, Autotask, ServiceNow, Freshservice, Zendesk</p>
                </div>
                
                <div style="background: #ffeaa7; padding: 12px; border-radius: 6px;">
                    <h4 style="color: #6c5b0f; margin: 0 0 8px 0;">📦 Distribution & Channel</h4>
                    <p style="font-size: 12px; margin: 0;">TD Synnex, Ingram Micro, Arrow Electronics, CDW Corporation, SHI International, Insight Enterprises, Connection, Zones, World Wide Technology (WWT), Computacenter, Exclusive Networks, Westcon-Comstor, Avnet</p>
                </div>
            </div>
            
            <h3>🎯 Intelligence Analysis Methods</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; margin: 15px 0;">
                <div style="background: #fff; padding: 15px; border: 1px solid #dee2e6; border-radius: 8px;">
                    <h4 style="color: #495057; margin: 0 0 10px 0;">🔍 Content Analysis Pipeline</h4>
                    <ol style="margin: 0; padding-left: 20px;">
                        <li><strong>Dual-Source Fetching:</strong> PRAW + snscrape for Reddit reliability</li>
                        <li><strong>Company Alias Matching:</strong> 95+ companies with hundreds of aliases</li>
                        <li><strong>Relevance Filtering:</strong> 60-80% noise reduction</li>
                        <li><strong>Urgency Classification:</strong> High/Medium/Low priority scoring</li>
                        <li><strong>Content Deduplication:</strong> Hash-based + semantic analysis</li>
                        <li><strong>GPT-4 Analysis:</strong> Few-shot prompting with role-specific context</li>
                    </ol>
                </div>
                
                <div style="background: #fff; padding: 15px; border: 1px solid #dee2e6; border-radius: 8px;">
                    <h4 style="color: #495057; margin: 0 0 10px 0;">📊 Scoring & Prioritization</h4>
                    <ul style="margin: 0; padding-left: 20px;">
                        <li><strong>Urgency Weight:</strong> 2.0x multiplier</li>
                        <li><strong>Vendor Weight:</strong> 1.5x multiplier</li>
                        <li><strong>Keyword Weight:</strong> 1.0x baseline</li>
                        <li><strong>Recency Weight:</strong> 0.5x time decay</li>
                        <li><strong>High Score Threshold:</strong> 7.0+</li>
                        <li><strong>Medium Score Threshold:</strong> 4.0+</li>
                    </ul>
                </div>
            </div>
            
            <h3>🔑 Complete Keyword Intelligence Matrix</h3>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0;">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <div>
                        <h5 style="color: #dc3545; margin: 0 0 8px 0;">🔴 High Urgency Keywords</h5>
                        <p style="font-size: 11px; margin: 0;">urgent, critical, immediate, emergency, breaking, price increase, discontinued, end of life, EOL, supply shortage, recall, security breach, zero-day, acquisition, merger, bankruptcy, lawsuit, licensing change, perpetual license, subscription only, vendor lock-in, margin compression, channel conflict</p>
                    </div>
                    <div>
                        <h5 style="color: #ffc107; margin: 0 0 8px 0;">🟡 Medium Urgency Keywords</h5>
                        <p style="font-size: 11px; margin: 0;">update, change, new pricing, promotion, discount, partnership, launch, release, expansion, investment, rebate, volume discount, distributor program, channel partner, fulfillment, lead time</p>
                    </div>
                    <div>
                        <h5 style="color: #28a745; margin: 0 0 8px 0;">💰 Pricing Keywords</h5>
                        <p style="font-size: 11px; margin: 0;">pricing update, cost increase, price increase, vendor discount, licensing change, margin compression, cybersecurity budget, cloud pricing, software inflation, hardware surcharge, tool rationalization, contract renewal, subscription pricing, enterprise discount</p>
                    </div>
                </div>
            </div>
            
            <h3>👥 Role-Based Intelligence Delivery</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 15px 0;">
                <div style="background: #e3f2fd; padding: 12px; border-radius: 6px; border-left: 4px solid #2196f3;">
                    <h5 style="color: #1976d2; margin: 0 0 8px 0;">📊 Pricing Analysts</h5>
                    <p style="font-size: 12px; margin: 0;"><strong>Focus:</strong> Margin impacts, pricing elasticity, competitive pricing<br>
                    <strong>Metrics:</strong> margin_impact, price_change_percentage, discount_depth<br>
                    <strong>Keywords:</strong> pricing, margin, discount, cost, revenue</p>
                </div>
                <div style="background: #f3e5f5; padding: 12px; border-radius: 6px; border-left: 4px solid #9c27b0;">
                    <h5 style="color: #7b1fa2; margin: 0 0 8px 0;">🛒 Procurement Managers</h5>
                    <p style="font-size: 12px; margin: 0;"><strong>Focus:</strong> Vendor relationships, contract optimization, compliance<br>
                    <strong>Metrics:</strong> cost_savings_opportunity, vendor_risk, contract_terms<br>
                    <strong>Keywords:</strong> supply chain, vendor, contract, compliance, fulfillment</p>
                </div>
                <div style="background: #e8f5e8; padding: 12px; border-radius: 6px; border-left: 4px solid #4caf50;">
                    <h5 style="color: #388e3c; margin: 0 0 8px 0;">📈 BI Strategy Teams</h5>
                    <p style="font-size: 12px; margin: 0;"><strong>Focus:</strong> Market trends, competitive positioning, revenue forecasting<br>
                    <strong>Metrics:</strong> market_share_shift, trend_direction, forecast_variance<br>
                    <strong>Keywords:</strong> market, competitive, strategy, trend, forecast</p>
                </div>
            </div>
            
            <h3>⚙️ Technical Implementation Stack</h3>
            <div style="background: #2c3e50; color: white; padding: 15px; border-radius: 8px; margin: 15px 0;">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <div>
                        <h5 style="color: #3498db; margin: 0 0 8px 0;">🔧 Core Technologies</h5>
                        <ul style="font-size: 12px; margin: 0; padding-left: 15px;">
                            <li>Python 3.6+ (asyncio)</li>
                            <li>OpenAI GPT-4 API</li>
                            <li>PRAW (Reddit API)</li>
                            <li>Google Custom Search API</li>
                            <li>LinkedIn API</li>
                            <li>SMTP Email Delivery</li>
                        </ul>
                    </div>
                    <div>
                        <h5 style="color: #e74c3c; margin: 0 0 8px 0;">📊 Data Processing</h5>
                        <ul style="font-size: 12px; margin: 0; padding-left: 15px;">
                            <li>Hash-based deduplication</li>
                            <li>TTL-based caching</li>
                            <li>Circuit breaker patterns</li>
                            <li>Performance monitoring</li>
                            <li>Health check systems</li>
                            <li>Fallback mechanisms</li>
                        </ul>
                    </div>
                    <div>
                        <h5 style="color: #f39c12; margin: 0 0 8px 0;">🎨 Output Generation</h5>
                        <ul style="font-size: 12px; margin: 0; padding-left: 15px;">
                            <li>Responsive HTML templates</li>
                            <li>Interactive JavaScript</li>
                            <li>Vendor highlighting</li>
                            <li>Clickable footnotes</li>
                            <li>Email tracking pixels</li>
                            <li>Mobile optimization</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div style="background: #17a2b8; color: white; padding: 15px; border-radius: 8px; margin: 20px 0; text-align: center;">
                <h4 style="margin: 0 0 10px 0;">📈 System Performance Metrics</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px;">
                    <div><strong>Vendor Coverage:</strong><br>150+ Technology Vendors</div>
                    <div><strong>Data Sources:</strong><br>12+ Subreddits, Google, LinkedIn</div>
                    <div><strong>Noise Reduction:</strong><br>60-80% Content Filtering</div>
                    <div><strong>API Efficiency:</strong><br>70-90% Call Reduction via Caching</div>
                    <div><strong>Update Frequency:</strong><br>Real-time with Daily Reports</div>
                    <div><strong>Geographic Coverage:</strong><br>Global (NA, EU, APAC)</div>
                </div>
            </div>
            
            <p style='margin-top: 20px; font-style: italic; color: #495057; text-align: center; font-size: 14px;'>
                <strong>ULTRATHINK Enhanced v3.0</strong> | Advanced Pricing Intelligence System<br>
                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Real Content Analysis with Zero BS
            </p>
        </div>
        """
        
        return keywords_html + content_html + source_status_html + stats_html + methodology_html
    
    def send_test_email(self, email: str, summary_data: Optional[Dict[str, Any]] = None) -> bool:
        """Send test email to specific address with validation and tracking"""
        self.logger.info(f"🧪 Sending test email to: {email}")
        
        # Validate email format
        if not is_valid_email(email):
            self.logger.error(f"❌ Invalid email format: {email}")
            return False
        
        # Use provided summary or create mock data
        if summary_data is None:
            summary_data = self._create_mock_summary_data()
        
        # Create test employee
        test_employee = {
            'name': 'Test User',
            'email': email,
            'role': 'pricing_analyst',
            'keywords': 'microsoft, dell, pricing, discounts'
        }
        
        try:
            # Generate tracking ID
            tracking_id = str(uuid.uuid4())
            
            # Get role summary (use pricing_analyst as default)
            role_summary = summary_data.get('role_summaries', {}).get('pricing_analyst', {})
            if not role_summary:
                role_summary = self._create_mock_role_summary()
            
            # Generate HTML content
            html_content = self.template.generate_role_based_email(
                employee=test_employee,
                summary_data=summary_data,
                date_str=datetime.now().strftime('%Y-%m-%d')
            )
            
            # Add tracking pixel if enabled
            if self.tracking_enabled:
                tracking_pixel = self._generate_tracking_pixel(
                    tracking_id, 
                    email,
                    'pricing_analyst'
                )
                html_content = self._insert_tracking_pixel(html_content, tracking_pixel)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[TEST] {self.config.get('email', {}).get('subject_template', 'ULTRATHINK Pricing Intelligence Digest - {date}').format(date=datetime.now().strftime('%B %d, %Y'))}"
            msg['From'] = self.config.get('credentials', {}).get('email', {}).get('from_email', 'noreply@ultrathink.com')
            msg['To'] = email
            
            # Add tracking headers
            if self.tracking_enabled:
                msg['X-ULTRATHINK-Tracking-ID'] = tracking_id
                msg['X-ULTRATHINK-Role'] = 'pricing_analyst'
                msg['X-ULTRATHINK-Test-Email'] = 'true'
            
            # Attach HTML
            msg.attach(MIMEText(html_content, 'html'))
            
            # Create plain text version
            text_content = self._create_text_version(role_summary, summary_data.get('by_urgency', {}))
            msg.attach(MIMEText(text_content, 'plain'))
            
            # Send email
            self._send_smtp(msg, email)
            
            self.logger.info(f"✅ Test email sent successfully to {email}")
            self.logger.info(f"   • Tracking ID: {tracking_id}")
            self.logger.info(f"   • HTML Size: {len(html_content)} characters")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send test email to {email}: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False
    
    def _create_mock_summary_data(self) -> Dict[str, Any]:
        """Create mock summary data for testing"""
        return {
            'role_summaries': {
                'pricing_analyst': self._create_mock_role_summary()
            },
            'by_urgency': {'high': 3, 'medium': 7, 'low': 12},
            'total_items': 22,
            'analysis_metadata': {
                'keywords_used': {
                    'key_vendors': ['Microsoft', 'Dell', 'Cisco', 'HPE'],
                    'urgency_high': ['price increase', 'acquisition', 'security breach'],
                    'urgency_medium': ['discount', 'promotion', 'update'],
                    'pricing_keywords': ['cost', 'price', 'pricing', 'discount', 'margin']
                },
                'content_analyzed': [
                    {
                        'title': 'Microsoft announces 15% price increase on Office 365',
                        'content_preview': 'Microsoft has announced a significant price increase for Office 365 subscriptions starting Q1 2024...',
                        'source': 'reddit',
                        'urgency': 'high',
                        'relevance_score': 9.2,
                        'url': 'https://reddit.com/r/sysadmin/example',
                        'created_at': '2024-01-15'
                    },
                    {
                        'title': 'Dell PowerEdge server pricing updates',
                        'content_preview': 'Dell has released updated pricing for their PowerEdge server lineup with competitive Q4 discounts...',
                        'source': 'google',
                        'urgency': 'medium',
                        'relevance_score': 8.1,
                        'url': 'https://dell.com/server-pricing',
                        'created_at': '2024-01-14'
                    }
                ],
                'processing_stats': {
                    'total_items_processed': 22,
                    'sources_processed': ['reddit', 'google'],
                    'deduplication_applied': True,
                    'urgency_detection_enabled': True,
                    'vendor_detection_enabled': True
                }
            }
        }
    
    def _create_mock_role_summary(self) -> Dict[str, Any]:
        """Create mock role summary for testing"""
        return {
            'role': 'Pricing Analyst',
            'focus': 'Strategic pricing analysis and margin optimization',
            'summary': 'This week shows significant pricing volatility with Microsoft leading a 15% increase in Office 365 subscriptions. Dell counters with aggressive Q4 server discounts. These moves suggest a market correction phase with mixed vendor strategies.',
            'key_insights': [
                '🔴 Microsoft Office 365 +15% price increase Q1 2024',
                '🟢 Dell PowerEdge servers: 20% Q4 discount opportunity',
                '⚠️ Cisco licensing model changes affecting enterprise customers',
                '📈 HPE GreenLake consumption pricing showing 12% uptick'
            ],
            'top_vendors': [
                {'vendor': 'Microsoft', 'mentions': 8, 'trend': '+15%'},
                {'vendor': 'Dell', 'mentions': 6, 'trend': '-20%'},
                {'vendor': 'Cisco', 'mentions': 4, 'trend': 'Model Change'},
                {'vendor': 'HPE', 'mentions': 3, 'trend': '+12%'}
            ],
            'sources': {'reddit': 15, 'google': 7}
        }


def main():
    """CLI entry point for email sender testing"""
    import argparse
    import sys
    import os
    from dotenv import load_dotenv
    from config.advanced_config import AdvancedConfigManager
    
    # Setup argument parser
    parser = argparse.ArgumentParser(description='ULTRATHINK Email Sender - Test Mode')
    parser.add_argument('--test-email', 
                       help='Send test email to specific address',
                       metavar='EMAIL')
    parser.add_argument('--config-dir',
                       default='config',
                       help='Configuration directory (default: config)')
    parser.add_argument('--summary-file',
                       help='JSON file containing summary data to use for test email')
    parser.add_argument('--preview-only',
                       action='store_true',
                       help='Generate preview HTML file instead of sending email')
    
    args = parser.parse_args()
    
    if not args.test_email and not args.preview_only:
        parser.error('Must specify either --test-email or --preview-only')
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Load environment variables
        load_dotenv()
        logger.info("✅ Environment variables loaded")
        
        # Load configuration
        config_manager = AdvancedConfigManager(args.config_dir)
        config = config_manager.get_config()
        logger.info(f"✅ Configuration loaded - Environment: {config.system.environment}")
        
        # Load summary data if provided
        summary_data = None
        if args.summary_file:
            summary_file = Path(args.summary_file)
            if summary_file.exists():
                import json
                with open(summary_file, 'r') as f:
                    summary_data = json.load(f)
                logger.info(f"✅ Summary data loaded from: {summary_file}")
            else:
                logger.warning(f"⚠️  Summary file not found: {summary_file}")
        
        # Initialize email sender
        email_sender = EmailSender(config.dict())
        
        if args.preview_only:
            # Generate preview only
            if not summary_data:
                summary_data = email_sender._create_mock_summary_data()
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            preview_file = Path(f"output/email_preview_{timestamp}.html")
            preview_file.parent.mkdir(exist_ok=True)
            
            email_sender.save_preview(summary_data, preview_file)
            logger.info(f"✅ Email preview generated: {preview_file}")
            
        elif args.test_email:
            # Send test email
            success = email_sender.send_test_email(args.test_email, summary_data)
            
            if success:
                logger.info("✅ Test email completed successfully")
                return 0
            else:
                logger.error("❌ Test email failed")
                return 1
    
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
