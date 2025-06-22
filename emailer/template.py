"""
Enhanced Email Template with Vendor Trends and Visual Design
"""

from datetime import datetime
from typing import Dict, List, Any


class EmailTemplate:
    """Professional HTML email template with vendor trends and responsive design"""
    
    def render(self, role_summary: Dict[str, Any], urgency_counts: Dict[str, int], 
               total_items: int) -> str:
        """Render the email template with enhanced styling and vendor trends"""
        
        # Calculate vendor trends
        vendor_trends = self._calculate_vendor_trends(role_summary.get('top_vendors', []))
        
        # Generate urgency chart
        urgency_chart = self._create_urgency_chart(urgency_counts)
        
        # Generate vendor trend badges
        vendor_badges = self._create_vendor_badges(vendor_trends)
        
        # Generate key insights with visual indicators
        insights_html = self._create_insights_section(role_summary.get('key_insights', []))
        
        # Generate source breakdown
        sources_html = self._create_sources_section(role_summary.get('sources', {}))
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ULTRATHINK Pricing Intelligence Digest</title>
    <!--[if mso]>
    <noscript>
        <xml>
            <o:OfficeDocumentSettings>
                <o:PixelsPerInch>96</o:PixelsPerInch>
            </o:OfficeDocumentSettings>
        </xml>
    </noscript>
    <![endif]-->
    <style>
        /* Reset styles */
        body, table, td, a {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
        table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
        img {{ -ms-interpolation-mode: bicubic; }}
        
        /* Remove default styling */
        img {{ border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }}
        table {{ border-collapse: collapse !important; }}
        body {{ height: 100% !important; margin: 0 !important; padding: 0 !important; width: 100% !important; }}
        
        /* Mobile styles */
        @media screen and (max-width: 600px) {{
            .mobile-hide {{ display: none !important; }}
            .mobile-center {{ text-align: center !important; }}
            .container {{ padding: 10px !important; }}
            h1 {{ font-size: 24px !important; }}
            h2 {{ font-size: 20px !important; }}
            h3 {{ font-size: 18px !important; }}
        }}
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {{
            .darkmode-bg {{ background-color: #1e1e1e !important; }}
            .darkmode-text {{ color: #ffffff !important; }}
        }}
    </style>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
    <table border="0" cellpadding="0" cellspacing="0" width="100%">
        <tr>
            <td align="center" style="padding: 40px 0;">
                <table class="container" border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; border-radius: 8px 8px 0 0;">
                            <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                <tr>
                                    <td>
                                        <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 700; text-align: center;">
                                            🧠 ULTRATHINK
                                        </h1>
                                        <p style="margin: 10px 0 0 0; color: #ffffff; font-size: 16px; text-align: center; opacity: 0.9;">
                                            Pricing Intelligence Digest
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Date and Role Info -->
                    <tr>
                        <td style="padding: 30px 30px 20px;">
                            <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                <tr>
                                    <td style="background-color: #f8f9fa; padding: 15px; border-radius: 6px;">
                                        <p style="margin: 0; color: #666; font-size: 14px;">
                                            <strong>Date:</strong> {datetime.now().strftime('%B %d, %Y')}
                                        </p>
                                        <p style="margin: 5px 0 0 0; color: #333; font-size: 16px;">
                                            <strong>Role:</strong> {role_summary.get('role', 'N/A')}
                                        </p>
                                        <p style="margin: 5px 0 0 0; color: #666; font-size: 14px;">
                                            <strong>Focus:</strong> {role_summary.get('focus', 'General market intelligence')}
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Urgency Overview -->
                    <tr>
                        <td style="padding: 0 30px 30px;">
                            <h2 style="color: #333; font-size: 22px; margin: 0 0 15px 0;">
                                ⚡ Urgency Overview
                            </h2>
                            {urgency_chart}
                        </td>
                    </tr>
                    
                    <!-- Executive Summary -->
                    <tr>
                        <td style="padding: 0 30px 30px;">
                            <h2 style="color: #333; font-size: 22px; margin: 0 0 15px 0;">
                                📋 Executive Summary
                            </h2>
                            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 6px; border-left: 4px solid #667eea;">
                                <p style="margin: 0; color: #333; font-size: 16px; line-height: 1.6;">
                                    {role_summary.get('summary', 'No summary available for this analysis period.')}
                                </p>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Vendor Trends -->
                    <tr>
                        <td style="padding: 0 30px 30px;">
                            <h2 style="color: #333; font-size: 22px; margin: 0 0 15px 0;">
                                📊 Vendor Activity & Trends
                            </h2>
                            {vendor_badges}
                        </td>
                    </tr>
                    
                    <!-- Key Insights -->
                    <tr>
                        <td style="padding: 0 30px 30px;">
                            <h2 style="color: #333; font-size: 22px; margin: 0 0 15px 0;">
                                💡 Key Insights
                            </h2>
                            {insights_html}
                        </td>
                    </tr>
                    
                    <!-- Sources -->
                    <tr>
                        <td style="padding: 0 30px 30px;">
                            <h2 style="color: #333; font-size: 22px; margin: 0 0 15px 0;">
                                📡 Data Sources
                            </h2>
                            {sources_html}
                        </td>
                    </tr>
                    
                    <!-- CTA Button -->
                    <tr>
                        <td style="padding: 0 30px 30px; text-align: center;">
                            <a href="#" style="display: inline-block; padding: 15px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px;">
                                View Full Dashboard →
                            </a>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px;">
                            <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                <tr>
                                    <td align="center">
                                        <p style="margin: 0; color: #999; font-size: 13px;">
                                            This email was generated by ULTRATHINK Pricing Intelligence System
                                        </p>
                                        <p style="margin: 5px 0 0 0; color: #999; font-size: 13px;">
                                            Analyzing {total_items} items from multiple sources
                                        </p>
                                        <p style="margin: 15px 0 0 0; color: #999; font-size: 12px;">
                                            © 2024 ULTRATHINK | <a href="#" style="color: #667eea; text-decoration: none;">Unsubscribe</a> | <a href="#" style="color: #667eea; text-decoration: none;">Preferences</a>
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
        return html
    
    def _calculate_vendor_trends(self, vendors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate vendor trends based on mentions"""
        trends = []
        for vendor in vendors[:5]:  # Top 5 vendors
            mentions = vendor.get('mentions', 0)
            # Simulate trend calculation (in real implementation, compare with historical data)
            if mentions > 10:
                trend = '+30%'
                trend_color = '#28a745'
                trend_icon = '↑'
            elif mentions > 5:
                trend = '+15%'
                trend_color = '#ffc107'
                trend_icon = '↗'
            else:
                trend = 'stable'
                trend_color = '#6c757d'
                trend_icon = '→'
            
            trends.append({
                'vendor': vendor['vendor'],
                'mentions': mentions,
                'trend': trend,
                'trend_color': trend_color,
                'trend_icon': trend_icon,
                'highlighted': vendor.get('highlighted', False)
            })
        
        return trends
    
    def _create_urgency_chart(self, urgency_counts: Dict[str, int]) -> str:
        """Create visual urgency chart"""
        total = sum(urgency_counts.values())
        if total == 0:
            total = 1  # Avoid division by zero
        
        high_pct = (urgency_counts.get('high', 0) / total) * 100
        medium_pct = (urgency_counts.get('medium', 0) / total) * 100
        low_pct = (urgency_counts.get('low', 0) / total) * 100
        
        return f"""
        <table width="100%" border="0" cellspacing="0" cellpadding="0">
            <tr>
                <td>
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 6px;">
                        <!-- Progress Bar -->
                        <div style="height: 30px; background-color: #e9ecef; border-radius: 15px; overflow: hidden; margin-bottom: 15px;">
                            <div style="height: 100%; width: {high_pct:.0f}%; background-color: #dc3545; float: left;"></div>
                            <div style="height: 100%; width: {medium_pct:.0f}%; background-color: #ffc107; float: left;"></div>
                            <div style="height: 100%; width: {low_pct:.0f}%; background-color: #28a745; float: left;"></div>
                        </div>
                        <!-- Legend -->
                        <table width="100%" border="0" cellspacing="0" cellpadding="0">
                            <tr>
                                <td width="33%" align="center">
                                    <span style="display: inline-block; width: 12px; height: 12px; background-color: #dc3545; border-radius: 2px;"></span>
                                    <span style="color: #666; font-size: 14px; margin-left: 5px;">High ({urgency_counts.get('high', 0)})</span>
                                </td>
                                <td width="33%" align="center">
                                    <span style="display: inline-block; width: 12px; height: 12px; background-color: #ffc107; border-radius: 2px;"></span>
                                    <span style="color: #666; font-size: 14px; margin-left: 5px;">Medium ({urgency_counts.get('medium', 0)})</span>
                                </td>
                                <td width="33%" align="center">
                                    <span style="display: inline-block; width: 12px; height: 12px; background-color: #28a745; border-radius: 2px;"></span>
                                    <span style="color: #666; font-size: 14px; margin-left: 5px;">Low ({urgency_counts.get('low', 0)})</span>
                                </td>
                            </tr>
                        </table>
                    </div>
                </td>
            </tr>
        </table>
        """
    
    def _create_vendor_badges(self, vendor_trends: List[Dict[str, Any]]) -> str:
        """Create vendor trend badges"""
        if not vendor_trends:
            return '<p style="color: #666; font-style: italic;">No vendor activity detected in this period.</p>'
        
        badges_html = '<table width="100%" border="0" cellspacing="0" cellpadding="0"><tr><td>'
        
        for i, vendor in enumerate(vendor_trends):
            if i > 0 and i % 2 == 0:
                badges_html += '</td></tr><tr><td style="padding-top: 10px;">'
            
            badge_style = 'background-color: #667eea;' if vendor['highlighted'] else 'background-color: #f8f9fa; border: 1px solid #dee2e6;'
            text_color = '#ffffff' if vendor['highlighted'] else '#333'
            
            badges_html += f"""
            <div style="display: inline-block; margin-right: 10px; margin-bottom: 10px; padding: 10px 15px; {badge_style} border-radius: 20px;">
                <span style="color: {text_color}; font-weight: 600;">{vendor['vendor']}</span>
                <span style="color: {text_color}; margin: 0 5px;">•</span>
                <span style="color: {text_color};">{vendor['mentions']} mentions</span>
                <span style="color: {vendor['trend_color']}; font-weight: 600; margin-left: 5px;">{vendor['trend_icon']} {vendor['trend']}</span>
            </div>
            """
        
        badges_html += '</td></tr></table>'
        return badges_html
    
    def _create_insights_section(self, insights: List[str]) -> str:
        """Create insights section with visual indicators"""
        if not insights:
            return '<p style="color: #666; font-style: italic;">No critical insights for this analysis period.</p>'
        
        insights_html = '<table width="100%" border="0" cellspacing="0" cellpadding="0">'
        
        for insight in insights[:5]:  # Limit to top 5
            # Determine insight type by emoji/indicator
            if '🔴' in insight or 'urgent' in insight.lower() or 'critical' in insight.lower():
                border_color = '#dc3545'
                bg_color = '#f8d7da'
            elif '🟡' in insight or 'medium' in insight.lower() or 'warning' in insight.lower():
                border_color = '#ffc107'
                bg_color = '#fff3cd'
            else:
                border_color = '#28a745'
                bg_color = '#d4edda'
            
            insights_html += f"""
            <tr>
                <td style="padding-bottom: 10px;">
                    <div style="background-color: {bg_color}; border-left: 4px solid {border_color}; padding: 15px; border-radius: 4px;">
                        <p style="margin: 0; color: #333; font-size: 15px; line-height: 1.5;">
                            {insight}
                        </p>
                    </div>
                </td>
            </tr>
            """
        
        insights_html += '</table>'
        return insights_html
    
    def _create_sources_section(self, sources: Dict[str, int]) -> str:
        """Create sources breakdown section"""
        if not sources:
            return '<p style="color: #666; font-style: italic;">No source data available.</p>'
        
        sources_html = '<table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f8f9fa; border-radius: 6px; padding: 15px;">'
        
        for source, count in sources.items():
            icon = {
                'reddit': '🔴',
                'google': '🔵',
                'linkedin': '🔷',
                'twitter': '🐦'
            }.get(source.lower(), '📊')
            
            sources_html += f"""
            <tr>
                <td style="padding: 5px 15px;">
                    <span style="font-size: 20px; vertical-align: middle;">{icon}</span>
                    <span style="color: #333; font-size: 16px; margin-left: 10px; vertical-align: middle;">
                        <strong>{source}</strong>: {count} items analyzed
                    </span>
                </td>
            </tr>
            """
        
        sources_html += '</table>'
        return sources_html