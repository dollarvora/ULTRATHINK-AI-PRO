"""
Performance Monitoring System for ULTRATHINK
Tracks execution times, API calls, and system metrics
"""

import time
import psutil
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from functools import wraps
from collections import defaultdict
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitors system performance and resource usage"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.active_timers = {}
        self.api_call_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        
    def start_timer(self, operation: str) -> None:
        """Start timing an operation"""
        self.active_timers[operation] = time.time()
        logger.debug(f"Started timer for: {operation}")
    
    def end_timer(self, operation: str) -> float:
        """End timing and record the duration"""
        if operation not in self.active_timers:
            logger.warning(f"No active timer for: {operation}")
            return 0.0
        
        start_time = self.active_timers.pop(operation)
        duration = time.time() - start_time
        
        self.metrics[operation].append({
            'timestamp': datetime.now().isoformat(),
            'duration': duration,
            'memory_mb': self._get_memory_usage(),
            'cpu_percent': psutil.cpu_percent(interval=0.1)
        })
        
        logger.info(f"{operation} completed in {duration:.2f}s")
        return duration
    
    def record_api_call(self, api_name: str, success: bool = True) -> None:
        """Record an API call"""
        self.api_call_counts[api_name] += 1
        if not success:
            self.error_counts[api_name] += 1
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of performance metrics"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'system_metrics': {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'memory_available_gb': psutil.virtual_memory().available / (1024**3)
            },
            'operation_metrics': {},
            'api_metrics': {
                'total_calls': sum(self.api_call_counts.values()),
                'by_api': dict(self.api_call_counts),
                'error_counts': dict(self.error_counts),
                'error_rate': self._calculate_error_rate()
            }
        }
        
        # Calculate operation statistics
        for operation, metrics in self.metrics.items():
            if metrics:
                durations = [m['duration'] for m in metrics]
                summary['operation_metrics'][operation] = {
                    'count': len(metrics),
                    'total_time': sum(durations),
                    'avg_time': sum(durations) / len(durations),
                    'min_time': min(durations),
                    'max_time': max(durations),
                    'last_run': metrics[-1]['timestamp']
                }
        
        return summary
    
    def _calculate_error_rate(self) -> float:
        """Calculate overall API error rate"""
        total_calls = sum(self.api_call_counts.values())
        total_errors = sum(self.error_counts.values())
        
        if total_calls == 0:
            return 0.0
        
        return (total_errors / total_calls) * 100
    
    def save_metrics(self, filepath: Path) -> None:
        """Save metrics to file"""
        summary = self.get_performance_summary()
        
        # Add historical data
        summary['history'] = {
            'operations': dict(self.metrics),
            'api_calls': dict(self.api_call_counts),
            'errors': dict(self.error_counts)
        }
        
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Performance metrics saved to {filepath}")
    
    def clear_metrics(self) -> None:
        """Clear all metrics"""
        self.metrics.clear()
        self.active_timers.clear()
        self.api_call_counts.clear()
        self.error_counts.clear()
        logger.info("Performance metrics cleared")


def monitor_performance(operation_name: str = None):
    """Decorator to monitor function performance"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use function name if operation_name not provided
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            # Get or create monitor instance
            if not hasattr(wrapper, '_monitor'):
                wrapper._monitor = PerformanceMonitor()
            
            monitor = wrapper._monitor
            monitor.start_timer(op_name)
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                monitor.record_api_call(op_name, success=False)
                raise
            finally:
                monitor.end_timer(op_name)
        
        # Attach monitor to wrapper for external access
        wrapper.get_monitor = lambda: getattr(wrapper, '_monitor', None)
        return wrapper
    
    return decorator


class PerformanceContext:
    """Context manager for performance monitoring"""
    
    def __init__(self, operation: str, monitor: PerformanceMonitor = None):
        self.operation = operation
        self.monitor = monitor or PerformanceMonitor()
    
    def __enter__(self):
        self.monitor.start_timer(self.operation)
        return self.monitor
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.monitor.end_timer(self.operation)
        if exc_type is not None:
            self.monitor.record_api_call(self.operation, success=False)