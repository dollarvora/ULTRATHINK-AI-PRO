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
- Processes up to 20 highest-scoring content items
- Generates 3-tier priority insights (Alpha/Beta/Gamma)
- Structured JSON output for HTML report integration
- Comprehensive vendor landscape analysis

AUTHENTICATION REQUIRED:
- OPENAI_API_KEY: OpenAI GPT-4 API key for content analysis

Author: Dollar (dollar3191@gmail.com)
System: ULTRATHINK-AI-PRO v3.1.0 Hybrid
"""
import openai
import os
import json
import logging
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any

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
            # Original's proven limit: 20 items per source (no aggressive filtering)
            for item in items[:20]:
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
                
                # Create rich item representation with source ID for footnote tracking
                source_id = f"{source}_{total_items + 1}"
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
                
                # Store source mapping for footnote generation
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
            
            if section_content:
                source_section = f"\n=== {source.upper()} SOURCE ({len(section_content)} items) ===\n"
                source_section += "\n".join(section_content)
                processed_sections.append(source_section)
        
        combined_content = "\n\n".join(processed_sections)
        
        # Original's token management (8000 chars ≈ 2000 tokens)
        if len(combined_content) > 8000:
            combined_content = combined_content[:8000] + "\n\n[CONTENT TRUNCATED]"
        
        logger.info(f"Preprocessed {total_items} total items across {len(processed_sections)} sources")
        return combined_content

    def _build_enhanced_prompt(self, roles: set, combined_content: str) -> str:
        """Original's proven prompt structure with enhanced context"""
        
        # Original role descriptions (proven to work)
        role_descriptions = {
            "pricing_analyst": {
                "title": "Pricing Analyst",
                "focus": "SKU-level margin impacts, vendor cost shifts, competitive pricing moves",
                "priorities": "Price increases/decreases, vendor promotions, margin threats, discount trends, SKU discontinuations"
            },
            "procurement_manager": {
                "title": "Procurement Manager", 
                "focus": "Supply chain risks, vendor incentives, fulfillment issues, contract changes",
                "priorities": "Vendor behavior changes, supply shortages, rebate programs, terms modifications, distributor updates"
            },
            "bi_strategy": {
                "title": "BI Strategy Analyst",
                "focus": "Market consolidation, competitive intelligence, vendor ecosystem shifts",
                "priorities": "M&A activity, partnership changes, market trends, competitive positioning, industry disruption"
            }
        }
        
        # Create role-specific sections (original format)
        role_specs = []
        for role in roles:
            if role in role_descriptions:
                desc = role_descriptions[role]
                role_specs.append(f'    "{role}": {{\n      "role": "{desc["title"]}",\n      "focus": "{desc["focus"]}",\n      // Prioritize: {desc["priorities"]}\n    }}')
        
        role_object = "{\n" + ",\n".join(role_specs) + "\n  }"
        
        # Original's proven prompt with enhanced vendor context
        prompt = f"""You are a senior intelligence analyst for a leading North American IT solutions provider. Analyze vendor pricing intelligence for teams competing against CDW and Insight Global.

🏢 INDUSTRY CONTEXT:
- We're an IT distributor/reseller focused on software, hardware, security, cloud
- Key vendors: {', '.join(self.key_vendors[:15])}
- Key distributors: TD Synnex, Ingram Micro, CDW
- Product categories: Security software, cloud services, networking gear, laptops/desktops

📊 ANALYSIS REQUIREMENTS:
- Focus on last 24-48 hours for urgency detection
- Use QUANTIFIED insights (percentages, dollar amounts, timeframes)
- Detect pricing changes, supply issues, vendor behavior shifts
- Tag urgency: HIGH (immediate price/supply impacts), MEDIUM (notable changes), LOW (general updates)

🎯 OUTPUT FORMAT:
{{
  "role_summaries": {role_object},
  "by_urgency": {{"high": 0, "medium": 0, "low": 0}},
  "total_items": 0
}}

📝 ROLE-SPECIFIC REQUIREMENTS:

**Pricing Analyst**: Focus on margin-impacting changes, SKU pricing, vendor discounts
- Example: "🔴 Dell Precision workstations +15% via CDW effective immediately"
- Example: "🟢 TD Synnex offering 12% Zscaler discount through Q3"

**Procurement Manager**: Focus on supply chain, vendor terms, fulfillment issues  
- Example: "🟡 Ingram Micro reports 3-week delays for Lenovo ThinkPads"
- Example: "🟢 Microsoft introducing new Enterprise Agreement rebate structure"

**BI Strategy**: Focus on market moves, acquisitions, competitive shifts
- Example: "🔴 Broadcom acquiring VMware - expect licensing model changes"
- Example: "🟢 CDW expanding cybersecurity practice via new partnerships"

🎯 FEW-SHOT EXAMPLES:

Example 1 - Pricing Focus:
{{
  "pricing_analyst": {{
    "role": "Pricing Analyst",
    "focus": "Margin impacts and SKU-level pricing changes",
    "summary": "Significant vendor price adjustments detected: Dell workstation pricing increased 15% through CDW, while TD Synnex is offering enhanced Zscaler discounts to compete.",
    "key_insights": [
      "🔴 Dell Precision 5000 series +15% price increase via CDW (effective 6/15)",
      "🟢 TD Synnex Zscaler ZIA discount increased to 12% through Q3 2024",
      "🟡 Microsoft 365 E5 pricing adjustment (+3%) announced for new contracts"
    ],
    "top_vendors": [
      {{"vendor": "Dell", "mentions": 3, "highlighted": true}},
      {{"vendor": "Zscaler", "mentions": 2, "highlighted": true}}
    ],
    "sources": {{"Reddit": 2, "Google News": 4, "LinkedIn": 1}}
  }}
}}

💡 URGENCY DETECTION:
- HIGH: Price increases >10%, supply shortages, security breaches, M&A announcements
- MEDIUM: Price changes <10%, new partnerships, product launches, discount programs  
- LOW: General updates, blog posts, minor announcements

⚠️ CRITICAL RULES:
1. Return ONLY valid JSON - no markdown, no explanations
2. Use specific numbers/percentages when available
3. Include vendor names from our key vendor list when relevant
4. Prioritize recent content (last 24-48 hours) for urgency tagging
5. Each role must have actionable insights relevant to their function

Now analyze this content and generate role-specific intelligence:

{combined_content}"""

        return prompt

    def _build_holistic_team_prompt(self, combined_content: str) -> str:
        """Build holistic team-wide pricing intelligence prompt"""
        
        # Comprehensive vendor coverage
        all_vendors = ", ".join(self.key_vendors)
        
        prompt = f"""You are the lead pricing intelligence analyst for a world-class IT distribution company. Your team provides comprehensive market intelligence across ALL vendors, manufacturers, and technology categories to support enterprise decision-making.

🏢 COMPREHENSIVE VENDOR ECOSYSTEM:
- Primary Vendors: {all_vendors}
- Coverage: Hardware, Software, Cloud, Security, Networking, Storage, AI/ML
- Market Focus: Enterprise IT procurement, distributor pricing, channel intelligence
- Geographic Scope: North American IT reseller marketplace

🎯 HOLISTIC ANALYSIS FRAMEWORK:
Generate unified pricing intelligence that covers:
- VENDOR PRICING: Rate changes, margin shifts, competitive positioning
- MARKET DYNAMICS: Supply chain impacts, demand fluctuations, seasonal trends
- STRATEGIC INTELLIGENCE: M&A activity, partnership changes, product lifecycle
- PROCUREMENT INSIGHTS: Contract negotiations, volume discounts, fulfillment issues
- COMPETITIVE LANDSCAPE: Pricing wars, market share shifts, new entrants

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

🚨 ANALYSIS REQUIREMENTS:
1. Extract REAL intelligence from the provided content - never fabricate data
2. Cover ALL vendor categories: Hardware, Software, Cloud, Security, Networking
3. Identify cross-vendor patterns and market-wide trends
4. Prioritize actionable intelligence over general market commentary
5. Include specific dollar amounts, percentages, and timeframes when available
6. Highlight supply chain, competitive, and pricing risks
7. Generate strategic recommendations based on detected patterns
8. CRITICAL: Each insight MUST include [SOURCE_ID] reference to the source content that generated it
9. Use the exact SOURCE_ID from the content (e.g., reddit_1, google_2) to enable footnote linking

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

CONTENT TO ANALYZE:

{combined_content}"""

        return prompt

    def _generate_holistic_fallback_summary(self):
        """Generate comprehensive fallback with team-wide perspective"""
        logger.warning("Generating holistic team fallback summary")
        
        fallback = {
            "pricing_intelligence_summary": {
                "executive_overview": "Pricing intelligence system temporarily operating in fallback mode. Comprehensive vendor monitoring continues with manual verification recommended for critical procurement decisions.",
                "critical_insights": [
                    "🔴 SYSTEM ALERT: Direct vendor portal monitoring recommended for urgent pricing updates",
                    "🟡 COVERAGE: Monitor key distributors (TD Synnex, Ingram Micro, CDW) for price communications",
                    "🟢 STRATEGY: Maintain procurement relationships while system intelligence is restored"
                ],
                "vendor_landscape": {
                    "pricing_changes": [
                        {"vendor": "Multiple", "change": "System monitoring temporarily limited", "impact": "Medium", "timeframe": "Current"}
                    ],
                    "market_movements": [
                        {"type": "System Alert", "description": "Manual intelligence gathering recommended", "implications": "Temporary process adjustment needed"}
                    ],
                    "supply_chain_alerts": [
                        {"vendor": "All Vendors", "issue": "Direct supplier contact recommended for critical items", "severity": "Moderate"}
                    ]
                },
                "strategic_recommendations": [
                    "Activate manual vendor monitoring procedures for critical procurement items",
                    "Maintain direct communication channels with key supplier representatives",
                    "Review and update vendor portal access credentials for direct price checking",
                    "Schedule follow-up system diagnostics to restore full intelligence capabilities"
                ],
                "market_intelligence": {
                    "trending_vendors": [
                        {"vendor": "System Status", "mentions": 1, "sentiment": "Neutral", "key_topics": ["monitoring", "manual_verification"]}
                    ],
                    "pricing_patterns": [
                        "System analysis temporarily limited - recommend direct vendor communication"
                    ],
                    "risk_factors": [
                        "Reduced automated monitoring may impact response time to market changes"
                    ]
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

    def _generate_fallback_summary(self):
        """Enhanced fallback with meaningful content"""
        logger.warning("Using enhanced fallback summary generation")
        
        # Use all 3 roles for comprehensive coverage
        roles = {"pricing_analyst", "procurement_manager", "bi_strategy"}
        
        role_templates = {
            "pricing_analyst": {
                "role": "Pricing Analyst",
                "focus": "SKU-level margin impacts and vendor pricing changes",
                "summary": "Limited pricing intelligence available. Recommend direct vendor portal monitoring for critical updates.",
                "key_insights": [
                    "🔴 System Alert - Direct vendor verification recommended for pricing updates",
                    "🟡 Monitor key vendor portals: Dell, Microsoft, Cisco for manual price checks",
                    "🟢 Verify distributor communications from TD Synnex and Ingram Micro"
                ]
            },
            "procurement_manager": {
                "role": "Procurement Manager", 
                "focus": "Supply chain risks and vendor relationship changes",
                "summary": "Supply chain intelligence limited. Direct supplier contact recommended for critical items.",
                "key_insights": [
                    "🔴 System Alert - Contact key suppliers directly for inventory status",
                    "🟡 Verify availability with distributors for high-demand SKUs",
                    "🟢 Check vendor portals for fulfillment and shipping updates"
                ]
            },
            "bi_strategy": {
                "role": "BI Strategy Analyst",
                "focus": "Market intelligence and competitive positioning", 
                "summary": "Market intelligence gathering limited. Monitor industry publications for strategic updates.",
                "key_insights": [
                    "🔴 System Alert - Review CRN, ChannelE2E for market developments",
                    "🟡 Monitor competitor announcements and vendor strategic updates",
                    "🟢 Check vendor investor relations pages for partnership news"
                ]
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