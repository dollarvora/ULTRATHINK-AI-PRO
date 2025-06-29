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
        
        # Role-specific context configurations (enhanced from employee_manager)
        self.role_contexts = {
            'pricing_analyst': {
                'focus': 'margin impacts, pricing elasticity, competitive pricing',
                'output_style': 'quantitative insights with specific percentages',
                'key_metrics': ['margin_impact', 'price_change_percentage', 'discount_depth'],
                'priority_keywords': ['pricing', 'margin', 'discount', 'cost', 'revenue']
            },
            'procurement_manager': {
                'focus': 'vendor relationships, contract optimization, compliance',
                'output_style': 'actionable procurement recommendations',
                'key_metrics': ['cost_savings_opportunity', 'vendor_risk', 'contract_terms'],
                'priority_keywords': ['supply chain', 'vendor', 'contract', 'compliance', 'fulfillment']
            },
            'bi_strategy': {
                'focus': 'market trends, competitive positioning, revenue forecasting',
                'output_style': 'strategic insights with trend analysis',
                'key_metrics': ['market_share_shift', 'trend_direction', 'forecast_variance'],
                'priority_keywords': ['market', 'competitive', 'strategy', 'trend', 'forecast']
            },
            'default': {
                'focus': 'general business intelligence and market awareness',
                'output_style': 'balanced insights with actionable recommendations',
                'key_metrics': ['business_impact', 'relevance_score', 'urgency_level'],
                'priority_keywords': ['business', 'intelligence', 'market', 'vendor', 'impact']
            }
        }
        
        logger.info(f"✅ Enhanced GPT Summarizer initialized with {len(self.key_vendors)} companies")
        if debug:
            logger.debug(f"🔍 Company alias matcher loaded with extensive mappings")

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
            for item in items[:20]:  # Limit items per source
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
                    item_text += f"RELEVANCE: {enhanced_score:.2f}\n"
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
        
        # Truncate to fit within token limits (roughly 8000 chars = ~2000 tokens)
        if len(combined_content) > 8000:
            combined_content = combined_content[:8000] + "\n\n[CONTENT TRUNCATED]"
        
        if self.debug:
            logger.debug(f"🔍 Enhanced preprocessing: {total_items} items, {len([i for i in enhanced_items if i['detected_companies']])} with companies")
        
        logger.info(f"Preprocessed {total_items} total items across {len(processed_sections)} sources")
        return combined_content
    
    def _calculate_enhanced_relevance_score(self, item: Dict, company_result, full_text: str) -> float:
        """Calculate enhanced relevance score using multiple factors"""
        base_score = item.get('relevance_score', 0)
        
        # Company detection boost
        company_boost = len(company_result.matched_companies) * 0.3
        
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
        
        prompt = f"""You are a senior intelligence analyst for a leading technology distribution company. Analyze vendor pricing intelligence for teams competing in the enterprise IT market.

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

🎯 FEW-SHOT EXAMPLE FORMAT TO FOLLOW:

**IMPORTANT**: This is an example format to guide your output structure. Your actual analysis should reflect the real content, roles from employees.csv, and industry relevance. The specific insights, vendors, and numbers will vary based on the actual content you're analyzing.

{few_shot_example}

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
6. The output structure should match the few-shot example format

🎯 EXPECTED OUTPUT FORMAT:
{{
  "role_summaries": {role_object},
  "by_urgency": {{"high": 0, "medium": 0, "low": 0}},
  "total_items": 0
}}

Now analyze this content and generate role-specific intelligence following the example format:

{combined_content}"""

        return prompt
    
    def _build_few_shot_example(self, roles: set) -> str:
        """Build a comprehensive few-shot example based on actual roles"""
        example = {
            "role_summaries": {},
            "by_urgency": {"high": 3, "medium": 7, "low": 15},
            "total_items": 25
        }
        
        # Add examples for each role that exists
        if "pricing_analyst" in roles:
            example["role_summaries"]["pricing_analyst"] = {
                "role": "Pricing Analyst",
                "focus": "Margin analysis and market trends",
                "summary": "Microsoft announced a 15% Azure price increase effective July 1st, impacting enterprise agreements. Dell server pricing through CDW shows a 30% increase on PowerEdge models. TD Synnex is offering aggressive Zscaler discounts to counter competitive pressure.",
                "key_insights": [
                    "🔴 Azure +15% across all enterprise SKUs - immediate margin impact",
                    "🔴 Dell PowerEdge servers +30% through CDW channel",
                    "🟢 TD Synnex Zscaler discount increased to 18% through Q4",
                    "🟡 Cisco Catalyst switches facing 8% price adjustment",
                    "🟢 Fortinet offering volume rebates on 500+ unit orders"
                ],
                "top_vendors": [
                    {"vendor": "Microsoft", "mentions": 5, "highlighted": True},
                    {"vendor": "Dell", "mentions": 4, "highlighted": True},
                    {"vendor": "Zscaler", "mentions": 3, "highlighted": False},
                    {"vendor": "Cisco", "mentions": 2, "highlighted": False},
                    {"vendor": "Fortinet", "mentions": 2, "highlighted": False}
                ],
                "sources": {"reddit": 10, "google": 5, "linkedin": 3, "twitter": 7}
            }
        
        if "procurement_manager" in roles:
            example["role_summaries"]["procurement_manager"] = {
                "role": "Procurement Manager",
                "focus": "Supply chain and vendor management",
                "summary": "Critical supply chain disruptions affecting Lenovo ThinkPad availability with 6-week lead times. Ingram Micro implementing new rebate tiers for Q3. Microsoft changing Enterprise Agreement terms requiring annual commitments.",
                "key_insights": [
                    "🔴 Lenovo ThinkPad T-series: 6-week delays from all distributors",
                    "🟡 Ingram Micro new rebate structure: 3% at $1M, 5% at $3M quarterly",
                    "🔴 Microsoft EA changes: No more monthly true-ups allowed",
                    "🟢 TD Synnex expanding warehouse capacity - improved fulfillment expected",
                    "🟡 HP announcing end-of-life for ProBook 450 G8 series"
                ],
                "top_vendors": [
                    {"vendor": "Lenovo", "mentions": 4, "highlighted": True},
                    {"vendor": "Ingram Micro", "mentions": 3, "highlighted": True},
                    {"vendor": "Microsoft", "mentions": 3, "highlighted": False},
                    {"vendor": "TD Synnex", "mentions": 2, "highlighted": False}
                ],
                "sources": {"reddit": 8, "google": 6, "linkedin": 4, "twitter": 2}
            }
        
        if "bi_strategy" in roles:
            example["role_summaries"]["bi_strategy"] = {
                "role": "BI Strategy Analyst",
                "focus": "Market intelligence and competitive analysis",
                "summary": "Broadcom's VMware acquisition driving licensing model disruption across virtualization market. CDW expanding managed services portfolio through acquisition. Competitive landscape shifting as Insight Global partners with Arctic Wolf for security services.",
                "key_insights": [
                    "🔴 Broadcom/VMware: Perpetual licenses eliminated, subscription-only model",
                    "🟡 CDW acquiring Sirius Computer Solutions for $2.5B - market consolidation",
                    "🟢 Insight Global + Arctic Wolf partnership targets mid-market security",
                    "🟡 Gartner reports 23% growth in security software spending for 2024",
                    "🟢 Channel margins improving in cloud services: AWS 17%, Azure 15%"
                ],
                "top_vendors": [
                    {"vendor": "Broadcom", "mentions": 3, "highlighted": True},
                    {"vendor": "CDW", "mentions": 3, "highlighted": True},
                    {"vendor": "Insight Global", "mentions": 2, "highlighted": False},
                    {"vendor": "Arctic Wolf", "mentions": 2, "highlighted": False}
                ],
                "sources": {"reddit": 5, "google": 8, "linkedin": 7, "twitter": 5}
            }
        
        # Convert to formatted JSON string
        import json
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
                # Normalize role names
                if role in self.role_contexts or role in ['pricing_analyst', 'procurement_manager', 'bi_strategy']:
                    roles.add(role)
                else:
                    # Try to map to standard roles
                    if 'pricing' in role or 'analyst' in role:
                        roles.add('pricing_analyst')
                    elif 'procurement' in role or 'buyer' in role or 'purchasing' in role:
                        roles.add('procurement_manager')
                    elif 'bi' in role or 'strategy' in role or 'intelligence' in role:
                        roles.add('bi_strategy')
            
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
        """Enhanced summary generation with company alias intelligence and role-specific targeting"""
        self.config = config
        
        # Initialize OpenAI with legacy format
        api_key = os.getenv("OPENAI_API_KEY")

        # Enhanced content preprocessing with company detection
        combined_content = self._preprocess_content(content_by_source)
        
        if not combined_content.strip():
            logger.warning("No content to process")
            return self._generate_fallback_summary()

        # Get roles dynamically from employee manager
        roles = self._get_dynamic_roles()
        if not roles:
            logger.warning("No roles found in employee configuration, using defaults")
            roles = {"pricing_analyst"}

        # Build enhanced prompt with role-specific context
        prompt = self._build_enhanced_prompt(roles, combined_content)

        try:
            # Enhanced GPT call with industry-specific system message
            system_message = self._build_enhanced_system_message()
            
            # Support both old and new OpenAI library versions
            try:
                # Try new OpenAI v1.0+ format
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                
                response = client.chat.completions.create(
                    model=config.get("summarization", {}).get("model", "gpt-4o-mini"),
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=config.get("summarization", {}).get("temperature", 0.2),
                    max_tokens=config.get("summarization", {}).get("max_tokens", 500),
                    presence_penalty=0.1,
                    frequency_penalty=0.1
                )
                content = response.choices[0].message.content.strip()
            except (ImportError, AttributeError):
                # Fall back to old OpenAI v0.x format
                logger.info("Using legacy OpenAI API format (v0.x)")
                openai.api_key = api_key
                
                response = openai.ChatCompletion.create(
                    model=config.get("summarization", {}).get("model", "gpt-4o-mini"),
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=config.get("summarization", {}).get("temperature", 0.2),
                    max_tokens=config.get("summarization", {}).get("max_tokens", 500),
                    presence_penalty=0.1,
                    frequency_penalty=0.1
                )
                content = response['choices'][0]['message']['content'].strip()

            # Enhanced JSON cleaning
            content = re.sub(r"^```(?:json)?\s*", "", content)
            content = re.sub(r"\s*```$", "", content).strip()
            content = re.sub(r"^[^{]*", "", content)
            
            last_brace = content.rfind('}')
            if last_brace != -1:
                content = content[:last_brace + 1]

            # Save enhanced raw output for debugging
            os.makedirs("output", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(f"output/last_gpt_raw_{timestamp}.txt", "w", encoding="utf-8") as f:
                f.write(f"ENHANCED PROMPT:\n{prompt}\n\n" + "="*50 + "\n\nRESPONSE:\n" + content)

            # Parse and validate JSON
            result = json.loads(content)
            
            # Validate structure
            if not self._validate_summary_structure(result, roles):
                logger.error("Generated summary failed validation")
                return self._generate_fallback_summary()

            # Add comprehensive analysis metadata with company intelligence
            result = self._add_enhanced_analysis_metadata(result, content_by_source)

            # Add disclaimer about variability
            for role_key, role_data in result.get('role_summaries', {}).items():
                if 'summary' in role_data:
                    role_data['disclaimer'] = "Summary will vary depending on data retrieved. All insights are personalized to role."

            logger.info(f"✅ Generated enhanced summary for {len(result.get('role_summaries', {}))} roles")
            if self.debug:
                logger.debug(f"🔍 Company detections: {len([i for i in getattr(self, '_enhanced_items', []) if i.get('detected_companies')])}")
            
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