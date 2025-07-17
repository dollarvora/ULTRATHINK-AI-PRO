#\!/usr/bin/env python3
"""
ULTRATHINK-AI-PRO Hybrid System
Combines original ultrathink's proven logic with enhanced features
"""
import asyncio
import logging
import os
import json
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/hybrid_system.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)
os.makedirs('output', exist_ok=True)

def load_config():
    """Load simplified configuration with fetcher compatibility"""
    config = {
        "sources": {
            "reddit": {
                "enabled": True,
                "subreddits": [
                    # Original core subreddits (proven)
                    "sysadmin", "msp", "cybersecurity", "vmware", "AZURE", "aws", 
                    "networking", "devops", "ITManagers", "BusinessIntelligence", "enterprise",
                    # Enhanced additions (valuable for enterprise IT)
                    "procurement", "purchasing", "accounting", 
                    "analytics", "consulting", "startups",
                    # Enterprise intelligence expansion (Tier 1: Critical)
                    "SaaS", "cto", "CloudComputing", "ITdept",
                    # Enterprise intelligence expansion (Tier 2: High Value)
                    "netsec", "Sales", "Business", "ecommerce",
                    # Enterprise intelligence expansion (Tier 3: Strategic - Enterprise focused)
                    "GovernmentContracting", "HigherEducation", "Manufacturing",
                    # NEW: Enterprise pricing-focused subreddits
                    "k12sysadmin", "Office365", "DataHoarder", "Intune", "HyperV",
                    "MicrosoftTeams", "SCCM", "PowerBI", "sharepoint"
                ],
                "post_limit": 50,
                "comment_limit": 20
            },
            "google": {
                "enabled": True,
                "queries": [
                    f"enterprise software pricing increase {datetime.now().year}",
                    "cybersecurity vendor price changes",
                    "IT distributor margin compression",
                    "cloud pricing updates AWS Azure",
                    "hardware vendor pricing announcements"
                ],
                "results_per_query": 10,
                "date_restriction": "d7"
            }
        },
        "keywords": {
            "pricing": [
                "price", "pricing", "cost", "margin", "discount", "rebate", "promotion",
                "increase", "decrease", "surcharge", "fee", "subscription", "licensing",
                # Additional pricing intelligence terms
                "deal registration", "special pricing", "bid pricing", "competency discount",
                "tier pricing", "authorization level", "channel conflict", "price protection",
                "margin erosion", "promotional window", "volume threshold", "contract pricing"
            ],
            "urgency_indicators": [
                "urgent", "critical", "immediate", "emergency", "breaking",
                "acquisition", "merger", "bankruptcy", "lawsuit", "security breach",
                # Enhanced business critical keywords for vendor program changes
                "program shutdown", "program closure", "partner program", "vcsp", "vcp",
                "channel program", "reseller program", "distributor program", "var program",
                "csp program", "certification program", "program discontinuation",
                "migrate clients", "migrate their clients", "smoothly migrate",
                "migrate to competition", "migrate to competitors", "client migration",
                "business shutdown", "shutdown business", "asked to shutdown",
                "program is closing", "program closing", "thousands of partners",
                "hundreds of partners", "all partners", "entire channel",
                "discontinuation", "end of life", "eol", "sunsetting",
                "broadcom", "vmware by broadcom", "licensing overhaul", "forced migration"
            ],
            # Enterprise intelligence categories for 10/10 system
            "price_point_intelligence": [
                "$100K+", "$50K+", "$25K+", "$10K+", "six figures", "seven figures",
                "enterprise tier", "premium tier", "professional tier", "business tier",
                "volume threshold", "volume breakpoint", "tier pricing", "seat pricing",
                "per user pricing", "per device pricing", "consumption pricing", "usage billing",
                "minimum commitment", "annual commitment", "multi-year deal", "contract value",
                "deal size", "transaction size", "enterprise discount", "volume discount",
                "bulk pricing", "quantity discount", "scale pricing", "negotiated rate"
            ],
            "competitive_displacement": [
                "switching from", "migrating from", "replacing", "migration project",
                "vendor switch", "platform migration", "alternative to", "replacement for",
                "moving away from", "leaving", "ditching", "abandoning", "phasing out",
                "competitive win", "competitive loss", "lost deal", "won deal", "market share",
                "displacing", "gaining ground", "losing customers", "customer retention",
                "churn", "retention rate", "competitive pressure", "market position",
                "vendor consolidation", "single vendor", "multi-vendor", "best of breed",
                "integrated solution", "point solution", "rip and replace", "forklift upgrade"
            ],
            "financial_impact": [
                "budget", "capex", "opex", "TCO", "total cost of ownership", "ROI",
                "return on investment", "payback period", "cost benefit", "business case",
                "budget allocation", "budget constraint", "cost center", "profit center",
                "financial impact", "bottom line", "cost savings", "cost avoidance",
                "efficiency gains", "productivity improvement", "resource optimization",
                "budget freeze", "spending freeze", "cost cutting", "expense reduction",
                "financial planning", "budget planning", "procurement budget", "IT budget",
                "capital expenditure", "operating expense", "cash flow", "working capital"
            ],
            "industry_verticals": [
                "healthcare IT", "health systems", "hospital technology", "medical devices",
                "financial services", "banking technology", "fintech", "insurance tech",
                "manufacturing ERP", "industrial automation", "supply chain technology",
                "retail technology", "point of sale", "e-commerce platform", "omnichannel",
                "government technology", "public sector", "federal", "state and local",
                "education technology", "edtech", "student information system", "LMS",
                "energy technology", "utilities", "smart grid", "renewable energy",
                "telecommunications", "telecom infrastructure", "5G", "network equipment",
                "transportation", "logistics technology", "fleet management", "autonomous"
            ],
            "economic_conditions": [
                "recession", "economic downturn", "budget cuts", "cost reduction",
                "inflation impact", "supply chain", "chip shortage", "component shortage",
                "economic uncertainty", "market volatility", "interest rates", "inflation",
                "cost of capital", "financing", "credit", "cash flow", "liquidity",
                "economic recovery", "growth", "expansion", "investment", "stimulus",
                "market conditions", "business climate", "economic outlook", "forecast"
            ],
            "technology_trends": [
                "AI pricing", "artificial intelligence", "machine learning costs", "ML pricing",
                "cloud migration", "cloud costs", "cloud pricing", "AWS pricing", "Azure pricing",
                "SaaS pricing", "subscription model", "per-seat pricing", "usage-based",
                "hybrid cloud", "multi-cloud", "cloud-native", "microservices", "containers",
                "cybersecurity pricing", "security as a service", "managed security",
                "automation pricing", "RPA pricing", "workflow automation", "process automation",
                "data analytics pricing", "big data", "business intelligence", "data lake",
                "IoT pricing", "edge computing", "5G pricing", "network modernization"
            ]
        },
        "vendors": {
            "hardware": ["Dell", "HP", "HPE", "Lenovo", "Intel", "AMD", "NVIDIA"],
            "software": ["Microsoft", "Oracle", "VMware", "Red Hat", "Adobe"],
            "cloud": ["AWS", "Azure", "Google Cloud", "Salesforce"],
            "security": ["CrowdStrike", "Fortinet", "Palo Alto Networks", "Zscaler"],
            "networking": ["Cisco", "Juniper", "Aruba", "Fortinet"]
        },
        "scoring": {
            "keyword_weight": 1.0,
            "urgency_weight": 2.0,
            "vendor_weight": 1.5,
            "high_score_threshold": 5.0,
            "medium_score_threshold": 2.0
        },
        "confidence": {
            "thresholds": {
                "high": 0.8,     # 80% confidence threshold
                "medium": 0.6    # 60% confidence threshold
            },
            "base_score": 0.5,   # 50% base confidence
            "vendor_tiers": {
                "tier_1_boost": 0.3,  # Major vendors (Microsoft, VMware, etc.)
                "tier_2_boost": 0.2,  # Established vendors (CrowdStrike, Fortinet, etc.)
                "tier_3_boost": 0.1,  # Distributors and hardware (CDW, Dell, etc.)
                "tier_4_boost": 0.0   # Emerging/niche vendors
            },
            "source_reliability": {
                "multiple_reddit": 0.15,
                "single_reddit": 0.1,
                "google_verification": 0.05
            },
            "data_quality": {
                "multiple_quantified": 0.15,
                "single_quantified": 0.1,
                "critical_keywords_multiple": 0.1,
                "critical_keywords_single": 0.05
            }
        },
        "system": {
            "cache_ttl_hours": 6
        },
        "credentials": {
            "google": {
                "api_key": os.getenv("GOOGLE_API_KEY"),
                "cse_id": os.getenv("GOOGLE_CSE_ID")
            }
        },
        "summarization": {
            "model": "gpt-4o",  # Proven model
            "max_tokens": 2000,  # Original's higher limit
            "temperature": 0.2   # Original's proven setting
        },
        "employees": [
            {"role": "pricing_strategy", "name": "Pricing Strategy Team", "email": "pricing@company.com"},
            {"role": "vendor_relations", "name": "Vendor Relations Team", "email": "vendor@company.com"},
            {"role": "inventory_procurement", "name": "Inventory & Procurement Team", "email": "procurement@company.com"},
            {"role": "sales_enablement", "name": "Sales Enablement Team", "email": "sales@company.com"},
            {"role": "revenue_operations", "name": "Revenue Operations Team", "email": "revops@company.com"}
        ]
    }
    return config

