"""
Advanced Caching System for ULTRATHINK
Reduces API calls and improves performance
"""

import json
import hashlib
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching for API responses and processed data"""
    
    def __init__(self, cache_dir: str = "cache", default_ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.default_ttl = timedelta(hours=default_ttl_hours)
        
        # Create subdirectories for different cache types
        self.api_cache_dir = self.cache_dir / "api"
        self.processed_cache_dir = self.cache_dir / "processed"
        self.summary_cache_dir = self.cache_dir / "summaries"
        
        for dir in [self.api_cache_dir, self.processed_cache_dir, self.summary_cache_dir]:
            dir.mkdir(exist_ok=True)
    
    def _generate_cache_key(self, identifier: str, params: Dict[str, Any] = None) -> str:
        """Generate a unique cache key based on identifier and parameters"""
        cache_string = identifier
        if params:
            # Sort params for consistent hashing
            sorted_params = json.dumps(params, sort_keys=True)
            cache_string += sorted_params
        
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get(self, cache_type: str, identifier: str, params: Dict[str, Any] = None) -> Optional[Any]:
        """Retrieve cached data if valid"""
        cache_key = self._generate_cache_key(identifier, params)
        cache_file = self._get_cache_path(cache_type) / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache is expired
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cached_time > self.default_ttl:
                logger.debug(f"Cache expired for {identifier}")
                cache_file.unlink()  # Delete expired cache
                return None
            
            logger.debug(f"Cache hit for {identifier}")
            return cache_data['data']
            
        except Exception as e:
            logger.error(f"Error reading cache for {identifier}: {e}")
            return None
    
    def set(self, cache_type: str, identifier: str, data: Any, params: Dict[str, Any] = None) -> None:
        """Cache data with timestamp"""
        cache_key = self._generate_cache_key(identifier, params)
        cache_file = self._get_cache_path(cache_type) / f"{cache_key}.json"
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'identifier': identifier,
            'params': params,
            'data': data
        }
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            logger.debug(f"Cached data for {identifier}")
        except Exception as e:
            logger.error(f"Error caching data for {identifier}: {e}")
    
    def _get_cache_path(self, cache_type: str) -> Path:
        """Get the appropriate cache directory for the cache type"""
        paths = {
            'api': self.api_cache_dir,
            'processed': self.processed_cache_dir,
            'summary': self.summary_cache_dir
        }
        return paths.get(cache_type, self.cache_dir)
    
    def clear_expired(self) -> int:
        """Clear all expired cache files"""
        cleared = 0
        for cache_dir in [self.api_cache_dir, self.processed_cache_dir, self.summary_cache_dir]:
            for cache_file in cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r') as f:
                        cache_data = json.load(f)
                    
                    cached_time = datetime.fromisoformat(cache_data['timestamp'])
                    if datetime.now() - cached_time > self.default_ttl:
                        cache_file.unlink()
                        cleared += 1
                except Exception:
                    # If we can't read the file, delete it
                    cache_file.unlink()
                    cleared += 1
        
        logger.info(f"Cleared {cleared} expired cache files")
        return cleared
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            'total_files': 0,
            'total_size_mb': 0,
            'by_type': {}
        }
        
        for cache_type, cache_dir in [
            ('api', self.api_cache_dir),
            ('processed', self.processed_cache_dir),
            ('summary', self.summary_cache_dir)
        ]:
            files = list(cache_dir.glob("*.json"))
            size = sum(f.stat().st_size for f in files) / (1024 * 1024)  # MB
            
            stats['by_type'][cache_type] = {
                'files': len(files),
                'size_mb': round(size, 2)
            }
            stats['total_files'] += len(files)
            stats['total_size_mb'] += size
        
        stats['total_size_mb'] = round(stats['total_size_mb'], 2)
        return stats