import openai
import os
import json
import logging
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class GPTSummarizer:
    def __init__(self):
        self.config = None
        # Industry-specific vendors and products for enhanced detection
        self.key_vendors = [
            "Dell", "Microsoft", "Cisco", "Lenovo", "Apple", "HP", "HPE",
            "CrowdStrike", "Fortinet", "Proofpoint", "Zscaler", "SentinelOne", 
            "Palo Alto Networks", "Check Point", "Splunk", "VMware",
            "Amazon", "AWS", "Azure", "Google Cloud", "Oracle",
            "TD Synnex", "Ingram Micro", "CDW", "Insight Global", "SHI",
            "Broadcom", "Intel", "AMD", "NVIDIA", "NetApp", "Pure Storage"
        ]
        
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

    def _deduplicate_content(self, content_by_source: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Deduplicate content using hash of title + first 100 chars"""
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
        """Enhanced content preprocessing with better structure"""
        # Deduplicate first
        content_by_source = self._deduplicate_content(content_by_source)
        
        processed_sections = []
        total_items = 0
        
        for source, items in content_by_source.items():
            if not items:
                continue
                
            section_content = []
            for item in items[:20]:  # Limit items per source
                # Enhanced item processing
                title = item.get('title', '')
                content = item.get('content', item.get('text', ''))
                url = item.get('url', '')
                score = item.get('relevance_score', 0)
                created_at = item.get('created_at', '')
                
                # Create rich item representation
                item_text = f"TITLE: {title}\n"
                if content and content != title:
                    item_text += f"CONTENT: {content[:500]}\n"
                if score:
                    item_text += f"RELEVANCE: {score}\n"
                if created_at:
                    item_text += f"DATE: {created_at}\n"
                item_text += "---\n"
                
                section_content.append(item_text)
                total_items += 1
            
            if section_content:
                source_section = f"\n=== {source.upper()} SOURCE ({len(section_content)} items) ===\n"
                source_section += "\n".join(section_content)
                processed_sections.append(source_section)
        
        combined_content = "\n\n".join(processed_sections)
        
        # Truncate to fit within token limits (roughly 8000 chars = ~2000 tokens)
        if len(combined_content) > 8000:
            combined_content = combined_content[:8000] + "\n\n[CONTENT TRUNCATED]"
        
        logger.info(f"Preprocessed {total_items} total items across {len(processed_sections)} sources")
        return combined_content

    def _build_enhanced_prompt(self, roles: set, combined_content: str) -> str:
        """Build industry-specific, role-targeted prompt"""
        
        # Build dynamic role descriptions
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
        
        # Create role-specific sections
        role_specs = []
        for role in roles:
            if role in role_descriptions:
                desc = role_descriptions[role]
                role_specs.append(f'    "{role}": {{\n      "role": "{desc["title"]}",\n      "focus": "{desc["focus"]}",\n      // Prioritize: {desc["priorities"]}\n    }}')
        
        role_object = "{\n" + ",\n".join(role_specs) + "\n  }"
        
        prompt = f"""You are a senior intelligence analyst for Softchoice, a leading North American IT solutions provider. Analyze vendor pricing intelligence for our teams competing against CDW and Insight Global.

🏢 INDUSTRY CONTEXT:
- We're an IT distributor/reseller focused on software, hardware, security, cloud
- Key vendors: Dell, Microsoft, Cisco, Lenovo, Apple, CrowdStrike, Fortinet, Zscaler
- Key distributors: TD Synnex, Ingram Micro
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

    def _generate_fallback_summary(self):
        """Generate enhanced fallback summary with industry context"""
        logger.warning("Using enhanced fallback summary generation")
        
        roles = {e['role'] for e in self.config.get('employees', [])} or {"pricing_analyst"}
        
        role_templates = {
            "pricing_analyst": {
                "role": "Pricing Analyst",
                "focus": "SKU-level margin impacts and vendor pricing changes",
                "summary": "Unable to process current pricing intelligence due to API limitations. Please check vendor portals directly for latest pricing updates.",
                "key_insights": [
                    "🔴 API Error - Direct vendor portal verification recommended",
                    "🟡 Monitor Dell, Microsoft, Cisco pricing for manual updates",
                    "🟢 Fallback: Review TD Synnex and Ingram Micro communications"
                ]
            },
            "procurement_manager": {
                "role": "Procurement Manager", 
                "focus": "Supply chain risks and vendor relationship changes",
                "summary": "Procurement intelligence unavailable due to system error. Recommend direct supplier contact for critical supply updates.",
                "key_insights": [
                    "🔴 API Error - Contact key vendors directly for supply status",
                    "🟡 Verify TD Synnex and Ingram Micro inventory levels manually",
                    "🟢 Fallback: Check vendor portals for fulfillment updates"
                ]
            },
            "bi_strategy": {
                "role": "BI Strategy Analyst",
                "focus": "Market intelligence and competitive positioning", 
                "summary": "Strategic intelligence processing failed. Monitor industry publications and vendor announcements directly.",
                "key_insights": [
                    "🔴 API Error - Review CRN, ChannelE2E for market updates",
                    "🟡 Monitor CDW and Insight Global announcements manually",
                    "🟢 Fallback: Check vendor investor relations for strategic updates"
                ]
            }
        }
        
        fallback = {
            "role_summaries": {},
            "by_urgency": {"high": 1, "medium": 0, "low": 0},  # Mark as high urgency due to system failure
            "total_items": 0
        }
        
        for role in roles:
            if role in role_templates:
                fallback["role_summaries"][role] = {
                    **role_templates[role],
                    "top_vendors": [
                        {"vendor": "System Error", "mentions": 1, "highlighted": True}
                    ],
                    "sources": {"System": 1}
                }
            else:
                # Generic fallback for unknown roles
                fallback["role_summaries"][role] = {
                    "role": role.replace('_', ' ').title(),
                    "focus": "Unable to determine focus due to API error",
                    "summary": "Intelligence processing failed - manual verification required",
                    "key_insights": ["🔴 API Error - Manual process recommended"],
                    "top_vendors": [],
                    "sources": {}
                }
        
        return fallback

    def generate_summary(self, content_by_source: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced summary generation with industry intelligence"""
        self.config = config
        openai.api_key = os.getenv("OPENAI_API_KEY")

        # Enhanced content preprocessing
        combined_content = self._preprocess_content(content_by_source)
        
        if not combined_content.strip():
            logger.warning("No content to process")
            return self._generate_fallback_summary()

        # Get roles from config
        roles = {e['role'] for e in config.get('employees', [])}
        if not roles:
            roles = {"pricing_analyst"}

        # Build enhanced prompt
        prompt = self._build_enhanced_prompt(roles, combined_content)

        try:
            # Enhanced GPT call with industry-specific system message
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
                temperature=config.get("summarization", {}).get("temperature", 0.2),  # Lower for more consistent output
                max_tokens=config.get("summarization", {}).get("max_tokens", 2000),  # Increased for richer content
                presence_penalty=0.1,  # Encourage diverse insights
                frequency_penalty=0.1   # Reduce repetition
            )

            content = response.choices[0].message.content.strip()

            # Enhanced JSON cleaning
            content = re.sub(r"^```(?:json)?\s*", "", content)
            content = re.sub(r"\s*```$", "", content).strip()
            
            # Remove any leading/trailing markdown or explanatory text
            content = re.sub(r"^[^{]*", "", content)
            # Find the last } and trim everything after it
            last_brace = content.rfind('}')
            if last_brace != -1:
                content = content[:last_brace + 1]

            # Save enhanced raw output for debugging
            os.makedirs("output", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(f"output/last_gpt_raw_{timestamp}.txt", "w", encoding="utf-8") as f:
                f.write(f"PROMPT:\n{prompt}\n\n" + "="*50 + "\n\nRESPONSE:\n" + content)

            # Parse and validate JSON
            result = json.loads(content)
            
            # Validate structure
            if not self._validate_summary_structure(result, roles):
                logger.error("Generated summary failed validation")
                return self._generate_fallback_summary()

            # Add comprehensive analysis metadata
            result = self._add_analysis_metadata(result, content_by_source)

            logger.info(f"✅ Generated enhanced summary for {len(result.get('role_summaries', {}))} roles")
            return result

        except openai.error.RateLimitError:
            logger.error("❌ OpenAI rate limit exceeded")
            return self._generate_fallback_summary()
            
        except openai.error.APIError as e:
            logger.error(f"❌ OpenAI API error: {e}")
            return self._generate_fallback_summary()
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON from GPT: {e}")
            logger.debug(f"Raw GPT output:\n{content}")
            return self._generate_fallback_summary()
            
        except Exception as e:
            logger.exception("❌ Unexpected error in GPT summarization")
            return self._generate_fallback_summary()

    def _validate_summary_structure(self, result: Dict[str, Any], expected_roles: set) -> bool:
        """Validate the generated summary structure"""
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
        """Add comprehensive analysis metadata including sources, keywords, and raw content"""
        
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
        
        # Count actual urgencies from processed items (this should match the summary)
        actual_urgency_counts = {"high": 0, "medium": 0, "low": 0}
        for item in analyzed_content:
            urgency = item.get('urgency', 'low')
            if urgency in actual_urgency_counts:
                actual_urgency_counts[urgency] += 1
        
        # Override the GPT-generated urgency counts with actual counts
        result['by_urgency'] = actual_urgency_counts
        
        # Update total_items to match actual processed items
        result['total_items'] = len(analyzed_content)
        
        # Fix vendor mention counts to be consistent across roles
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
                    if actual_count > 0:  # Only include vendors that actually appear
                        updated_vendors.append({
                            'vendor': vendor_name,
                            'mentions': actual_count,
                            'highlighted': vendor_info.get('highlighted', False)
                        })
                
                # Sort by mention count and limit to top 5
                updated_vendors.sort(key=lambda x: x['mentions'], reverse=True)
                role_data['top_vendors'] = updated_vendors[:5]
            
            # Fix source counts to reflect actual processed items, not GPT estimates
            source_counts = {}
            for item in analyzed_content:
                source = item['source'].title()
                source_counts[source] = source_counts.get(source, 0) + 1
            
            role_data['sources'] = source_counts
        
        # Add metadata to result
        result['analysis_metadata'] = {
            "keywords_used": {
                "urgency_high": self.urgency_keywords["high"],
                "urgency_medium": self.urgency_keywords["medium"],
                "key_vendors": self.key_vendors,
                "pricing_keywords": [
                    "price increase", "cost increase", "discount", "margin", "pricing", 
                    "rebate", "promotion", "SKU", "cost", "fee", "subscription",
                    "licensing", "contract", "enterprise agreement", "volume discount"
                ],
                "supply_chain_keywords": [
                    "supply", "shortage", "delay", "fulfillment", "inventory", 
                    "distribution", "warehouse", "logistics", "lead time", "availability"
                ],
                "strategy_keywords": [
                    "acquisition", "merger", "partnership", "competition", "market share",
                    "consolidation", "expansion", "investment", "strategic", "competitive"
                ]
            },
            "content_analyzed": analyzed_content,
            "processing_stats": {
                "total_items_processed": len(analyzed_content),
                "sources_processed": list(content_by_source.keys()),
                "deduplication_applied": True,
                "urgency_detection_enabled": True,
                "vendor_detection_enabled": True
            }
        }
        
        return result

    def get_analysis_keywords(self) -> Dict[str, List[str]]:
        """Return all keywords and criteria used for analysis"""
        return {
            "key_vendors": self.key_vendors,
            "urgency_keywords": self.urgency_keywords,
            "pricing_indicators": [
                "price increase", "cost increase", "discount", "margin", "pricing", 
                "rebate", "promotion", "SKU", "cost", "fee", "subscription",
                "licensing", "contract", "enterprise agreement", "volume discount",
                "markup", "margin compression", "vendor pricing", "distributor pricing"
            ],
            "supply_chain_indicators": [
                "supply", "shortage", "delay", "fulfillment", "inventory", 
                "distribution", "warehouse", "logistics", "lead time", "availability",
                "supply chain", "vendor relationship", "procurement", "sourcing"
            ],
            "strategic_indicators": [
                "acquisition", "merger", "partnership", "competition", "market share",
                "consolidation", "expansion", "investment", "strategic", "competitive",
                "market positioning", "competitive advantage", "industry trends"
            ]
        }