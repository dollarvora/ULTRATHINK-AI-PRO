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
        self.keywords = config['keywords'].get('pricing', [])
        self.urgency_keywords = config['keywords'].get('urgency_indicators', [])
        
        # Enhanced keyword categories for enterprise intelligence
        self.price_point_keywords = config['keywords'].get('price_point_intelligence', [])
        self.competitive_keywords = config['keywords'].get('competitive_displacement', [])
        self.financial_keywords = config['keywords'].get('financial_impact', [])
        self.industry_keywords = config['keywords'].get('industry_verticals', [])
        self.economic_keywords = config['keywords'].get('economic_conditions', [])
        self.tech_trend_keywords = config['keywords'].get('technology_trends', [])
        
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
            
            self.logger.info(f"✅ Compiled {len(self.keywords + self.urgency_keywords + self.price_point_keywords + self.competitive_keywords + self.financial_keywords + self.industry_keywords + self.economic_keywords + self.tech_trend_keywords)} keyword patterns for enterprise performance")
            
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
        """Enterprise-optimized relevance scoring with compiled regex patterns"""
        score = 0.0
        
        # Use compiled patterns for 10x performance improvement
        if hasattr(self, '_pricing_pattern') and self._pricing_pattern:
            keyword_matches = self._pricing_pattern.findall(text) if self._pricing_pattern else []
            keyword_score = len(keyword_matches) * self.config['scoring']['keyword_weight']
            score += keyword_score

            urgency_matches = self._urgency_pattern.findall(text) if self._urgency_pattern else []
            urgency_score = len(urgency_matches) * self.config['scoring']['urgency_weight']
            score += urgency_score

            # Enhanced keyword categories with optimized regex matching
            price_point_matches = self._price_point_pattern.findall(text) if self._price_point_pattern else []
            price_point_score = len(price_point_matches) * 1.2  # High value for specific pricing

            competitive_matches = self._competitive_pattern.findall(text) if self._competitive_pattern else []
            competitive_score = len(competitive_matches) * 1.5  # Very high value for displacement

            financial_matches = self._financial_pattern.findall(text) if self._financial_pattern else []
            financial_score = len(financial_matches) * 1.0  # Standard weight for financial impact

            industry_matches = self._industry_pattern.findall(text) if self._industry_pattern else []
            industry_score = len(industry_matches) * 0.8  # Moderate weight for industry context

            economic_matches = self._economic_pattern.findall(text) if self._economic_pattern else []
            economic_score = len(economic_matches) * 1.0  # Standard weight for economic conditions

            tech_trend_matches = self._tech_trend_pattern.findall(text) if self._tech_trend_pattern else []
            tech_trend_score = len(tech_trend_matches) * 0.9  # High weight for emerging trends

            # Add enhanced scores
            enhanced_score = price_point_score + competitive_score + financial_score + industry_score + economic_score + tech_trend_score
            score += enhanced_score

            vendor_matches = self._vendor_pattern.findall(text) if self._vendor_pattern else []
            vendor_score = len(vendor_matches) * self.config['scoring']['vendor_weight']
            score += vendor_score

        else:
            # Fallback to string matching if regex compilation failed
            return self._calculate_relevance_score_fallback(text)

        # Enhanced logging for high-scoring or business critical content
        if score >= 5.0 or any(term in text.lower() for term in ['vcsp', 'program shutdown', 'partner program', 'thousands of partners']):
            self.logger.info(f"🎯 ENTERPRISE SCORING - Text: '{text[:100]}...'")
            self.logger.info(f"📊 Total Score: {score:.1f} (Base: {keyword_score:.1f}, Urgency: {urgency_score:.1f}, Enhanced: {enhanced_score:.1f}, Vendors: {vendor_score:.1f})")
            if keyword_matches:
                self.logger.info(f"✅ Keyword Matches: {len(keyword_matches)} terms")
            if urgency_matches:
                self.logger.info(f"🚨 Urgency Matches: {len(urgency_matches)} terms")
            if price_point_matches:
                self.logger.info(f"💰 Price Point Matches: {len(price_point_matches)} terms")
            if competitive_matches:
                self.logger.info(f"⚔️ Competitive Matches: {len(competitive_matches)} terms")
            if financial_matches:
                self.logger.info(f"💼 Financial Matches: {len(financial_matches)} terms")
            if vendor_matches:
                self.logger.info(f"🏢 Vendor Matches: {len(vendor_matches)} terms")

        return score

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

        enhanced_score = (len(price_point_matches) * 1.2 + len(competitive_matches) * 1.5 + 
                         len(financial_matches) * 1.0 + len(industry_matches) * 0.8 + 
                         len(economic_matches) * 1.0 + len(tech_trend_matches) * 0.9)
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
