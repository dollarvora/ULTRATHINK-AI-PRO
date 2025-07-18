"""
Base Fetcher Class
Abstract base class for all content fetchers
"""

import json
import logging
import hashlib
import re
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Pattern


class BaseFetcher(ABC):
    """Abstract base class for content fetchers"""

    def __init__(self, config: Dict[str, Any], test_mode: bool = False):
        self.config = config
        self.test_mode = test_mode
        self.logger = logging.getLogger(self.__class__.__name__)
        self.cache_dir = Path('cache')
        self.cache_dir.mkdir(exist_ok=True)

        # Get source-specific config
        self.source_name = self.get_source_name()
        self.source_config = config['sources'].get(self.source_name, {})
        self.enabled = self.source_config.get('enabled', True)

        # Keywords and vendors for scoring - Fixed to match runtime config structure
        self.keywords = config['keywords'].get('pricing_keywords', [])
        self.urgency_keywords = config['keywords'].get('urgency_high', [])
        
        # Enhanced keyword categories for enterprise intelligence
        self.price_point_keywords = config['keywords'].get('price_point_intelligence', [])
        self.competitive_keywords = config['keywords'].get('competitive_displacement', [])
        self.financial_keywords = config['keywords'].get('financial_impact', [])
        self.industry_keywords = config['keywords'].get('industry_verticals', [])
        self.economic_keywords = config['keywords'].get('economic_conditions', [])
        self.tech_trend_keywords = config['keywords'].get('technology_trends', [])
        self.ma_intelligence_keywords = config['keywords'].get('ma_intelligence', [])
        
        # ENHANCED: CNAPP and Cloud Security Intelligence Keywords
        self.cnapp_keywords = config['keywords'].get('cnapp_pricing_intelligence', [])
        self.cnapp_cloud_security_keywords = config['keywords'].get('cnapp_cloud_security', [])
        self.channel_intelligence_keywords = config['keywords'].get('channel_intelligence', [])
        
        # ENHANCED: MSP and Security Intelligence Keywords for better scoring
        self.msp_keywords = [
            'msp', 'managed service provider', 'service provider', 'what\'s your experience with',
            'experience with', 'thoughts on', 'anyone using', 'has anyone used', 'opinions on',
            'server procurement', 'storage evaluation', 'vendor experience', 'vendor comparison',
            'procurement decision', 'purchasing decision', 'vendor selection', 'product evaluation',
            'hardware evaluation', 'software evaluation', 'solution evaluation', 'pilot project',
            'proof of concept', 'poc', 'vendor trial', 'demo', 'evaluation period'
        ]
        
        self.security_keywords = [
            'security performance', 'security issues', 'security problems', 'security challenges',
            'defender issues', 'defender problems', 'defender performance', 'security adoption',
            'security deployment', 'security implementation', 'security migration', 'security upgrade',
            'endpoint security', 'antivirus', 'anti-malware', 'threat protection', 'vulnerability',
            'security solution', 'security software', 'security tool', 'security platform',
            'makes me suffer', 'frustrated with', 'issues with', 'problems with', 'struggling with'
        ]
        
        # Set vendors before compiling patterns
        self.vendors = self._flatten_vendors(config.get('vendors', {}))
        
        # Compile regex patterns for enterprise performance (10x speedup)
        self._compile_keyword_patterns()

    def _compile_keyword_patterns(self):
        """Compile regex patterns for high-performance keyword matching"""
        try:
            # Compile patterns for each keyword category
            self._pricing_pattern = self._compile_pattern_list(self.keywords)
            self._urgency_pattern = self._compile_pattern_list(self.urgency_keywords)
            self._price_point_pattern = self._compile_pattern_list(self.price_point_keywords)
            self._competitive_pattern = self._compile_pattern_list(self.competitive_keywords)
            self._financial_pattern = self._compile_pattern_list(self.financial_keywords)
            self._industry_pattern = self._compile_pattern_list(self.industry_keywords)
            self._economic_pattern = self._compile_pattern_list(self.economic_keywords)
            self._tech_trend_pattern = self._compile_pattern_list(self.tech_trend_keywords)
            self._vendor_pattern = self._compile_pattern_list(self.vendors)
            self._ma_intelligence_pattern = self._compile_pattern_list(self.ma_intelligence_keywords)
            
            # ENHANCED: Compile CNAPP and Cloud Security patterns for better scoring
            self._cnapp_pattern = self._compile_pattern_list(self.cnapp_keywords)
            self._cnapp_cloud_security_pattern = self._compile_pattern_list(self.cnapp_cloud_security_keywords)
            self._channel_intelligence_pattern = self._compile_pattern_list(self.channel_intelligence_keywords)
            
            # ENHANCED: Compile MSP and Security patterns for better scoring
            self._msp_pattern = self._compile_pattern_list(self.msp_keywords)
            self._security_pattern = self._compile_pattern_list(self.security_keywords)
            
            total_keywords = len(self.keywords + self.urgency_keywords + self.price_point_keywords + 
                               self.competitive_keywords + self.financial_keywords + self.industry_keywords + 
                               self.economic_keywords + self.tech_trend_keywords + self.ma_intelligence_keywords +
                               self.cnapp_keywords + self.cnapp_cloud_security_keywords + self.channel_intelligence_keywords +
                               self.msp_keywords + self.security_keywords)
            self.logger.info(f"✅ Compiled {total_keywords} keyword patterns for enterprise performance")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Regex compilation failed, falling back to string matching: {e}")
            # Set patterns to None to fall back to string matching
            self._pricing_pattern = None
            self._urgency_pattern = None
            self._price_point_pattern = None
            self._competitive_pattern = None
            self._financial_pattern = None
            self._industry_pattern = None
            self._economic_pattern = None
            self._tech_trend_pattern = None
            self._vendor_pattern = None
            self._ma_intelligence_pattern = None
            self._cnapp_pattern = None
            self._cnapp_cloud_security_pattern = None
            self._channel_intelligence_pattern = None
            self._msp_pattern = None
            self._security_pattern = None

    def _compile_pattern_list(self, keywords: List[str]) -> Pattern:
        """Compile a list of keywords into a single optimized regex pattern"""
        if not keywords:
            return None
        
        # Escape special regex characters and create word boundary matches
        escaped_keywords = [re.escape(kw.lower()) for kw in keywords]
        
        # Create pattern with word boundaries for exact matches
        pattern_str = r'\b(?:' + '|'.join(escaped_keywords) + r')\b'
        
        return re.compile(pattern_str, re.IGNORECASE | re.MULTILINE)

    @abstractmethod
    def get_source_name(self) -> str:
        """Return the source name (reddit, twitter, etc.)"""
        pass

    @abstractmethod
    async def fetch_raw(self) -> List[Dict[str, Any]]:
        """Fetch raw content from the source"""
        pass

    async def fetch(self) -> List[Dict[str, Any]]:
        """Fetch and process content"""
        if not self.enabled:
            self.logger.info(f"{self.source_name} fetcher is disabled")
            return []

        if self.test_mode:
            return self._load_test_data()

        try:
            # Check cache first
            cached_data = self._get_cached_data()
            if cached_data is not None:
                self.logger.info(f"Using cached data for {self.source_name}")
                return cached_data

            # Fetch fresh data
            self.logger.info(f"Fetching fresh data from {self.source_name}")
            raw_data = await self.fetch_raw()

            # Process and score
            processed_data = self._process_data(raw_data)

            # Cache the results
            self._cache_data(processed_data)

            return processed_data

        except Exception as e:
            self.logger.error(f"Error fetching from {self.source_name}: {e}")
            raise

    def _flatten_vendors(self, vendors_dict: Dict[str, List[str]]) -> List[str]:
        """Flatten vendor categories into a single list"""
        all_vendors = []
        for category in vendors_dict.values():
            all_vendors.extend(category)
        return [v.lower() for v in all_vendors]

    def _calculate_relevance_score(self, text: str) -> float:
        """Revenue Impact Scoring system for world-class pricing intelligence"""
        return self._calculate_revenue_impact_score(text)
    
    def _calculate_revenue_impact_score(self, text: str) -> float:
        """
        Revenue Impact Scoring System:
        - Immediate Revenue Impact (30%)
        - Margin Opportunity (25%) 
        - Competitive Advantage (20%)
        - Strategic Value (15%)
        - Urgency Factor (10%)
        + MSP Context Multiplier (1.5x when MSP context detected)
        + Partnership Intelligence Boosts (Microsoft, Channel, Partner Tier, Business Relationship)
        """
        text_lower = text.lower()
        
        # Use compiled patterns for 10x performance improvement
        if hasattr(self, '_pricing_pattern') and self._pricing_pattern:
            # Factor 1: Immediate Revenue Impact (30%)
            immediate_revenue_score = self._calculate_immediate_revenue_impact(text, text_lower)
            
            # Factor 2: Margin Opportunity (25%)
            margin_opportunity_score = self._calculate_margin_opportunity(text, text_lower)
            
            # Factor 3: Competitive Advantage (20%)
            competitive_advantage_score = self._calculate_competitive_advantage(text, text_lower)
            
            # Factor 4: Strategic Value (15%)
            strategic_value_score = self._calculate_strategic_value(text, text_lower)
            
            # Factor 5: Urgency Factor (10%)
            urgency_factor_score = self._calculate_urgency_factor(text, text_lower)
            
            # Calculate weighted Revenue Impact Score
            base_revenue_impact_score = (
                immediate_revenue_score * 0.30 +
                margin_opportunity_score * 0.25 +
                competitive_advantage_score * 0.20 +
                strategic_value_score * 0.15 +
                urgency_factor_score * 0.10
            )
            
            # ENHANCED: MSP Context Detection and Multiplier
            msp_context_multiplier = self._detect_msp_context(text, text_lower)
            revenue_impact_score = base_revenue_impact_score * msp_context_multiplier
            
            # ENHANCED: Partnership Intelligence Boosts
            partnership_intelligence_boost = self._calculate_partnership_intelligence_boost(text, text_lower)
            revenue_impact_score += partnership_intelligence_boost
            
            # ENHANCED: Business Context Scoring - MSP and Security Intelligence Boost
            business_context_boost = self._calculate_business_context_boost(text, text_lower)
            revenue_impact_score += business_context_boost
            
            # Enhanced logging for high-scoring or business critical content
            if revenue_impact_score >= 5.0 or business_context_boost > 0 or partnership_intelligence_boost > 0 or msp_context_multiplier > 1.0 or any(term in text_lower for term in ['vcsp', 'program shutdown', 'partner program', 'thousands of partners']):
                self.logger.info(f"🎯 REVENUE IMPACT SCORING - Text: '{text[:100]}...'")
                self.logger.info(f"💰 Total Revenue Impact Score: {revenue_impact_score:.1f}")
                self.logger.info(f"   📊 Base Score: {base_revenue_impact_score:.1f}")
                self.logger.info(f"   📊 Immediate Revenue (30%): {immediate_revenue_score:.1f}")
                self.logger.info(f"   📈 Margin Opportunity (25%): {margin_opportunity_score:.1f}")
                self.logger.info(f"   ⚔️ Competitive Advantage (20%): {competitive_advantage_score:.1f}")
                self.logger.info(f"   🎯 Strategic Value (15%): {strategic_value_score:.1f}")
                self.logger.info(f"   🚨 Urgency Factor (10%): {urgency_factor_score:.1f}")
                if msp_context_multiplier > 1.0:
                    self.logger.info(f"   🔥 MSP Context Multiplier: {msp_context_multiplier:.1f}x")
                if partnership_intelligence_boost > 0:
                    self.logger.info(f"   🤝 Partnership Intelligence Boost: +{partnership_intelligence_boost:.1f}")
                if business_context_boost > 0:
                    self.logger.info(f"   🚀 Business Context Boost: +{business_context_boost:.1f}")
            
            return revenue_impact_score
        else:
            # Fallback to string matching if regex compilation failed
            return self._calculate_relevance_score_fallback(text)

    def _calculate_immediate_revenue_impact(self, text: str, text_lower: str) -> float:
        """Factor 1: Immediate Revenue Impact (30%) - Direct pricing/sales opportunities"""
        score = 0.0
        
        # Direct pricing opportunities
        price_point_matches = self._price_point_pattern.findall(text) if self._price_point_pattern else []
        score += len(price_point_matches) * 3.0  # High value for pricing opportunities
        
        # Sales opportunities
        pricing_matches = self._pricing_pattern.findall(text) if self._pricing_pattern else []
        score += len(pricing_matches) * 2.0  # Direct pricing discussions
        
        # Revenue-specific terms
        revenue_indicators = ['revenue', 'sales', 'deal', 'contract', 'purchase', 'order', 'demand']
        for indicator in revenue_indicators:
            if indicator in text_lower:
                score += 1.5
        
        # ENHANCED: Pricing change indicators (critical for CNAPP intelligence)
        pricing_change_indicators = [
            'pricing doubled', 'price doubled', 'pricing increase', 'price increase', 
            'cost increase', 'pricing overhaul', 'price overhaul', 'pricing change',
            'price change', 'pricing adjustment', 'price adjustment', 'pricing model',
            'pricing sees', 'pricing has', 'dramatic increase', 'unprecedented increase',
            'significant increase', 'substantial increase', 'major increase'
        ]
        for indicator in pricing_change_indicators:
            if indicator in text_lower:
                score += 3.0  # High boost for pricing changes
        
        return min(score, 10.0)  # Cap at 10

    def _calculate_margin_opportunity(self, text: str, text_lower: str) -> float:
        """Factor 2: Margin Opportunity (25%) - Vendor shifts, cost optimization"""
        score = 0.0
        
        # Competitive displacement opportunities
        competitive_matches = self._competitive_pattern.findall(text) if self._competitive_pattern else []
        score += len(competitive_matches) * 2.5  # High value for displacement
        
        # Cost optimization opportunities
        financial_matches = self._financial_pattern.findall(text) if self._financial_pattern else []
        score += len(financial_matches) * 1.5  # Financial optimization
        
        # Vendor relationship changes
        vendor_matches = self._vendor_pattern.findall(text) if self._vendor_pattern else []
        score += len(vendor_matches) * 1.0  # Vendor mentions
        
        # M&A Intelligence as margin opportunity (acquisitions create pricing power)
        if self._ma_intelligence_pattern:
            ma_matches = self._ma_intelligence_pattern.findall(text)
            if ma_matches:
                score += 2.5  # M&A intelligence indicates margin opportunity
        
        # CNAPP Intelligence as margin opportunity (cloud security pricing power)
        if self._cnapp_pattern:
            cnapp_matches = self._cnapp_pattern.findall(text)
            if cnapp_matches:
                score += 3.0  # CNAPP intelligence indicates high margin opportunity
        
        # CNAPP Cloud Security Intelligence as margin opportunity
        if self._cnapp_cloud_security_pattern:
            cnapp_cloud_matches = self._cnapp_cloud_security_pattern.findall(text)
            if cnapp_cloud_matches:
                score += 2.0  # Cloud security intelligence indicates margin opportunity
        
        # Margin-specific terms
        margin_indicators = ['margin', 'profit', 'discount', 'rebate', 'commission', 'markup']
        for indicator in margin_indicators:
            if indicator in text_lower:
                score += 2.0
        
        return min(score, 10.0)  # Cap at 10

    def _calculate_competitive_advantage(self, text: str, text_lower: str) -> float:
        """Factor 3: Competitive Advantage (20%) - Early mover benefits, market positioning"""
        score = 0.0
        
        # Early market signals
        tech_trend_matches = self._tech_trend_pattern.findall(text) if self._tech_trend_pattern else []
        score += len(tech_trend_matches) * 2.0  # Technology trends
        
        # Competitive positioning
        competitive_terms = ['competitive', 'market share', 'positioning', 'advantage', 'differentiation']
        for term in competitive_terms:
            if term in text_lower:
                score += 1.5
        
        # Market timing indicators
        timing_indicators = ['first', 'early', 'ahead', 'leading', 'pioneer', 'before']
        for indicator in timing_indicators:
            if indicator in text_lower:
                score += 1.0
        
        return min(score, 10.0)  # Cap at 10

    def _calculate_strategic_value(self, text: str, text_lower: str) -> float:
        """Factor 4: Strategic Value (15%) - Long-term portfolio positioning"""
        score = 0.0
        
        # Industry vertical alignment
        industry_matches = self._industry_pattern.findall(text) if self._industry_pattern else []
        score += len(industry_matches) * 1.5  # Industry relevance
        
        # Economic conditions impact
        economic_matches = self._economic_pattern.findall(text) if self._economic_pattern else []
        score += len(economic_matches) * 1.0  # Economic context
        
        # M&A Intelligence as strategic value (acquisitions are strategic moves)
        if self._ma_intelligence_pattern:
            ma_matches = self._ma_intelligence_pattern.findall(text)
            if ma_matches:
                score += 2.0  # M&A intelligence has high strategic value
        
        # Channel Intelligence as strategic value (partner relationships are strategic)
        if self._channel_intelligence_pattern:
            channel_matches = self._channel_intelligence_pattern.findall(text)
            if channel_matches:
                score += 2.5  # Channel intelligence has high strategic value
        
        # Strategic terms
        strategic_terms = ['strategy', 'strategic', 'portfolio', 'roadmap', 'vision', 'future']
        for term in strategic_terms:
            if term in text_lower:
                score += 1.0
        
        return min(score, 10.0)  # Cap at 10

    def _calculate_urgency_factor(self, text: str, text_lower: str) -> float:
        """Factor 5: Urgency Factor (10%) - Time-sensitive opportunities"""
        score = 0.0
        
        # Urgency indicators
        urgency_matches = self._urgency_pattern.findall(text) if self._urgency_pattern else []
        score += len(urgency_matches) * 3.0  # High urgency value
        
        # Time-sensitive terms
        time_sensitive = ['immediate', 'urgent', 'asap', 'deadline', 'expires', 'limited time']
        for term in time_sensitive:
            if term in text_lower:
                score += 2.0
        
        return min(score, 10.0)  # Cap at 10
    
    def _detect_msp_context(self, text: str, text_lower: str) -> float:
        """Detect MSP context and return appropriate multiplier"""
        msp_context_indicators = [
            'msp', 'managed service provider', 'service provider', 'channel partner',
            'reseller', 'distributor', 'var', 'value added reseller', 'solution provider',
            'system integrator', 'si', 'consulting partner', 'partner program',
            'channel program', 'partner tier', 'partner level', 'partner status',
            'partner portal', 'partner agreement', 'partner relationship',
            'partner benefits', 'partner requirements', 'partner certification',
            'partner training', 'partner support', 'partner enablement',
            'vcsp', 'vcp', 'csp', 'cloud solution provider', 'cloud service provider',
            'microsoft partner', 'microsoft partnership', 'microsoft channel',
            'microsoft reseller', 'microsoft distributor', 'microsoft var',
            'azure partner', 'office 365 partner', 'dynamics partner',
            'enterprise agreement', 'ea', 'select plus', 'open license',
            'volume licensing', 'vlsc', 'volume licensing service center'
        ]
        
        for indicator in msp_context_indicators:
            if indicator in text_lower:
                self.logger.info(f"🔥 MSP CONTEXT DETECTED: '{indicator}' in '{text[:80]}...'")
                return 1.5  # 1.5x multiplier for MSP context
        
        return 1.0  # No multiplier for non-MSP content
    
    def _calculate_partnership_intelligence_boost(self, text: str, text_lower: str) -> float:
        """Calculate partnership intelligence boost for critical MSP ecosystem changes"""
        boost_score = 0.0
        
        # Microsoft partnership changes: +2.5 boost
        microsoft_partnership_patterns = [
            r'microsoft.*business.*relationship',
            r'microsoft.*partnership.*chang',
            r'microsoft.*partner.*program.*chang',
            r'microsoft.*channel.*chang',
            r'microsoft.*reseller.*program.*chang',
            r'microsoft.*distributor.*program.*chang',
            r'microsoft.*var.*program.*chang',
            r'microsoft.*csp.*program.*chang',
            r'microsoft.*vcsp.*program.*chang',
            r'microsoft.*partnership.*modification',
            r'microsoft.*partnership.*update',
            r'microsoft.*partnership.*restructur',
            r'microsoft.*business.*relationship.*chang',
            r'microsoft.*announces.*channel',
            r'microsoft.*announces.*partner',
            r'microsoft.*announces.*program'
        ]
        
        for pattern in microsoft_partnership_patterns:
            import re
            matches = re.findall(pattern, text_lower)
            if matches:
                boost_score += 3.0
                self.logger.info(f"🤝 MICROSOFT PARTNERSHIP BOOST: +3.0 for pattern '{pattern}' in '{text[:80]}...'")
                break
        
        # Channel program modifications: +2.0 boost
        channel_program_patterns = [
            r'channel.*program.*chang',
            r'channel.*program.*modification',
            r'channel.*program.*update',
            r'channel.*program.*restructur',
            r'channel.*program.*overhaul',
            r'channel.*program.*reform',
            r'channel.*strategy.*chang',
            r'channel.*strategy.*shift',
            r'channel.*model.*chang',
            r'partner.*program.*chang',
            r'partner.*program.*modification',
            r'partner.*program.*update',
            r'partner.*program.*restructur',
            r'reseller.*program.*chang',
            r'distributor.*program.*chang',
            r'var.*program.*chang',
            r'csp.*program.*chang',
            r'vcsp.*program.*chang'
        ]
        
        for pattern in channel_program_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                boost_score += 2.0
                self.logger.info(f"🔄 CHANNEL PROGRAM BOOST: +2.0 for pattern '{pattern}' in '{text[:80]}...'")
                break
        
        # Partner tier changes: +2.0 boost
        partner_tier_patterns = [
            r'partner.*tier.*chang',
            r'partner.*level.*chang',
            r'partner.*status.*chang',
            r'partner.*certification.*chang',
            r'partner.*accreditation.*chang',
            r'partner.*qualification.*chang',
            r'partner.*requirements.*chang',
            r'partner.*benefits.*chang',
            r'competency.*requirements.*chang',
            r'gold.*partner',
            r'silver.*partner',
            r'authorized.*partner',
            r'certified.*partner',
            r'premier.*partner',
            r'elite.*partner',
            r'tier.*chang.*gold',
            r'tier.*chang.*silver',
            r'tier.*chang.*status',
            r'tier.*chang.*certification',
            r'tier.*chang.*requirements'
        ]
        
        for pattern in partner_tier_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                boost_score += 4.0
                self.logger.info(f"🏆 PARTNER TIER BOOST: +4.0 for pattern '{pattern}' in '{text[:80]}...'")
                break
        
        # Business relationship changes: +2.5 boost
        business_relationship_patterns = [
            r'business.*relationship.*chang',
            r'business.*relationship.*shift',
            r'business.*relationship.*modification',
            r'business.*relationship.*update',
            r'business.*relationship.*restructur',
            r'business.*relationship.*reform',
            r'business.*relationship.*overhaul',
            r'commercial.*relationship.*chang',
            r'commercial.*partnership.*chang',
            r'strategic.*relationship.*chang',
            r'strategic.*partnership.*chang',
            r'vendor.*relationship.*chang',
            r'supplier.*relationship.*chang',
            r'partnership.*model.*chang',
            r'go-to-market.*relationship.*chang',
            r'sales.*relationship.*chang',
            r'distribution.*relationship.*chang'
        ]
        
        for pattern in business_relationship_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                boost_score += 3.0
                self.logger.info(f"🎯 BUSINESS RELATIONSHIP BOOST: +3.0 for pattern '{pattern}' in '{text[:80]}...'")
                break
        
        return min(boost_score, 8.0)  # Cap at 8.0 to prevent excessive scoring

    def _calculate_business_context_boost(self, text: str, text_lower: str) -> float:
        """Business Context Scoring - MSP and Security Intelligence Boost"""
        boost_score = 0.0
        
        # MSP Procurement Intelligence Boost
        if self._msp_pattern:
            msp_matches = self._msp_pattern.findall(text)
            if msp_matches:
                boost_score += 2.0  # Significant boost for MSP content
                self.logger.info(f"🎯 MSP CONTENT BOOST: +2.0 for MSP intelligence: '{text[:80]}...'")
        
        # Security Software Intelligence Boost
        if self._security_pattern:
            security_matches = self._security_pattern.findall(text)
            if security_matches:
                boost_score += 1.5  # Boost for security content
                self.logger.info(f"🎯 SECURITY CONTENT BOOST: +1.5 for security intelligence: '{text[:80]}...'")
        
        # Vendor Experience Pattern Boost
        vendor_experience_patterns = [
            r'what\'s your experience with\s+(\w+)',
            r'experience with\s+(\w+)',
            r'thoughts on\s+(\w+)',
            r'anyone using\s+(\w+)',
            r'has anyone used\s+(\w+)',
            r'opinions on\s+(\w+)'
        ]
        
        for pattern in vendor_experience_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                boost_score += 1.5  # Boost for vendor experience discussions
                self.logger.info(f"🎯 VENDOR EXPERIENCE BOOST: +1.5 for vendor experience: '{text[:80]}...'")
                break
        
        # Server/Storage Procurement Boost
        server_storage_patterns = [
            r'server\s+procurement',
            r'storage\s+evaluation',
            r'hardware\s+evaluation',
            r'server\s+(.+)\s+storage',
            r'lenovo\s+(.+)\s+server',
            r'dell\s+(.+)\s+server',
            r'hp\s+(.+)\s+server'
        ]
        
        for pattern in server_storage_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                boost_score += 1.0  # Boost for server/storage discussions
                self.logger.info(f"🎯 SERVER/STORAGE BOOST: +1.0 for procurement intelligence: '{text[:80]}...'")
                break
        
        # MSP Subreddit Context Boost
        if 'r/msp' in text_lower or '/r/msp' in text_lower:
            boost_score += 1.0  # Additional boost for MSP subreddit content
            self.logger.info(f"🎯 MSP SUBREDDIT BOOST: +1.0 for MSP context: '{text[:80]}...'")
        
        # Security Performance Issues Boost
        performance_issue_patterns = [
            r'makes me suffer',
            r'frustrated with',
            r'issues with',
            r'problems with',
            r'struggling with',
            r'defender\s+(.+)\s+issues',
            r'defender\s+(.+)\s+problems'
        ]
        
        for pattern in performance_issue_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                boost_score += 1.0  # Boost for security performance issues
                self.logger.info(f"🎯 SECURITY PERFORMANCE BOOST: +1.0 for performance issues: '{text[:80]}...'")
                break
        
        # M&A Intelligence Boost - Critical for post-acquisition monetization patterns
        ma_boost = self._calculate_ma_intelligence_boost(text, text_lower)
        if ma_boost > 0:
            boost_score += ma_boost
            self.logger.info(f"🎯 M&A INTELLIGENCE BOOST: +{ma_boost:.1f} for M&A patterns: '{text[:80]}...'")
        
        # ENHANCED: Cloud Security Platform Intelligence Boost - Critical for CNAPP scoring
        cloud_security_boost = self._calculate_cloud_security_platform_boost(text, text_lower)
        if cloud_security_boost > 0:
            boost_score += cloud_security_boost
            self.logger.info(f"🔒 CLOUD SECURITY PLATFORM BOOST: +{cloud_security_boost:.1f} for CNAPP patterns: '{text[:80]}...'")
        
        return min(boost_score, 10.0)  # Increased cap to 10.0 for critical intelligence

    def _calculate_ma_intelligence_boost(self, text: str, text_lower: str) -> float:
        """M&A Intelligence Boost - Critical for post-acquisition monetization patterns"""
        boost_score = 0.0
        
        # M&A Intelligence Pattern Matching using compiled patterns
        if self._ma_intelligence_pattern:
            ma_matches = self._ma_intelligence_pattern.findall(text)
            if ma_matches:
                boost_score += 2.5  # Base M&A intelligence boost (increased)
                self.logger.info(f"🎯 M&A PATTERN MATCH: +2.5 for compiled patterns: '{text[:80]}...'")
        
        # Post-acquisition audits: +3.0 boost
        post_acquisition_audit_patterns = [
            r'post-acquisition\s+audit',
            r'post-acquisition\s+audits',
            r'post-acquisition\s+licensing',
            r'post-acquisition\s+monetization',
            r'post-acquisition\s+enforcement',
            r'post-acquisition\s+compliance',
            r'begins\s+auditing',
            r'starts\s+auditing',
            r'conducting\s+audits',
            r'auditing\s+organizations',
            r'auditing\s+customers',
            r'auditing\s+clients'
        ]
        
        for pattern in post_acquisition_audit_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                boost_score += 3.0  # High boost for post-acquisition audits
                self.logger.info(f"🎯 POST-ACQUISITION AUDIT BOOST: +3.0 for audit patterns: '{text[:80]}...'")
                break
        
        # License enforcement: +3.0 boost
        license_enforcement_patterns = [
            r'license\s+enforcement',
            r'license\s+audits',
            r'license\s+compliance',
            r'license\s+review',
            r'license\s+verification',
            r'license\s+reconciliation',
            r'licensing\s+overhaul',
            r'licensing\s+enforcement',
            r'forced\s+migration',
            r'mandatory\s+migration',
            r'compliance\s+audit',
            r'usage\s+audit'
        ]
        
        for pattern in license_enforcement_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                boost_score += 3.0  # High boost for license enforcement
                self.logger.info(f"🎯 LICENSE ENFORCEMENT BOOST: +3.0 for license patterns: '{text[:80]}...'")
                break
        
        # Broadcom/VMware specific: +2.0 additional boost
        broadcom_vmware_patterns = [
            r'broadcom\s+vmware',
            r'vmware\s+by\s+broadcom',
            r'broadcom\s+audit',
            r'broadcom\s+begins',
            r'broadcom\s+starts',
            r'broadcom.*audit',
            r'vmware.*broadcom.*audit',
            r'broadcom.*vmware.*audit'
        ]
        
        for pattern in broadcom_vmware_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                boost_score += 2.0  # Additional boost for Broadcom/VMware specific patterns
                self.logger.info(f"🎯 BROADCOM/VMWARE BOOST: +2.0 for specific patterns: '{text[:80]}...'")
                break
        
        # Acquisition monetization: +3.0 boost
        acquisition_monetization_patterns = [
            r'acquisition\s+monetization',
            r'acquisition\s+strategy',
            r'acquisition\s+integration',
            r'merger\s+monetization',
            r'merger\s+integration',
            r'merger\s+audit',
            r'merger\s+compliance'
        ]
        
        for pattern in acquisition_monetization_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                boost_score += 3.0  # High boost for acquisition monetization
                self.logger.info(f"🎯 ACQUISITION MONETIZATION BOOST: +3.0 for monetization patterns: '{text[:80]}...'")
                break
        
        # Business impact multiplier for enterprise-scale M&A patterns
        enterprise_scale_patterns = [
            r'organizations\s+using',
            r'customers\s+using',
            r'clients\s+using',
            r'enterprise\s+customers',
            r'business\s+customers',
            r'customer\s+base',
            r'client\s+base'
        ]
        
        for pattern in enterprise_scale_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                boost_score += 1.0  # Additional boost for enterprise scale
                self.logger.info(f"🎯 ENTERPRISE SCALE BOOST: +1.0 for enterprise patterns: '{text[:80]}...'")
                break
        
        return min(boost_score, 6.5)  # Cap M&A boost at 6.5 for critical M&A intelligence

    def _calculate_cloud_security_platform_boost(self, text: str, text_lower: str) -> float:
        """Cloud Security Platform Intelligence Boost - Critical for CNAPP scoring consistency"""
        import re
        boost_score = 0.0
        
        # CNAPP Platform Intelligence Pattern Matching using compiled patterns
        if self._cnapp_pattern:
            cnapp_matches = self._cnapp_pattern.findall(text)
            if cnapp_matches:
                boost_score += 3.0  # High boost for CNAPP platform intelligence
                self.logger.info(f"🔒 CNAPP PLATFORM MATCH: +3.0 for CNAPP patterns: '{text[:80]}...'")
        
        # CNAPP Cloud Security Pattern Matching using compiled patterns
        if self._cnapp_cloud_security_pattern:
            cnapp_cloud_matches = self._cnapp_cloud_security_pattern.findall(text)
            if cnapp_cloud_matches:
                boost_score += 2.5  # Significant boost for cloud security patterns
                self.logger.info(f"🔒 CNAPP CLOUD SECURITY MATCH: +2.5 for cloud security patterns: '{text[:80]}...'")
        
        # Cloud Security Platform Pricing Intelligence: +3.0 boost
        cloud_security_pricing_patterns = [
            r'cnapp.*pricing.*doubled',
            r'cloud.*security.*platform.*pricing.*doubled',
            r'container.*security.*pricing.*doubled',
            r'kubernetes.*security.*pricing.*doubled',
            r'cloud.*workload.*protection.*pricing.*doubled',
            r'cwpp.*pricing.*doubled',
            r'cspm.*pricing.*doubled',
            r'ciem.*pricing.*doubled',
            r'cloud.*security.*posture.*management.*pricing',
            r'cloud.*infrastructure.*entitlement.*management.*pricing',
            r'cloud.*native.*application.*protection.*platform.*pricing',
            r'devsecops.*pricing.*doubled',
            r'shift-left.*security.*pricing.*doubled',
            r'runtime.*security.*pricing.*doubled',
            r'vulnerability.*management.*pricing.*doubled',
            r'compliance.*management.*pricing.*doubled',
            r'policy.*as.*code.*pricing.*doubled',
            r'infrastructure.*as.*code.*security.*pricing',
            r'api.*security.*pricing.*doubled',
            r'zero.*trust.*security.*pricing.*doubled',
            r'threat.*detection.*pricing.*doubled',
            r'security.*orchestration.*pricing.*doubled',
            r'managed.*security.*services.*pricing.*doubled',
            r'security.*as.*a.*service.*pricing.*doubled'
        ]
        
        for pattern in cloud_security_pricing_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                boost_score += 3.0  # High boost for cloud security pricing intelligence
                self.logger.info(f"🔒 CLOUD SECURITY PRICING BOOST: +3.0 for pricing pattern '{pattern}': '{text[:80]}...'")
                break
        
        # Cloud Security Platform Cost Increase: +2.5 boost
        cloud_security_cost_patterns = [
            r'cnapp.*cost.*increase',
            r'cloud.*security.*platform.*cost.*increase',
            r'container.*security.*cost.*increase',
            r'kubernetes.*security.*cost.*increase',
            r'cloud.*workload.*protection.*cost.*increase',
            r'cwpp.*cost.*increase',
            r'cspm.*cost.*increase',
            r'ciem.*cost.*increase',
            r'cloud.*security.*posture.*management.*cost',
            r'cloud.*infrastructure.*entitlement.*management.*cost',
            r'devsecops.*cost.*increase',
            r'shift-left.*security.*cost.*increase',
            r'runtime.*security.*cost.*increase',
            r'vulnerability.*management.*cost.*increase',
            r'compliance.*management.*cost.*increase',
            r'policy.*as.*code.*cost.*increase',
            r'api.*security.*cost.*increase',
            r'zero.*trust.*security.*cost.*increase',
            r'threat.*detection.*cost.*increase',
            r'security.*orchestration.*cost.*increase',
            r'managed.*security.*services.*cost.*increase',
            r'security.*as.*a.*service.*cost.*increase'
        ]
        
        for pattern in cloud_security_cost_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                boost_score += 2.5  # Significant boost for cloud security cost increase
                self.logger.info(f"🔒 CLOUD SECURITY COST BOOST: +2.5 for cost pattern '{pattern}': '{text[:80]}...'")
                break
        
        # Cloud Security Platform Overhaul: +2.0 boost
        cloud_security_overhaul_patterns = [
            r'cnapp.*pricing.*overhaul',
            r'cloud.*security.*platform.*pricing.*overhaul',
            r'container.*security.*pricing.*overhaul',
            r'kubernetes.*security.*pricing.*overhaul',
            r'cloud.*workload.*protection.*pricing.*overhaul',
            r'cwpp.*pricing.*overhaul',
            r'cspm.*pricing.*overhaul',
            r'ciem.*pricing.*overhaul',
            r'cloud.*security.*posture.*management.*pricing.*overhaul',
            r'cloud.*infrastructure.*entitlement.*management.*pricing.*overhaul',
            r'devsecops.*pricing.*overhaul',
            r'shift-left.*security.*pricing.*overhaul',
            r'runtime.*security.*pricing.*overhaul',
            r'vulnerability.*management.*pricing.*overhaul',
            r'compliance.*management.*pricing.*overhaul',
            r'policy.*as.*code.*pricing.*overhaul',
            r'api.*security.*pricing.*overhaul',
            r'zero.*trust.*security.*pricing.*overhaul',
            r'threat.*detection.*pricing.*overhaul',
            r'security.*orchestration.*pricing.*overhaul',
            r'managed.*security.*services.*pricing.*overhaul',
            r'security.*as.*a.*service.*pricing.*overhaul'
        ]
        
        for pattern in cloud_security_overhaul_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                boost_score += 2.0  # Boost for cloud security pricing overhaul
                self.logger.info(f"🔒 CLOUD SECURITY OVERHAUL BOOST: +2.0 for overhaul pattern '{pattern}': '{text[:80]}...'")
                break
        
        # Cloud Security Platform Vendor Intelligence: +1.5 boost
        cloud_security_vendor_patterns = [
            r'cnapp.*vendor.*pricing',
            r'cloud.*security.*platform.*vendor.*pricing',
            r'container.*security.*vendor.*pricing',
            r'kubernetes.*security.*vendor.*pricing',
            r'cloud.*workload.*protection.*vendor.*pricing',
            r'cwpp.*vendor.*pricing',
            r'cspm.*vendor.*pricing',
            r'ciem.*vendor.*pricing',
            r'prisma.*cloud.*pricing',
            r'wiz.*pricing',
            r'aqua.*security.*pricing',
            r'snyk.*pricing',
            r'twistlock.*pricing',
            r'sysdig.*pricing',
            r'lacework.*pricing',
            r'orca.*security.*pricing',
            r'defender.*for.*cloud.*pricing',
            r'guardduty.*pricing',
            r'security.*hub.*pricing',
            r'inspector.*pricing'
        ]
        
        for pattern in cloud_security_vendor_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                boost_score += 1.5  # Boost for cloud security vendor pricing
                self.logger.info(f"🔒 CLOUD SECURITY VENDOR BOOST: +1.5 for vendor pattern '{pattern}': '{text[:80]}...'")
                break
        
        # Cloud Security Platform Enterprise Impact: +1.0 boost
        cloud_security_enterprise_patterns = [
            r'cloud.*security.*platform.*enterprise.*deployments',
            r'cnapp.*enterprise.*deployments',
            r'container.*security.*enterprise.*deployments',
            r'kubernetes.*security.*enterprise.*deployments',
            r'cloud.*workload.*protection.*enterprise.*deployments',
            r'cwpp.*enterprise.*deployments',
            r'cspm.*enterprise.*deployments',
            r'ciem.*enterprise.*deployments',
            r'cloud.*security.*affects.*enterprise',
            r'cloud.*security.*hits.*enterprise',
            r'cloud.*security.*impacts.*enterprise',
            r'enterprise.*cloud.*security.*costs',
            r'enterprise.*cloud.*security.*pricing',
            r'enterprise.*cloud.*security.*budget'
        ]
        
        for pattern in cloud_security_enterprise_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                boost_score += 1.0  # Boost for enterprise cloud security impact
                self.logger.info(f"🔒 CLOUD SECURITY ENTERPRISE BOOST: +1.0 for enterprise pattern '{pattern}': '{text[:80]}...'")
                break
        
        return min(boost_score, 4.0)  # Cap cloud security boost at 4.0 for consistent scoring

    def _calculate_relevance_score_fallback(self, text: str) -> float:
        """Fallback scoring method using string matching"""
        text_lower = text.lower()
        score = 0.0

        # Base pricing keywords (fallback)
        keyword_matches = [kw for kw in self.keywords if kw.lower() in text_lower]
        keyword_score = len(keyword_matches) * self.config['scoring']['keyword_weight']
        score += keyword_score

        # Urgency indicators (fallback)
        urgency_matches = [kw for kw in self.urgency_keywords if kw.lower() in text_lower]
        urgency_score = len(urgency_matches) * self.config['scoring']['urgency_weight']
        score += urgency_score

        # Enhanced keyword categories (fallback)
        price_point_matches = [kw for kw in self.price_point_keywords if kw.lower() in text_lower]
        competitive_matches = [kw for kw in self.competitive_keywords if kw.lower() in text_lower]
        financial_matches = [kw for kw in self.financial_keywords if kw.lower() in text_lower]
        industry_matches = [kw for kw in self.industry_keywords if kw.lower() in text_lower]
        economic_matches = [kw for kw in self.economic_keywords if kw.lower() in text_lower]
        tech_trend_matches = [kw for kw in self.tech_trend_keywords if kw.lower() in text_lower]
        ma_intelligence_matches = [kw for kw in self.ma_intelligence_keywords if kw.lower() in text_lower]
        cnapp_matches = [kw for kw in self.cnapp_keywords if kw.lower() in text_lower]
        cnapp_cloud_matches = [kw for kw in self.cnapp_cloud_security_keywords if kw.lower() in text_lower]
        channel_intelligence_matches = [kw for kw in self.channel_intelligence_keywords if kw.lower() in text_lower]

        enhanced_score = (len(price_point_matches) * 1.2 + len(competitive_matches) * 1.5 + 
                         len(financial_matches) * 1.0 + len(industry_matches) * 0.8 + 
                         len(economic_matches) * 1.0 + len(tech_trend_matches) * 0.9 +
                         len(ma_intelligence_matches) * 2.0 + len(cnapp_matches) * 3.0 + 
                         len(cnapp_cloud_matches) * 2.0 + len(channel_intelligence_matches) * 2.5)
        score += enhanced_score

        # Vendor mentions (fallback)
        vendor_matches = [vendor for vendor in self.vendors if vendor.lower() in text_lower]
        vendor_score = len(vendor_matches) * self.config['scoring']['vendor_weight']
        score += vendor_score

        return score

    def _determine_content_urgency(self, text: str, score: float) -> str:
        """Enhanced urgency detection with vendor ecosystem awareness"""
        text_lower = text.lower()
        
        # Load urgency keywords from config if available
        high_urgency_keywords = self.config['keywords'].get('urgency_indicators', [])
        medium_urgency_keywords = self.config['keywords'].get('urgency_medium', [])
        
        # Fallback to hardcoded keywords if config not available
        if not high_urgency_keywords:
            high_urgency_keywords = [
                'acquisition', 'merger', 'acquired', 'acquires', 'buying', 'bought',
                'bankruptcy', 'lawsuit', 'security breach', 'data breach', 'zero-day',
                'critical vulnerability', 'emergency', 'urgent', 'immediate',
                'discontinued', 'end of life', 'eol', 'supply shortage', 'recall',
                'price increase', 'cost increase', 'breaking', 'alert'
            ]
        
        if not medium_urgency_keywords:
            medium_urgency_keywords = [
                'partnership', 'collaboration', 'investment', 'funding',
                'new pricing', 'discount', 'promotion', 'update', 'change',
                'launch', 'release', 'expansion', 'announcement'
            ]
        
        # ENHANCED: Vendor ecosystem urgency detection
        vendor_ecosystem_high = [
            'shutdown', 'termination', 'discontinued', 'sunsetted', 'cancelled',
            'program closure', 'program end', 'program termination', 'program shutdown',
            'vcsp', 'vcp', 'var program', 'csp program', 'partner program shutdown',
            'channel program end', 'reseller program terminated', 'distributor program',
            'migration deadline', 'migration required', 'forced migration', 'mandatory migration',
            'certification expires', 'certification discontinued', 'accreditation removed',
            'license model change', 'licensing overhaul', 'subscription mandatory',
            'end of support', 'end of sales', 'last order date', 'final orders',
            'asked to shutdown', 'migrate their clients', 'migrate clients',
            'program is closing', 'program closing', 'is closing', 'closing',
            'smoothly migrate', 'migrate to competition', 'migrate to competitors',
            'client migration', 'business shutdown', 'shutdown business',
            'program phase out', 'phasing out', 'sunsetting', 'program discontinuation'
        ]
        
        # ENHANCED: Time-based urgency detection
        time_urgency_high = self._detect_time_urgency(text_lower, months_threshold=6)
        
        # ENHANCED: Scale-based urgency detection
        scale_urgency = self._detect_scale_urgency(text_lower)
        
        # ENHANCED: Business impact detection for IT procurement teams
        business_impact_high = [
            'all partners', 'all resellers', 'all distributors', 'global program',
            'thousands of partners', 'hundreds of partners', 'entire channel',
            'program overhaul', 'business model change', 'go-to-market change',
            'channel strategy shift', 'partner model restructure', 'program consolidation'
        ]
        
        # Check for vendor ecosystem high urgency
        for keyword in vendor_ecosystem_high:
            if keyword in text_lower:
                return 'high'
        
        # Check for business impact high urgency
        for keyword in business_impact_high:
            if keyword in text_lower:
                return 'high'
        
        # Check for time-based urgency
        if time_urgency_high:
            return 'high'
        
        # Check for scale-based urgency
        if scale_urgency == 'high':
            return 'high'
        
        # Check for standard high urgency content
        for keyword in high_urgency_keywords:
            if keyword in text_lower:
                return 'high'
        
        # Check for medium urgency content or scale
        if scale_urgency == 'medium':
            return 'medium'
        
        for keyword in medium_urgency_keywords:
            if keyword in text_lower:
                return 'medium'
        
        # Fall back to score-based detection
        if score >= self.config['scoring']['high_score_threshold']:
            return 'high'
        elif score >= self.config['scoring']['medium_score_threshold']:
            return 'medium'
        else:
            return 'low'

    def _detect_time_urgency(self, text: str, months_threshold: int = 6) -> bool:
        """Detect time-based urgency for deadlines and specific dates"""
        import re
        from datetime import datetime, timedelta
        
        # Patterns for dates and deadlines
        deadline_patterns = [
            r'(?:by|until|before|deadline|expires?|ends?)\s+(?:on\s+)?(\w+\s+\d{1,2},?\s+\d{4})',
            r'(?:by|until|before|deadline|expires?|ends?)\s+(?:on\s+)?(\w+\s+\d{4})',
            r'(?:by|until|before|deadline|expires?|ends?)\s+(?:on\s+)?([a-z]+\s+\d{1,2})',
            r'(?:effective|starting|beginning)\s+(\w+\s+\d{1,2},?\s+\d{4})',
            r'(?:q[1-4]\s+\d{4}|h[12]\s+\d{4})',  # Quarter/half year
            r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{4}',
            r'(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}',
            r'(?:end of|eoy|end of year|end of quarter|eoq)\s+\d{4}',
            r'(?:fiscal year|fy)\s+\d{4}',
            r'(?:migration|transition|switch|move)\s+(?:by|before|until)\s+(\w+\s+\d{4})',
            r'(?:last day|final day|cutoff)\s+(?:is|will be)\s+(\w+\s+\d{1,2},?\s+\d{4})'
        ]
        
        # Look for any deadline patterns
        for pattern in deadline_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return True
        
        # Look for specific urgency time indicators
        urgent_time_indicators = [
            'immediately', 'asap', 'urgent', 'critical deadline', 'time sensitive',
            'expires soon', 'ending soon', 'final notice', 'last chance',
            'limited time', 'time-limited', 'deadline approaching', 'urgent action required',
            'within days', 'within weeks', 'next month', 'this quarter',
            'before year end', 'by end of month', 'by end of quarter'
        ]
        
        for indicator in urgent_time_indicators:
            if indicator in text:
                return True
        
        return False

    def _detect_scale_urgency(self, text: str) -> str:
        """Detect scale-based urgency based on impact scope"""
        
        # High scale indicators
        high_scale_indicators = [
            'thousands of', 'hundreds of', 'all partners', 'all resellers',
            'all distributors', 'entire channel', 'global program', 'worldwide',
            'industry-wide', 'across all', 'complete overhaul', 'major restructure',
            'significant impact', 'massive change', 'affects everyone',
            'comprehensive change', 'universal requirement', 'mandatory for all',
            'company-wide', 'organization-wide', 'enterprise-wide'
        ]
        
        # Medium scale indicators
        medium_scale_indicators = [
            'many partners', 'multiple partners', 'several partners',
            'regional program', 'select partners', 'key partners',
            'major partners', 'tier 1 partners', 'enterprise partners',
            'significant portion', 'substantial impact', 'considerable change',
            'widespread', 'broad impact', 'numerous', 'extensive'
        ]
        
        # Check for high scale
        for indicator in high_scale_indicators:
            if indicator in text:
                return 'high'
        
        # Check for medium scale
        for indicator in medium_scale_indicators:
            if indicator in text:
                return 'medium'
        
        return 'low'

    def _process_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process raw data and add metadata"""
        processed = []

        for item in raw_data:
            # Calculate relevance score
            text = f"{item.get('title', '')} {item.get('content', '')} {item.get('text', '')}"
            score = self._calculate_relevance_score(text)

            # Only include items above minimum threshold
            if score > 0:
                item['relevance_score'] = score
                item['source'] = self.source_name
                item['fetched_at'] = datetime.now().isoformat()

                # Determine urgency level with content-aware detection
                item['urgency'] = self._determine_content_urgency(text, score)

                processed.append(item)

        # Sort by relevance score
        processed.sort(key=lambda x: x['relevance_score'], reverse=True)

        self.logger.info(f"Processed {len(processed)} relevant items from {len(raw_data)} total")
        return processed

    def _get_cache_key(self) -> str:
        """Generate cache key for this source"""
        date_str = datetime.now().strftime('%Y%m%d')
        return f"{self.source_name}_{date_str}"

    def _get_cached_data(self) -> Optional[List[Dict[str, Any]]]:
        """Get cached data if available and fresh"""
        cache_file = self.cache_dir / f"{self._get_cache_key()}.json"

        if cache_file.exists():
            # Check if cache is still fresh
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age < timedelta(hours=self.config['system']['cache_ttl_hours']):
                try:
                    with open(cache_file, 'r') as f:
                        return json.load(f)
                except Exception as e:
                    self.logger.warning(f"Corrupt or invalid cache in {cache_file.name}: {e}")
                    return None

        return None

    def _cache_data(self, data: List[Dict[str, Any]]) -> None:
        """Cache processed data"""
        cache_file = self.cache_dir / f"{self._get_cache_key()}.json"
        # Convert datetime objects to strings before dumping
        for item in data:
            for key, value in item.items():
                if isinstance(value, datetime):
                    item[key] = value.isoformat()
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _load_test_data(self) -> List[Dict[str, Any]]:
        """Load test data for this source"""
        test_file = Path('test_data') / f"{self.source_name}_mock.json"
        if test_file.exists():
            with open(test_file, 'r') as f:
                data = json.load(f)
                # Process test data same as real data
                return self._process_data(data)
        else:
            self.logger.warning(f"Test data file {test_file} not found")
            return []
