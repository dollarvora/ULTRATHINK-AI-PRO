"""
ULTRATHINK-AI-PRO Hybrid GPT Summarizer - Advanced Pricing Intelligence Analysis
===============================================================================

PURPOSE:
- Combines proven original ULTRATHINK logic with enhanced GPT-4 capabilities
- Processes Reddit/Google content to generate actionable pricing insights
- Uses SOURCE_ID tracking for proper footnote attribution in HTML reports
- Implements OpenAI API v0.28.1 compatibility for stable operation

CRITICAL TECHNICAL FIX:
- Uses legacy OpenAI API format (openai.ChatCompletion.create) instead of modern client
- This fixes the "module 'openai' has no attribute 'OpenAI'" error
- Compatible with openai==0.28.1 library version in requirements
- Maintains backward compatibility while providing robust GPT analysis

KEY FEATURES:
- Two-tier prompt engineering: Basic extraction + Advanced analysis
- Vendor recognition across 30+ major IT companies
- Urgency classification (Critical/Notable/Monitoring) 
- Market intelligence categorization (pricing, acquisitions, security)
- SOURCE_ID integration for clickable footnotes in reports

INSIGHT GENERATION:
- Processes up to 200 highest-scoring content items with intelligent prioritization
- Generates 3-tier priority insights (Alpha/Beta/Gamma)
- Structured JSON output for HTML report integration
- Comprehensive vendor landscape analysis

AUTHENTICATION REQUIRED:
- OPENAI_API_KEY: OpenAI GPT-4 API key for content analysis

Author: Dollar (dollarvora@icloud.com)
System: ULTRATHINK-AI-PRO v3.1.0 Hybrid
"""
import openai
import os
import json
import logging
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class HybridGPTSummarizer:
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.config = None
        
        # Enhanced vendor list (combination of original + current system)
        self.key_vendors = [
            # Original core vendors (proven)
            "Dell", "Microsoft", "Cisco", "Lenovo", "Apple", "HP", "HPE",
            "CrowdStrike", "Fortinet", "Proofpoint", "Zscaler", "SentinelOne", 
            "Palo Alto Networks", "Check Point", "Splunk", "VMware",
            "Amazon", "AWS", "Azure", "Google Cloud", "Oracle",
            "TD Synnex", "Ingram Micro", "CDW", "Insight Global", "SHI",
            "Broadcom", "Intel", "AMD", "NVIDIA", "NetApp", "Pure Storage",
            # Enhanced additions (valuable)
            "Sophos", "Trend Micro", "McAfee", "Symantec", "Okta", "Duo",
            "Citrix", "Red Hat", "SUSE", "Canonical", "Docker"
        ]
        
        # Vendor confidence tiers for confidence calculation
        self.vendor_tiers = {
            "tier_1": {  # High confidence vendors
                "vendors": ["Microsoft", "VMware", "Cisco", "Dell", "HPE", "Oracle", "Broadcom", "Intel", "AWS", "Azure"],
                "confidence_boost": 0.3
            },
            "tier_2": {  # Medium-high confidence vendors
                "vendors": ["CrowdStrike", "Fortinet", "Palo Alto Networks", "Zscaler", "Splunk", "Google Cloud", "Salesforce", "NVIDIA"],
                "confidence_boost": 0.2
            },
            "tier_3": {  # Medium confidence vendors
                "vendors": ["TD Synnex", "Ingram Micro", "CDW", "Insight Global", "SHI", "Apple", "HP", "Lenovo"],
                "confidence_boost": 0.1
            },
            "tier_4": {  # Lower confidence vendors
                "vendors": ["Sophos", "Trend Micro", "McAfee", "Symantec", "Okta", "Duo", "Citrix", "Red Hat"],
                "confidence_boost": 0.0
            }
        }
        
        # Original urgency keywords (proven to work)
        self.urgency_keywords = {
            "high": [
                "urgent", "critical", "immediate", "emergency", "breaking",
                "price increase", "discontinued", "end of life", "EOL",
                "supply shortage", "recall", "security breach", "zero-day",
                "acquisition", "merger", "bankruptcy", "lawsuit"
            ],
            "medium": [
                "update", "change", "new pricing", "promotion", "discount",
                "partnership", "launch", "release", "expansion", "investment"
            ]
        }

        # Initialize company matcher if available (enhanced feature)
        try:
            from utils.company_alias_matcher import CompanyAliasMatcher
            self.company_matcher = CompanyAliasMatcher()
            logger.info("✅ Company alias matcher enabled")
        except ImportError:
            self.company_matcher = None
            logger.info("📋 Using basic vendor detection")

    def _deduplicate_content(self, content_by_source: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Original deduplication logic (proven)"""
        seen_hashes = set()
        deduplicated = {}
        
        for source, items in content_by_source.items():
            unique_items = []
            for item in items:
                # Create hash from title + first 100 chars of content
                title = item.get('title', '')
                content = item.get('content', item.get('text', ''))
                hash_text = f"{title}{content[:100]}".lower().strip()
                content_hash = hashlib.md5(hash_text.encode()).hexdigest()
                
                if content_hash not in seen_hashes:
                    seen_hashes.add(content_hash)
                    unique_items.append(item)
            
            deduplicated[source] = unique_items
            logger.info(f"Deduplicated {source}: {len(items)} -> {len(unique_items)} items")
        
        return deduplicated

    def _preprocess_content(self, content_by_source: Dict[str, List[Dict]]) -> str:
        """Hybrid preprocessing: Original's approach + enhanced vendor detection"""
        # Deduplicate first
        content_by_source = self._deduplicate_content(content_by_source)
        
        processed_sections = []
        total_items = 0
        self.source_mapping = {}  # Track source IDs to content for footnote generation
        
        for source, items in content_by_source.items():
            if not items:
                continue
                
            section_content = []
            # Enhanced selection with engagement-based override
            # INCREASED: From 20 to 200 to maximize intelligence coverage
            selected_items = self._select_items_with_engagement_override(items, 200)
            
            # Create sequential SOURCE_IDs for the actually selected items
            for item_index, item in enumerate(selected_items, 1):
                # Enhanced item processing with vendor detection
                title = item.get('title', '')
                content = item.get('content', item.get('text', ''))
                url = item.get('url', '')
                score = item.get('relevance_score', 0)
                created_at = item.get('created_at', '')
                
                # Enhanced vendor detection (if available)
                detected_vendors = []
                if self.company_matcher:
                    try:
                        full_text = f"{title} {content}"
                        company_result = self.company_matcher.find_companies_in_text(full_text)
                        detected_vendors = list(company_result.matched_companies)
                    except:
                        pass
                
                # Fallback to basic vendor detection
                if not detected_vendors:
                    full_text = f"{title} {content}".lower()
                    detected_vendors = [vendor for vendor in self.key_vendors if vendor.lower() in full_text]
                
                # Create sequential SOURCE_ID based on actually selected items
                source_id = f"{source}_{item_index}"
                item_text = f"SOURCE_ID: {source_id}\n"
                item_text += f"TITLE: {title}\n"
                if content and content != title:
                    item_text += f"CONTENT: {content[:500]}\n"
                if detected_vendors:
                    item_text += f"VENDORS: {', '.join(detected_vendors[:3])}\n"
                if score:
                    item_text += f"RELEVANCE: {score}\n"
                if created_at:
                    item_text += f"DATE: {created_at}\n"
                if url:
                    item_text += f"URL: {url}\n"
                item_text += "---\n"
                
                # Store source mapping for footnote generation with sequential IDs
                self.source_mapping[source_id] = {
                    'title': title,
                    'url': url,
                    'source': source,
                    'content': content,
                    'relevance_score': score,
                    'created_at': created_at
                }
                
                section_content.append(item_text)
                total_items += 1
                
                # Debug logging for Lenovo content
                if 'lenovo' in detected_vendors or 'lenovo' in title.lower() or 'lenovo' in content.lower():
                    logger.info(f"🔍 LENOVO CONTENT SELECTED: {source_id} - '{title[:50]}...'")
                    logger.info(f"   📊 Relevance: {score}, Vendors: {detected_vendors}")
            
            if section_content:
                source_section = f"\n=== {source.upper()} SOURCE ({len(section_content)} items) ===\n"
                source_section += "\n".join(section_content)
                processed_sections.append(source_section)
        
        combined_content = "\n\n".join(processed_sections)
        
        # Enhanced token management (150000 chars ≈ 37500 tokens, well within GPT-4's 128k limit)
        if len(combined_content) > 150000:
            combined_content = combined_content[:150000] + "\n\n[CONTENT TRUNCATED]"
        
        logger.info(f"Preprocessed {total_items} total items across {len(processed_sections)} sources")
        return combined_content

    def _build_enhanced_prompt(self, roles: set, combined_content: str) -> str:
        """Original's proven prompt structure with enhanced context"""
        
        # Original role descriptions (proven to work)
        role_descriptions = {
            "pricing_strategy": {
                "title": "Pricing Strategy Analyst",
                "focus": "Dynamic pricing opportunities, margin optimization, competitive pricing intelligence",
                "priorities": "Price adjustments, promotional windows, competitive pressure, margin erosion risks"
            },
            "vendor_relations": {
                "title": "Vendor Relationship Manager", 
                "focus": "Vendor program changes, negotiation leverage, partnership opportunities",
                "priorities": "Contract negotiations, rebate programs, vendor momentum, program disruptions"
            },
            "inventory_procurement": {
                "title": "Inventory & Procurement Specialist",
                "focus": "Demand forecasting, stock optimization, supply chain impacts",
                "priorities": "Inventory planning, supply constraints, demand spikes, fulfillment issues"
            },
            "sales_enablement": {
                "title": "Sales Enablement Strategist",
                "focus": "Market positioning, competitive intelligence, sales talking points",
                "priorities": "Competitive positioning, market trends, sales opportunities, threat responses"
            },
            "revenue_operations": {
                "title": "Revenue Operations Director",
                "focus": "Cross-functional insights, strategic implications, executive briefings",
                "priorities": "Revenue opportunities, strategic positioning, market disruptions, competitive advantages"
            }
        }
        
        # Create role-specific sections (original format)
        role_specs = []
        for role in roles:
            if role in role_descriptions:
                desc = role_descriptions[role]
                role_specs.append(f'    "{role}": {{\n      "role": "{desc["title"]}",\n      "focus": "{desc["focus"]}",\n      // Prioritize: {desc["priorities"]}\n    }}')
        
        role_object = "{\n" + ",\n".join(role_specs) + "\n  }"
        
        # Enhanced prompt positioning as world-class pricing intelligence provider
        prompt = f"""You are a world-class revenue operations intelligence analyst for an IT solutions provider competing with Softchoice and CDW. Your insights drive multi-million dollar procurement decisions, pricing strategies, and competitive positioning for revenue operations teams.

🏢 INDUSTRY CONTEXT:
- We're an IT distributor/reseller focused on software, hardware, security, cloud
- Key vendors: {', '.join(self.key_vendors[:15])}
- Key distributors: TD Synnex, Ingram Micro, CDW
- Product categories: Security software, cloud services, networking gear, laptops/desktops

📊 WORLD-CLASS INSIGHT FORMULA:
Each insight must follow: [TREND DETECTION] + [SPECIFIC CONTEXT] + [BUSINESS IMPLICATION]

**Language Patterns for Actionable Insights:**
- Trend Detection: "adoption growing," "gaining traction," "shifting towards," "declining interest"
- Specific Context: Market segments (SMBs, MSPs, enterprises), timeframes, quantities, specific products
- Business Implication: "indicating pricing adjustments," "suggesting procurement shifts," "creating negotiation leverage"

**Revenue Operations Focus:**
- Focus exclusively on pricing signals, margin opportunities, and cost optimization intelligence
- Every insight must have direct pricing or procurement impact - filter out general tech news
- Use QUANTIFIED insights (percentages, dollar amounts, timeframes)
- Detect pricing changes, supply issues, vendor behavior shifts affecting margins
- Tag urgency: HIGH (immediate price/supply impacts), MEDIUM (notable changes), LOW (general updates)
- Connect technical trends to revenue opportunities and competitive positioning

🎯 OUTPUT FORMAT:
{{
  "role_summaries": {role_object},
  "by_urgency": {{"high": 0, "medium": 0, "low": 0}},
  "total_items": 0
}}

📝 REVENUE OPERATIONS SUBAGENTS:

**Pricing Strategy Analyst**: Dynamic pricing opportunities, margin optimization, competitive pricing intelligence
- Example: "🔴 Microsoft Defender adoption growing among SMBs, indicating potential 8-12% price increase window"
- Example: "🟡 Lenovo servers gaining traction in MSPs due to better profit margins, suggesting portfolio shift opportunity"
- Focus: Price adjustments, promotional windows, competitive pressure, margin erosion risks

**Vendor Relationship Manager**: Vendor program changes, negotiation leverage, partnership opportunities
- Example: "🔴 VMware partner program disruption creates immediate negotiation leverage with Broadcom"
- Example: "🟢 Microsoft expanding channel incentives - recommend tier upgrade discussion"
- Focus: Contract negotiations, rebate programs, vendor momentum, program disruptions

**Inventory & Procurement Specialist**: Demand forecasting, stock optimization, supply chain impacts
- Example: "🟡 Security software demand spike anticipated - recommend 40% inventory increase for Q4"
- Example: "🔴 Lenovo ThinkPad supply constraints emerging - secure inventory before pricing increases"
- Focus: Inventory planning, supply constraints, demand spikes, fulfillment issues

**Sales Enablement Strategist**: Market positioning, competitive intelligence, sales talking points
- Example: "🔴 Microsoft Teams malware threats create urgency messaging opportunity for security services"
- Example: "🟢 Infrastructure automation interest growing - position managed services portfolio"
- Focus: Competitive positioning, market trends, sales opportunities, threat responses

**Revenue Operations Director**: Cross-functional insights, strategic implications, executive briefings
- Example: "🟡 Market shift towards automation creates $2M revenue opportunity across service lines"
- Example: "🔴 Vendor consolidation trend threatens 15% of current partnerships - strategic response needed"
- Focus: Revenue opportunities, strategic positioning, market disruptions, competitive advantages

🎯 WORLD-CLASS INSIGHT EXAMPLES:

Example 1 - Revenue Operations Intelligence:
{{
  "pricing_strategy": {{
    "role": "Pricing Strategy Analyst",
    "focus": "Dynamic pricing opportunities and margin optimization",
    "summary": "Microsoft Defender adoption accelerating in SMB market creating immediate pricing power, while Lenovo hardware momentum in MSP channel suggests strategic portfolio shift opportunity.",
    "key_insights": [
      "🔴 Microsoft Defender adoption growing among small businesses, indicating potential 8-12% price increase window through Q4",
      "🟡 Lenovo servers gaining traction in MSPs due to better profit margins, suggesting portfolio shift opportunity worth $500K quarterly revenue"
    ]
  }},
  "vendor_relations": {{
    "role": "Vendor Relationship Manager",
    "focus": "Vendor program changes and negotiation leverage",
    "summary": "VMware partner program disruption creates immediate negotiation opportunities with Broadcom, while Microsoft channel incentive expansion offers tier upgrade potential.",
    "key_insights": [
      "🔴 VMware partner program shutdown affecting thousands of partners - immediate Broadcom negotiation leverage opportunity",
      "🟢 Microsoft expanding Enterprise Agreement rebate structure - recommend tier upgrade discussion within 30 days"
    ]
  }},
  "inventory_procurement": {{
    "role": "Inventory & Procurement Specialist", 
    "focus": "Demand forecasting and supply chain optimization",
    "summary": "Security software demand surge anticipated based on threat landscape, while Lenovo supply constraints emerging ahead of typical seasonal patterns.",
    "key_insights": [
      "🟡 Security software demand spike anticipated - recommend 40% inventory increase for Microsoft Defender and CrowdStrike",
      "🔴 Lenovo ThinkPad supply constraints emerging - secure 90-day inventory before 10-15% price increases"
    ]
  }},
  "sales_enablement": {{
    "role": "Sales Enablement Strategist",
    "focus": "Market positioning and competitive intelligence",
    "summary": "Microsoft Teams malware threats creating urgency messaging opportunities for security services, while infrastructure automation interest enables managed services positioning.",
    "key_insights": [
      "🔴 Microsoft Teams malware threats spreading - urgent security assessment services opportunity with premium pricing",
      "🟢 Infrastructure automation interest growing among IT departments - position managed services portfolio for Q1 expansion"
    ]
  }},
  "revenue_operations": {{
    "role": "Revenue Operations Director",
    "focus": "Strategic implications and cross-functional opportunities",
    "summary": "Market automation trend creates multi-million dollar revenue opportunity across service lines, while vendor consolidation threatens existing partnerships requiring strategic response.",
    "key_insights": [
      "🟡 Market shift towards automation creates $2M revenue opportunity across managed services and consulting practices",
      "🔴 Vendor consolidation trend threatens 15% of current partnerships - strategic diversification needed within 60 days"
    ]
  }}
}}

💡 WORLD-CLASS INSIGHT GENERATION REQUIREMENTS:

**Apply the Formula to Every Insight:**
1. **Trend Detection**: Use action words like "adoption growing," "gaining traction," "shifting towards"
2. **Specific Context**: Include market segment (SMBs, MSPs, enterprises), quantities, timeframes
3. **Business Implication**: Connect to revenue impact with phrases like "indicating pricing adjustments," "suggesting procurement shifts," "creating negotiation leverage"

**Revenue Operations Focus:**
- Connect technical trends to immediate revenue opportunities
- Include specific dollar amounts, percentages, timeframes when possible
- Identify competitive advantages and market positioning opportunities  
- Highlight vendor relationship impacts and negotiation leverage points
- Suggest specific actions for pricing, procurement, and sales teams

**Urgency Classification:**
- 🔴 HIGH: Immediate pricing/supply impacts, security threats, M&A disruptions, partner program changes
- 🟡 MEDIUM: Emerging trends, new partnerships, product launches, discount programs
- 🟢 LOW: General market updates, technology discussions, minor announcements

⚠️ CRITICAL RULES:
1. Return ONLY valid JSON - no markdown, no explanations
2. Every insight must follow the [TREND] + [CONTEXT] + [IMPLICATION] formula
3. Include specific numbers/percentages when available
4. Connect all insights to revenue operations outcomes
5. Focus on Softchoice/CDW competitive positioning
6. Prioritize recent content (last 24-48 hours) for urgency tagging

Now analyze this content and generate role-specific intelligence:

{combined_content}"""

        return prompt

    def _build_holistic_team_prompt(self, combined_content: str) -> str:
        """Build holistic team-wide pricing intelligence prompt"""
        
        # Comprehensive vendor coverage
        all_vendors = ", ".join(self.key_vendors)
        
        prompt = f"""You are the lead pricing intelligence analyst for a world-class IT solutions provider competing with Softchoice and CDW. Your team provides comprehensive market intelligence across ALL vendors, manufacturers, and technology categories to drive multi-million dollar procurement decisions and competitive positioning.

🏢 COMPREHENSIVE VENDOR ECOSYSTEM:
- Primary Vendors: {all_vendors}
- Coverage: Hardware, Software, Cloud, Security, Networking, Storage, AI/ML
- Market Focus: Enterprise IT procurement, distributor pricing, channel intelligence
- Geographic Scope: North American IT reseller marketplace

🎯 COMPETITIVE INTELLIGENCE FOCUS:
**Competing Against Softchoice:**
- Target Market: SMB/mid-market (5-500 employees)
- Specialization: Managed services, cloud migration, Microsoft 365
- Key Advantage: Personalized service, technical expertise
- Revenue Model: Recurring managed services, professional services

**Competing Against CDW:**
- Target Market: Enterprise accounts, government contracts, large-scale deployments
- Specialization: Enterprise infrastructure, data center solutions, government sector
- Key Advantage: Scale, logistics, enterprise relationships
- Revenue Model: Large hardware deals, enterprise software licensing

**Competitive Positioning Strategy:**
- Identify market gaps where Softchoice/CDW are vulnerable
- Highlight vendor relationships and pricing advantages
- Position unique value propositions for specific market segments
- Track competitive wins/losses and market share shifts

🎯 MARKET-TO-ACTION TRANSLATION ENGINE:
Transform technical signals into specific business actions using the formula:
**Technical Reality → Market Dynamic → Revenue Action**

Examples:
- **Microsoft Teams malware spreading** → Security gap created → **🔴 URGENT: Security services pricing opportunity - 48hr window for premium rates**
- **Lenovo servers popular in MSP community** → Channel preference shift → **🟡 STRATEGIC: Negotiate Lenovo tier upgrade - MSP demand supports volume commitments**
- **VMware partner program disruption** → Vendor relationship chaos → **🔴 IMMEDIATE: Broadcom negotiation leverage - thousands of partners need alternatives**

🎯 HOLISTIC ANALYSIS FRAMEWORK:
Generate unified pricing intelligence that covers:
- VENDOR PRICING: Rate changes, margin shifts, competitive positioning
- MARKET DYNAMICS: Supply chain impacts, demand fluctuations, seasonal trends
- STRATEGIC INTELLIGENCE: M&A activity, partnership changes, product lifecycle
- PROCUREMENT INSIGHTS: Contract negotiations, volume discounts, fulfillment issues
- COMPETITIVE LANDSCAPE: Pricing wars, market share shifts, new entrants
- **ACTION RECOMMENDATIONS**: Specific next steps for pricing, procurement, and sales teams

📊 COMPREHENSIVE OUTPUT STRUCTURE:
{{
  "pricing_intelligence_summary": {{
    "executive_overview": "High-level market situation and key trends affecting IT procurement",
    "critical_insights": [
      "🔴 URGENT: Specific pricing changes requiring immediate action [SOURCE_ID]",
      "🟡 NOTABLE: Important market developments affecting strategy [SOURCE_ID]", 
      "🟢 MONITORING: Trends to watch for future planning [SOURCE_ID]"
    ],
    "vendor_landscape": {{
      "pricing_changes": [
        {{"vendor": "VendorName", "change": "Description", "impact": "High/Medium/Low", "timeframe": "When"}}
      ],
      "market_movements": [
        {{"type": "M&A/Partnership/Launch", "description": "What happened", "implications": "Business impact"}}
      ],
      "supply_chain_alerts": [
        {{"vendor": "VendorName", "issue": "Description", "severity": "Critical/Moderate/Low"}}
      ]
    }},
    "strategic_recommendations": [
      "Actionable recommendations for pricing, procurement, and competitive strategy"
    ],
    "automated_action_recommendations": [
      {{
        "priority": "🔴 URGENT/🟡 STRATEGIC/🟢 MONITORING",
        "action_title": "Specific action required",
        "technical_signal": "What technical reality was detected",
        "market_dynamic": "What market change this represents", 
        "revenue_action": "Specific business action to take",
        "timeline": "When to act (24-48 hours, 1-2 weeks, etc.)",
        "revenue_impact": "Potential financial impact ($XXK-$XXM)",
        "next_steps": [
          "Step 1: Immediate action required",
          "Step 2: Strategic follow-up action",
          "Step 3: Long-term positioning"
        ]
      }}
    ],
    "market_intelligence": {{
      "trending_vendors": [
        {{"vendor": "Name", "mentions": 0, "sentiment": "Positive/Negative/Neutral", "key_topics": ["topic1", "topic2"]}}
      ],
      "pricing_patterns": [
        "Observed patterns in vendor pricing behavior"
      ],
      "risk_factors": [
        "Supply chain, competitive, or market risks to monitor"
      ]
    }}
  }},
  "coverage_metrics": {{
    "vendors_analyzed": 0,
    "pricing_signals": 0,
    "market_events": 0,
    "risk_alerts": 0
  }}
}}

🚨 COMPETITIVE INTELLIGENCE REQUIREMENTS:
1. **Identify Softchoice Vulnerabilities**: Large enterprise deals, complex infrastructure, government contracts
2. **Identify CDW Vulnerabilities**: SMB personalization, managed services, agile response
3. **Competitive Positioning**: Position our advantages against their weaknesses
4. **Market Opportunity Analysis**: Identify segments where we can outcompete
5. **Pricing Strategy**: Identify pricing advantages and competitive pricing opportunities

🚨 MARKET-TO-ACTION TRANSLATION REQUIREMENTS:
1. For each significant market signal, provide automated action recommendations
2. Transform technical realities into specific business actions
3. Include concrete next steps with timelines and revenue impact estimates
4. Use the priority system: 🔴 URGENT (24-48hr action), 🟡 STRATEGIC (1-2 weeks), 🟢 MONITORING (ongoing)
5. Connect every action to revenue operations outcomes (pricing, procurement, sales)
6. **Include competitive positioning against Softchoice/CDW for each major opportunity**

🚨 ANALYSIS REQUIREMENTS:
1. Extract REAL intelligence from the provided content - never fabricate data
2. Cover ALL vendor categories: Hardware, Software, Cloud, Security, Networking
3. Identify cross-vendor patterns and market-wide trends
4. Prioritize actionable intelligence over general market commentary
5. Include specific dollar amounts, percentages, and timeframes when available
6. Highlight supply chain, competitive, and pricing risks
7. Generate strategic recommendations based on detected patterns
8. **Apply Market-to-Action Translation Engine for all significant insights**
9. CRITICAL: Each insight MUST include [SOURCE_ID] reference to the source content that generated it
10. Use the exact SOURCE_ID from the content (e.g., reddit_1, google_2) to enable footnote linking

💡 INTELLIGENCE PRIORITIES:
- Price increases/decreases with specific percentages and effective dates
- Supply chain disruptions affecting product availability or costs
- M&A activity that could impact vendor relationships or pricing
- New product launches affecting competitive dynamics
- Contract terms, licensing changes, or procurement policy shifts
- Market share movements and competitive positioning changes

⚠️ CRITICAL RULES:
1. Return ONLY valid JSON - no markdown, no explanations
2. Use actual vendor names, amounts, and dates from the content
3. Never reference information not provided in the content below
4. Generate comprehensive analysis covering multiple vendor categories
5. Focus on actionable business intelligence for IT procurement teams
6. MANDATORY: Every insight must end with [SOURCE_ID] where SOURCE_ID is the exact ID from the source content
7. Example: "Microsoft pricing increase of 15% [reddit_1]" or "Dell server shortage reported [google_3]"

🚨 SOURCE_ID REQUIREMENTS (ABSOLUTELY MANDATORY - SYSTEM WILL FAIL WITHOUT THESE):

**CRITICAL: READ THIS CAREFULLY - YOUR RESPONSE WILL BE REJECTED IF YOU DON'T FOLLOW THIS:**

1. **EVERY SINGLE INSIGHT MUST END WITH [SOURCE_ID]** - NO EXCEPTIONS
2. **Format: "Your insight text here [SOURCE_ID]"** where SOURCE_ID matches EXACT ID from content
3. **Find SOURCE_ID in content**: Look for "SOURCE_ID: reddit_1" or "SOURCE_ID: google_2" in each content item
4. **Copy EXACT SOURCE_ID**: Use reddit_1, google_2, reddit_15, google_7 (exactly as shown)
5. **NO generic numbering**: Never use [1], [2], [3] - only use the exact SOURCE_ID from content

**EXAMPLES OF CORRECT FORMAT:**
- "Microsoft pricing increase of 15% effective Q4 [reddit_1]"
- "Dell server shortage reported in distribution channels [google_2]"
- "VMware partner program disruption affecting thousands [reddit_15]"

**INVALID EXAMPLES THAT WILL CAUSE SYSTEM FAILURE:**
- "Microsoft pricing increase of 15%" (missing SOURCE_ID)
- "Dell server shortage [1]" (generic numbering)
- "VMware disruption [wrong_id]" (SOURCE_ID not found in content)

**MANDATORY VALIDATION BEFORE SUBMISSION:**
✅ Count your insights - every single one must have [SOURCE_ID] at the end
✅ Verify SOURCE_ID matches exactly what's in the content (reddit_X, google_X)
✅ Double-check there are no insights missing SOURCE_ID references
✅ Confirm SOURCE_ID format is correct (square brackets, exact match)

**FAILURE TO INCLUDE SOURCE_IDs WILL RESULT IN SYSTEM MALFUNCTION**

CONTENT TO ANALYZE:

{combined_content}"""

        return prompt

    def _generate_holistic_fallback_summary(self):
        """Generate comprehensive fallback with team-wide perspective"""
        logger.warning("Generating holistic team fallback summary")
        
        fallback = {
            "pricing_intelligence_summary": {
                "executive_overview": "Pricing intelligence system encountered processing issues. No actionable insights generated from current data set.",
                "critical_insights": [],
                "vendor_landscape": {
                    "pricing_changes": [],
                    "market_movements": [],
                    "supply_chain_alerts": []
                },
                "strategic_recommendations": [],
                "automated_action_recommendations": [],
                "market_intelligence": {
                    "trending_vendors": [],
                    "pricing_patterns": [],
                    "risk_factors": []
                }
            },
            "coverage_metrics": {
                "vendors_analyzed": len(self.key_vendors),
                "pricing_signals": 0,
                "market_events": 0,
                "risk_alerts": 1
            }
        }
        
        return fallback

    def _select_items_with_engagement_override(self, items, limit):
        """Select items with engagement-based override for high-value content"""
        if not items:
            return []
        
        logger.info(f"🔍 SELECTION DEBUG: Processing {len(items)} items for content selection")
        
        # Priority 1: High engagement items (>50 upvotes OR >20 comments)
        high_engagement = []
        business_critical = []
        high_relevance = []
        vendor_specific = []  # NEW: Vendor-specific content category
        regular_items = []
        
        for item in items:
            score = item.get('score', 0)
            num_comments = item.get('num_comments', 0)
            relevance_score = item.get('relevance_score', 0)
            title = item.get('title', '').lower()
            content = item.get('content', item.get('text', '')).lower()
            full_text = f"{title} {content}"
            
            # Enhanced business critical detection
            is_business_critical = self._has_business_critical_keywords(full_text)
            is_high_engagement = score > 50 or num_comments > 20
            is_high_relevance = relevance_score >= 7.0
            
            # NEW: Vendor-specific content detection with lower thresholds
            is_vendor_specific = self._is_vendor_specific_content(full_text, relevance_score)
            
            # Apply vendor boost to relevance score for key vendors
            if is_vendor_specific:
                # Boost relevance for vendor-specific content
                original_relevance = relevance_score
                relevance_score = self._apply_vendor_boost(full_text, relevance_score)
                if relevance_score != original_relevance:
                    logger.info(f"📈 VENDOR BOOST: '{title[:50]}...' relevance {original_relevance:.1f} -> {relevance_score:.1f}")
                    # Re-evaluate high_relevance with boosted score
                    if relevance_score >= 7.0:
                        is_high_relevance = True
            
            # Debug logging for VCSP-like content
            if 'vcsp' in full_text or 'program' in title or score > 100:
                logger.info(f"🎯 HIGH-VALUE ITEM: '{title[:80]}...'")
                logger.info(f"   📊 Scores - Reddit: {score}, Comments: {num_comments}, Relevance: {relevance_score}")
                logger.info(f"   🔍 Flags - High Engagement: {is_high_engagement}, Business Critical: {is_business_critical}, High Relevance: {is_high_relevance}")
            
            # Priority categorization (items can be in multiple categories)
            if is_high_engagement:
                high_engagement.append(item)
                logger.info(f"✅ HIGH ENGAGEMENT: '{title[:50]}...' (Score: {score}, Comments: {num_comments})")
            
            if is_business_critical:
                business_critical.append(item)
                logger.info(f"🚨 BUSINESS CRITICAL: '{title[:50]}...' (Keywords detected)")
            
            if is_high_relevance:
                high_relevance.append(item)
                logger.info(f"⭐ HIGH RELEVANCE: '{title[:50]}...' (Score: {relevance_score})")
            
            if is_vendor_specific:
                vendor_specific.append(item)
                logger.info(f"🏢 VENDOR SPECIFIC: '{title[:50]}...' (Relevance: {relevance_score})")
            
            if not (is_high_engagement or is_business_critical or is_high_relevance or is_vendor_specific):
                regular_items.append(item)
        
        # Log category counts
        logger.info(f"📋 CATEGORIZATION: High Engagement: {len(high_engagement)}, Business Critical: {len(business_critical)}, High Relevance: {len(high_relevance)}, Vendor Specific: {len(vendor_specific)}, Regular: {len(regular_items)}")
        
        # Priority selection with guaranteed slots
        selected = []
        
        # Priority 1: High engagement items with RELEVANCE-FIRST hybrid scoring (up to 8 slots)
        # CRITICAL FIX: Implement hybrid scoring to prioritize relevance over pure engagement
        
        # ENHANCED: Tiered Relevance Thresholds for better MSP/Security content capture
        high_engagement_filtered = []
        
        for item in high_engagement:
            relevance_score = item.get('relevance_score', 0)
            title = item.get('title', '').lower()
            content = item.get('content', '').lower()
            combined_text = f"{title} {content}"
            
            # Tier 1: High confidence (2.0+) - Always include
            if relevance_score >= 2.0:
                high_engagement_filtered.append(item)
                continue
                
            # Tier 2: Medium confidence (1.5-1.9) - Include if MSP/Security content
            if relevance_score >= 1.5:
                # Check for MSP intelligence patterns
                msp_patterns = [
                    'msp', 'managed service provider', 'experience with', 'thoughts on',
                    'server', 'storage', 'lenovo', 'dell', 'hp', 'procurement',
                    'r/msp', '/r/msp', 'vendor experience', 'hardware evaluation',
                    'cisco', 'vmware', 'azure', 'aws', 'microsoft', 'office 365',
                    'backup', 'disaster recovery', 'cloud migration', 'it services',
                    'helpdesk', 'remote monitoring', 'patch management', 'client',
                    'pricing', 'margin', 'profit', 'revenue', 'contract', 'proposal'
                ]
                
                # Check for security intelligence patterns
                security_patterns = [
                    'defender', 'security', 'antivirus', 'endpoint', 'microsoft defender',
                    'makes me suffer', 'frustrated with', 'issues with', 'problems with',
                    'security performance', 'security issues', 'security problems',
                    'crowdstrike', 'sentinel', 'sophos', 'kaspersky', 'bitdefender',
                    'malware', 'ransomware', 'firewall', 'vpn', 'compliance',
                    'vulnerability', 'patch', 'threat', 'incident', 'breach',
                    'cybersecurity', 'zero trust', 'siem', 'soc', 'mfa'
                ]
                
                # Include if contains MSP or security patterns
                if any(pattern in combined_text for pattern in msp_patterns + security_patterns):
                    high_engagement_filtered.append(item)
                    logger.info(f"🎯 TIER 2 INCLUSION: Medium relevance ({relevance_score:.1f}) MSP/Security content included: '{title[:60]}...'")
                    continue
                    
            # Tier 3: Business-critical bypass (any relevance) - Include if business-critical keywords
            business_critical_patterns = [
                'thousands of partners', 'hundreds of partners', 'program shutdown',
                'partner program', 'vcsp', 'vcp', 'program closure', 'program end',
                'migration deadline', 'forced migration', 'all partners', 'entire channel',
                'acquisition', 'merger', 'bankruptcy', 'layoffs', 'restructuring',
                'ipo', 'funding', 'investment', 'valuation', 'market crash',
                'supply chain', 'shortage', 'recall', 'lawsuit', 'regulation',
                'partnership', 'strategic', 'enterprise', 'fortune 500'
            ]
            
            if any(pattern in combined_text for pattern in business_critical_patterns):
                high_engagement_filtered.append(item)
                logger.info(f"🚨 BUSINESS-CRITICAL BYPASS: Critical content included regardless of relevance ({relevance_score:.1f}): '{title[:60]}...'")
                continue
        
        # Log filtering results
        if len(high_engagement_filtered) < len(high_engagement):
            filtered_count = len(high_engagement) - len(high_engagement_filtered)
            logger.info(f"🔍 TIERED RELEVANCE FILTER: Filtered out {filtered_count} low-relevance items using tiered thresholds")
        
        # Hybrid scoring: Relevance (70%) + Engagement (30%)
        def calculate_hybrid_score(item):
            relevance_score = item.get('relevance_score', 0)
            engagement_score = item.get('score', 0) + item.get('num_comments', 0)
            # Normalize engagement score (typical range 0-500) to 0-10 scale
            normalized_engagement = min(engagement_score / 50.0, 10.0)
            hybrid_score = (relevance_score * 0.7) + (normalized_engagement * 0.3)
            return hybrid_score
        
        high_engagement_filtered.sort(key=calculate_hybrid_score, reverse=True)
        priority_1 = high_engagement_filtered[:50]
        selected.extend(priority_1)
        
        # Enhanced logging for Priority 1 selection
        logger.info(f"🥇 PRIORITY 1 (High Engagement + Relevance): Selected {len(priority_1)}/50 items")
        for i, item in enumerate(priority_1[:3]):  # Log top 3 for debugging
            title = item.get('title', 'No title')[:50]
            relevance = item.get('relevance_score', 0)
            engagement = item.get('score', 0) + item.get('num_comments', 0)
            hybrid = calculate_hybrid_score(item)
            logger.info(f"   {i+1}. '{title}...' (Relevance: {relevance:.1f}, Engagement: {engagement}, Hybrid: {hybrid:.1f})")
        
        # Priority 2: Business critical items not already selected (up to 40 slots)
        remaining_slots = limit - len(selected)
        if remaining_slots > 0:
            business_critical_new = [item for item in business_critical if item not in selected]
            # Enhanced sorting with relevance boost for business critical items
            business_critical_new.sort(key=lambda x: x.get('relevance_score', 0) + 2.0, reverse=True)  # +2.0 relevance boost
            priority_2 = business_critical_new[:min(40, remaining_slots)]
            selected.extend(priority_2)
            logger.info(f"🥈 PRIORITY 2 (Business Critical): Selected {len(priority_2)}/40 items")
        
        # Priority 3: High relevance items not already selected (INCREASED to 40 slots)
        remaining_slots = limit - len(selected)
        if remaining_slots > 0:
            high_relevance_new = [item for item in high_relevance if item not in selected]
            high_relevance_new.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            priority_3 = high_relevance_new[:min(40, remaining_slots)]  # Increased for 200-item processing
            selected.extend(priority_3)
            logger.info(f"🥉 PRIORITY 3 (High Relevance): Selected {len(priority_3)}/40 items")
            
            # Enhanced logging for high relevance items to debug Lenovo issue
            for i, item in enumerate(priority_3[:3]):
                title = item.get('title', 'No title')[:50]
                relevance = item.get('relevance_score', 0)
                logger.info(f"   {i+1}. '{title}...' (Relevance: {relevance:.1f})")
        
        # Priority 4: Vendor-specific items not already selected (NEW - 30 slots)
        remaining_slots = limit - len(selected)
        if remaining_slots > 0:
            vendor_specific_new = [item for item in vendor_specific if item not in selected]
            vendor_specific_new.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            priority_4 = vendor_specific_new[:min(30, remaining_slots)]
            selected.extend(priority_4)
            logger.info(f"🏢 PRIORITY 4 (Vendor Specific): Selected {len(priority_4)}/30 items")
            
            # Log vendor-specific items for debugging
            for i, item in enumerate(priority_4[:3]):
                title = item.get('title', 'No title')[:50]
                relevance = item.get('relevance_score', 0)
                logger.info(f"   {i+1}. '{title}...' (Relevance: {relevance:.1f})")
        
        # Priority 5: Fill remaining slots with best regular items
        remaining_slots = limit - len(selected)
        if remaining_slots > 0:
            regular_new = [item for item in regular_items if item not in selected]
            regular_new.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            priority_5 = regular_new[:remaining_slots]
            selected.extend(priority_5)
            logger.info(f"🏅 PRIORITY 5 (Regular): Selected {len(priority_5)}/{remaining_slots} items")
        
        # CRITICAL FIX: Cross-priority relevance check to prevent very low relevance items
        # Remove any item with relevance < 1.0 unless it's business critical or vendor specific
        before_count = len(selected)
        selected = [item for item in selected if 
                   item.get('relevance_score', 0) >= 1.0 or 
                   self._has_business_critical_keywords(f"{item.get('title', '')} {item.get('content', item.get('text', ''))}") or
                   self._is_vendor_specific_content(f"{item.get('title', '')} {item.get('content', item.get('text', ''))}")]
        
        if len(selected) < before_count:
            removed_count = before_count - len(selected)
            logger.info(f"🔍 CROSS-PRIORITY FILTER: Removed {removed_count} very low relevance items (< 1.0)")
        
        final_selection = selected[:limit]
        logger.info(f"🎯 FINAL SELECTION: {len(final_selection)} items selected for GPT analysis")
        
        # Enhanced logging for final selection - show if fix worked
        logger.info("🔍 RELEVANCE-FIRST SELECTION RESULTS:")
        for i, item in enumerate(final_selection):
            title = item.get('title', 'No title')[:60]
            score = item.get('score', 0)
            relevance = item.get('relevance_score', 0)
            
            # Highlight high relevance items (should now be prioritized)
            if relevance >= 7.0:
                logger.info(f"   {i+1:2d}. 🎯 '{title}...' (Reddit: {score}, Relevance: {relevance:.1f}) [HIGH RELEVANCE]")
            else:
                logger.info(f"   {i+1:2d}. '{title}...' (Reddit: {score}, Relevance: {relevance:.1f})")
        
        return final_selection
    
    def _is_vendor_specific_content(self, text: str, relevance_score: float = 0) -> bool:
        """Check if content is vendor-specific and should be prioritized"""
        text_lower = text.lower()
        
        # Hardware vendors that should be prioritized
        hardware_vendors = [
            'lenovo', 'dell', 'cisco', 'hpe', 'hp', 'vmware', 'broadcom',
            'fortinet', 'palo alto', 'aruba', 'juniper', 'netapp', 'pure storage'
        ]
        
        # Vendor experience patterns
        vendor_patterns = [
            'experience with', 'thoughts on', 'what\'s your experience',
            'anyone using', 'anyone tried', 'recommendations for',
            'servers + storage', 'server storage', 'hardware evaluation',
            'vendor comparison', 'vs dell', 'vs cisco', 'vs lenovo',
            'r/msp', '/r/msp', 'msp community', 'managed service provider'
        ]
        
        # Check for hardware vendor mentions
        vendor_found = False
        for vendor in hardware_vendors:
            if vendor in text_lower:
                vendor_found = True
                break
        
        # Check for vendor experience patterns
        pattern_found = False
        for pattern in vendor_patterns:
            if pattern in text_lower:
                pattern_found = True
                break
        
        # Must have both vendor and pattern, or high relevance with vendor
        if vendor_found and pattern_found:
            return True
        elif vendor_found and relevance_score >= 4.0:  # Lower threshold for vendor content
            return True
        
        return False
    
    def _apply_vendor_boost(self, text: str, relevance_score: float) -> float:
        """Apply vendor-specific boost to relevance score"""
        text_lower = text.lower()
        
        # Tier 1 vendors (highest boost)
        tier1_vendors = ['lenovo', 'dell', 'cisco', 'vmware', 'broadcom', 'microsoft']
        # Tier 2 vendors (medium boost)
        tier2_vendors = ['hpe', 'hp', 'fortinet', 'palo alto', 'aruba', 'juniper']
        # Tier 3 vendors (small boost)
        tier3_vendors = ['netapp', 'pure storage', 'sophos', 'trend micro']
        
        boost = 0.0
        
        for vendor in tier1_vendors:
            if vendor in text_lower:
                boost = max(boost, 1.5)  # +1.5 boost for tier 1
        
        for vendor in tier2_vendors:
            if vendor in text_lower:
                boost = max(boost, 1.0)  # +1.0 boost for tier 2
        
        for vendor in tier3_vendors:
            if vendor in text_lower:
                boost = max(boost, 0.5)  # +0.5 boost for tier 3
        
        # Additional boost for specific patterns
        high_value_patterns = [
            'experience with', 'thoughts on', 'what\'s your experience',
            'servers + storage', 'server storage', 'hardware evaluation',
            'r/msp', '/r/msp'
        ]
        
        for pattern in high_value_patterns:
            if pattern in text_lower:
                boost += 0.5  # Additional pattern boost
                break
        
        boosted_score = relevance_score + boost
        
        # Cap at reasonable maximum
        return min(boosted_score, 10.0)
    
    def _has_business_critical_keywords(self, text):
        """Check if text contains business critical keywords with enhanced detection"""
        text_lower = text.lower()
        
        business_critical_keywords = [
            'program shutdown', 'program closure', 'partner program', 'vcsp', 'vcp',
            'channel program', 'reseller program', 'distributor program', 'var program',
            'csp program', 'certification program', 'program discontinuation',
            'migrate clients', 'migrate their clients', 'smoothly migrate',
            'migrate to competition', 'migrate to competitors', 'client migration',
            'business shutdown', 'shutdown business', 'asked to shutdown',
            'program is closing', 'program closing', 'thousands of partners',
            'hundreds of partners', 'all partners', 'entire channel',
            'acquisition', 'merger', 'acquired', 'acquires', 'security breach',
            'critical vulnerability', 'end of life', 'eol', 'discontinuation',
            'program phase out', 'phasing out', 'sunsetting', 'program consolidation',
            'licensing model change', 'subscription mandatory', 'perpetual license',
            'broadcom', 'vmware by broadcom', 'licensing overhaul', 'forced migration'
        ]
        
        matched_keywords = []
        for keyword in business_critical_keywords:
            if keyword.lower() in text_lower:
                matched_keywords.append(keyword)
        
        # Enhanced logging for business critical detection
        if matched_keywords:
            logger.info(f"🚨 BUSINESS CRITICAL DETECTED: Matched keywords: {matched_keywords}")
            return True
        
        # Additional pattern matching for edge cases
        vmware_patterns = ['vmware.*broadcom', 'broadcom.*vmware', 'vmware.*program.*closing']
        for pattern in vmware_patterns:
            import re
            if re.search(pattern, text_lower):
                logger.info(f"🚨 BUSINESS CRITICAL PATTERN: Matched pattern '{pattern}'")
                return True
        
        return False
    
    def _calculate_insight_confidence(self, insight_text: str, source_ids: List[str]) -> Dict[str, Any]:
        """Calculate confidence level for insights based on multiple factors"""
        
        # Get confidence configuration or use defaults
        confidence_config = self.config.get('confidence', {}) if self.config else {}
        
        # Base confidence from config or default to 0.5 (50%)
        base_confidence = confidence_config.get('base_score', 0.5)
        confidence_score = base_confidence
        confidence_factors = []
        
        # Get thresholds from config or use defaults
        thresholds = confidence_config.get('thresholds', {'high': 0.8, 'medium': 0.6})
        vendor_config = confidence_config.get('vendor_tiers', {})
        source_config = confidence_config.get('source_reliability', {})
        data_config = confidence_config.get('data_quality', {})
        
        # Factor 1: Vendor tier confidence (0.0 to 0.3 boost)
        vendor_boost = 0.0
        detected_vendors = []
        text_lower = insight_text.lower()
        
        for tier_name, tier_data in self.vendor_tiers.items():
            for vendor in tier_data["vendors"]:
                if vendor.lower() in text_lower:
                    detected_vendors.append(vendor)
                    # Use config-based boost or fallback to hardcoded
                    if tier_name == "tier_1":
                        boost = vendor_config.get('tier_1_boost', 0.3)
                    elif tier_name == "tier_2":
                        boost = vendor_config.get('tier_2_boost', 0.2)
                    elif tier_name == "tier_3":
                        boost = vendor_config.get('tier_3_boost', 0.1)
                    else:
                        boost = vendor_config.get('tier_4_boost', 0.0)
                    vendor_boost = max(vendor_boost, boost)
        
        if vendor_boost > 0:
            confidence_factors.append(f"Tier 1-3 vendor detected (+{vendor_boost:.1f})")
            confidence_score += vendor_boost
        
        # Factor 2: Source reliability (0.0 to 0.2 boost)
        source_boost = 0.0
        reddit_sources = len([sid for sid in source_ids if 'reddit' in sid.lower()])
        google_sources = len([sid for sid in source_ids if 'google' in sid.lower()])
        
        multiple_reddit_boost = source_config.get('multiple_reddit', 0.15)
        single_reddit_boost = source_config.get('single_reddit', 0.1)
        google_boost = source_config.get('google_verification', 0.05)
        
        if reddit_sources >= 2:  # Multiple Reddit sources
            source_boost = multiple_reddit_boost
            confidence_factors.append(f"Multiple Reddit sources (+{multiple_reddit_boost})")
        elif reddit_sources >= 1:
            source_boost = single_reddit_boost
            confidence_factors.append(f"Reddit source (+{single_reddit_boost})")
        
        if google_sources >= 1:
            source_boost += google_boost
            confidence_factors.append(f"Google verification (+{google_boost})")
        
        confidence_score += source_boost
        
        # Factor 3: Quantified data presence (0.0 to 0.15 boost)
        quantified_patterns = [
            r'\d+%',  # Percentages
            r'\$\d+',  # Dollar amounts
            r'\d+\s*million',  # Millions
            r'\d+\s*billion',  # Billions
            r'increase.*\d+',  # Increases with numbers
            r'decrease.*\d+',  # Decreases with numbers
            r'\d+\s*days?',  # Days
            r'\d+\s*weeks?',  # Weeks
            r'\d+\s*months?'  # Months
        ]
        
        import re
        quantified_boost = 0.0
        quantified_matches = []
        
        for pattern in quantified_patterns:
            matches = re.findall(pattern, insight_text, re.IGNORECASE)
            if matches:
                quantified_matches.extend(matches[:2])  # Limit to prevent over-boost
        
        multiple_quantified_boost = data_config.get('multiple_quantified', 0.15)
        single_quantified_boost = data_config.get('single_quantified', 0.1)
        
        if len(quantified_matches) >= 3:
            quantified_boost = multiple_quantified_boost
            confidence_factors.append(f"Multiple quantified data (+{multiple_quantified_boost})")
        elif len(quantified_matches) >= 1:
            quantified_boost = single_quantified_boost
            confidence_factors.append(f"Quantified data present (+{single_quantified_boost})")
        
        confidence_score += quantified_boost
        
        # Factor 4: Business critical keywords (0.0 to 0.1 boost)
        critical_keywords = [
            'acquisition', 'merger', 'shutdown', 'discontinuation', 'end of life',
            'price increase', 'security breach', 'recall', 'bankruptcy', 'lawsuit'
        ]
        
        critical_boost = 0.0
        critical_matches = []
        for keyword in critical_keywords:
            if keyword in text_lower:
                critical_matches.append(keyword)
        
        multiple_critical_boost = data_config.get('critical_keywords_multiple', 0.1)
        single_critical_boost = data_config.get('critical_keywords_single', 0.05)
        
        if len(critical_matches) >= 2:
            critical_boost = multiple_critical_boost
            confidence_factors.append(f"Multiple critical indicators (+{multiple_critical_boost})")
        elif len(critical_matches) >= 1:
            critical_boost = single_critical_boost
            confidence_factors.append(f"Critical business indicator (+{single_critical_boost})")
        
        confidence_score += critical_boost
        
        # Cap confidence at 1.0 (100%)
        confidence_score = min(confidence_score, 1.0)
        
        # Determine confidence level category using configured thresholds
        high_threshold = thresholds.get('high', 0.8)
        medium_threshold = thresholds.get('medium', 0.6)
        
        if confidence_score >= high_threshold:
            confidence_level = "high"
            confidence_color = "#28a745"  # Green
        elif confidence_score >= medium_threshold:
            confidence_level = "medium"
            confidence_color = "#ffc107"  # Yellow
        else:
            confidence_level = "low"
            confidence_color = "#6c757d"  # Gray
        
        return {
            "confidence_score": round(confidence_score, 2),
            "confidence_level": confidence_level,
            "confidence_color": confidence_color,
            "confidence_percentage": round(confidence_score * 100),
            "confidence_factors": confidence_factors,
            "detected_vendors": detected_vendors,
            "quantified_data_points": len(quantified_matches),
            "source_count": len(source_ids)
        }
    
    def _fix_invalid_source_id(self, invalid_id: str, available_ids: List[str]) -> Optional[str]:
        """Try to fix invalid SOURCE_ID by finding closest match"""
        # Try exact prefix match (e.g., 'reddit_1' matches 'reddit_15')
        prefix = invalid_id.split('_')[0] if '_' in invalid_id else invalid_id
        for available_id in available_ids:
            if available_id.startswith(prefix + '_'):
                return available_id
        
        # Try fuzzy matching (simple edit distance)
        best_match = None
        best_score = float('inf')
        
        for available_id in available_ids:
            # Simple character difference scoring
            score = abs(len(invalid_id) - len(available_id))
            if invalid_id.lower() in available_id.lower() or available_id.lower() in invalid_id.lower():
                score -= 10  # Bonus for substring match
            
            if score < best_score:
                best_score = score
                best_match = available_id
        
        # Only return if it's a reasonable match
        if best_score < 5:  # Arbitrary threshold
            return best_match
        
        return None
    
    def _find_best_source_match(self, insight_text: str, available_ids: List[str]) -> Optional[str]:
        """Find best SOURCE_ID match using enhanced content analysis"""
        if not hasattr(self, 'source_mapping'):
            return None
        
        best_match_id = None
        best_match_score = 0
        
        insight_lower = insight_text.lower()
        
        for source_id in available_ids:
            source_data = self.source_mapping.get(source_id, {})
            source_text = f"{source_data.get('title', '')} {source_data.get('content', '')}".lower()
            
            # Enhanced matching algorithm
            matching_score = 0
            
            # 1. Keyword matching
            insight_words = set(word for word in insight_lower.split() if len(word) > 3)
            for word in insight_words:
                if word in source_text:
                    matching_score += 1
            
            # 2. Vendor name matching (higher weight)
            for vendor in self.key_vendors:
                if vendor.lower() in insight_lower and vendor.lower() in source_text:
                    matching_score += 3
            
            # 3. Title similarity bonus
            source_title = source_data.get('title', '').lower()
            if source_title:
                common_words = set(insight_lower.split()) & set(source_title.split())
                matching_score += len(common_words) * 2
            
            if matching_score > best_match_score:
                best_match_score = matching_score
                best_match_id = source_id
        
        # Only return if we have a reasonable match
        if best_match_score >= 2:  # Minimum threshold
            return best_match_id
        
        return None
    
    def _validate_and_inject_source_ids(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate SOURCE_IDs in insights and inject them if missing"""
        import re
        
        if not hasattr(self, 'source_mapping') or not self.source_mapping:
            logger.warning("No source mapping available for SOURCE_ID injection")
            return result
        
        # Get list of available SOURCE_IDs
        available_source_ids = list(self.source_mapping.keys())
        logger.info(f"Available SOURCE_IDs: {available_source_ids}")
        
        def inject_source_id_if_missing(insight_text: str) -> str:
            """Inject SOURCE_ID if missing from insight"""
            # Check if insight already has SOURCE_ID
            existing_source_ids = re.findall(r'\[([^]]+)\]', insight_text)
            if existing_source_ids:
                # Validate existing SOURCE_IDs
                for source_id in existing_source_ids:
                    if source_id in available_source_ids:
                        logger.info(f"✅ Valid SOURCE_ID found: {source_id}")
                        return insight_text
                    else:
                        logger.warning(f"⚠️ Invalid SOURCE_ID found: {source_id}")
                        # Try to fix invalid SOURCE_ID using enhanced matching
                        fixed_id = self._fix_invalid_source_id(source_id, available_source_ids)
                        if fixed_id:
                            fixed_insight = insight_text.replace(f'[{source_id}]', f'[{fixed_id}]')
                            logger.info(f"🔧 Fixed SOURCE_ID: {source_id} -> {fixed_id}")
                            return fixed_insight
                return insight_text
            
            # No SOURCE_ID found - need to inject one
            logger.warning(f"⚠️ Missing SOURCE_ID in insight: '{insight_text[:80]}...'")
            
            # Try intelligent matching using enhanced algorithm
            best_match_id = self._find_best_source_match(insight_text, available_source_ids)
            
            if best_match_id:
                injected_insight = f"{insight_text.rstrip()} [{best_match_id}]"
                logger.info(f"🎯 Intelligently injected SOURCE_ID: {best_match_id}")
                return injected_insight
            
            # Fallback to first available SOURCE_ID
            if available_source_ids:
                fallback_id = available_source_ids[0]
                injected_insight = f"{insight_text.rstrip()} [{fallback_id}]"
                logger.warning(f"⚠️ Fallback SOURCE_ID injection: {fallback_id}")
                return injected_insight
            
            logger.error(f"❌ Cannot inject SOURCE_ID - no sources available")
            return insight_text
        
        # Process insights in pricing_intelligence_summary
        if "pricing_intelligence_summary" in result:
            summary = result["pricing_intelligence_summary"]
            
            # Process critical_insights
            if "critical_insights" in summary and isinstance(summary["critical_insights"], list):
                for i, insight in enumerate(summary["critical_insights"]):
                    if isinstance(insight, str):
                        summary["critical_insights"][i] = inject_source_id_if_missing(insight)
            
            # Process strategic_recommendations
            if "strategic_recommendations" in summary and isinstance(summary["strategic_recommendations"], list):
                for i, recommendation in enumerate(summary["strategic_recommendations"]):
                    if isinstance(recommendation, str):
                        summary["strategic_recommendations"][i] = inject_source_id_if_missing(recommendation)
            
            # Process automated_action_recommendations
            if "automated_action_recommendations" in summary and isinstance(summary["automated_action_recommendations"], list):
                for action in summary["automated_action_recommendations"]:
                    if isinstance(action, dict) and "action_title" in action:
                        action["action_title"] = inject_source_id_if_missing(action["action_title"])
                    if isinstance(action, dict) and "technical_signal" in action:
                        action["technical_signal"] = inject_source_id_if_missing(action["technical_signal"])
        
        return result
    
    def _add_confidence_to_insights(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Add confidence calculations to all insights in the holistic summary"""
        import re
        
        # Process insights in pricing_intelligence_summary
        if "pricing_intelligence_summary" in result:
            summary = result["pricing_intelligence_summary"]
            
            # Process critical_insights
            if "critical_insights" in summary and isinstance(summary["critical_insights"], list):
                enhanced_insights = []
                for insight in summary["critical_insights"]:
                    if isinstance(insight, str):
                        # Extract source IDs from insight text
                        source_ids = re.findall(r'\[([^]]+)\]', insight)
                        
                        # Debug logging for Lenovo insights
                        if 'lenovo' in insight.lower():
                            logger.info(f"🔍 LENOVO INSIGHT DETECTED: {insight[:100]}...")
                            logger.info(f"   📋 Source IDs: {source_ids}")
                        
                        # Calculate confidence
                        confidence_data = self._calculate_insight_confidence(insight, source_ids)
                        
                        # Create enhanced insight object
                        enhanced_insight = {
                            "text": insight,
                            "confidence": confidence_data,
                            "source_ids": source_ids
                        }
                        enhanced_insights.append(enhanced_insight)
                        
                        if self.debug:
                            logger.info(f"🎯 CONFIDENCE: '{insight[:60]}...' = {confidence_data['confidence_level']} ({confidence_data['confidence_percentage']}%)")
                
                summary["critical_insights"] = enhanced_insights
            
            # Process strategic_recommendations
            if "strategic_recommendations" in summary and isinstance(summary["strategic_recommendations"], list):
                enhanced_recommendations = []
                for recommendation in summary["strategic_recommendations"]:
                    if isinstance(recommendation, str):
                        # Extract source IDs from recommendation text
                        source_ids = re.findall(r'\[([^]]+)\]', recommendation)
                        
                        # Debug logging for Lenovo recommendations
                        if 'lenovo' in recommendation.lower():
                            logger.info(f"🔍 LENOVO RECOMMENDATION DETECTED: {recommendation[:100]}...")
                            logger.info(f"   📋 Source IDs: {source_ids}")
                        
                        # Calculate confidence (recommendations typically have medium confidence)
                        confidence_data = self._calculate_insight_confidence(recommendation, source_ids)
                        
                        # Adjust confidence for recommendations (slightly lower)
                        confidence_data["confidence_score"] = max(0.4, confidence_data["confidence_score"] - 0.1)
                        confidence_data["confidence_percentage"] = round(confidence_data["confidence_score"] * 100)
                        
                        if confidence_data["confidence_score"] >= 0.8:
                            confidence_data["confidence_level"] = "high"
                        elif confidence_data["confidence_score"] >= 0.6:
                            confidence_data["confidence_level"] = "medium"
                        else:
                            confidence_data["confidence_level"] = "low"
                        
                        enhanced_recommendation = {
                            "text": recommendation,
                            "confidence": confidence_data,
                            "source_ids": source_ids
                        }
                        enhanced_recommendations.append(enhanced_recommendation)
                
                summary["strategic_recommendations"] = enhanced_recommendations
        
        # Also process legacy role_summaries structure if present
        if "role_summaries" in result:
            for role_name, role_data in result["role_summaries"].items():
                if "key_insights" in role_data and isinstance(role_data["key_insights"], list):
                    enhanced_insights = []
                    for insight in role_data["key_insights"]:
                        if isinstance(insight, str):
                            # Extract source IDs from insight text
                            source_ids = re.findall(r'\[([^]]+)\]', insight)
                            
                            # Calculate confidence
                            confidence_data = self._calculate_insight_confidence(insight, source_ids)
                            
                            enhanced_insight = {
                                "text": insight,
                                "confidence": confidence_data,
                                "source_ids": source_ids
                            }
                            enhanced_insights.append(enhanced_insight)
                    
                    role_data["key_insights"] = enhanced_insights
        
        return result

    def _generate_fallback_summary(self):
        """Enhanced fallback with meaningful content"""
        logger.warning("Using enhanced fallback summary generation")
        
        # Use all 3 roles for comprehensive coverage
        roles = {"pricing_analyst", "procurement_manager", "bi_strategy"}
        
        role_templates = {
            "pricing_analyst": {
                "role": "Pricing Analyst",
                "focus": "SKU-level margin impacts and vendor pricing changes",
                "summary": "Pricing intelligence system encountered processing issues. No actionable insights generated.",
                "key_insights": []
            },
            "procurement_manager": {
                "role": "Procurement Manager", 
                "focus": "Supply chain risks and vendor relationship changes",
                "summary": "Supply chain intelligence system encountered processing issues. No actionable insights generated.",
                "key_insights": []
            },
            "bi_strategy": {
                "role": "BI Strategy Analyst",
                "focus": "Market intelligence and competitive positioning", 
                "summary": "Market intelligence system encountered processing issues. No actionable insights generated.",
                "key_insights": []
            }
        }
        
        fallback = {
            "role_summaries": {},
            "by_urgency": {"high": 1, "medium": 2, "low": 0},
            "total_items": 0
        }
        
        for role in roles:
            fallback["role_summaries"][role] = {
                **role_templates[role],
                "top_vendors": [
                    {"vendor": "System Alert", "mentions": 1, "highlighted": True}
                ],
                "sources": {"System": 1}
            }
        
        return fallback

    def generate_summary(self, content_by_source: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Hybrid summary generation with holistic team perspective"""
        self.config = config
        
        # Set API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OpenAI API key not found - cannot generate real insights")
            return {"error": "No API key - real insights require OpenAI access"}

        # Enhanced content preprocessing (no aggressive filtering)
        combined_content = self._preprocess_content(content_by_source)
        
        if not combined_content.strip():
            logger.warning("No content to process - real insights require actual data")
            return {"error": "No content available - cannot generate real insights without data"}

        # Use unified team perspective instead of role-based
        logger.info("Using holistic team-wide pricing intelligence perspective")

        # Build holistic team prompt
        prompt = self._build_holistic_team_prompt(combined_content)

        try:
            # Use original ultrathink's exact OpenAI API format (v0.28.1 compatible)
            openai.api_key = api_key
            
            response = openai.ChatCompletion.create(
                model=config.get("summarization", {}).get("model", "gpt-4"),
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a senior intelligence analyst for a leading IT solutions provider. You specialize in vendor pricing intelligence, supply chain analysis, and competitive market intelligence. Your analyses directly impact procurement decisions, pricing strategies, and business intelligence for technology distribution operations."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=config.get("summarization", {}).get("temperature", 0.2),
                max_tokens=2000,  # Original's higher limit for richer content
                presence_penalty=0.1,  # Original's parameters for diverse insights
                frequency_penalty=0.1   # Reduce repetition
            )

            content = response.choices[0].message.content.strip()

            # Enhanced JSON cleaning (original approach)
            content = re.sub(r"^```(?:json)?\s*", "", content)
            content = re.sub(r"\s*```$", "", content).strip()
            
            # Remove any leading/trailing markdown or explanatory text
            content = re.sub(r"^[^{]*", "", content)
            # Find the last } and trim everything after it
            last_brace = content.rfind('}')
            if last_brace != -1:
                content = content[:last_brace + 1]

            # Save raw output for debugging
            os.makedirs("output", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(f"output/hybrid_gpt_raw_{timestamp}.txt", "w", encoding="utf-8") as f:
                f.write(f"PROMPT:\n{prompt}\n\n" + "="*50 + "\n\nRESPONSE:\n" + content)

            # Parse and validate JSON
            result = json.loads(content)
            
            # Validate holistic structure
            if not self._validate_holistic_structure(result):
                logger.error("Generated summary failed validation")
                return self._generate_holistic_fallback_summary()

            # Validate and inject SOURCE_IDs if missing
            result = self._validate_and_inject_source_ids(result)
            
            # Add confidence calculations to insights
            result = self._add_confidence_to_insights(result)
            
            # Add enhanced analysis metadata
            result = self._add_analysis_metadata(result, content_by_source)

            logger.info(f"✅ Generated hybrid summary for {len(result.get('role_summaries', {}))} roles")
            return result

        except openai.error.RateLimitError:
            logger.error("❌ OpenAI rate limit exceeded")
            return {"error": "Rate limit exceeded - please try again later"}
        except openai.error.APIError as e:
            logger.error(f"❌ OpenAI API error: {e}")
            return {"error": f"OpenAI API error: {e}"}
        except Exception as e:
            logger.error(f"❌ GPT summarization failed: {e}")
            return {"error": f"Summarization failed: {e}"}

    def _validate_holistic_structure(self, result: Dict[str, Any]) -> bool:
        """Validate the holistic summary structure"""
        try:
            # Check top-level structure
            if "pricing_intelligence_summary" not in result:
                logger.error("Missing pricing_intelligence_summary")
                return False
            
            summary = result["pricing_intelligence_summary"]
            required_keys = {"executive_overview", "critical_insights", "vendor_landscape", "strategic_recommendations", "market_intelligence"}
            
            if not all(key in summary for key in required_keys):
                logger.error(f"Missing required keys in summary: {required_keys - set(summary.keys())}")
                return False
            
            # Check vendor_landscape structure
            vendor_landscape = summary.get("vendor_landscape", {})
            vendor_required = {"pricing_changes", "market_movements", "supply_chain_alerts"}
            
            if not all(key in vendor_landscape for key in vendor_required):
                logger.error(f"Missing vendor_landscape keys: {vendor_required - set(vendor_landscape.keys())}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False

    def _validate_summary_structure(self, result: Dict[str, Any], expected_roles: set) -> bool:
        """Original validation logic"""
        try:
            # Check top-level structure
            required_keys = {"role_summaries", "by_urgency", "total_items"}
            if not all(key in result for key in required_keys):
                logger.error(f"Missing required keys: {required_keys - set(result.keys())}")
                return False
            
            # Check role summaries
            role_summaries = result.get("role_summaries", {})
            for role in expected_roles:
                if role not in role_summaries:
                    logger.error(f"Missing role summary for: {role}")
                    return False
                
                role_data = role_summaries[role]
                required_role_keys = {"role", "focus", "summary", "key_insights", "top_vendors", "sources"}
                if not all(key in role_data for key in required_role_keys):
                    logger.error(f"Missing keys in role {role}: {required_role_keys - set(role_data.keys())}")
                    return False
            
            # Check urgency structure
            urgency = result.get("by_urgency", {})
            if not all(level in urgency for level in ["high", "medium", "low"]):
                logger.error("Invalid urgency structure")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False

    def _add_analysis_metadata(self, result: Dict[str, Any], content_by_source: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Enhanced metadata generation"""
        
        # Collect all analyzed content with metadata
        analyzed_content = []
        for source, items in content_by_source.items():
            for item in items:
                analyzed_item = {
                    "title": item.get('title', 'No title'),
                    "source": source,
                    "url": item.get('url', ''),
                    "relevance_score": item.get('relevance_score', 0),
                    "created_at": item.get('created_at', ''),
                    "urgency": item.get('urgency', 'low'),
                    "content_preview": item.get('content', item.get('text', ''))[:200] + "..." if item.get('content', item.get('text', '')) else ""
                }
                analyzed_content.append(analyzed_item)
        
        # Sort by relevance score
        analyzed_content.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Fix vendor mention counts to be consistent
        actual_vendor_mentions = {}
        for item in analyzed_content:
            text = f"{item.get('title', '')} {item.get('content_preview', '')}".lower()
            for vendor in self.key_vendors:
                if vendor.lower() in text:
                    actual_vendor_mentions[vendor] = actual_vendor_mentions.get(vendor, 0) + 1
        
        # Update vendor counts in each role summary
        for role_key, role_data in result.get('role_summaries', {}).items():
            if 'top_vendors' in role_data:
                # Update with actual counts
                updated_vendors = []
                for vendor_info in role_data['top_vendors']:
                    vendor_name = vendor_info['vendor']
                    actual_count = actual_vendor_mentions.get(vendor_name, 0)
                    if actual_count > 0:
                        updated_vendors.append({
                            'vendor': vendor_name,
                            'mentions': actual_count,
                            'highlighted': vendor_info.get('highlighted', False)
                        })
                
                # Sort by mention count and limit to top 5
                updated_vendors.sort(key=lambda x: x['mentions'], reverse=True)
                role_data['top_vendors'] = updated_vendors[:5]
            
            # Fix source counts
            source_counts = {}
            for item in analyzed_content:
                source = item['source'].title()
                source_counts[source] = source_counts.get(source, 0) + 1
            
            role_data['sources'] = source_counts
        
        # Update totals
        result['total_items'] = len(analyzed_content)
        
        return result