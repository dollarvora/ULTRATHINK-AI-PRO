"""
Google News Fetcher
Fetches pricing-related news from Google using Custom Search API
Enhanced with relevance filtering and vendor-specific searches
"""

import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import re

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from fetchers.base_fetcher import BaseFetcher
from config.utils import calculate_relevance_score, extract_vendor_mentions


class GoogleFetcher(BaseFetcher):
    """Fetches news articles from Google Custom Search with enhanced relevance filtering"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Define trusted news/blog domains for filtering
        self.trusted_domains = [
            'crn.com', 'channele2e.com', 'channelnews.com', 'channelpartner.com',
            'zdnet.com', 'computerworld.com', 'informationweek.com', 'cio.com',
            'techcrunch.com', 'venturebeat.com', 'businesswire.com', 'prnewswire.com',
            'reuters.com', 'bloomberg.com', 'wsj.com', 'marketwatch.com',
            'gartner.com', 'forrester.com', 'idc.com', 'theregister.com',
            'siliconangle.com', 'techtarget.com', 'itbusiness.ca', 'channeldaily.com'
        ]
        
        # Define keywords that indicate pricing/cost relevance
        self.pricing_keywords = [
            'price', 'pricing', 'cost', 'margin', 'discount', 'rebate', 'promotion',
            'increase', 'decrease', 'surcharge', 'fee', 'subscription', 'licensing',
            'contract', 'agreement', 'savings', 'budget', 'spend', 'investment',
            'acquisition', 'merger', 'partnership', 'layoff', 'earnings', 'revenue'
        ]
        
        # Define keywords to exclude (irrelevant content)
        self.exclude_keywords = [
            'review', 'how to', 'tutorial', 'guide', 'best practices', 'tips',
            'cryptocurrency', 'bitcoin', 'nft', 'metaverse', 'gaming', 'entertainment'
        ]
    
    def get_source_name(self) -> str:
        return 'google'
    
    async def fetch_raw(self) -> List[Dict[str, Any]]:
        """Fetch news articles from Google"""
        # Google API client is synchronous, so we run in executor
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._fetch_sync)
    
    def _fetch_sync(self) -> List[Dict[str, Any]]:
        """Synchronous fetch method for Google"""
        creds = self.config['credentials']['google']
        
        if not creds.get('api_key') or not creds.get('cse_id'):
            self.logger.error("Google API credentials not configured")
            return []
        
        # Build service
        service = build('customsearch', 'v1', developerKey=creds['api_key'])
        
        all_results = []
        
        # Execute searches for each query
        for query in self.source_config['queries']:
            try:
                self.logger.info(f"Searching Google for: {query}")
                
                # Add date restriction
                date_restrict = self.source_config.get('date_restriction', 'd7')
                
                # Execute search
                result = service.cse().list(
                    q=query,
                    cx=creds['cse_id'],
                    num=self.source_config['results_per_query'],
                    dateRestrict=date_restrict,
                    sort='date:d'  # Sort by date descending
                ).execute()
                
                # Process results
                if 'items' in result:
                    for item in result['items']:
                        article_data = self._extract_article_data(item)
                        all_results.append(article_data)
                
            except HttpError as e:
                self.logger.error(f"Google API error for query '{query}': {e}")
                continue
            except Exception as e:
                self.logger.error(f"Unexpected error for query '{query}': {e}")
                continue
        
        # Enhance with vendor-specific searches
        for vendor in self.vendors[:5]:  # Top 5 vendors
            for term in ['pricing announcement', 'price increase']:
                try:
                    query = f"{vendor} {term}"
                    result = service.cse().list(
                        q=query,
                        cx=creds['cse_id'],
                        num=5,
                        dateRestrict='d30',
                        sort='date:d'
                    ).execute()
                    
                    if 'items' in result:
                        for item in result['items']:
                            article_data = self._extract_article_data(item)
                            # Avoid duplicates
                            if article_data['url'] not in [a['url'] for a in all_results]:
                                all_results.append(article_data)
                
                except Exception as e:
                    self.logger.debug(f"Error in vendor search for {vendor}: {e}")
                    continue
        
        # Apply relevance filtering
        filtered_results = self._filter_results(all_results)
        
        return filtered_results
    
    def _extract_article_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant data from a Google search result"""
        # Parse domain from URL
        parsed_url = urlparse(item['link'])
        domain = parsed_url.netloc.replace('www.', '')
        
        # Try to extract date from various sources
        published_date = None
        
        # Check pagemap for date
        if 'pagemap' in item:
            if 'metatags' in item['pagemap'] and item['pagemap']['metatags']:
                metatag = item['pagemap']['metatags'][0]
                for date_field in ['article:published_time', 'publishdate', 'date']:
                    if date_field in metatag:
                        try:
                            published_date = datetime.fromisoformat(
                                metatag[date_field].replace('Z', '+00:00')
                            )
                            break
                        except:
                            pass
            
            # Check for NewsArticle schema
            if not published_date and 'newsarticle' in item['pagemap']:
                article = item['pagemap']['newsarticle'][0]
                if 'datepublished' in article:
                    try:
                        published_date = datetime.fromisoformat(
                            article['datepublished'].replace('Z', '+00:00')
                        )
                    except:
                        pass
        
        # Default to now if no date found
        if not published_date:
            published_date = datetime.now()
        
        # Extract thumbnail
        thumbnail = None
        if 'pagemap' in item and 'cse_thumbnail' in item['pagemap']:
            thumbnail = item['pagemap']['cse_thumbnail'][0]['src']
        elif 'pagemap' in item and 'metatags' in item['pagemap']:
            metatag = item['pagemap']['metatags'][0]
            thumbnail = metatag.get('og:image') or metatag.get('twitter:image')
        
        return {
            'id': item.get('cacheId', item['link']),
            'title': item['title'],
            'content': item.get('snippet', ''),
            'url': item['link'],
            'domain': domain,
            'published_date': published_date,
            'thumbnail': thumbnail,
            'mime_type': item.get('mime', 'text/html')
        }
    
    def _is_relevant_content(self, item: Dict[str, Any]) -> bool:
        """Check if content is relevant based on domain and keywords"""
        # Check domain trustworthiness
        domain = item.get('domain', '')
        domain_trusted = any(trusted in domain for trusted in self.trusted_domains)
        
        # Combine title and content for keyword checking
        text = f"{item.get('title', '')} {item.get('content', '')}".lower()
        
        # Check for exclusion keywords
        if any(exclude in text for exclude in self.exclude_keywords):
            self.logger.debug(f"Excluding '{item.get('title', '')}' - contains excluded keywords")
            return False
        
        # Check for pricing keywords
        has_pricing_keywords = any(kw in text for kw in self.pricing_keywords)
        
        # Check for vendor mentions
        vendor_mentions = extract_vendor_mentions(text, self.vendors)
        has_vendor = len(vendor_mentions) > 0
        
        # Calculate relevance score
        relevance_score = calculate_relevance_score(text, self.keywords, self.vendors)
        
        # Content is relevant if:
        # 1. From trusted domain AND has pricing keywords OR vendor mentions
        # 2. Has high relevance score regardless of domain
        # 3. Has both pricing keywords AND vendor mentions
        is_relevant = (
            (domain_trusted and (has_pricing_keywords or has_vendor)) or
            relevance_score > 5.0 or
            (has_pricing_keywords and has_vendor)
        )
        
        if not is_relevant:
            self.logger.debug(f"Filtering out '{item.get('title', '')}' - low relevance")
        
        return is_relevant
    
    def _filter_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter results based on relevance and deduplication"""
        # First, apply relevance filtering
        filtered = [item for item in results if self._is_relevant_content(item)]
        
        # Then, deduplicate by URL
        seen_urls = set()
        deduplicated = []
        
        for item in filtered:
            url = item.get('url', '')
            if url not in seen_urls:
                seen_urls.add(url)
                deduplicated.append(item)
        
        self.logger.info(f"Google filtering: {len(results)} → {len(filtered)} → {len(deduplicated)} items")
        
        return deduplicated
