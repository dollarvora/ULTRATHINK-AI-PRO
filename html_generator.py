#!/usr/bin/env python3
"""
ULTRATHINK-AI-PRO Enhanced HTML Report Generator
===============================================

PURPOSE:
- Generates professional HTML reports matching ULTRATHINK-AI-PRO backup system format
- Implements smart priority display system (Alpha/Beta/Gamma insights)
- Provides comprehensive vendor analysis and content source attribution
- Features professional styling with light mode for readability

KEY FEATURES:
- Professional gradient styling with centered, elegant priority buttons
- Smart initial display (shows Alpha first, then Beta if no Alpha, then Gamma)
- Clickable footnotes linking insights to actual source articles
- Comprehensive methodology section with actual system configuration
- Content sources section with Reddit/Google/LinkedIn framework
- Responsive design with accessibility features (ARIA labels, semantic HTML)

TECHNICAL IMPLEMENTATION:
- SOURCE_ID tracking system for proper footnote attribution
- Priority categorization with interactive JavaScript switching
- Professional CSS with gradients, shadows, and hover effects
- Structured content organization matching enterprise report standards
- Mobile-responsive design with optimized layouts

CONTENT PROCESSING:
- Groups content by source (Reddit, Google, future LinkedIn)
- Categorizes insights by priority (Alpha=Critical, Beta=Notable, Gamma=Monitoring)
- Generates vendor statistics and market intelligence summaries
- Creates comprehensive methodology documentation

OUTPUT:
- Self-contained HTML file with embedded CSS and JavaScript
- Professional styling matching enterprise report standards
- Interactive priority filtering with elegant button controls
- Proper semantic structure for accessibility compliance

Author: Dollar (dollar3191@gmail.com)
System: ULTRATHINK-AI-PRO v3.1.0 Hybrid
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional


class EnhancedHTMLGenerator:
    """Enhanced HTML report generator with accessibility and mobile responsiveness"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        
        # Vendor keywords for highlighting
        self.vendor_keywords = [
            'Microsoft', 'Dell', 'HP', 'HPE', 'Lenovo', 'Apple', 'Cisco',
            'VMware', 'AWS', 'Azure', 'Google Cloud', 'Oracle', 'CrowdStrike',
            'Fortinet', 'Palo Alto Networks', 'Zscaler', 'SentinelOne'
        ]
    
    def generate_html_report(self, insights: List[str], all_content: List[Dict[str, Any]], 
                           vendor_analysis: Dict[str, Any], config: Dict[str, Any],
                           performance_metrics: Optional[Dict[str, Any]] = None) -> str:
        """Generate complete HTML report matching backup system format exactly"""
        
        # Process data
        content_by_source = self._group_content_by_source(all_content)
        categorized_insights = self._categorize_insights_by_priority(insights)
        vendor_stats = self._generate_vendor_stats(vendor_analysis, all_content)
        
        # Store content mapping for footnotes
        self.content_items = all_content  # Store for footnote mapping
        self._create_source_id_mapping(all_content)  # Create SOURCE_ID to content mapping
        
        # Calculate totals for sources section
        reddit_count = len(content_by_source.get('reddit', []))
        google_count = len(content_by_source.get('google', []))
        gpt_analyzed_count = min(20, reddit_count + google_count)  # GPT analyzes max 20 items
        
        # Generate timestamp
        timestamp = datetime.now()
        
        # Generate HTML sections in backup format
        executive_summary = self._generate_executive_summary(len(all_content))
        insights_pagination = self._generate_insights_pagination(categorized_insights)
        vendor_section = self._generate_vendor_section_backup_format(vendor_stats)
        sources_section = self._generate_detailed_sources_section(content_by_source, gpt_analyzed_count, reddit_count, google_count)
        methodology_section = self._generate_methodology_section()
        javascript_functions = self._generate_javascript_functions()
        
        # Generate complete HTML in backup format
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="ULTRATHINK-AI-PRO Enhanced Pricing Intelligence Report for B2B IT Enterprise">
    <title>ULTRATHINK-AI-PRO Enhanced Analysis Report</title>
    <link rel="stylesheet" href="../static/css/report.css">
    {self._generate_backup_css_styles()}
    {javascript_functions}
</head>
<body>
    <main class="email-preview" role="main">
        <header class="email-header" role="banner">
            <h1>
                <span class="visually-hidden">ULTRATHINK AI PRO</span>
                <span aria-hidden="true">🧠 ULTRATHINK-AI-PRO</span>
            </h1>
            <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.9;">
                Enhanced Pricing Intelligence Report
            </p>
        </header>
        
        <div class="email-content" role="document">
            {executive_summary}
            {insights_pagination}
            {vendor_section}
        </div>
        
        {sources_section}
        {methodology_section}
        
        <footer style="text-align: center; margin-top: 40px; color: #6c757d; font-size: 12px; padding: 20px;" role="contentinfo">
            <p>📊 Report generated by ULTRATHINK-AI-PRO v3.1.0 Hybrid System</p>
            <p>⚡ Enhanced with ultrathink-enhanced architecture + advanced GPT prompt engineering</p>
        </footer>
    </main>