async def fetch_content():
    """Fetch content from all sources"""
    logger.info("🌐 STEP 1: Fetching Pricing Intelligence")
    logger.info("-----------------------------------------------")
    
    all_content = {"reddit": [], "google": []}
    
    try:
        # Import fetchers
        from fetchers.reddit_fetcher import RedditFetcher
        from fetchers.google_fetcher import GoogleFetcher
        
        config = load_config()
        
        # Fetch Reddit content
        logger.info("🔴 Fetching pricing intelligence from Reddit...")
        reddit_fetcher = RedditFetcher(config)
        reddit_content = await reddit_fetcher.fetch()
        all_content["reddit"] = reddit_content
        logger.info(f"✅ Reddit: {len(reddit_content)} pricing-related posts")
        
        # Fetch Google content (with error handling)
        logger.info("🔍 Fetching pricing intelligence from Google...")
        try:
            google_fetcher = GoogleFetcher(config)
            google_content = await google_fetcher.fetch()
            all_content["google"] = google_content
            logger.info(f"✅ Google: {len(google_content)} pricing results")
        except Exception as e:
            logger.warning(f"Google fetching failed: {e}")
            all_content["google"] = []
            logger.info("⚠️ Continuing with Reddit data only")
        
        total_items = len(all_content['reddit']) + len(all_content['google'])
        logger.info(f"📊 Total pricing intelligence: {total_items} items")
        
        return all_content, config
        
    except Exception as e:
        logger.error(f"❌ Content fetching failed: {e}")
        return {"reddit": [], "google": []}, load_config()

