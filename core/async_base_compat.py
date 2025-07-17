"""
Python Version Compatible Async Base Architecture for ULTRATHINK-AI-PRO
Works with Python 3.6+ while maintaining superior async patterns
"""
import asyncio
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import random
import concurrent.futures

logger = logging.getLogger(__name__)

class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class PerformanceMetrics:
    """Performance tracking for async operations"""
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    duration: Optional[float] = None
    
    def complete(self, success: bool = True, error_message: Optional[str] = None):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = success
        self.error_message = error_message

class AsyncRateLimiter:
    """Token bucket rate limiter for API calls - Python 3.6+ compatible"""
    
    def __init__(self, requests_per_second: float = 10.0, burst_limit: int = 50):
        self.requests_per_second = requests_per_second
        self.burst_limit = burst_limit
        self.tokens = burst_limit
        self.last_update = time.time()
        self._lock = None
    
    async def _get_lock(self):
        """Get or create lock (compatible with older Python)"""
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock
    
    async def acquire(self) -> bool:
        """Acquire a token for making a request"""
        lock = await self._get_lock()
        async with lock:
            now = time.time()
            elapsed = now - self.last_update
            
            # Add tokens based on elapsed time
            self.tokens = min(
                self.burst_limit,
                self.tokens + elapsed * self.requests_per_second
            )
            self.last_update = now
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            
            return False
    
    async def wait_for_token(self) -> None:
        """Wait until a token is available"""
        while not await self.acquire():
            await asyncio.sleep(0.1)

