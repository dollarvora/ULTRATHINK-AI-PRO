"""
Base Fetcher Class
Abstract base class for all content fetchers
"""

import json
import logging
import hashlib
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional


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

        # Keywords and vendors for scoring
        self.keywords = config['keywords']['pricing']
        self.urgency_keywords = config['keywords']['urgency_indicators']
        self.vendors = self._flatten_vendors(config['vendors'])

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
        """Calculate relevance score based on keywords and vendors"""
        text_lower = text.lower()
        score = 0.0

        # Check keywords
        keyword_matches = sum(1 for kw in self.keywords if kw in text_lower)
        score += keyword_matches * self.config['scoring']['keyword_weight']

        # Check urgency indicators
        urgency_matches = sum(1 for kw in self.urgency_keywords if kw in text_lower)
        score += urgency_matches * self.config['scoring']['urgency_weight']

        # Check vendor mentions
        vendor_matches = sum(1 for vendor in self.vendors if vendor in text_lower)
        score += vendor_matches * self.config['scoring']['vendor_weight']

        return score

    def _determine_content_urgency(self, text: str, score: float) -> str:
        """Determine urgency level using both content analysis and score"""
        text_lower = text.lower()
        
        # High urgency keywords that override score-based detection
        high_urgency_keywords = [
            'acquisition', 'merger', 'acquired', 'acquires', 'buying', 'bought',
            'bankruptcy', 'lawsuit', 'security breach', 'data breach', 'zero-day',
            'critical vulnerability', 'emergency', 'urgent', 'immediate',
            'discontinued', 'end of life', 'eol', 'supply shortage', 'recall',
            'price increase', 'cost increase', 'breaking', 'alert'
        ]
        
        # Medium urgency keywords
        medium_urgency_keywords = [
            'partnership', 'collaboration', 'investment', 'funding',
            'new pricing', 'discount', 'promotion', 'update', 'change',
            'launch', 'release', 'expansion', 'announcement'
        ]
        
        # Check for high urgency content
        for keyword in high_urgency_keywords:
            if keyword in text_lower:
                return 'high'
        
        # Check for medium urgency content
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