async def analyze_content(all_content: Dict[str, Any], config: Dict[str, Any]):
    """Analyze content using hybrid GPT summarizer"""
    logger.info("")
    logger.info("🧠 STEP 2: Running Hybrid GPT-4 Analysis")
    logger.info("--------------------------------------------")
    logger.info("🤖 Using hybrid summarizer with multi-role intelligence...")
    
    try:
        from summarizer.gpt_summarizer_hybrid import HybridGPTSummarizer
        
        # Initialize hybrid summarizer
        summarizer = HybridGPTSummarizer(debug=True)
        
        # Generate comprehensive analysis
        summary = await asyncio.to_thread(
            summarizer.generate_summary,
            all_content,
            config
        )
        
        # Log results for holistic structure
        if 'pricing_intelligence_summary' in summary:
            intel_summary = summary['pricing_intelligence_summary']
            insights_count = len(intel_summary.get('critical_insights', []))
            vendors_count = summary.get('coverage_metrics', {}).get('vendors_analyzed', 0)
            
            logger.info(f"✅ Holistic Analysis completed with comprehensive team perspective")
            logger.info(f"📊 Generated {insights_count} critical insights covering {vendors_count} vendors")
        else:
            # Fallback for old structure
            role_count = len(summary.get('role_summaries', {}))
            insights_count = sum(len(role_data.get('key_insights', [])) 
                               for role_data in summary.get('role_summaries', {}).values())
            
            logger.info(f"✅ Analysis completed with {role_count} perspectives")
            logger.info(f"📊 Generated {insights_count} actionable insights")
        
        return summary
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        from summarizer.gpt_summarizer_hybrid import HybridGPTSummarizer
        summarizer = HybridGPTSummarizer()
        return summarizer._generate_fallback_summary()

