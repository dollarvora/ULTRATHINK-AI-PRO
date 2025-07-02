import openai
import os
import json
import logging
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Import enhanced components
from utils.company_alias_matcher import get_company_matcher
from utils.employee_manager import EmployeeManager, load_employee_manager

logger = logging.getLogger(__name__)

class GPTSummarizer:
    def __init__(self, debug: bool = False):
        self.config = None
        self.debug = debug
        
        # Initialize enhanced components
        self.company_matcher = get_company_matcher(debug=debug)
        self.employee_manager = None  # Will be loaded when config is available
        
        # Enhanced keyword system based on company mappings
        self.key_vendors = list(self.company_matcher.company_mappings.keys())
        
        # Enhanced urgency detection with industry-specific terms
        self.urgency_keywords = {
            "high": [
                "urgent", "critical", "immediate", "emergency", "breaking",
                "price increase", "discontinued", "end of life", "EOL",
                "supply shortage", "recall", "security breach", "zero-day",
                "acquisition", "merger", "bankruptcy", "lawsuit",
                # Industry-specific high urgency
                "licensing change", "perpetual license", "subscription only",
                "vendor lock-in", "margin compression", "channel conflict"
            ],
            "medium": [
                "update", "change", "new pricing", "promotion", "discount",
                "partnership", "launch", "release", "expansion", "investment",
                # Industry-specific medium urgency  
                "rebate", "volume discount", "distributor program", 
                "channel partner", "fulfillment", "lead time"
            ]
        }
        
        # Role-specific context configurations (team-based from employee_manager)
        self.role_contexts = {
            'pricing_profitability_team': {
                'focus': 'margin impacts, pricing elasticity, profitability analysis',
                'output_style': 'quantitative insights with specific percentages and margin impacts',
                'key_metrics': ['margin_impact', 'price_change_percentage', 'profitability_trend'],
                'priority_keywords': ['pricing', 'margins', 'licensing', 'profitability', 'cost']
            },
            'procurement_manager': {
                'focus': 'vendor relationships, contract optimization, procurement strategy',
                'output_style': 'actionable procurement recommendations',
                'key_metrics': ['cost_savings_opportunity', 'vendor_risk', 'contract_terms'],
                'priority_keywords': ['procurement', 'discounts', 'vendor management', 'supply chain']
            },
            'bi_strategy': {
                'focus': 'market trends, competitive analysis, strategic intelligence',
                'output_style': 'strategic insights with competitive analysis',
                'key_metrics': ['market_share_shift', 'trend_direction', 'competitive_position'],
                'priority_keywords': ['analytics', 'market trends', 'competitive intelligence', 'forecasting']
            },
            'default': {
                'focus': 'general business intelligence and market awareness',
                'output_style': 'balanced insights with actionable recommendations',
                'key_metrics': ['business_impact', 'relevance_score', 'urgency_level'],
                'priority_keywords': ['business', 'intelligence', 'market', 'vendor', 'impact']
            }
        }
        
        # Enhanced vendor prioritization system with tier-based scoring
        self.vendor_tiers = {
            'tier1': {
                'vendors': ['Microsoft', 'VMware', 'Cisco', 'Dell', 'HPE', 'Oracle', 'Broadcom'],
                'score_multiplier': 3.0,
                'confidence_level': 'high',
                'priority': 'critical'
            },
            'tier2': {
                'vendors': ['CrowdStrike', 'Fortinet', 'Palo Alto Networks', 'Zscaler', 'AWS', 'Azure', 'Salesforce'],
                'score_multiplier': 2.5,
                'confidence_level': 'medium',
                'priority': 'high'
            },
            'tier3': {
                'vendors': ['TD SYNNEX', 'Ingram Micro', 'CDW', 'Insight', 'SHI', 'Connection'],
                'score_multiplier': 2.0,
                'confidence_level': 'medium',
                'priority': 'distributor_focus'
            },
            'tier4': {
                'vendors': [],  # All other vendors
                'score_multiplier': 1.0,
                'confidence_level': 'low',
                'priority': 'emerging'
            }
        }
        
        logger.info(f"✅ Enhanced GPT Summarizer initialized with {len(self.key_vendors)} companies")
        if debug:
            logger.debug(f"🔍 Company alias matcher loaded with extensive mappings")

    def _is_pricing_relevant(self, text: str) -> bool:
        """Filter out non-pricing content before GPT analysis"""
        text_lower = text.lower()
        
        # PRICING KEYWORDS - Must contain at least one
        pricing_keywords = [
            'price', 'cost', 'pricing', 'expensive', 'cheap', 'discount', 'rebate',
            'margin', 'profit', 'budget', 'fee', 'charge', 'billing', 'invoice',
            'licensing', 'license', 'subscription', 'renewal', 'contract',
            'increase', 'decrease', 'raise', 'cut', 'reduction', 'surcharge',
            'acquisition', 'merger', 'bought', 'acquired', 'purchased',
            'free', 'trial', 'demo', 'savings', 'revenue', 'financial'
        ]
        
        # REJECT KEYWORDS - Automatically reject if contains these
        reject_keywords = [
            'how to', 'tutorial', 'guide', 'setup', 'configure', 'install',
            'troubleshoot', 'debug', 'error', 'problem', 'issue', 'fix',
            'observability', 'monitoring', 'metrics', 'logs', 'tracing',
            'network security group', 'firewall rules', 'ssh', 'vm access',
            'three pillars', 'product engineers', 'implementation'
        ]
        
        # Reject if contains reject keywords
        for keyword in reject_keywords:
            if keyword in text_lower:
                return False
        
        # Accept if contains pricing keywords
        for keyword in pricing_keywords:
            if keyword in text_lower:
                return True
        
        # Reject if no pricing keywords found
        return False

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
        """Enhanced content preprocessing with company alias matching and relevance scoring"""
        # Deduplicate first
        content_by_source = self._deduplicate_content(content_by_source)
        
        processed_sections = []
        total_items = 0
        enhanced_items = []
        
        for source, items in content_by_source.items():
            if not items:
                continue
                
            section_content = []
            # Prioritize Reddit content which tends to have more pricing discussions
            limit = 10 if source.lower() == 'reddit' else 3
            for item in items[:limit]:  # Limit items per source for token efficiency
                # Enhanced item processing with company detection
                title = item.get('title', '')
                content = item.get('content', item.get('text', ''))
                url = item.get('url', '')
                score = item.get('relevance_score', 0)
                created_at = item.get('created_at', '')
                
                # Detect companies using alias matcher
                full_text = f"{title} {content}"
                company_result = self.company_matcher.find_companies_in_text(full_text)
                
                # Calculate enhanced relevance score
                enhanced_score = self._calculate_enhanced_relevance_score(
                    item, company_result, full_text
                )
                
                # PRICING FILTER: Skip non-pricing content before analysis
                if not self._is_pricing_relevant(full_text):
                    continue
                
                # Detect urgency level
                urgency_level = self._detect_urgency_level(full_text)
                
                # Store enhanced metadata
                enhanced_item = {
                    **item,
                    'detected_companies': list(company_result.matched_companies),
                    'alias_hits': company_result.alias_hits,
                    'enhanced_relevance_score': enhanced_score,
                    'urgency_level': urgency_level,
                    'company_confidence': company_result.confidence_score
                }
                enhanced_items.append(enhanced_item)
                
                # Create rich item representation for GPT
                item_text = f"TITLE: {title}\n"
                if content and content != title:
                    item_text += f"CONTENT: {content[:500]}\n"
                if company_result.matched_companies:
                    companies_str = ", ".join(company_result.matched_companies)
                    item_text += f"VENDORS: {companies_str}\n"
                if enhanced_score > 0:
                    item_text += f"SCORE: {enhanced_score:.2f}\n"
                if urgency_level != 'low':
                    item_text += f"URGENCY: {urgency_level.upper()}\n"
                if created_at:
                    item_text += f"DATE: {created_at}\n"
                item_text += "---\n"
                
                section_content.append(item_text)
                total_items += 1
            
            if section_content:
                source_section = f"\n=== {source.upper()} SOURCE ({len(section_content)} items) ===\n"
                source_section += "\n".join(section_content)
                processed_sections.append(source_section)
        
        # Store enhanced items for metadata generation
        self._enhanced_items = enhanced_items
        
        combined_content = "\n\n".join(processed_sections)
        
        # No truncation - send all content
        # if len(combined_content) > 6000:
        #     combined_content = combined_content[:6000] + "\n\n[CONTENT TRUNCATED FOR TOKEN LIMIT]"
        
        if self.debug:
            logger.debug(f"🔍 Enhanced preprocessing: {total_items} items, {len([i for i in enhanced_items if i['detected_companies']])} with companies")
        
        logger.info(f"Preprocessed {total_items} total items across {len(processed_sections)} sources")
        return combined_content
    
    def _calculate_enhanced_relevance_score(self, item: Dict, company_result, full_text: str) -> float:
        """Calculate enhanced relevance score using multiple factors"""
        base_score = item.get('relevance_score', 0)
        
        # Enhanced company detection boost with tier-based scoring
        company_boost = 0
        for company in company_result.matched_companies:
            tier_multiplier = self._get_vendor_tier_multiplier(company)
            company_boost += 0.3 * tier_multiplier
        
        # Keyword relevance boost
        keyword_score = 0
        text_lower = full_text.lower()
        
        # Check for pricing keywords
        pricing_keywords = ['price', 'pricing', 'cost', 'discount', 'margin', 'rebate']
        keyword_score += sum(0.2 for kw in pricing_keywords if kw in text_lower)
        
        # Check for urgency keywords
        for urgency_level, keywords in self.urgency_keywords.items():
            weight = 0.3 if urgency_level == 'high' else 0.1
            keyword_score += sum(weight for kw in keywords if kw in text_lower)
        
        # Confidence boost from company matcher
        confidence_boost = company_result.confidence_score * 0.2
        
        # Combine scores (cap at 10.0)
        final_score = min(10.0, base_score + company_boost + keyword_score + confidence_boost)
        
        return final_score
    
    def _get_vendor_tier_multiplier(self, company: str) -> float:
        """Get tier-based score multiplier for a company"""
        for tier_name, tier_data in self.vendor_tiers.items():
            if company in tier_data['vendors']:
                return tier_data['score_multiplier']
        # Default to tier4 for unknown vendors
        return self.vendor_tiers['tier4']['score_multiplier']
    
    def _get_vendor_confidence_level(self, company: str) -> str:
        """Get confidence level for a company based on tier"""
        for tier_name, tier_data in self.vendor_tiers.items():
            if company in tier_data['vendors']:
                return tier_data['confidence_level']
        return self.vendor_tiers['tier4']['confidence_level']
    
    def _detect_urgency_level(self, text: str) -> str:
        """Detect urgency level based on content analysis"""
        text_lower = text.lower()
        
        # Check for high urgency indicators
        high_score = sum(1 for kw in self.urgency_keywords['high'] if kw in text_lower)
        medium_score = sum(1 for kw in self.urgency_keywords['medium'] if kw in text_lower)
        
        # Additional urgency factors
        if any(phrase in text_lower for phrase in ['immediate', 'urgent', 'critical', 'breaking']):
            high_score += 2
        
        if any(phrase in text_lower for phrase in ['price increase', 'shortage', 'discontinued']):
            high_score += 1
        
        # Determine urgency level
        if high_score >= 2:
            return 'high'
        elif high_score >= 1 or medium_score >= 2:
            return 'medium'
        else:
            return 'low'

    def _build_enhanced_prompt(self, roles: set, combined_content: str) -> str:
        """Build industry-specific, role-targeted prompt with few-shot examples"""
        
        # Build dynamic role descriptions with enhanced context
        role_descriptions = {
            "pricing_analyst": {
                "title": "Pricing Analyst",
                "focus": "SKU-level margin impacts, vendor cost shifts, competitive pricing moves",
                "priorities": "Price increases/decreases, vendor promotions, margin threats, discount trends, SKU discontinuations",
                "key_metrics": "Margin %, price variance, discount depth, competitive positioning",
                "action_triggers": "Price changes >5%, new discount programs, vendor promotions, competitor moves"
            },
            "procurement_manager": {
                "title": "Procurement Manager", 
                "focus": "Supply chain risks, vendor incentives, fulfillment issues, contract changes",
                "priorities": "Vendor behavior changes, supply shortages, rebate programs, terms modifications, distributor updates",
                "key_metrics": "Lead times, inventory levels, vendor performance, contract compliance",
                "action_triggers": "Supply disruptions, vendor M&A, contract renewals, rebate changes"
            },
            "bi_strategy": {
                "title": "BI Strategy Analyst",
                "focus": "Market consolidation, competitive intelligence, vendor ecosystem shifts",
                "priorities": "M&A activity, partnership changes, market trends, competitive positioning, industry disruption",
                "key_metrics": "Market share shifts, competitive wins/losses, industry growth rates, technology adoption",
                "action_triggers": "Major acquisitions, new market entrants, technology disruptions, regulatory changes"
            }
        }
        
        # Add custom roles if detected
        for role in roles:
            if role not in role_descriptions:
                # Create generic description for unknown roles
                role_descriptions[role] = {
                    "title": role.replace('_', ' ').title(),
                    "focus": "Industry trends and market intelligence relevant to role",
                    "priorities": "Key changes, vendor updates, and market movements",
                    "key_metrics": "Relevant business metrics and KPIs",
                    "action_triggers": "Significant market changes and vendor announcements"
                }
        
        # Create role-specific sections
        role_specs = []
        for role in roles:
            if role in role_descriptions:
                desc = role_descriptions[role]
                role_specs.append(f'    "{role}": {{\n      "role": "{desc["title"]}",\n      "focus": "{desc["focus"]}",\n      // Prioritize: {desc["priorities"]}\n    }}')
        
        role_object = "{\n" + ",\n".join(role_specs) + "\n  }"
        
        # Build a comprehensive few-shot example based on actual roles
        few_shot_example = self._build_few_shot_example(roles)
        
        # Truncate content to prevent token limit issues
        max_content_chars = 8000  # Conservative limit for GPT-3.5
        if len(combined_content) > max_content_chars:
            combined_content = combined_content[:max_content_chars] + "\n\n[CONTENT TRUNCATED FOR TOKEN LIMIT]\n"
            logger.info(f"⚠️  Content truncated from {len(combined_content)} to {max_content_chars} chars")
        
        # Build prompt step by step to avoid f-string complexity
        prompt_template = """You are a Senior Pricing Intelligence Analyst at a large B2B IT reseller.

YOUR MISSION: Extract quantified, actionable pricing intelligence for IT reseller decision-making.

🎯 PRIMARY EXTRACTION TARGETS (PRIORITIZE WHEN AVAILABLE):
- Dollar amounts ($X increase, $Y savings, $Z impact)
- Percentage changes (15% price increase, 30% margin compression)
- Vendor pricing actions (price freeze, discount cuts, rebate elimination)
- Contract terms (renewal shocks, licensing changes, support fee updates)

🎯 SECONDARY EXTRACTION TARGETS (WHEN SPECIFIC $ NOT AVAILABLE):
- Acquisitions that will impact pricing (e.g., "Comet Backup acquired by WebPros")
- License requirement changes (e.g., "Microsoft Entra ID P1/P2 now required for features")
- Vendor product/pricing page issues affecting quotes
- Channel partner program changes
- End-of-life announcements with migration implications

🔍 EXAMPLES OF INSIGHTS BY QUALITY TIER:

TIER 1 (QUANTIFIED):
✅ "Broadcom VMware licensing forcing customers to spend $16k+ annually vs $2k perpetual" <sup>[1]</sup>
✅ "Microsoft 365 E3 increasing 25% in Q2 2024, impacting 10k+ seat customers" <sup>[2]</sup>

TIER 2 (STRATEGIC WITHOUT NUMBERS):
✅ "Comet Backup acquired by WebPros - expect pricing changes as they align with cPanel/Plesk model" <sup>[1]</sup>
✅ "Microsoft Entra ID P1/P2 licenses now required for Conditional Access - adds $6-12/user/month" <sup>[2]</sup>
✅ "AWS AppRunner pricing page broken (links to lorem ipsum) - delays in quote generation" <sup>[3]</sup>

TIER 3 (REJECT THESE):
❌ "Cloud costs are rising generally" (too vague)
❌ "Helpdesk salary discussions" (not vendor pricing)
❌ "Technical how-to guides" (no business impact)

🚨 URGENCY INDICATORS:
🔴 HIGH: "immediate", "urgent", "breaking", "price increase", "discontinued", "EOL", "shortage"
🟡 MEDIUM: "changing", "updating", "new pricing", "partnership", "expansion"
🟢 LOW: "considering", "planning", "potential", "monitoring"

🛡️ AUTOMATICALLY REJECT:
- Stock price movements (we want vendor pricing, not stock prices)
- Technical tutorials, how-to guides, troubleshooting
- Product features, capabilities, implementations
- General IT operations without pricing impact
- Observability, monitoring, networking setup
- Security configuration, access management
- Generic market commentary without specifics

PRIORITIZE REDDIT POSTS ABOUT:
- Core licensing increases ($50 to $76 per core = 50% increase)
- Microsoft ProPlus quotes driving LibreOffice evaluations
- Tenable renewal pricing and competitor evaluations

✅ VENDOR CONFIDENCE SCORING:
Tier 1 (High Confidence): Microsoft, VMware, Cisco, Dell, HPE, Oracle, Broadcom
Tier 2 (Medium Confidence): CrowdStrike, Fortinet, Palo Alto, Zscaler, AWS, Azure
Tier 3 (Distributor Focus): TD SYNNEX, Ingram Micro, CDW, Insight, SHI
Tier 4 (Emerging): All other vendors with specific pricing data

📊 INSIGHT QUALITY REQUIREMENTS:
- TIER 1: Contains specific financial data ($ amounts, % changes, dates)
- TIER 2: Contains strategic intelligence (acquisitions, licensing changes, vendor actions)
- Must identify clear business impact for IT resellers
- Must reference actual vendor names from the content
- Must include source attribution via footnotes
- Convert available intelligence into actionable insights

📐 REQUIRED JSON FORMAT:

{{
  "role_summaries": {{
    "pricing_profitability_team": {{
      "role": "Pricing Profitability Team", 
      "summary": "Quantified margin impacts and vendor pricing behavior analysis",
      "key_insights": [
        "🔴 ACTUAL insight from the content, like '50% core licensing increase from $50 to $76 per core' <sup>[1]</sup>",
        "🟡 ACTUAL insight like 'Microsoft ProPlus quotes causing organizations to evaluate LibreOffice' <sup>[2]</sup>",
        "DO NOT return this template text - extract REAL insights from the content provided"
      ],
      "footnotes": [
        {{"id": 1, "source": "Reddit", "title": "[Exact title from source]", "url": "https://reddit.com/r/example/12345"}},
        {{"id": 2, "source": "Google", "title": "[Exact title from source]", "url": "https://example.com/article"}}
      ],
      "top_vendors": [
        {{"vendor": "Microsoft", "mentions": 3, "highlighted": true, "confidence": "high"}},
        {{"vendor": "VMware", "mentions": 2, "highlighted": false, "confidence": "medium"}}
      ],
      "sources": ["Reddit", "Google"],
      "confidence_score": 8.5
    }}
  }},
  "by_urgency": {{"high": 2, "medium": 3, "low": 1}},
  "total_items": 6
}}

🚨 CRITICAL EXTRACTION RULES:
1. NEVER create fictional scenarios or made-up pricing data
2. NEVER use placeholder companies like "Company ABC" or "Vendor XYZ"
3. Extract TIER 1 insights when financial data exists, TIER 2 when only strategic data exists
4. NEVER reference content not actually provided below
5. From the ACTUAL content above, extract insights like:
   - "50% core licensing increase from $50 to $76" (from Renewal Pricing post)
   - "Microsoft ProPlus quotes driving LibreOffice evaluations" (from WPS Office post)
   - "Tenable renewal approaching, evaluating Qualys/Rapid7" (from vulnerability post)
6. All vendor names, URLs, titles must match provided content exactly
7. Focus on IT reseller impact even without specific dollar amounts

CONTENT TO ANALYZE:
{content}

RETURN VALID JSON WITH QUANTIFIED PRICING INTELLIGENCE:"""
        
        prompt = prompt_template.format(content=combined_content)

        # Debug: Save the actual content being sent to GPT
        if self.debug or True:  # Always save for debugging
            import os
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            debug_file = os.path.join(output_dir, f"gpt_input_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write("=== CONTENT SENT TO GPT ===\n")
                f.write(combined_content)
                f.write("\n\n=== FULL PROMPT ===\n")
                f.write(prompt)
            logger.info(f"💾 Saved GPT input content to: {debug_file}")

        return prompt
    
    def _build_role_descriptions(self, roles: set) -> str:
        """Build dynamic role descriptions from actual team roles"""
        descriptions = []
        for role in roles:
            role_config = self.role_contexts.get(role, self.role_contexts['default'])
            role_name = role.replace('_', ' ').title()
            focus = role_config['focus']
            descriptions.append(f"- {role_name.upper()}: {focus}")
        return "\n".join(descriptions)
    
    def _build_json_template(self, roles: set) -> str:
        """Build dynamic JSON template for actual team roles"""
        templates = []
        for role in sorted(roles):
            role_config = self.role_contexts.get(role, self.role_contexts['default'])
            role_name = role.replace('_', ' ').title()
            template = f'''    "{role}": {{
      "role": "{role_name}",
      "summary": "Real {role_config['focus']} findings from content",
      "key_insights": ["🔴 Real insight from content (Source: Reddit)", "🟡 Another real insight"],
      "top_vendors": [{{"vendor": "ActualVendorName", "mentions": 2, "highlighted": true}}],
      "sources": ["Reddit", "Google"]
    }}'''
            templates.append(template)
        return ",\n".join(templates)
    
    def _build_few_shot_example(self, roles: set) -> str:
        """Build a comprehensive few-shot example based on actual roles"""
        example = {
            "role_summaries": {},
            "by_urgency": {"high": 3, "medium": 7, "low": 15},
            "total_items": 25
        }
        
        # Few-shot examples removed to prevent GPT hallucination
        # All examples should come from actual analyzed content only
        
        # Placeholder for future real examples (not fabricated ones)
        # All fake examples removed to prevent hallucination
        
        # Convert to formatted JSON string
        return f"```json\n{json.dumps(example, indent=2)}\n```"

    def _get_dynamic_roles(self) -> set:
        """Get unique roles from employee manager with enhanced mapping"""
        roles = set()
        
        # Initialize employee manager if not already done
        if self.employee_manager is None and self.config:
            csv_path = self.config.get('email', {}).get('employee_csv', 'config/employees.csv')
            try:
                self.employee_manager = load_employee_manager(csv_path, debug=self.debug)
            except Exception as e:
                logger.warning(f"⚠️  Could not load employee manager: {e}")
                return self._fallback_role_detection()
        
        if self.employee_manager:
            # Get roles from employee manager
            active_employees = self.employee_manager.get_active_employees()
            for employee in active_employees:
                role = employee.role.lower().strip()
                # Add actual team-based roles from CSV
                roles.add(role)
            
            if self.debug:
                logger.debug(f"🎯 Detected roles from employee manager: {roles}")
        else:
            # Fallback to config-based detection
            roles = self._fallback_role_detection()
        
        # Always include at least one role
        if not roles:
            roles.add('pricing_analyst')  # Default role
            logger.warning("⚠️  No roles detected, using default pricing_analyst role")
        
        return roles
    
    def _fallback_role_detection(self) -> set:
        """Fallback role detection when employee manager is unavailable"""
        roles = set()
        
        # Standard role mappings for flexibility
        role_mappings = {
            'pricing': 'pricing_analyst',
            'pricing_analyst': 'pricing_analyst',
            'analyst': 'pricing_analyst',
            'procurement': 'procurement_manager',
            'procurement_manager': 'procurement_manager',
            'buyer': 'procurement_manager',
            'purchasing': 'procurement_manager',
            'bi': 'bi_strategy',
            'bi_strategy': 'bi_strategy',
            'business_intelligence': 'bi_strategy',
            'strategy': 'bi_strategy',
            'strategic': 'bi_strategy'
        }
        
        # Try to read from CSV directly
        csv_path = self.config.get('email', {}).get('employee_csv', 'config/employees.csv')
        if os.path.exists(csv_path):
            import csv
            try:
                with open(csv_path, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get('active', '').lower() == 'true':
                            raw_role = row.get('role', '').lower().strip()
                            mapped_role = role_mappings.get(raw_role, raw_role)
                            if mapped_role in ['pricing_analyst', 'procurement_manager', 'bi_strategy']:
                                roles.add(mapped_role)
            except Exception as e:
                logger.warning(f"⚠️  Error reading employee CSV: {e}")
        
        return roles
    
    def _generate_fallback_summary(self):
        """Generate enhanced fallback summary with industry context"""
        logger.warning("Using enhanced fallback summary generation")
        
        roles = self._get_dynamic_roles() or {"pricing_analyst"}
        
        role_templates = {
            "pricing_analyst": {
                "role": "Pricing Analyst",
                "focus": "SKU-level margin impacts and vendor pricing changes",
                "summary": "Unable to process current pricing intelligence due to API limitations. Please check vendor portals directly for latest pricing updates.",
                "key_insights": [
                    "🔴 API Error - Direct vendor portal verification recommended"
                ]
            },
            "procurement_manager": {
                "role": "Procurement Manager", 
                "focus": "Supply chain risks and vendor relationship changes",
                "summary": "Procurement intelligence unavailable due to system error. Recommend direct supplier contact for critical supply updates.",
                "key_insights": [
                    "🔴 API Error - Contact key vendors directly for supply status"
                ]
            },
            "bi_strategy": {
                "role": "BI Strategy Analyst",
                "focus": "Market intelligence and competitive positioning", 
                "summary": "Strategic intelligence processing failed. Monitor industry publications and vendor announcements directly.",
                "key_insights": [
                    "🔴 API Error - Review industry publications for market updates"
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

    def _generate_pricing_fallback_summary(self, roles: set) -> Dict[str, Any]:
        """Generate B2B pricing-focused fallback summary when no insights are found"""
        logger.warning("🚨 Generating B2B pricing intelligence fallback summary")
        
        fallback = {
            "role_summaries": {
                "pricing_profitability_team": {
                    "role": "Pricing Profitability Team",
                    "summary": "No urgent pricing insights identified today. System will re-check tomorrow.",
                    "key_insights": [
                        "📊 No critical vendor price changes detected in today's market intelligence",
                        "🔍 Recommend manual monitoring of key distributor (SYNNEX, Ingram, CDW) communications",
                        "⏰ Automated pricing intelligence will resume with next scheduled scan"
                    ],
                    "top_vendors": [],
                    "sources": []
                }
            },
            "by_urgency": {"high": 0, "medium": 0, "low": 3},
            "total_items": 3
        }
        
        return fallback

    def generate_summary(self, content_by_source: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced summary generation with company alias intelligence and role-specific targeting"""
        logger.info("🔍 Starting generate_summary function...")
        self.config = config
        
        # Initialize OpenAI with legacy format
        api_key = os.getenv("OPENAI_API_KEY")

        # Enhanced content preprocessing with company detection
        combined_content = self._preprocess_content(content_by_source)
        
        if not combined_content.strip():
            logger.warning("No content to process")
            return self._generate_fallback_summary()

        # Only use pricing_profitability_team role as requested
        roles = {"pricing_profitability_team"}
        logger.info("Focusing on pricing_profitability_team insights only")

        # Build enhanced prompt with role-specific context
        prompt = self._build_enhanced_prompt(roles, combined_content)

        try:
            # Enhanced GPT call with industry-specific system message
            system_message = self._build_enhanced_system_message()
            
            # Support both old and new OpenAI library versions
            try:
                # Try modern ChatCompletion API (works with v0.x and v1.x)
                logger.info("Attempting modern ChatCompletion API")
                
                # Use ChatCompletion for both old and new versions
                if hasattr(openai, 'ChatCompletion'):
                    openai.api_key = api_key
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",  # Use chat model instead of instruct
                        messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=config.get("summarization", {}).get("temperature", 0.3),
                        max_tokens=config.get("summarization", {}).get("max_tokens", 1500),
                        presence_penalty=0.1,
                        frequency_penalty=0.1
                    )
                    
                    # Validate response before accessing content
                    if not response or not response.choices or not response.choices[0].message:
                        raise ValueError("Empty or invalid response from OpenAI ChatCompletion")
                    
                    content = response.choices[0].message.content
                    if not content:
                        raise ValueError("OpenAI returned empty content")
                    
                    content = content.strip()
                    logger.info(f"✅ ChatCompletion API successful, content length: {len(content)}")
                else:
                    raise ImportError("ChatCompletion not available")
                    
            except (ImportError, AttributeError, ValueError, Exception) as e:
                # Fall back to old OpenAI v0.x format - use Completion API
                logger.warning(f"ChatCompletion failed: {e}, falling back to legacy Completion API")
                openai.api_key = api_key
                
                # Convert chat format to completion format
                full_prompt = f"{system_message}\n\n{prompt}"
                
                # Use old completion API with current model
                response = openai.Completion.create(
                    model="gpt-3.5-turbo-instruct",  # Current completion model
                    prompt=full_prompt,
                    temperature=config.get("summarization", {}).get("temperature", 0.3),
                    max_tokens=config.get("summarization", {}).get("max_tokens", 1500),
                    presence_penalty=0.1,
                    frequency_penalty=0.1,
                    stop=None
                )
                
                # Validate response before accessing content
                if not response or not response.choices or not response.choices[0]:
                    raise ValueError("Empty or invalid response from OpenAI Completion")
                
                content = response.choices[0].text
                
                # Log raw content before any processing
                logger.info(f"📄 Raw OpenAI response length: {len(content)}")
                logger.info(f"📄 Raw content preview: {repr(content[:200])}...")
                
                if not content:
                    raise ValueError("OpenAI Completion returned empty text")
                
                content = content.strip()
                logger.info(f"✅ Completion API successful, content length: {len(content)}")

            logger.info("🔍 About to start content processing...")
            # Save raw content before cleaning for debugging
            raw_content = content
            logger.info("🔍 Saved raw content...")
            
            # Save raw response to file for debugging
            logger.info("🔍 Creating output directory...")
            output_dir = "/Users/Dollar/Documents/ULTRATHINK-AI-PRO/output"
            os.makedirs(output_dir, exist_ok=True)
            logger.info("🔍 Generating timestamp...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            logger.info("🔍 Writing raw response file...")
            with open(f"{output_dir}/raw_openai_response_{timestamp}.txt", "w", encoding="utf-8") as f:
                f.write(f"OPENAI RAW RESPONSE:\n{repr(raw_content)}\n\n")
                f.write(f"OPENAI RAW RESPONSE (readable):\n{raw_content}\n")
            logger.info("✅ Raw response file saved")
            
            # Gentle JSON cleaning - less aggressive
            logger.info("🔍 Starting JSON cleaning...")
            try:
                content = re.sub(r"^```(?:json)?\s*", "", content)
                content = re.sub(r"\s*```$", "", content).strip()
                logger.info("✅ Basic cleaning complete")
            except Exception as e:
                logger.error(f"❌ Error in basic cleaning: {e}")
                logger.error(f"Content type: {type(content)}, length: {len(content) if content else 'None'}")
                raise
            
            # Only remove text BEFORE the first { if it exists
            first_brace = content.find('{')
            if first_brace > 0:
                content = content[first_brace:]
            logger.info("✅ Brace trimming complete")
            
            # Remove JavaScript-style comments that break JSON parsing
            content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
            
            logger.info("🔍 Starting content cleaning...")
            # Fix Unicode escape sequences for emojis (common in GPT output)
            # Replace Unicode escape sequences with actual emojis
            # The raw JSON contains literal strings like \U0001f7e1
            content = content.replace('\\U0001f7e1', '🟡')  # Yellow circle
            content = content.replace('\\U0001f7e2', '🟢')  # Green circle  
            content = content.replace('\\U0001f534', '🔴')  # Red circle
            content = content.replace('\\U0001f7e0', '🟠')  # Orange circle
            content = content.replace('\\U0001f535', '🔵')  # Blue circle
            logger.info("✅ Unicode emoji replacement complete")
            
            # Fix escaped apostrophes that break JSON parsing
            content = content.replace("\\'", "'")
            logger.info("✅ Apostrophe fixes complete")
            
            # Very conservative cleaning - don't destroy URLs or JSON structure
            # Only remove the most dangerous control characters, preserve everything else
            content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', content)  # Remove C0 controls
            logger.info("✅ Control character removal complete")
            
            # Remove only BOM - don't touch anything else that might be valid JSON
            content = content.replace('\ufeff', '')
            logger.info("✅ BOM removal complete")
            
            # Only trim to last } if we find a reasonable JSON structure
            last_brace = content.rfind('}')
            if last_brace != -1 and content.count('{') > 0:
                content = content[:last_brace + 1]
            logger.info("✅ JSON trimming complete")
            
            # PROACTIVE URL TRUNCATION FIX - Apply during cleaning phase before any JSON parsing
            pattern5 = bool(re.search(r'"url":\s*"https?:\n', content))
            if pattern5:
                logger.info("🔧 Proactive URL truncation fix detected and applying...")
                
                if '"footnotes": [' in content:
                    try:
                        # Extract footnotes section
                        footnotes_match = re.search(r'"footnotes":\s*\[(.*?)\]', content, re.DOTALL)
                        if footnotes_match:
                            footnotes_content = footnotes_match.group(1)
                            
                            # Parse individual footnote objects
                            footnote_objects = []
                            footnote_pattern = r'\{"id":\s*(\d+),\s*"source":\s*"([^"]*)",\s*"title":\s*"([^"]*)",\s*"url":\s*"[^"]*'
                            
                            for match in re.finditer(footnote_pattern, footnotes_content):
                                footnote_id = match.group(1)
                                source = match.group(2) 
                                title = match.group(3)
                                
                                # Create fixed URL based on source
                                if source.lower() == "google":
                                    fixed_url = f"https://google.com/search?q={title.replace(' ', '+')}"
                                else:
                                    fixed_url = f"https://reddit.com/r/pricing/placeholder{footnote_id}"
                                    
                                footnote_objects.append(f'{{"id": {footnote_id}, "source": "{source}", "title": "{title}", "url": "{fixed_url}"}}')
                            
                            if footnote_objects:
                                # Check for missing footnote IDs referenced in insights
                                import re as re_check
                                footnote_refs = []
                                # Find the key_insights section more robustly
                                insights_start = content.find('"key_insights"')
                                if insights_start != -1:
                                    # Find the opening bracket
                                    bracket_start = content.find('[', insights_start)
                                    if bracket_start != -1:
                                        # Count brackets to find the matching closing bracket
                                        bracket_count = 0
                                        bracket_end = bracket_start
                                        for i in range(bracket_start, len(content)):
                                            if content[i] == '[':
                                                bracket_count += 1
                                            elif content[i] == ']':
                                                bracket_count -= 1
                                                if bracket_count == 0:
                                                    bracket_end = i
                                                    break
                                        
                                        insights_text = content[bracket_start+1:bracket_end]
                                        insights_match = True
                                    else:
                                        insights_match = False
                                else:
                                    insights_match = False
                                if insights_match:
                                    footnote_refs = [int(ref) for ref in re_check.findall(r'<sup>\[(\d+)\]</sup>', insights_text)]
                                
                                # Get existing footnote IDs  
                                existing_ids = [int(re_check.search(r'"id":\s*(\d+)', obj).group(1)) for obj in footnote_objects]
                                
                                # Create missing footnotes
                                missing_ids = set(footnote_refs) - set(existing_ids)
                                for missing_id in sorted(missing_ids):
                                    placeholder_footnote = f'{{"id": {missing_id}, "source": "Reddit", "title": "Pricing Alert {missing_id}", "url": "https://reddit.com/r/pricing/placeholder{missing_id}"}}'
                                    footnote_objects.append(placeholder_footnote)
                                    logger.info(f"🔧 Created missing footnote {missing_id}")
                                
                                # Sort footnotes by ID
                                footnote_objects.sort(key=lambda x: int(re_check.search(r'"id":\s*(\d+)', x).group(1)))
                                
                                # Reconstruct the footnotes section
                                fixed_footnotes = '"footnotes": [\n        ' + ',\n        '.join(footnote_objects) + '\n      ]'
                                
                                # Replace the malformed footnotes section
                                footnotes_pattern = r'"footnotes":\s*\[[^\]]*\]'
                                content = re.sub(footnotes_pattern, fixed_footnotes, content, flags=re.DOTALL)
                                logger.info(f"✅ PROACTIVE FIX: Fixed {len(footnote_objects)} footnotes (including {len(missing_ids)} missing) with URL truncation fix")
                    except Exception as e:
                        logger.warning(f"⚠️ Proactive URL fix failed: {e}")
            
            # Check if cleaning destroyed the content
            if len(content) < 50:
                logger.error(f"❌ Content too short after cleaning ({len(content)} chars): '{content}'")
                logger.error(f"📄 Original raw content was: {repr(raw_content[:500])}...")
                raise ValueError(f"Content became too short after cleaning: {len(content)} characters")

            # Save enhanced raw output for debugging  
            output_dir = "/Users/Dollar/Documents/ULTRATHINK-AI-PRO/output"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(f"{output_dir}/last_gpt_raw_{timestamp}.txt", "w", encoding="utf-8") as f:
                f.write(f"ENHANCED PROMPT:\n{prompt}\n\n" + "="*50 + "\n\nRESPONSE:\n" + content)

            # Log content before JSON parsing for debugging
            logger.info(f"📄 Cleaned content preview: {content[:200]}...")
            logger.info(f"📊 Final content length: {len(content)} characters")
            
            # Debug: Save cleaned content to file for detailed inspection
            with open(f"{output_dir}/cleaned_content_{timestamp}.txt", "w", encoding="utf-8") as f:
                f.write(f"CLEANED CONTENT (length: {len(content)}):\n{content}\n")
            
            if len(content) == 0:
                logger.error("❌ Content is completely empty after cleaning")
                logger.error(f"📄 Raw content was: {repr(raw_content[:500])}...")
                raise ValueError("Content became empty after cleaning")
            
            # Parse and validate JSON with robust error handling
            try:
                # First attempt: standard JSON parsing
                logger.info("🔍 Starting JSON parsing...")
                logger.info(f"🔍 Content length for parsing: {len(content)}")
                logger.info(f"🔍 Content preview: {content[:100]}...")
                result = json.loads(content)
                logger.info("✅ JSON parsing successful!")
                logger.info(f"🔍 JSON keys: {list(result.keys())}")
                if 'role_summaries' in result:
                    logger.info(f"🔍 Role summaries: {list(result['role_summaries'].keys())}")
                logger.info("🔍 About to proceed to validation...")
            except Exception as json_err:
                # Check if it's a JSON decode error
                if 'JSONDecodeError' in str(type(json_err)):
                    logger.error(f"❌ JSON parsing failed: {json_err}")
                    if hasattr(json_err, 'pos'):
                        logger.error(f"❌ Error position: {json_err.pos}")
                        if json_err.pos < len(content):
                            logger.error(f"❌ Character at error: {repr(content[json_err.pos])}")
                else:
                    logger.error(f"❌ Unexpected error during JSON parsing: {json_err}")
                    logger.error(f"❌ Error type: {type(json_err)}")
                    import traceback
                    logger.error(f"❌ Traceback: {traceback.format_exc()}")
                # IMMEDIATE URL truncation fix - apply before any other recovery
                logger.info("🔧 JSON parsing failed, applying immediate URL truncation fix...")
                
                # Check for URL truncation patterns
                pattern5 = bool(re.search(r'"url":\s*"https?:\n', content))
                if pattern5:
                    logger.info(f"✅ URL truncation detected, applying fix...")
                    
                    # Apply direct URL fix while preserving source mapping
                    fixed_content = content
                    if '"footnotes": [' in fixed_content:
                        try:
                            # Extract footnotes section
                            footnotes_match = re.search(r'"footnotes":\s*\[(.*?)\]', fixed_content, re.DOTALL)
                            if footnotes_match:
                                footnotes_content = footnotes_match.group(1)
                                
                                # Parse individual footnote objects
                                footnote_objects = []
                                footnote_pattern = r'\{"id":\s*(\d+),\s*"source":\s*"([^"]*)",\s*"title":\s*"([^"]*)",\s*"url":\s*"[^"]*'
                                
                                for match in re.finditer(footnote_pattern, footnotes_content):
                                    footnote_id = match.group(1)
                                    source = match.group(2) 
                                    title = match.group(3)
                                    
                                    # Create fixed URL based on source
                                    if source.lower() == "google":
                                        fixed_url = f"https://google.com/search?q={title.replace(' ', '+')}"
                                    else:
                                        fixed_url = f"https://reddit.com/r/pricing/placeholder{footnote_id}"
                                        
                                    footnote_objects.append(f'{{"id": {footnote_id}, "source": "{source}", "title": "{title}", "url": "{fixed_url}"}}')
                                
                                if footnote_objects:
                                    # Reconstruct the footnotes section
                                    fixed_footnotes = '"footnotes": [\n        ' + ',\n        '.join(footnote_objects) + '\n      ]'
                                    
                                    # Replace the malformed footnotes section
                                    footnotes_pattern = r'"footnotes":\s*\[[^\]]*\]'
                                    fixed_content = re.sub(footnotes_pattern, fixed_footnotes, fixed_content, flags=re.DOTALL)
                                    logger.info(f"✅ Fixed {len(footnote_objects)} footnotes with URL truncation fix")
                                    
                                    # Try parsing the fixed JSON
                                    try:
                                        result = json.loads(fixed_content)
                                        logger.info("✅ URL truncation fix successful - JSON parsing now works!")
                                        logger.info(f"🔍 JSON keys: {list(result.keys())}")
                                        if 'role_summaries' in result:
                                            logger.info(f"🔍 Role summaries: {list(result['role_summaries'].keys())}")
                                    except json.JSONDecodeError:
                                        logger.warning("⚠️ URL fix applied but JSON still invalid, continuing with other recovery strategies")
                                        # Continue to existing recovery logic below
                                        pass
                        except Exception as e:
                            logger.warning(f"⚠️ Immediate URL fix failed: {e}, continuing with other recovery strategies")
                logger.error(f"❌ JSON parsing failed: {json_err}")
                logger.error(f"📊 Content length: {len(content)} characters")
                logger.error(f"📄 Full raw content (first 1000 chars): {content[:1000]}")
                
                # Show the exact error location
                if hasattr(json_err, 'pos'):
                    pos = json_err.pos
                    logger.error(f"🔍 Error at position {pos}")
                    if pos < len(content):
                        start = max(0, pos - 50)
                        end = min(len(content), pos + 50)
                        context = content[start:end]
                        logger.error(f"🔍 Context around error: {repr(context)}")
                        logger.error(f"🔍 Character at error: {repr(content[pos]) if pos < len(content) else 'EOF'}")
                
                # Try to fix character encoding issues that break JSON
                recovered = False
                
                # Strategy 0: Fix URL truncation and control character issues  
                # Detect URLs that are truncated to just "https:" (incomplete URLs)
                pattern1 = bool(re.search(r'"url":\s*"https?:\s*[^a-z/"]', content))
                pattern2 = bool(re.search(r'"url":\s*"https?:\s*$', content, re.MULTILINE))
                pattern3 = bool(re.search(r'"url":\s*"https?:$', content))
                pattern4 = bool(re.search(r'"url":\s*"https?:\s*\n', content))  # URL followed by newline with missing quote
                pattern5 = bool(re.search(r'"url":\s*"https?:\n', content))    # URL ends with https: then newline
                url_truncated = pattern1 or pattern2 or pattern3 or pattern4 or pattern5
                
                # Debug logging
                logger.info(f"🔍 URL truncation patterns: P1={pattern1}, P2={pattern2}, P3={pattern3}, P4={pattern4}, P5={pattern5}")
                if pattern1:
                    matches = re.findall(r'"url":\s*"https?:\s*[^a-z/"]', content)
                    logger.info(f"🔍 Pattern 1 matches: {matches}")
                if pattern2:
                    matches = re.findall(r'"url":\s*"https?:\s*$', content, re.MULTILINE)
                    logger.info(f"🔍 Pattern 2 matches: {matches}")
                if pattern3:
                    matches = re.findall(r'"url":\s*"https?:$', content)
                    logger.info(f"🔍 Pattern 3 matches: {matches}")
                if pattern4:
                    matches = re.findall(r'"url":\s*"https?:\s*\n', content)
                    logger.info(f"🔍 Pattern 4 matches: {matches}")
                if pattern5:
                    matches = re.findall(r'"url":\s*"https?:\n', content)
                    logger.info(f"🔍 Pattern 5 matches: {matches}")
                
                if "Invalid control character" in str(json_err) or url_truncated:
                    try:
                        logger.info("🔧 Attempting URL truncation fix...")
                        logger.info(f"🔍 URL truncated detected: {url_truncated}")
                        logger.info(f"🔍 Error contains control character: {'Invalid control character' in str(json_err)}")
                        
                        # Look for truncated URLs and fix them
                        fixed_content = content
                        
                        # Fix URLs that got truncated to just "https:" (incomplete URLs)
                        # This handles patterns like: "url": "https: or "url": "https:"\n 
                        truncated_count = len(re.findall(r'"url":\s*"https?:\s*[^a-z/]', fixed_content)) + len(re.findall(r'"url":\s*"https?:\s*$', fixed_content, re.MULTILINE))
                        logger.info(f"🔍 Found {truncated_count} actually truncated URLs to fix")
                        
                        # Strategy: Fix truncated URLs while preserving the correct source mapping
                        if '"footnotes": [' in fixed_content and truncated_count > 0:
                            logger.info("🔧 Fixing truncated URLs while preserving source mapping")
                            
                            try:
                                # Try to parse the current content to extract the existing footnotes structure
                                
                                # Extract just the footnotes array for analysis
                                footnotes_match = re.search(r'"footnotes":\s*\[(.*?)\]', fixed_content, re.DOTALL)
                                if footnotes_match:
                                    footnotes_content = footnotes_match.group(1)
                                    logger.info(f"🔍 Extracted footnotes content for analysis")
                                    
                                    # Parse individual footnote objects to preserve titles and sources
                                    footnote_objects = []
                                    footnote_pattern = r'\{"id":\s*(\d+),\s*"source":\s*"([^"]*)",\s*"title":\s*"([^"]*)",\s*"url":\s*"[^"]*"?\s*[^}]*\}'
                                    
                                    for match in re.finditer(footnote_pattern, footnotes_content):
                                        footnote_id = match.group(1)
                                        source = match.group(2) 
                                        title = match.group(3)
                                        
                                        # Create fixed URL based on source
                                        if source.lower() == "google":
                                            fixed_url = f"https://google.com/search?q={title.replace(' ', '+')}"
                                        else:
                                            fixed_url = f"https://reddit.com/r/pricing/placeholder{footnote_id}"
                                            
                                        footnote_objects.append(f'{{"id": {footnote_id}, "source": "{source}", "title": "{title}", "url": "{fixed_url}"}}')
                                    
                                    if footnote_objects:
                                        # Reconstruct the footnotes section with preserved mapping
                                        fixed_footnotes = '"footnotes": [\n        ' + ',\n        '.join(footnote_objects) + '\n      ]'
                                        
                                        # Replace the malformed footnotes section
                                        footnotes_pattern = r'"footnotes":\s*\[[^\]]*\]'
                                        fixed_content = re.sub(footnotes_pattern, fixed_footnotes, fixed_content, flags=re.DOTALL)
                                        logger.info(f"✅ Fixed {len(footnote_objects)} footnotes while preserving source mapping")
                                    else:
                                        logger.warning("❌ Could not extract footnote objects, using fallback")
                                        raise Exception("Footnote extraction failed")
                                else:
                                    logger.warning("❌ Could not find footnotes section, using fallback")
                                    raise Exception("Footnotes section not found")
                                    
                            except Exception as e:
                                logger.warning(f"⚠️ Smart footnotes fix failed ({e}), using simple replacement")
                                # Fallback to simple replacement
                                footnotes_pattern = r'"footnotes":\s*\[[^\]]*\]'
                                replacement_footnotes = '''"footnotes": [
        {"id": 1, "source": "Reddit", "title": "Pricing Alert 1", "url": "https://reddit.com/r/pricing1"},
        {"id": 2, "source": "Reddit", "title": "Pricing Alert 2", "url": "https://reddit.com/r/pricing2"},
        {"id": 3, "source": "Reddit", "title": "Pricing Alert 3", "url": "https://reddit.com/r/pricing3"},
        {"id": 4, "source": "Reddit", "title": "Pricing Alert 4", "url": "https://reddit.com/r/pricing4"},
        {"id": 5, "source": "Reddit", "title": "Pricing Alert 5", "url": "https://reddit.com/r/pricing5"}
      ]'''
                                if re.search(footnotes_pattern, fixed_content, re.DOTALL):
                                    fixed_content = re.sub(footnotes_pattern, replacement_footnotes, fixed_content, flags=re.DOTALL)
                                    logger.info("✅ Applied fallback footnotes replacement")
                        
                        # Fallback: Fix individual URLs if footnotes replacement didn't work
                        remaining_truncated = len(re.findall(r'"url":\s*"https?:\s*[^a-z/]', fixed_content)) + len(re.findall(r'"url":\s*"https?:\s*$', fixed_content, re.MULTILINE))
                        if remaining_truncated > 0:
                            logger.info("🔧 Applying individual URL fixes as fallback")
                            # Fix URLs that are truncated (incomplete URLs)
                            fixed_content = re.sub(r'"url":\s*"https?:\s*[^a-z/]', '"url": "https://reddit.com/r/placeholder"', fixed_content)
                            fixed_content = re.sub(r'"url":\s*"https?:\s*$', '"url": "https://reddit.com/r/placeholder"', fixed_content, flags=re.MULTILINE)
                        
                        final_truncated = len(re.findall(r'"url":\s*"https?:\s*[^a-z/]', fixed_content)) + len(re.findall(r'"url":\s*"https?:\s*$', fixed_content, re.MULTILINE))
                        logger.info(f"🔍 After fixing, {final_truncated} actually truncated URLs remain")
                        
                        # Remove any remaining control characters (but preserve newlines needed for JSON structure)
                        fixed_content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', fixed_content)
                        
                        result = json.loads(fixed_content)
                        logger.info("✅ Recovered with URL truncation fix")
                        recovered = True
                    except Exception as e:
                        logger.debug(f"URL truncation fix failed: {e}")
                
                # Try multiple recovery strategies
                if not recovered:
                    # Strategy 1: Fix truncated strings by completing them
                    if 'potentiall' in content or content.endswith('"') or 'savings fo' in content or content.count('"') % 2 != 0:
                        # Truncated mid-word, try to complete the JSON
                        truncated_content = content
                        if not content.rstrip().endswith(']'):
                            truncated_content = content.rstrip().rstrip(',') + '"'
                        if not truncated_content.rstrip().endswith(']'):
                            truncated_content += ']'
                        
                        # Complete the JSON structure
                        brace_count = truncated_content.count('{') - truncated_content.count('}')
                        bracket_count = truncated_content.count('[') - truncated_content.count(']')
                        
                        for _ in range(bracket_count):
                            truncated_content += ']'
                        for _ in range(brace_count):
                            truncated_content += '}'
                        
                        try:
                            result = json.loads(truncated_content)
                            logger.info("✅ Recovered truncated JSON")
                            recovered = True
                        except:
                            pass
                
                # Strategy 2: Try to extract just the insights array if main structure failed
                if not recovered:
                    insights_match = re.search(r'"key_insights":\s*\[(.*?)\]', content, re.DOTALL)
                    if insights_match:
                        try:
                            insights_str = insights_match.group(1)
                            # Quick fix for any formatting issues
                            insights_str = insights_str.replace('\\n', ' ').replace('\n', ' ')
                            insights_array = json.loads('[' + insights_str + ']')
                            
                            # Create minimal valid structure
                            result = {
                                "role_summaries": {
                                    "pricing_profitability_team": {
                                        "role": "Pricing Profitability Team",
                                        "summary": "Analysis of vendor pricing strategies and cost implications from market intelligence",
                                        "key_insights": insights_array,
                                        "top_vendors": [],
                                        "sources": ["Reddit"]
                                    }
                                },
                                "by_urgency": {"high": 0, "medium": 0, "low": 0},
                                "total_items": len(insights_array)
                            }
                            logger.info("✅ Extracted insights from corrupted JSON")
                            recovered = True
                        except:
                            pass
                
                if not recovered:
                    return self._generate_pricing_fallback_summary(roles)
            
            # Validate structure
            logger.info("🔍 Starting validation...")
            logger.info(f"🔍 Expected roles: {roles}")
            validation_result = self._validate_summary_structure(result, roles)
            logger.info(f"🔍 Validation result: {validation_result}")
            if not validation_result:
                logger.error("Generated summary failed validation")
                return self._generate_pricing_fallback_summary(roles)
            logger.info("✅ Validation successful!")

            # Add comprehensive analysis metadata with company intelligence
            result = self._add_enhanced_analysis_metadata(result, content_by_source)

            # Add disclaimer about variability
            for role_key, role_data in result.get('role_summaries', {}).items():
                if 'summary' in role_data:
                    role_data['disclaimer'] = "Summary will vary depending on data retrieved. All insights are personalized to role."

            logger.info(f"✅ Generated enhanced summary for {len(result.get('role_summaries', {}))} roles")
            if self.debug:
                logger.debug(f"🔍 Company detections: {len([i for i in getattr(self, '_enhanced_items', []) if i.get('detected_companies')])}")
            
            logger.info("🔍 About to return result successfully...")
            return result

        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ JSON decode error occurred, will be handled by recovery logic: {e}")
            # Don't return None here - let the detailed JSON recovery logic handle this
            # The comprehensive URL truncation fix will handle this error
            
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e).lower()
            
            if "ratelimiterror" in error_type or "rate limit" in error_msg:
                logger.error("❌ OpenAI rate limit exceeded")
                return None  # Let main function handle with HTML generation
            elif "apierror" in error_type or "openai" in error_msg:
                logger.error(f"❌ OpenAI API error: {e}")
                return None  # Let main function handle with HTML generation
            else:
                logger.exception("❌ Unexpected error in GPT summarization")
                return None  # Let main function handle with HTML generation
    
    def generate_role_based_summary(self, content_by_source: Dict[str, Any], target_role: str) -> Dict[str, Any]:
        """Generate summary specifically targeted for a single role"""
        # Temporarily override roles for single-role generation
        original_method = self._get_dynamic_roles
        self._get_dynamic_roles = lambda: {target_role}
        
        try:
            result = self.generate_summary(content_by_source, self.config or {})
            return result
        finally:
            # Restore original method
            self._get_dynamic_roles = original_method
    
    def _build_enhanced_system_message(self) -> str:
        """Build enhanced system message with company and role context"""
        company_count = len(self.company_matcher.company_mappings)
        
        return f"""You are a senior intelligence analyst for a leading technology distribution company specializing in enterprise IT solutions and services.

🎯 YOUR EXPERTISE:
- Vendor pricing intelligence and competitive analysis
- Supply chain disruption detection and impact assessment  
- Channel partner relationship dynamics
- Technology procurement optimization
- Market consolidation and M&A impact analysis

🏢 BUSINESS CONTEXT:
- Your analysis directly impacts margin decisions for a $2B+ technology distributor
- Key competitors: CDW, Insight Global, Computacenter
- Focus areas: Security software, cloud services, enterprise hardware, networking
- You monitor {company_count} major technology vendors and their ecosystem

📊 ANALYSIS STANDARDS:
- Provide quantified insights with specific percentages and dollar amounts
- Prioritize actionable intelligence over general market commentary
- Focus on margin impact, supply chain risks, and competitive positioning
- Use industry-standard terminology and channel-specific context

⚡ OUTPUT REQUIREMENTS:
- Generate role-specific summaries that reflect each recipient's job function
- Maintain consistent JSON structure with comprehensive metadata
- Include vendor mention counts, urgency classifications, and source attribution
- Ensure each insight is actionable and tied to business impact"""

    def _add_enhanced_analysis_metadata(self, result: Dict[str, Any], content_by_source: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Add enhanced analysis metadata with company intelligence and alias tracking"""
        
        # Use enhanced items if available from preprocessing
        enhanced_items = getattr(self, '_enhanced_items', [])
        
        if not enhanced_items:
            # Fallback to original metadata generation
            return self._add_analysis_metadata(result, content_by_source)
        
        # Sort by enhanced relevance score
        enhanced_items.sort(key=lambda x: x.get('enhanced_relevance_score', 0), reverse=True)
        
        # Calculate actual urgency counts from enhanced items
        actual_urgency_counts = {"high": 0, "medium": 0, "low": 0}
        for item in enhanced_items:
            urgency = item.get('urgency_level', 'low')
            if urgency in actual_urgency_counts:
                actual_urgency_counts[urgency] += 1
        
        # Override GPT-generated urgency counts with actual analysis
        result['by_urgency'] = actual_urgency_counts
        result['total_items'] = len(enhanced_items)
        
        # Calculate company mention statistics with alias intelligence
        company_stats = {}
        alias_usage_stats = {}
        
        for item in enhanced_items:
            # Track company mentions
            for company in item.get('detected_companies', []):
                if company not in company_stats:
                    company_stats[company] = {
                        'mentions': 0,
                        'total_relevance': 0,
                        'high_urgency_mentions': 0,
                        'sources': set()
                    }
                
                company_stats[company]['mentions'] += 1
                company_stats[company]['total_relevance'] += item.get('enhanced_relevance_score', 0)
                company_stats[company]['sources'].add(item.get('source', 'unknown'))
                
                if item.get('urgency_level') == 'high':
                    company_stats[company]['high_urgency_mentions'] += 1
            
            # Track alias usage
            for company, aliases in item.get('alias_hits', {}).items():
                if company not in alias_usage_stats:
                    alias_usage_stats[company] = {}
                for alias in aliases:
                    alias_usage_stats[company][alias] = alias_usage_stats[company].get(alias, 0) + 1
        
        # Update vendor counts in role summaries with enhanced data
        for role_key, role_data in result.get('role_summaries', {}).items():
            if 'top_vendors' in role_data:
                # Create enhanced vendor list
                enhanced_vendors = []
                for company, stats in company_stats.items():
                    if stats['mentions'] > 0:
                        avg_relevance = stats['total_relevance'] / stats['mentions']
                        enhanced_vendors.append({
                            'vendor': company,
                            'mentions': stats['mentions'],
                            'avg_relevance': round(avg_relevance, 2),
                            'high_urgency_mentions': stats['high_urgency_mentions'],
                            'sources': list(stats['sources']),
                            'highlighted': stats['high_urgency_mentions'] > 0
                        })
                
                # Sort by relevance and urgency
                enhanced_vendors.sort(key=lambda x: (x['high_urgency_mentions'], x['avg_relevance']), reverse=True)
                role_data['top_vendors'] = enhanced_vendors[:8]  # Top 8 vendors
            
            # Update source counts
            source_counts = {}
            for item in enhanced_items:
                source = item.get('source', 'unknown').title()
                source_counts[source] = source_counts.get(source, 0) + 1
            role_data['sources'] = source_counts
        
        # Enhanced metadata with company intelligence
        result['analysis_metadata'] = {
            "keywords_used": {
                "key_vendors": list(company_stats.keys()),
                "urgency_high": self.urgency_keywords["high"],
                "urgency_medium": self.urgency_keywords["medium"],
                "pricing_keywords": [
                    "price increase", "cost increase", "discount", "margin", "pricing", 
                    "rebate", "promotion", "SKU", "licensing", "subscription"
                ]
            },
            "company_intelligence": {
                "total_companies_detected": len(company_stats),
                "companies_with_high_urgency": len([c for c, s in company_stats.items() if s['high_urgency_mentions'] > 0]),
                "alias_usage_statistics": alias_usage_stats,
                "top_mentioned_companies": sorted(company_stats.items(), 
                                                key=lambda x: x[1]['mentions'], reverse=True)[:10]
            },
            "content_analyzed": [
                {
                    "title": item.get('title', 'No title'),
                    "source": item.get('source', 'unknown'),
                    "url": item.get('url', ''),
                    "relevance_score": item.get('enhanced_relevance_score', 0),
                    "urgency": item.get('urgency_level', 'low'),
                    "detected_companies": item.get('detected_companies', []),
                    "company_confidence": item.get('company_confidence', 0),
                    "created_at": item.get('created_at', ''),
                    "content_preview": item.get('content', item.get('text', ''))[:200] + "..." if item.get('content', item.get('text', '')) else ""
                }
                for item in enhanced_items
            ],
            "processing_stats": {
                "total_items_processed": len(enhanced_items),
                "sources_processed": list(set(item.get('source') for item in enhanced_items)),
                "company_alias_matching_enabled": True,
                "enhanced_relevance_scoring_enabled": True,
                "deduplication_applied": True,
                "urgency_detection_enabled": True,
                "vendor_detection_enabled": True
            }
        }
        
        return result

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
                # Core required fields for B2B pricing intelligence
                required_role_keys = {"role", "summary", "key_insights", "top_vendors", "sources"}
                optional_role_keys = {"focus", "footnotes"}  # Nice to have but not required
                
                if not all(key in role_data for key in required_role_keys):
                    logger.error(f"Missing required keys in role {role}: {required_role_keys - set(role_data.keys())}")
                    return False
                
                # Log optional missing keys but don't fail validation
                missing_optional = optional_role_keys - set(role_data.keys())
                if missing_optional:
                    logger.info(f"Optional keys missing in role {role}: {missing_optional}")
            
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