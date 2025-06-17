"""
Email Sender
Handles email composition and delivery
"""

import smtplib
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List

#from .template import build_html
from .template import EmailTemplate


class EmailSender:
    """Handles email sending for pricing intelligence digests"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.template = EmailTemplate()
        
        # Load employee list
        self.employees = self._load_employees()
    
    def _load_employees(self) -> pd.DataFrame:
        """Load employee list from CSV"""
        csv_path = Path(self.config['email']['employee_csv'])
        
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            # Filter active employees only
            return df[df['active'] == True]
        else:
            self.logger.warning(f"Employee CSV not found at {csv_path}")
            # Return empty dataframe with expected columns
            return pd.DataFrame(columns=['name', 'email', 'role', 'keywords'])
    
    def send_digest(self, summaries: Dict[str, Any]) -> None:
        """Send email digests to all active employees"""
        if not self.config['email']['enabled']:
            self.logger.info("Email sending is disabled")
            return
        
        # Get urgency counts
        urgency_counts = summaries['by_urgency']
        total_items = summaries['total_items']
        
        # Group employees by role
        role_groups = self.employees.groupby('role')
        
        for role, employees in role_groups:
            if role not in summaries['role_summaries']:
                self.logger.warning(f"No summary generated for role: {role}")
                continue
            
            role_summary = summaries['role_summaries'][role]
            
            # Send to each employee in this role
            for _, employee in employees.iterrows():
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
        """Send email to a single recipient"""
        
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
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = self.config['email']['subject_template'].format(
            date=datetime.now().strftime('%B %d, %Y')
        )
        msg['From'] = self.config['credentials']['email']['from_email']
        msg['To'] = employee['email']
        
        # Attach HTML
        msg.attach(MIMEText(html_content, 'html'))
        
        # Also create plain text version
        text_content = self._create_text_version(personalized_summary, urgency_counts)
        msg.attach(MIMEText(text_content, 'plain'))
        
        # Send email
        self._send_smtp(msg, employee['email'])
        self.logger.info(f"Email sent to {employee['name']} ({employee['email']})")
    
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
        
        # Methodology footer
        methodology_html = f"""
        <div class='analysis-section' style='background-color: #e9ecef; border-color: #adb5bd;'>
            <h2>🧠 Analysis Methodology</h2>
            <p><strong>ULTRATHINK</strong> is an AI-powered pricing intelligence system designed for IT distribution and resale professionals. Here's how it works:</p>
            
            <h3>📊 Data Collection</h3>
            <ul>
                <li><strong>Reddit:</strong> Monitors 9 key subreddits (sysadmin, msp, cybersecurity, ITManagers, procurement, enterprise, cloudcomputing, aws, azure)</li>
                <li><strong>Google:</strong> Executes strategic search queries for pricing changes, vendor updates, and market shifts</li>
                <li><strong>LinkedIn:</strong> Tracks professional network discussions and vendor announcements</li>
            </ul>
            
            <h3>🎯 Content-Aware Analysis</h3>
            <ul>
                <li><strong>Vendor Detection:</strong> Monitors 32 key technology vendors (Dell, Microsoft, Cisco, Lenovo, Apple, HP, HPE, CrowdStrike, Fortinet, Proofpoint, Zscaler, SentinelOne, Palo Alto Networks, Check Point, Splunk, VMware, Amazon, AWS, Azure, Google Cloud, Oracle, TD Synnex, Ingram Micro, CDW, Insight Global, SHI, Broadcom, Intel, AMD, NVIDIA, NetApp, Pure Storage)</li>
                <li><strong>Urgency Classification:</strong> Uses strategic keywords to identify high-impact events (acquisitions, security breaches, pricing changes)</li>
                <li><strong>Role-Specific Filtering:</strong> Tailors insights for Pricing Analysts, Procurement Managers, and BI Strategy teams</li>
            </ul>
            
            <h3>🔄 Quality Assurance</h3>
            <ul>
                <li><strong>Deduplication:</strong> Removes duplicate content across sources</li>
                <li><strong>Relevance Scoring:</strong> Ranks content by business impact and industry relevance</li>
                <li><strong>Fallback Processing:</strong> Continues operation even if individual sources fail</li>
            </ul>
            
            <p style='margin-top: 20px; font-style: italic; color: #495057;'>
                Generated by ULTRATHINK v1.0 | Softchoice Pricing Intelligence | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </div>
        """
        
        return keywords_html + content_html + source_status_html + stats_html + methodology_html