async def generate_report(summary: Dict[str, Any], all_content: Dict[str, Any], config: Dict[str, Any]):
    """Generate enhanced HTML report"""
    logger.info("")
    logger.info("📄 STEP 3: Creating Enhanced Report")
    logger.info("----------------------------------------")
    
    try:
        from html_generator import get_html_generator
        
        # Extract insights for HTML generation (holistic structure with confidence data preserved)
        insights = []
        if 'pricing_intelligence_summary' in summary:
            # New holistic structure - preserve confidence data
            intel_summary = summary['pricing_intelligence_summary']
            critical_insights = intel_summary.get('critical_insights', [])
            strategic_recommendations = intel_summary.get('strategic_recommendations', [])
            
            # Handle both string and enhanced object formats
            for insight in critical_insights:
                if isinstance(insight, dict) and 'text' in insight:
                    insights.append(insight)  # Enhanced object with confidence
                else:
                    insights.append({'text': str(insight), 'confidence': None})  # Fallback
            
            for recommendation in strategic_recommendations:
                if isinstance(recommendation, dict) and 'text' in recommendation:
                    insights.append(recommendation)  # Enhanced object with confidence
                else:
                    insights.append({'text': str(recommendation), 'confidence': None})  # Fallback
        else:
            # Fallback to old role structure
            for role_data in summary.get('role_summaries', {}).values():
                role_insights = role_data.get('key_insights', [])
                for insight in role_insights:
                    if isinstance(insight, dict) and 'text' in insight:
                        insights.append(insight)  # Enhanced object with confidence
                    else:
                        insights.append({'text': str(insight), 'confidence': None})  # Fallback
        
        # Generate vendor analysis (holistic structure)
        vendor_analysis = {}
        if 'pricing_intelligence_summary' in summary:
            # Extract vendors from holistic structure
            intel_summary = summary['pricing_intelligence_summary']
            market_intel = intel_summary.get('market_intelligence', {})
            
            for vendor_info in market_intel.get('trending_vendors', []):
                vendor_name = vendor_info['vendor']
                vendor_analysis[vendor_name] = {
                    'mentions': vendor_info.get('mentions', 0),
                    'highlighted': vendor_info.get('sentiment') == 'Positive'
                }
        else:
            # Fallback to old role structure
            for role_data in summary.get('role_summaries', {}).values():
                for vendor_info in role_data.get('top_vendors', []):
                    vendor_name = vendor_info['vendor']
                    if vendor_name not in vendor_analysis:
                        vendor_analysis[vendor_name] = {
                            'mentions': 0,
                            'highlighted': False
                        }
                    vendor_analysis[vendor_name]['mentions'] += vendor_info.get('mentions', 0)
                    if vendor_info.get('highlighted'):
                        vendor_analysis[vendor_name]['highlighted'] = True
        
        # Generate HTML report
        generator = get_html_generator(debug=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"output/ultrathink_hybrid_{timestamp}.html"
        
        html_content = generator.generate_html_report(
            insights=insights,
            all_content=sum(all_content.values(), []),
            vendor_analysis=vendor_analysis,
            config=config
        )
        
        # Save report
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"✅ Enhanced report saved: {output_file}")
        logger.info(f"🎯 Generated report with {len(insights)} insights and {len(vendor_analysis)} vendors")
        
        return output_file
        
    except Exception as e:
        logger.error(f"❌ Report generation failed: {e}")
        return None

async def save_analysis_data(summary: Dict[str, Any]):
    """Save detailed analysis data"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save full summary
        summary_file = f"output/hybrid_summary_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Analysis data saved: {summary_file}")
        
        return summary_file
        
    except Exception as e:
        logger.error(f"❌ Failed to save analysis data: {e}")
        return None

async def main():
    """Main execution function"""
    try:
        logger.info("🚀 ULTRATHINK Hybrid System")
        logger.info("=" * 80)
        logger.info(f"🔧 Working directory: {os.getcwd()}")
        
        # Step 1: Fetch content
        all_content, config = await fetch_content()
        
        # Step 2: Analyze content
        summary = await analyze_content(all_content, config)
        
        # Step 3: Generate reports
        html_report = await generate_report(summary, all_content, config)
        json_data = await save_analysis_data(summary)
        
        logger.info("")
        logger.info("✅ System completed successfully\!")
        if html_report:
            logger.info(f"📊 Report: {html_report}")
        if json_data:
            logger.info(f"💾 Data: {json_data}")
        
        return summary
        
    except Exception as e:
        logger.exception("❌ System execution failed")
        return None

if __name__ == "__main__":
    # Run the hybrid system
    result = asyncio.run(main())
    
    if result:
        print("✅ System completed! Check output folder for results.")
    else:
        print("❌ System failed. Check logs for details.")
