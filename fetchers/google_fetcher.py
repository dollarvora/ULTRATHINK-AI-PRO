"""
Google News Fetcher
Fetches pricing-related news from Google using Custom Search API
"""

import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict, Any
from urllib.parse import urlparse

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from fetchers.base_fetcher import BaseFetcher


class GoogleFetcher(BaseFetcher):
    """Fetches news articles from Google Custom Search"""
    
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
        
        return all_results
    
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