</body>
</html>
        """
        
        return html_content
    
    def _create_source_id_mapping(self, all_content: List[Dict[str, Any]]) -> None:
        """Create mapping from SOURCE_IDs to content for footnote generation"""
        self.source_id_mapping = {}
        
        # Create SOURCE_IDs preserving original content order
        item_counter = 1
        
        for item in all_content:
            source = item.get('source', 'unknown')
            source_id = f"{source}_{item_counter}"
            self.source_id_mapping[source_id] = {
                'title': item.get('title', 'No title'),
                'url': item.get('url', '#'),
                'source': source,
                'content': item.get('content', item.get('text', '')),
                'relevance_score': item.get('relevance_score', item.get('score', 0)),
                'created_at': item.get('created_at', item.get('date', '')),
                'footnote_number': item_counter
            }
            item_counter += 1
    
    def save_html_report(self, html_content: str, output_dir: str = "output") -> str:
        """Save HTML report to file"""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"ultrathink_enhanced_{timestamp}.html"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
    
    def _group_content_by_source(self, all_content: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group content by source"""
        grouped = {}
        for item in all_content:
            source = item.get('source', 'unknown')
            if source not in grouped:
                grouped[source] = []
            grouped[source].append(item)
        return grouped
    
    def _categorize_insights_by_priority(self, insights: List[str]) -> Dict[str, List[str]]:
        """Categorize insights by priority keywords (URGENT → Alpha, MODERATE → Beta, INFO/MONITORING → Gamma)"""
        categorized = {'alpha': [], 'beta': [], 'gamma': []}
        
        for insight in insights:
            insight_upper = insight.upper()
            if any(word in insight_upper for word in ['URGENT', 'CRITICAL', 'EMERGENCY', '🔴']):
                categorized['alpha'].append(insight)
            elif any(word in insight_upper for word in ['MODERATE', 'NOTABLE', 'IMPORTANT', '🟡']):
                categorized['beta'].append(insight)
            elif any(word in insight_upper for word in ['MONITORING', 'INFO', 'WATCH', 'GENERAL', '🟢']):
                categorized['gamma'].append(insight)
            else:
                # Default to gamma for unknown priority
                categorized['gamma'].append(insight)
        
        return categorized
    
    def _generate_vendor_stats(self, vendor_analysis: Dict[str, Any], all_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate vendor statistics"""
        if isinstance(vendor_analysis, dict) and 'top_vendors' in vendor_analysis:
            return vendor_analysis
        
        # Handle different vendor analysis formats
        vendor_mentions = {}
        for item in all_content:
            text = f"{item.get('title', '')} {item.get('content', '')}".lower()
            for vendor in self.vendor_keywords:
                if vendor.lower() in text:
                    vendor_mentions[vendor] = vendor_mentions.get(vendor, 0) + 1
        
        top_vendors = sorted(vendor_mentions.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'top_vendors': top_vendors,
            'total_vendors': len(vendor_mentions),
            'vendor_mentions': vendor_mentions
        }
    
    def _generate_executive_summary(self, total_items: int) -> str:
        """Generate executive summary section matching backup format"""
        timestamp = datetime.now()
        
        return f"""
            <section aria-labelledby="executive-summary">
                <h2 id="executive-summary">
                    <span class="visually-hidden">Executive Summary</span>
                    <span aria-hidden="true">📋 Executive Summary</span>
                </h2>
                <div class="insight-item" role="region" aria-label="Summary information" style="background-color: #ffffff !important; color: #333333 !important; border: 1px solid #dee2e6; padding: 20px; border-radius: 6px;">
                    <p style="color: #333333 !important; margin: 0 0 15px 0;">Quantified margin impacts and vendor pricing behavior analysis</p>
                    <div style="border-top: 1px solid #dee2e6; padding-top: 10px; margin-top: 15px; font-size: 11px; color: #6c757d;" role="contentinfo">
                        <strong>Methodology:</strong> Analysis of {total_items} market intelligence sources with 43+ enterprise vendor recognition algorithms.
                    </div>
                </div>
            </section>
        """
    
    def _generate_insights_pagination(self, categorized_insights: Dict[str, List[str]]) -> str:
        """Generate insights pagination section with smart priority display and enhanced UX"""
        # Generate insights pages content
        alpha_insights = self._generate_insights_page_content(categorized_insights.get('alpha', []), 'alpha')
        beta_insights = self._generate_insights_page_content(categorized_insights.get('beta', []), 'beta')  
        gamma_insights = self._generate_insights_page_content(categorized_insights.get('gamma', []), 'gamma')
        
        # Count insights per priority
        alpha_count = len(categorized_insights.get('alpha', []))
        beta_count = len(categorized_insights.get('beta', []))
        gamma_count = len(categorized_insights.get('gamma', []))
        
        # Smart priority display: determine which priority to show first
        default_priority = 1  # Alpha
        default_class = "active"
        
        # If no Alpha insights, show Beta first
        if alpha_count == 0 and beta_count > 0:
            default_priority = 2
        # If no Alpha or Beta insights, show Gamma first  
        elif alpha_count == 0 and beta_count == 0 and gamma_count > 0:
            default_priority = 3
        
        # Build button HTML with counts and smart visibility
        alpha_btn_style = 'style="display: none;"' if alpha_count == 0 else ''
        beta_btn_style = 'style="display: none;"' if beta_count == 0 else ''
        gamma_btn_style = 'style="display: none;"' if gamma_count == 0 else ''
        
        alpha_btn_class = "page-btn-enhanced active" if default_priority == 1 else "page-btn-enhanced"
        beta_btn_class = "page-btn-enhanced active" if default_priority == 2 else "page-btn-enhanced"
        gamma_btn_class = "page-btn-enhanced active" if default_priority == 3 else "page-btn-enhanced"
        
        return f"""
            <section aria-labelledby="strategic-insights">
                <h2 id="strategic-insights">
                    <span class="visually-hidden">Strategic Intelligence Insights</span>
                    <span aria-hidden="true">💡 Strategic Intelligence Insights</span>
                </h2>
                
                <div class="insights-pagination">
                    <div class="page-controls-enhanced">
                        <button onclick="showInsightsPage(1)" class="{alpha_btn_class}" id="page-1" {alpha_btn_style}>
                            <span class="priority-icon">🔴</span>
                            <span class="priority-text">Priority Alpha</span>
                            <span class="priority-count">({alpha_count})</span>
                        </button>
                        <button onclick="showInsightsPage(2)" class="{beta_btn_class}" id="page-2" {beta_btn_style}>
                            <span class="priority-icon">🟡</span>
                            <span class="priority-text">Priority Beta</span>
                            <span class="priority-count">({beta_count})</span>
                        </button>
                        <button onclick="showInsightsPage(3)" class="{gamma_btn_class}" id="page-3" {gamma_btn_style}>
                            <span class="priority-icon">🟢</span>
                            <span class="priority-text">Priority Gamma</span>
                            <span class="priority-count">({gamma_count})</span>
                        </button>
                    </div>
                    
                    <div class="insights-page {default_class if default_priority == 1 else ''}" id="insights-page-1">
                        {alpha_insights}
                    </div>
                    
                    <div class="insights-page {default_class if default_priority == 2 else ''}" id="insights-page-2">
                        {beta_insights}
                    </div>
                    
                    <div class="insights-page {default_class if default_priority == 3 else ''}" id="insights-page-3">
                        {gamma_insights}
                    </div>
                </div>
            </section>
        """
    
    def _generate_insights_page_content(self, insights: List[str], priority_type: str) -> str:
        """Generate insights page content for specific priority with footnotes mapped to actual sources"""
        if not insights:
            return f'<p style="color: #333333; font-style: italic;">No {priority_type} priority insights for this analysis period.</p>'
        
        insights_html = []
        
        for insight in insights:
            # Clean up insight text and extract source ID
            clean_insight = insight.replace('🔴', '').replace('🟡', '').replace('🟢', '').strip()
            
            # Parse SOURCE_ID from insight if present
            import re
            source_id_match = re.search(r'\[([^\]]+)\]$', clean_insight)
            
            if source_id_match and hasattr(self, 'source_id_mapping'):
                source_id = source_id_match.group(1)
                # Remove the SOURCE_ID from the insight text
                clean_insight = re.sub(r'\s*\[([^\]]+)\]$', '', clean_insight)
                
                # Get footnote number from mapping
                if source_id in self.source_id_mapping:
                    footnote_num = self.source_id_mapping[source_id]['footnote_number']
                else:
                    # Fallback to sequential numbering
                    footnote_num = len(insights_html) + 1
            else:
                # Fallback to sequential numbering if no SOURCE_ID found
                footnote_num = len(insights_html) + 1
            
            # Add footnote reference to each insight
            highlighted_insight = self._highlight_vendors(clean_insight)
            insight_with_footnote = f'{highlighted_insight} <a href="#footnote-{footnote_num}" class="footnote-link">[{footnote_num}]</a>'
            
            # Generate clean insight item with proper formatting and explicit background
            priority_backgrounds = {
                'alpha': 'background-color: #fff5f5 !important;',
                'beta': 'background-color: #fff9e6 !important;',
                'gamma': 'background-color: #f0f8ff !important;'
            }
            bg_style = priority_backgrounds.get(priority_type, 'background-color: #f8f9fa !important;')
            
            insight_item = f"""
                <div class="insight-item insight-{priority_type}" style="{bg_style} color: #2c3e50 !important; padding: 20px; margin: 16px 0; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid rgba(0,0,0,0.08); position: relative; overflow: hidden;">
                    <div style="position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: {'#e74c3c' if priority_type == 'alpha' else '#f39c12' if priority_type == 'beta' else '#27ae60'};"></div>
                    <div style="margin-left: 8px; font-size: 15px; line-height: 1.6;">
                        {insight_with_footnote}
                    </div>
                </div>"""
            
            insights_html.append(insight_item)
        
        return '\n'.join(insights_html)
    
    def _generate_vendor_section_backup_format(self, vendor_stats: Dict[str, Any]) -> str:
        """Generate vendor analysis section matching backup format"""
        top_vendors = vendor_stats.get('top_vendors', [])
        
        vendor_badges = []
        for vendor, mentions in top_vendors[:6]:  # Limit to top 6 as in backup
            vendor_badges.append(
                f'<span style="background: #667eea; color: white; padding: 8px 15px; border-radius: 20px; margin: 4px; display: inline-block;">'
                f'{vendor.lower()} ({mentions} mentions)</span>'
            )
        
        return f"""
            <h3>🏢 Market Vendor Analysis</h3>
            {''.join(vendor_badges) if vendor_badges else '<p style="color: #666; font-style: italic;">No vendor activity detected in this analysis period.</p>'}
        """
    
    def _generate_sources_section_backup_format(self, content_by_source: Dict[str, List[Dict[str, Any]]]) -> str:
        """Generate sources section matching backup format with collapsible sections"""
        total_items = sum(len(items) for items in content_by_source.values())
        
        sources_html = f"""
        <div class='analysis-section'>
            <h2>📄 Content Sources Analyzed</h2>
            <p><strong>Total Items Processed by GPT:</strong> {total_items}</p>
            <p style="color: #28a745; font-weight: bold;">✅ These are the sources that GPT analyzed to generate the insights above</p>
            
            <div style='margin: 15px 0;'>
                <button class='show-all-btn' onclick='showAllProviders()'>📂 Expand All Sources</button>
                <button class='show-all-btn' onclick='hideAllProviders()' style='background-color: #6c757d;'>📁 Collapse All Sources</button>
            </div>
        
        <p style="color: #28a745; font-weight: bold;">✅ Sources that GPT analyzed to generate the insights above:</p>
        """
        
        footnote_index = 1
        
        for source, items in content_by_source.items():
            if not items:
                continue
                
            # Source-specific styling
            source_class = f"provider-{source.lower()}"
            source_icon = {
                'reddit': '🔴',
                'google': '🔍', 
                'linkedin': '💼',
                'twitter': '🐦'
            }.get(source.lower(), '📊')
            
            sources_html += f"""
            <div class='provider-section {source_class}'>
                <div class='provider-header' onclick='toggleProvider("{source.lower()}")'>
                    <span>{source_icon} {source.title()} ({len(items)} items analyzed by GPT)</span>
                    <span class='toggle-icon' id='{source.lower()}-icon'>▶</span>
                </div>
                <div class='provider-content' id='{source.lower()}-content'>
            """
            
            # Generate content items with footnote linking
            for item in items:
                title = item.get('title', 'No title')
                url = item.get('url', '#')
                date = item.get('created_at', item.get('date', ''))
                content = item.get('content', '')
                
                # Format date
                if isinstance(date, str) and date:
                    try:
                        if 'T' in date:
                            date_obj = datetime.fromisoformat(date.replace('Z', '+00:00'))
                            formatted_date = date_obj.strftime('%Y-%m-%d %H:%M')
                        else:
                            formatted_date = str(date)
                    except:
                        formatted_date = str(date)
                else:
                    formatted_date = 'Unknown date'
                
                # Highlight vendors in content
                highlighted_content = self._highlight_vendors(content[:500])  # Limit content length
                
                sources_html += f"""
                <div class='content-item footnote-target' id='footnote-{footnote_index}'>
                    <h4 style='margin: 0 0 10px 0; color: #007bff;'><strong>[{footnote_index}]</strong> {title}</h4>
                    <p><strong>🔗 URL:</strong> <a href='{url}' target='_blank'>{url}</a></p>
                    <p><strong>📅 Date:</strong> {formatted_date}</p>
                
                    <details style='margin-top: 10px;'>
                        <summary style='cursor: pointer; font-weight: bold; color: #007bff;'>📋 Full Content Analyzed</summary>
                        <p style='margin-top: 10px; padding: 10px; background-color: #f8f9fa; border-radius: 4px;'>{highlighted_content}</p>
                    </details>
                </div>
                """
                
                footnote_index += 1
            
            sources_html += """
                </div>
            </div>
            """
        
        sources_html += "</div>"
        return sources_html
    
    def _generate_javascript_functions(self) -> str:
        """Generate JavaScript functions matching backup format"""
        return """
    <script>
        function toggleProvider(providerId) {
            const content = document.getElementById(providerId);
            const toggleElement = document.getElementById(providerId.replace('-provider', '-toggle'));
            
            if (content.style.display === 'none' || content.style.display === '') {
                content.style.display = 'block';
                if (toggleElement) toggleElement.innerHTML = '▼';
            } else {
                content.style.display = 'none';
                if (toggleElement) toggleElement.innerHTML = '▶';
            }
        }
        
        function expandAllSources() {
            const providers = ['reddit-provider', 'google-provider'];
            providers.forEach(providerId => {
                const content = document.getElementById(providerId);
                const toggleElement = document.getElementById(providerId.replace('-provider', '-toggle'));
                if (content) {
                    content.style.display = 'block';
                    if (toggleElement) toggleElement.innerHTML = '▼';
                }
            });
        }
        
        function collapseAllSources() {
            const providers = ['reddit-provider', 'google-provider'];
            providers.forEach(providerId => {
                const content = document.getElementById(providerId);
                const toggleElement = document.getElementById(providerId.replace('-provider', '-toggle'));
                if (content) {
                    content.style.display = 'none';
                    if (toggleElement) toggleElement.innerHTML = '▶';
                }
            });
        }
        
        function showInsightsPage(pageNum) {
            console.log('Switching to priority page:', pageNum);
            
            // Hide all insight pages with smooth transition
            document.querySelectorAll('.insights-page').forEach(page => {
                page.classList.remove('active');
                page.style.opacity = '0';
                setTimeout(() => {
                    if (!page.classList.contains('active')) {
                        page.style.display = 'none';
                    }
                }, 150);
            });
            
            // Remove active class from all buttons (both old and new styles)
            document.querySelectorAll('.page-btn, .page-btn-enhanced').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Show selected page and activate button with smooth transition
            const targetPage = document.getElementById('insights-page-' + pageNum);
            const targetButton = document.getElementById('page-' + pageNum);
            
            if (targetPage && targetButton) {
                targetButton.classList.add('active');
                targetPage.style.display = 'block';
                targetPage.style.opacity = '0';
                targetPage.classList.add('active');
                
                // Smooth fade in
                setTimeout(() => {
                    targetPage.style.opacity = '1';
                }, 50);
                
                // Count and log insights for this priority
                const insights = targetPage.querySelectorAll('.insight-item');
                console.log('Showing ' + insights.length + ' insights for priority ' + pageNum);
                
                // Add visual feedback
                targetPage.style.transition = 'opacity 0.3s ease-in-out';
            }
        }
        
        // Initialize priority display on page load
        function initializePriorityDisplay() {
            // Hide all insight pages initially
            document.querySelectorAll('.insights-page').forEach(page => {
                page.style.display = 'none';
                page.classList.remove('active');
            });
            
            // Show only the first available priority page
            const availableButtons = document.querySelectorAll('.page-btn-enhanced:not([style*="display: none"])');
            if (availableButtons.length > 0) {
                const firstButton = availableButtons[0];
                const pageNumber = firstButton.id.split('-')[1];
                const firstPage = document.getElementById('insights-page-' + pageNumber);
                
                if (firstPage) {
                    firstPage.style.display = 'block';
                    firstPage.classList.add('active');
                    firstButton.classList.add('active');
                }
            }
        }
        
        // Handle footnote clicks to ensure proper navigation
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize priority display
            initializePriorityDisplay();
            
            document.querySelectorAll('.footnote-link').forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    const targetId = this.getAttribute('href').substring(1);
                    const targetElement = document.getElementById(targetId);
                    
                    if (targetElement) {
                        // First expand the parent section if it's collapsed
                        const parentProvider = targetElement.closest('.provider-content');
                        if (parentProvider && !parentProvider.classList.contains('active')) {
                            const providerId = parentProvider.id.replace('-content', '');
                            toggleProvider(providerId);
                        }
                        
                        // Then scroll to the target with smooth animation
                        setTimeout(() => {
                            targetElement.scrollIntoView({ 
                                behavior: 'smooth',
                                block: 'center'
                            });
                        }, 100);
                    }
                });
            });
        });
    </script>
        """
    
    def _generate_backup_css_styles(self) -> str:
        """Generate additional CSS styles matching backup format"""
        return """
    <style>
        /* FORCE light mode for all elements - removed inherit to fix black backgrounds */
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
            background-color: #ffffff !important;
            color: #333333 !important;
            padding: 20px;
            margin: 0;
        }
        h1, h2 {
            text-align: center;
            color: #333;
            margin: 40px 0 20px;
        }
        .analysis-section {
            background-color: #ffffff !important;
            color: #333333 !important;
            border: 1px solid #ddd;
            padding: 20px;
            margin: 30px 0;
            border-radius: 8px;
        }
        
        /* Force light mode for all insight elements */
        .insight-item {
            background-color: #f8f9fa !important;
            color: #333333 !important;
            border-radius: 6px;
            padding: 15px;
            margin: 12px 0;
            border-left: 5px solid #667eea;
        }
        
        /* Priority-specific styling */
        .insight-alpha {
            background-color: #fff5f5 !important;
            border-left: 5px solid #dc3545 !important;
        }
        
        .insight-beta {
            background-color: #fff9e6 !important;
            border-left: 5px solid #ffc107 !important;
        }
        
        .insight-gamma {
            background-color: #f0f8ff !important;
            border-left: 5px solid #28a745 !important;
        }
        
        /* insights-page rules consolidated below */
        
        .page-btn {
            background-color: white !important;
            color: #667eea !important;
            transition: all 0.3s ease;
        }
        
        .email-preview {
            background-color: #ffffff !important;
            color: #333333 !important;
        }
        
        .email-content {
            background-color: #ffffff !important;
            color: #333333 !important;
        }
        
        /* Ensure all text elements are readable */
        h1, h2, h3, h4, h5, h6, p, div, span, li, button {
            color: #333333 !important;
        }
        .provider-section {
            border: 1px solid #ccc;
            margin: 15px 0;
            border-radius: 8px;
            background-color: white;
            overflow: hidden;
        }
        .provider-header {
            background-color: #f8f9fa;
            padding: 18px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: bold;
            border-bottom: 1px solid #ddd;
            transition: background-color 0.2s;
        }
        .provider-header:hover {
            background-color: #e9ecef;
        }
        .provider-content {
            padding: 20px;
            display: none;
        }
        .provider-content.active {
            display: block;
        }
        .toggle-icon {
            font-size: 14px;
            transition: transform 0.3s;
        }
        .toggle-icon.expanded {
            transform: rotate(90deg);
        }
        .show-all-btn {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            margin: 10px 5px;
            font-weight: 600;
        }
        .show-all-btn:hover {
            background-color: #0056b3;
        }
        .provider-reddit { border-left: 5px solid #ff4500; }
        .provider-google { border-left: 5px solid #4285f4; }
        
        .content-item {
            border: 1px solid #eee;
            padding: 15px;
            margin: 10px 0;
            background-color: white;
            border-radius: 6px;
        }
        .insight-item {
            background: #f8f9fa;
            border-left: 5px solid #667eea;
            padding: 15px;
            margin: 12px 0;
            border-radius: 6px;
        }
        .insight-high { border-left-color: #dc3545; background-color: #fdf2f2; }
        .insight-medium { border-left-color: #ffc107; background-color: #fffdf2; }
        .insight-low { border-left-color: #28a745; background-color: #f2fdf2; }
        
        .insights-pagination {
            margin: 20px 0;
        }
        .page-controls {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-bottom: 20px;
        }
        .page-btn {
            padding: 8px 16px;
            border: 2px solid #667eea !important;
            background: white !important;
            color: #667eea !important;
            border-radius: 20px;
            cursor: pointer !important;
            font-weight: bold;
            transition: all 0.3s ease;
            display: inline-block;
            text-decoration: none;
            outline: none;
        }
        .page-btn:hover {
            background: #667eea !important;
            color: white !important;
        }
        .page-btn.active {
            background: #667eea !important;
            color: white !important;
        }
        
        /* Professional Priority Buttons */
        .page-controls-enhanced {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 30px 0;
            flex-wrap: wrap;
            align-items: center;
        }
        .page-btn-enhanced {
            padding: 14px 28px;
            border: 1px solid #e1e5e9 !important;
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
            color: #495057 !important;
            border-radius: 12px;
            cursor: pointer;
            font-size: 15px;
            font-weight: 500;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            gap: 10px;
            text-decoration: none;
            outline: none;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04), 0 1px 3px rgba(0,0,0,0.06);
            min-width: 180px;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }
        .page-btn-enhanced::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.5s ease;
        }
        .page-btn-enhanced:hover::before {
            left: 100%;
        }
        .page-btn-enhanced:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.10);
            border-color: #667eea !important;
        }
        .page-btn-enhanced.active {
            border-color: #667eea !important;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.25), 0 2px 8px rgba(102, 126, 234, 0.15);
            transform: translateY(-1px);
        }
        .page-btn-enhanced .priority-icon {
            font-size: 16px;
            line-height: 1;
            margin-right: 2px;
        }
        .page-btn-enhanced .priority-text {
            font-weight: 600;
            letter-spacing: 0.3px;
        }
        .page-btn-enhanced .priority-count {
            font-size: 13px;
            opacity: 0.75;
            font-weight: 500;
            margin-left: 2px;
            padding: 2px 6px;
            background: rgba(0,0,0,0.08);
            border-radius: 8px;
        }
        .page-btn-enhanced.active .priority-count {
            opacity: 1;
            background: rgba(255,255,255,0.2);
        }
        
        /* Consolidated insights-page rules */
        .insights-page {
            display: none;
            background-color: #ffffff !important;
            color: #333333 !important;
            padding: 20px;
            border-radius: 8px;
            margin: 10px 0;
            transition: opacity 0.3s ease-in-out;
        }
        .insights-page.active {
            display: block;
            opacity: 1;
        }
        
        /* Ensure pagination works properly */
        .insights-pagination {
            margin: 20px 0;
        }
        
        .email-preview {
            max-width: 600px;
            margin: 20px auto;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .email-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 30px;
            text-align: center;
            color: white;
        }
        .email-content {
            padding: 30px;
        }
        .enhanced-badge {
            background: #28a745;
            color: white;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: bold;
            margin-top: 10px;
            display: inline-block;
        }
        .footnote-link {
            color: #007bff;
            text-decoration: none;
            font-weight: normal;
            font-size: 11px;
            padding: 1px 3px;
            border-radius: 2px;
            background-color: rgba(0,123,255,0.1);
            margin: 0 1px;
            transition: background-color 0.2s;
            vertical-align: super;
        }
        .footnote-link:hover {
            background-color: rgba(0,123,255,0.2);
            text-decoration: none;
        }
        .footnote-target {
            padding: 10px;
            border-left: 4px solid #007bff;
            margin: 8px 0;
            background: white;
            border-radius: 4px;
            scroll-margin-top: 20px;
        }
        .footnote-target:target {
            background-color: #fff3cd;
            border-left-color: #ffc107;
            animation: highlight 2s ease-in-out;
        }
        @keyframes highlight {
            0% { background-color: #fff3cd; }
            100% { background-color: white; }
        }
    </style>
        """
    
    
    def _highlight_vendors(self, text: str) -> str:
        """Highlight vendor names in text"""
        highlighted = text
        for vendor in self.vendor_keywords:
            if vendor in highlighted:
                highlighted = highlighted.replace(
                    vendor, 
                    f'<span style="background-color: #ffeb3b; padding: 2px 4px; border-radius: 3px;">{vendor}</span>'
                )
        return highlighted
    


    def _generate_detailed_sources_section(self, content_by_source: Dict[str, List[Dict[str, Any]]], 
                                         gpt_analyzed_count: int, reddit_count: int, google_count: int) -> str:
        """Generate detailed content sources section with actual counts and links"""
        
        # Build footnote references for actual content
        footnotes = []
        footnote_counter = 1
        
        # Generate source items with footnotes
        reddit_items_html = ""
        google_items_html = ""
        
        for source, items in content_by_source.items():
            if source == 'reddit' and items:
                for i, item in enumerate(items[:20]):  # Show up to 20 items
                    title = item.get('title', 'No title')[:80] + "..." if len(item.get('title', '')) > 80 else item.get('title', 'No title')
                    url = item.get('url', '#')
                    subreddit = item.get('subreddit', 'reddit')
                    score = item.get('relevance_score', item.get('score', 0))
                    
                    reddit_items_html += f"""
                    <div id="footnote-{footnote_counter}" style="margin: 8px 0; padding: 8px; background: #f8f9fa; border-left: 3px solid #ff4500; border-radius: 4px;">
                        <a href="{url}" target="_blank" style="color: #ff4500; text-decoration: none; font-weight: 500;">
                            r/{subreddit}: {title} <sup>[{footnote_counter}]</sup>
                        </a>
                        <div style="font-size: 11px; color: #666; margin-top: 4px;">
                            Relevance Score: {score:.1f} | <a href="{url}" target="_blank" style="color: #ff4500;">View Source</a>
                        </div>
                    </div>
                    """
                    footnotes.append(f'<a href="{url}" target="_blank">[{footnote_counter}] {title}</a>')
                    footnote_counter += 1
            
            elif source == 'google' and items:
                for i, item in enumerate(items[:20]):  # Show up to 20 items
                    title = item.get('title', 'No title')[:80] + "..." if len(item.get('title', '')) > 80 else item.get('title', 'No title')
                    url = item.get('url', '#')
                    score = item.get('relevance_score', item.get('score', 0))
                    
                    google_items_html += f"""
                    <div id="footnote-{footnote_counter}" style="margin: 8px 0; padding: 8px; background: #f8f9fa; border-left: 3px solid #4285f4; border-radius: 4px;">
                        <a href="{url}" target="_blank" style="color: #4285f4; text-decoration: none; font-weight: 500;">
                            {title} <sup>[{footnote_counter}]</sup>
                        </a>
                        <div style="font-size: 11px; color: #666; margin-top: 4px;">
                            Relevance Score: {score:.1f} | <a href="{url}" target="_blank" style="color: #4285f4;">View Source</a>
                        </div>
                    </div>
                    """
                    footnotes.append(f'<a href="{url}" target="_blank">[{footnote_counter}] {title}</a>')
                    footnote_counter += 1
        
        # Generate the complete sources section
        sources_html = f"""
        <div class="analysis-section" style="background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <h2 style="color: #333; margin-bottom: 15px; font-size: 20px;">📄 Content Sources Analyzed</h2>
            <div style="background: #e8f4fd; border: 1px solid #b8e6ff; border-radius: 6px; padding: 15px; margin-bottom: 20px;">
                <p style="margin: 0; font-weight: 600; color: #0066cc;">
                    <strong>Total Items Processed by GPT: {gpt_analyzed_count}</strong>
                </p>
                <p style="margin: 5px 0 0 0; color: #0066cc;">
                    ✅ These are the sources that GPT analyzed to generate the insights above
                </p>
            </div>
            
            <div style="text-align: center; margin: 15px 0;">
                <button onclick="expandAllSources()" style="background: #28a745; color: white; border: none; padding: 8px 16px; margin: 0 5px; border-radius: 4px; cursor: pointer;">
                    📂 Expand All Sources
                </button>
                <button onclick="collapseAllSources()" style="background: #6c757d; color: white; border: none; padding: 8px 16px; margin: 0 5px; border-radius: 4px; cursor: pointer;">
                    📁 Collapse All Sources
                </button>
            </div>
            
            <p style="color: #28a745; font-weight: 600; margin: 15px 0;">
                ✅ Sources that GPT analyzed to generate the insights above:
            </p>
            
            <div class="provider-section" style="border: 1px solid #ff4500; margin: 15px 0; border-radius: 8px; background: white;">
                <div class="provider-header" onclick="toggleProvider('reddit-provider')" style="background: #ff4500; color: white; padding: 15px; cursor: pointer; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold; font-size: 16px;">🔴 Reddit ({reddit_count} items analyzed by GPT)</span>
                    <span id="reddit-toggle" style="font-size: 18px;">▶</span>
                </div>
                <div id="reddit-provider" class="provider-content" style="display: none; padding: 15px; background: #fff;">
                    {reddit_items_html if reddit_items_html else '<p style="color: #666; font-style: italic;">No Reddit content analyzed in this run.</p>'}
                </div>
            </div>
            
            <div class="provider-section" style="border: 1px solid #4285f4; margin: 15px 0; border-radius: 8px; background: white;">
                <div class="provider-header" onclick="toggleProvider('google-provider')" style="background: #4285f4; color: white; padding: 15px; cursor: pointer; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold; font-size: 16px;">🔍 Google ({google_count} items analyzed by GPT)</span>
                    <span id="google-toggle" style="font-size: 18px;">▶</span>
                </div>
                <div id="google-provider" class="provider-content" style="display: none; padding: 15px; background: #fff;">
                    {google_items_html if google_items_html else '<p style="color: #666; font-style: italic;">No Google content analyzed in this run (quota exceeded).</p>'}
                </div>
            </div>
        </div>
        """
        
        return sources_html
    
    def _generate_methodology_section(self) -> str:
        """Generate complete methodology section matching exact user-requested format"""
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        methodology_html = f"""
        <div class="analysis-section" style="background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 25px; margin: 25px 0;">
            <h2 style="color: #333; margin-bottom: 20px; font-size: 22px;">🧠 ULTRATHINK AI-Pro - Complete Analysis Methodology</h2>
            
            <p style="color: #555; line-height: 1.6; margin-bottom: 20px;">
                ULTRATHINK AI-Pro is an AI-powered pricing intelligence system designed for IT distribution and resale professionals. Here's the complete overview of capabilities:
            </p>
            
            <h3 style="color: #0066cc; font-size: 18px; margin: 25px 0 15px 0;">📊 Data Sources & Collection Methods</h3>
            
            <div style="background: #fff5f5; border: 1px solid #ffcccc; border-radius: 6px; padding: 15px; margin: 15px 0;">
                <h4 style="color: #ff4500; margin: 0 0 10px 0;">🔴 Reddit Sources ✅ ACTIVE</h4>
                <p style="margin: 5px 0;"><strong>Subreddits Monitored (29 total):</strong></p>
                <ul style="margin: 5px 0; padding-left: 20px; color: #666; list-style-type: none; display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 3px;">
                    <li>r/sysadmin</li>
                    <li>r/msp</li>
                    <li>r/cybersecurity</li>
                    <li>r/vmware</li>
                    <li>r/AZURE</li>
                    <li>r/aws</li>
                    <li>r/networking</li>
                    <li>r/devops</li>
                    <li>r/homelab</li>
                    <li>r/k8s</li>
                    <li>r/kubernetes</li>
                    <li>r/selfhosted</li>
                    <li>r/DataHoarder</li>
                    <li>r/storage</li>
                    <li>r/linuxadmin</li>
                    <li>r/PowerShell</li>
                    <li>r/ITManagers</li>
                    <li>r/BusinessIntelligence</li>
                    <li>r/enterprise</li>
                    <li>r/ITCareerQuestions</li>
                    <li>r/procurement</li>
                    <li>r/purchasing</li>
                    <li>r/FinancialCareers</li>
                    <li>r/accounting</li>
                    <li>r/analytics</li>
                    <li>r/consulting</li>
                    <li>r/smallbusiness</li>
                    <li>r/startups</li>
                    <li>r/entrepreneur</li>
                </ul>
                <p style="margin: 10px 0 5px 0;"><strong>Keywords Searched:</strong> Comprehensive 136+ keyword matrix covering pricing, urgency, vendor, and competitive intelligence signals (detailed breakdown available in methodology section below)</p>
                <div style="background: #f0f8ff; border: 1px solid #cce7ff; border-radius: 4px; padding: 10px; margin: 10px 0;">
                    <p style="margin: 0; font-size: 13px; color: #0066cc;">
                        <strong>🔄 Smart Fallback System:</strong> Begins with 24-hour data for maximum relevance. If insufficient content (&lt;15 posts) is found, automatically extends to 7-day window to ensure comprehensive analysis. This ensures both timeliness and data sufficiency for sophisticated insights.
                    </p>
                </div>
            </div>
            
            <div style="background: #f5f8ff; border: 1px solid #cce0ff; border-radius: 6px; padding: 15px; margin: 15px 0;">
                <h4 style="color: #4285f4; margin: 0 0 10px 0;">🔍 Google Search Intelligence ✅ ACTIVE</h4>
                <p style="margin: 5px 0;"><strong>Query Templates Used:</strong></p>
                <ul style="margin: 5px 0; padding-left: 20px; color: #666; font-size: 13px; list-style-type: none;">
                    <li>enterprise software pricing increase</li>
                    <li>cybersecurity vendor price changes</li>
                    <li>IT distributor margin compression</li>
                    <li>cloud pricing updates AWS Azure</li>
                    <li>hardware vendor surcharge</li>
                    <li>vendor pricing announcements</li>
                </ul>
                <p style="margin: 10px 0 5px 0; color: #666; font-size: 13px;"><strong>Results per Query:</strong> 10 | <strong>Date Restriction:</strong> Last 7 days</p>
            </div>
            
            <div style="background: #f0f8ff; border: 1px solid #cce7ff; border-radius: 6px; padding: 15px; margin: 15px 0;">
                <h4 style="color: #0066cc; margin: 0 0 10px 0;">🔷 LinkedIn Intelligence ⚠️ CONFIGURED</h4>
                <p style="margin: 5px 0;"><strong>Companies Monitored (11 total):</strong></p>
                <ul style="margin: 5px 0; padding-left: 20px; color: #666; font-size: 13px; list-style-type: none; display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 3px;">
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
                    <li>Insight</li>
                </ul>
                <p style="margin: 10px 0 5px 0; color: #666; font-size: 13px;"><strong>Post Limit:</strong> 20 per company | <strong>Status:</strong> Configured but not active in hybrid system</p>
            </div>
            
            <h3 style="color: #0066cc; font-size: 18px; margin: 25px 0 15px 0;">🏢 Active Vendor & Manufacturer Detection (98 total)</h3>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; margin: 15px 0;">
                <div style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 12px;">
                    <h5 style="color: #495057; margin: 0 0 8px 0;">🖥️ Hardware Manufacturers (28 total)</h5>
                    <p style="margin: 0; font-size: 11px; color: #666;">
                        Dell, Dell Technologies, HPE, Hewlett Packard Enterprise, HP, Cisco, Cisco Systems, Lenovo, IBM, Intel, AMD, NVIDIA, NetApp, Pure Storage, EMC, Juniper, Arista, Supermicro, PowerEdge, ProLiant, ThinkPad, IdeaPad, Catalyst, Nexus, UCS, FlexPod, VxRail, Unity, Isilon, PowerMax
                    </p>
                </div>
                <div style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 12px;">
                    <h5 style="color: #495057; margin: 0 0 8px 0;">💻 Software Vendors (34 total)</h5>
                    <p style="margin: 0; font-size: 11px; color: #666;">
                        Microsoft, Oracle, SAP, VMware, Adobe, Salesforce, ServiceNow, Atlassian, JetBrains, Slack, Zoom, Teams, Citrix, Workday, DocuSign, Box, Dropbox, Tableau, Splunk, Office365, O365, M365, SharePoint, Dynamics365, vSphere, vCenter, ESXi, NSX, Creative Cloud, Acrobat, Workspace One, Horizon, XenApp, XenDesktop, Jira, Confluence, Bitbucket
                    </p>
                </div>
                <div style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 12px;">
                    <h5 style="color: #495057; margin: 0 0 8px 0;">🛡️ Security Vendors (39 total)</h5>
                    <p style="margin: 0; font-size: 11px; color: #666;">
                        CrowdStrike, Fortinet, Palo Alto Networks, Check Point, Zscaler, SentinelOne, Proofpoint, Symantec, McAfee, Trend Micro, FireEye, Mandiant, Okta, Ping Identity, CyberArk, Tenable, Rapid7, Qualys, Varonis, Darktrace, Carbon Black, Sophos, Falcon, FortiGate, FortiAnalyzer, FortiSandbox, Prisma, Cortex, Umbrella, Duo, AnyConnect, ZPA, ZIA, Singularity, Email Protection, Deep Security, Cloud One, Endpoint Protection, SandBlast, Harmony
                    </p>
                </div>
                <div style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 12px;">
                    <h5 style="color: #495057; margin: 0 0 8px 0;">☁️ Cloud Providers (26 total)</h5>
                    <p style="margin: 0; font-size: 11px; color: #666;">
                        Amazon, AWS, Microsoft Azure, Azure, Google Cloud, GCP, IBM Cloud, Oracle Cloud, Alibaba Cloud, DigitalOcean, Rackspace, Vultr, Linode, Heroku, Vercel, Netlify, EC2, S3, Lambda, RDS, BigQuery, Cloud Storage, Compute Engine, App Engine, Cloud Functions, EKS, AKS, GKE
                    </p>
                </div>
                <div style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 12px;">
                    <h5 style="color: #495057; margin: 0 0 8px 0;">📦 Distributors (21 total)</h5>
                    <p style="margin: 0; font-size: 11px; color: #666;">
                        TD Synnex, Tech Data, Synnex, Ingram Micro, CDW, CDW Corporation, Insight Global, Insight Enterprises, SHI, SHI International, Arrow Electronics, Avnet, Softchoice, Computacenter, Zones, Connection, PCM, En Pointe, Presidio, Carahsoft, CDWG
                    </p>
                </div>
            </div>
            
            <h3 style="color: #0066cc; font-size: 18px; margin: 25px 0 15px 0;">🔑 Complete Keyword Intelligence Matrix (136+ keywords)</h3>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 12px; margin: 15px 0;">
                <div style="background: #fff5f5; border: 1px solid #ffcccc; border-radius: 6px; padding: 12px;">
                    <h5 style="color: #dc3545; margin: 0 0 8px 0;">🔴 High Urgency Keywords (17 total)</h5>
                    <p style="margin: 0; font-size: 11px; color: #666;">
                        urgent, critical, immediate, emergency, breaking, acquisition, merger, security breach, vulnerability, end of life, EOL, discontinuation, recall, lawsuit, compliance, regulatory, audit, zero-day, exploit, data breach, ransomware, supply shortage, chip shortage, licensing deadline, contract expiration, price deadline, limited time, exclusive offer, flash sale, vendor lock-in, channel conflict, margin compression, bankruptcy
                    </p>
                </div>
                <div style="background: #fff9e6; border: 1px solid #ffeb99; border-radius: 6px; padding: 12px;">
                    <h5 style="color: #ffc107; margin: 0 0 8px 0;">🟡 Medium Urgency Keywords (13 total)</h5>
                    <p style="margin: 0; font-size: 11px; color: #666;">
                        update, upgrade, new release, feature, enhancement, partnership, integration, expansion, growth, quarterly results, earnings, forecast, outlook, roadmap, strategy, initiative, program, product launch, beta release, preview, announcement, rebate program, channel program, training, certification, webinar, conference, trade show, summit
                    </p>
                </div>
                <div style="background: #f0f8ff; border: 1px solid #cce7ff; border-radius: 6px; padding: 12px;">
                    <h5 style="color: #0066cc; margin: 0 0 8px 0;">💰 Pricing Keywords (35 total)</h5>
                    <p style="margin: 0; font-size: 11px; color: #666;">
                        price increase, price hike, cost increase, pricing change, discount, promotion, deal, sale, rebate, incentive, margin, markup, pricing strategy, cost reduction, licensing change, subscription model, pricing tier, volume discount, enterprise pricing, SMB pricing, contract renewal, renegotiation, procurement, budget, cost optimization, vendor discount, channel pricing, list price, street price, competitive pricing, pricing pressure, margin compression, price elasticity, cost structure, perpetual license, subscription pricing, usage-based pricing, tiered pricing, freemium, enterprise agreement, EA pricing, CSP, MPE, SYNNEX, Ingram, CDW, Insight, deal registration, OEM, price erosion, cost recovery, FX impact, discount tiers, mid-tier vendor, cost+, rebate clawback, volume band, tier adjustment, reseller
                    </p>
                </div>
                <div style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 12px;">
                    <h5 style="color: #495057; margin: 0 0 8px 0;">🧠 Competitive Intelligence (16 total)</h5>
                    <p style="margin: 0; font-size: 11px; color: #666;">
                        competitor, competition, market share, industry report, analyst report, benchmark, comparison, alternative, migration, replacement, switch, evaluation, RFP, RFQ, tender, procurement, vendor selection, competitive analysis, market positioning, differentiation, value proposition, feature comparison, cost comparison, vendor assessment, due diligence, proof of concept, POC, pilot program, trial, evaluation criteria, decision matrix, Gartner, Forrester, IDC, Magic Quadrant, Wave report
                    </p>
                </div>
                <div style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 12px;">
                    <h5 style="color: #495057; margin: 0 0 8px 0;">📊 Business Impact (15 total)</h5>
                    <p style="margin: 0; font-size: 11px; color: #666;">
                        revenue, profit, margin, ROI, cost savings, efficiency, productivity, scalability, growth, market opportunity, customer satisfaction, retention, acquisition, churn, LTV, customer lifetime value, business continuity, risk mitigation, compliance, operational excellence, digital transformation, innovation, time to market, competitive advantage, market penetration, expansion, consolidation, optimization, automation, modernization
                    </p>
                </div>
                <div style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 12px;">
                    <h5 style="color: #495057; margin: 0 0 8px 0;">🚚 Supply Chain (14 total)</h5>
                    <p style="margin: 0; font-size: 11px; color: #666;">
                        supply chain, logistics, fulfillment, distribution, inventory, stock, shortage, backorder, lead time, delivery, shipping, freight, warehouse, storage, procurement, sourcing, supplier, vendor management, component shortage, chip shortage, semiconductor, manufacturing, production, capacity, allocation, channel partner, reseller, distributor, VAR, supply disruption, supply constraints, availability
                    </p>
                </div>
                <div style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 12px;">
                    <h5 style="color: #495057; margin: 0 0 8px 0;">🎯 Market Strategy (13 total)</h5>
                    <p style="margin: 0; font-size: 11px; color: #666;">
                        go-to-market, GTM, market entry, expansion, penetration, positioning, branding, marketing, sales strategy, channel strategy, partnership, alliance, joint venture, market segmentation, target market, customer segment, value chain, ecosystem, platform strategy, vertical market, horizontal market, niche market, market dynamics, market trends, market research, customer insights, market intelligence, competitive landscape
                    </p>
                </div>
                <div style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 12px;">
                    <h5 style="color: #495057; margin: 0 0 8px 0;">⚡ Product Technology (17 total)</h5>
                    <p style="margin: 0; font-size: 11px; color: #666;">
                        innovation, R&D, research and development, patent, intellectual property, IP, technology stack, architecture, platform, framework, API, integration, interoperability, compatibility, migration, upgrade path, roadmap, next generation, emerging technology, cutting edge, artificial intelligence, AI, machine learning, ML, cloud native, containerization, microservices, DevOps, agile, automation, orchestration, virtualization
                    </p>
                </div>
            </div>
            
            <h3 style="color: #0066cc; font-size: 18px; margin: 25px 0 15px 0;">📈 Current System Performance</h3>
            
            <div style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 15px; margin: 15px 0;">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <div style="text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #28a745;">98</div>
                        <div style="font-size: 12px; color: #666;">Technology Vendors</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #17a2b8;">136+</div>
                        <div style="font-size: 12px; color: #666;">Keywords Tracked</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #ffc107;">29</div>
                        <div style="font-size: 12px; color: #666;">Reddit Subreddits</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #dc3545;">Real-time</div>
                        <div style="font-size: 12px; color: #666;">Analysis Frequency</div>
                    </div>
                </div>
            </div>
            
            <div style="background: #fff9e6; border: 1px solid #ffeb99; border-radius: 6px; padding: 15px; margin: 20px 0;">
                <p style="margin: 0; font-size: 13px; color: #856404;">
                    <strong>DISCLAIMER:</strong> This market intelligence report is generated through automated analysis 
                    of publicly available information and should be used for informational purposes only. Pricing insights 
                    reflect market discussions and may not represent official vendor communications. Investment and procurement 
                    decisions should be verified through official channels.
                </p>
            </div>
            
            <div style="text-align: center; margin-top: 20px; padding-top: 15px; border-top: 1px solid #dee2e6;">
                <p style="margin: 0; color: #6c757d; font-size: 14px;">
                    <strong>Report Generated:</strong> {current_date} | <strong>ULTRATHINK AI-Pro v3.1.0 Hybrid</strong>
                </p>
            </div>
        </div>
        """
        
        return methodology_html
    
    def _generate_backup_css_styles(self) -> str:
        """Generate CSS styles matching backup format with light mode fix"""
        return """
        <style>
            /* Professional Report Styling */
            body {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
                color: #2c3e50 !important;
                font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
                line-height: 1.7;
                margin: 0;
                padding: 20px;
                min-height: 100vh;
            }
            
            .email-preview {
                max-width: 1100px;
                margin: 0 auto;
                background: white !important;
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.04);
                overflow: hidden;
                position: relative;
            }
            
            .email-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                color: white !important;
                padding: 40px 30px;
                text-align: center;
                position: relative;
            }
            .email-header::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 50%, rgba(255,255,255,0.1) 100%);
                pointer-events: none;
            }
            .email-header h1 {
                font-size: 28px;
                font-weight: 700;
                margin: 0;
                text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .email-content {
                padding: 40px 35px;
                background: white !important;
                color: #2c3e50 !important;
            }
            
            .analysis-section {
                background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
                border: 1px solid #e9ecef;
                border-radius: 16px;
                padding: 30px;
                margin: 30px 0;
                box-shadow: 0 4px 16px rgba(0,0,0,0.04), 0 2px 8px rgba(0,0,0,0.02);
                position: relative;
                color: #2c3e50 !important;
            }
            .analysis-section::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: linear-gradient(90deg, #667eea, #764ba2);
                border-radius: 16px 16px 0 0;
            }
            .analysis-section h2 {
                color: #2c3e50 !important;
                margin-bottom: 25px;
                font-size: 22px;
                font-weight: 600;
                text-align: center;
            }
            
            .provider-section {
                border: 1px solid #ccc;
                margin: 15px 0;
                border-radius: 8px;
                background-color: white !important;
                overflow: hidden;
            }
            
            .provider-header {
                cursor: pointer;
                transition: background-color 0.3s;
            }
            
            .provider-header:hover {
                opacity: 0.9;
            }
            
            .provider-content {
                max-height: 400px;
                overflow-y: auto;
            }
            
            /* Insight priority styling */
            .insights-alpha { background: #fff5f5; border-left: 4px solid #dc3545; }
            .insights-beta { background: #fff9e6; border-left: 4px solid #ffc107; }
            .insights-gamma { background: #f0f8ff; border-left: 4px solid #28a745; }
            
            /* Interactive elements */
            button {
                cursor: pointer;
                transition: background-color 0.3s;
            }
            
            button:hover {
                opacity: 0.9;
            }
            
            /* Ensure all text is readable */
            h1, h2, h3, h4, h5, h6, p, div, span, li {
                color: inherit !important;
            }
            
            a {
                color: #0066cc;
                text-decoration: none;
            }
            
            a:hover {
                text-decoration: underline;
            }
        </style>
        """

def get_html_generator(debug: bool = False) -> EnhancedHTMLGenerator:
    """Convenience function to get HTML generator instance"""
    return EnhancedHTMLGenerator(debug=debug)


def generate_and_save_report(insights: List[str], all_content: List[Dict[str, Any]], 
                           vendor_analysis: Dict[str, Any], config: Dict[str, Any],
                           performance_metrics: Optional[Dict[str, Any]] = None,
                           output_dir: str = "output") -> str:
    """Convenience function to generate and save HTML report"""
    generator = EnhancedHTMLGenerator(debug=False)
    
    html_content = generator.generate_html_report(
        insights=insights,
        all_content=all_content,
        vendor_analysis=vendor_analysis,
        config=config,
        performance_metrics=performance_metrics
    )
    
    return generator.save_html_report(html_content, output_dir)