class CircuitBreaker:
    """Circuit breaker pattern for API protection - Python 3.6+ compatible"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0, half_open_max_calls: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        self.half_open_calls = 0
        self._lock = None
    
    async def _get_lock(self):
        """Get or create lock (compatible with older Python)"""
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock
    
    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        lock = await self._get_lock()
        async with lock:
            if self.state == CircuitBreakerState.OPEN:
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.half_open_calls = 0
                else:
                    raise Exception("Circuit breaker is OPEN")
            
            if self.state == CircuitBreakerState.HALF_OPEN:
                if self.half_open_calls >= self.half_open_max_calls:
                    raise Exception("Circuit breaker half-open limit exceeded")
                self.half_open_calls += 1
        
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            raise e
    
    async def _on_success(self):
        """Handle successful call"""
        lock = await self._get_lock()
        async with lock:
            self.failure_count = 0
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.CLOSED
    
    async def _on_failure(self):
        """Handle failed call"""
        lock = await self._get_lock()
        async with lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN

class AsyncRetryHandler:
    """Exponential backoff retry handler with jitter"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    async def execute(self, func: Callable, *args, **kwargs):
        """Execute function with exponential backoff retry"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt == self.max_retries:
                    break
                
                # Calculate delay with exponential backoff and jitter
                delay = min(
                    self.base_delay * (2 ** attempt),
                    self.max_delay
                )
                
                # Add jitter (±25% of delay)
                jitter = delay * 0.25 * (2 * random.random() - 1)
                delay += jitter
                
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s")
                await asyncio.sleep(delay)
        
        raise last_exception

class AsyncBaseFetcher(ABC):
    """Abstract base class for async fetchers - Python 3.6+ compatible"""
    
    def __init__(self, name: str, config: Dict[str, Any], debug: bool = False):
        self.name = name
        self.config = config
        self.debug = debug
        
        # Initialize resilience components
        self.rate_limiter = AsyncRateLimiter(
            requests_per_second=config.get('rate_limit', 10.0),
            burst_limit=config.get('burst_limit', 50)
        )
        
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=config.get('failure_threshold', 5),
            recovery_timeout=config.get('recovery_timeout', 60.0)
        )
        
        self.retry_handler = AsyncRetryHandler(
            max_retries=config.get('max_retries', 3),
            base_delay=config.get('retry_base_delay', 1.0)
        )
        
        self.metrics: List[PerformanceMetrics] = []
        
        logger.info(f"✅ {self.name} async fetcher initialized with resilience patterns")
    
    @abstractmethod
    async def fetch_content(self) -> List[Dict[str, Any]]:
        """Abstract method for fetching content"""
        pass
    
    async def protected_fetch(self, fetch_func: Callable, *args, **kwargs) -> Any:
        """Execute fetch function with full protection (rate limiting, circuit breaker, retry)"""
        # Rate limiting
        await self.rate_limiter.wait_for_token()
        
        # Circuit breaker + retry
        return await self.circuit_breaker.call(
            self.retry_handler.execute,
            fetch_func,
            *args,
            **kwargs
        )
    
    def start_metrics(self, operation_name: str) -> PerformanceMetrics:
        """Start tracking metrics for an operation"""
        metrics = PerformanceMetrics(operation_name=operation_name, start_time=time.time())
        self.metrics.append(metrics)
        return metrics

class CompatAsyncPipeline:
    """Orchestrate multiple async fetchers with concurrent execution - Python 3.6+ compatible"""
    
    def __init__(self, fetchers: List[AsyncBaseFetcher], debug: bool = False):
        self.fetchers = fetchers
        self.debug = debug
        self.pipeline_metrics: List[PerformanceMetrics] = []
    
    async def execute_concurrent(self) -> Dict[str, List[Dict[str, Any]]]:
        """Execute all fetchers concurrently - Python 3.6+ compatible"""
        overall_metrics = PerformanceMetrics("pipeline_execution", time.time())
        
        try:
            if self.debug:
                logger.info(f"🚀 Starting concurrent execution of {len(self.fetchers)} fetchers")
            
            # Python 3.6+ compatible concurrent execution
            if hasattr(asyncio, 'create_task') and hasattr(asyncio, 'gather'):
                # Python 3.7+ - optimal approach
                tasks = []
                for fetcher in self.fetchers:
                    task = asyncio.create_task(
                        self._safe_fetch(fetcher)
                    )
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
            else:
                # Python 3.6 compatibility - use ensure_future and manual gathering
                futures = []
                for fetcher in self.fetchers:
                    future = asyncio.ensure_future(self._safe_fetch(fetcher))
                    futures.append(future)
                
                # Wait for all futures to complete
                done, pending = await asyncio.wait(futures, return_when=asyncio.ALL_COMPLETED)
                
                # Collect results
                results = []
                for future in futures:
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        results.append(e)
            
            # Process results
            processed_results = {}
            for fetcher, result in zip(self.fetchers, results):
                if isinstance(result, Exception):
                    logger.error(f"❌ {fetcher.name} failed: {result}")
                    processed_results[fetcher.name] = []
                else:
                    processed_results[fetcher.name] = result
                    if self.debug:
                        logger.info(f"✅ {fetcher.name} completed: {len(result)} items")
            
            overall_metrics.complete(success=True)
            self.pipeline_metrics.append(overall_metrics)
            
            if self.debug:
                logger.info(f"🎯 Pipeline completed in {overall_metrics.duration:.2f}s")
            
            return processed_results
            
        except Exception as e:
            overall_metrics.complete(success=False, error_message=str(e))
            self.pipeline_metrics.append(overall_metrics)
            logger.error(f"❌ Pipeline execution failed: {e}")
            raise
    
    async def _safe_fetch(self, fetcher: AsyncBaseFetcher) -> List[Dict[str, Any]]:
        """Safely execute fetcher with error handling"""
        try:
            return await fetcher.fetch_content()
        except Exception as e:
            logger.error(f"❌ {fetcher.name} fetch failed: {e}")
            return []
    
    async def close_all(self):
        """Close all fetchers"""
        for fetcher in self.fetchers:
            if hasattr(fetcher, 'close'):
                await fetcher.close()

class ThreadPoolAsyncAdapter:
    """Adapter to run sync functions in async context using thread pool"""
    
    def __init__(self, max_workers: int = 4):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
    
    async def run_sync(self, sync_func: Callable, *args, **kwargs):
        """Run synchronous function in thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, sync_func, *args, **kwargs)
    
    def close(self):
        """Close thread pool executor"""
        self.executor.shutdown(wait=True)

# Compatibility functions
def create_task_compat(coro):
    """Create task with Python 3.6+ compatibility"""
    if hasattr(asyncio, 'create_task'):
        return asyncio.create_task(coro)
    else:
        return asyncio.ensure_future(coro)

async def gather_compat(*coros, return_exceptions=False):
    """Gather coroutines with Python 3.6+ compatibility"""
    if hasattr(asyncio, 'gather'):
        return await asyncio.gather(*coros, return_exceptions=return_exceptions)
    else:
        # Manual implementation for older versions
        if return_exceptions:
            results = []
            for coro in coros:
                try:
                    result = await coro
                    results.append(result)
                except Exception as e:
                    results.append(e)
            return results
        else:
            results = []
            for coro in coros:
                result = await coro
                results.append(result)
            return results

# Global thread pool adapter instance
_global_thread_adapter = ThreadPoolAsyncAdapter()

async def run_sync_in_thread(sync_func: Callable, *args, **kwargs):
    """Run synchronous function in thread pool"""
    return await _global_thread_adapter.run_sync(sync_func, *args, **kwargs)

def cleanup_thread_adapter():
    """Cleanup global thread adapter"""
    _global_thread_adapter.close()