"""
Performance Monitoring System for ULTRATHINK-AI-PRO
Enhanced with async capabilities and advanced metrics tracking
Integrated from ultrathink-enhanced's superior monitoring patterns
"""

import time
import psutil
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from functools import wraps
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
import json
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System resource metrics snapshot"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    disk_usage_percent: float
    active_connections: int

@dataclass
class OperationMetrics:
    """Individual operation performance metrics"""
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    data_size: int = 0
    api_calls: int = 0
    
    def complete(self, success: bool = True, error_message: Optional[str] = None, data_size: int = 0, api_calls: int = 0):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = success
        self.error_message = error_message
        self.data_size = data_size
        self.api_calls = api_calls


class PerformanceMonitor:
    """Enhanced performance monitor with async capabilities and comprehensive metrics"""
    
    def __init__(self, name: str = "ULTRATHINK-AI-PRO", debug: bool = False):
        # Existing functionality
        self.metrics = defaultdict(list)
        self.active_timers = {}
        self.api_call_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        
        # Enhanced functionality
        self.name = name
        self.debug = debug
        self.start_time = time.time()
        
        # Enhanced metrics storage
        self.operation_metrics: List[OperationMetrics] = []
        self.system_metrics: deque = deque(maxlen=1000)  # Keep last 1000 measurements
        
        # Performance tracking
        self.peak_memory_mb = 0
        self.peak_cpu_percent = 0
        self.total_api_calls = 0
        self.total_data_processed = 0
        
        # Async monitoring
        self._monitoring_task = None
        self._monitoring_active = False
        
        if debug:
            logger.info(f"📊 Enhanced Performance Monitor initialized for {self.name}")
        
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
    
    # Enhanced async methods
    async def start_monitoring(self, interval: float = 5.0):
        """Start continuous system monitoring"""
        self._monitoring_active = True
        self._monitoring_task = asyncio.create_task(self._monitor_system(interval))
        if self.debug:
            logger.info(f"🎯 System monitoring started (interval: {interval}s)")
    
    async def stop_monitoring(self):
        """Stop system monitoring"""
        self._monitoring_active = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        if self.debug:
            logger.info("⏹️ System monitoring stopped")
    
    async def _monitor_system(self, interval: float):
        """Continuous system monitoring loop"""
        while self._monitoring_active:
            try:
                metrics = self._capture_system_metrics()
                self.system_metrics.append(metrics)
                
                # Update peaks
                self.peak_memory_mb = max(self.peak_memory_mb, metrics.memory_mb)
                self.peak_cpu_percent = max(self.peak_cpu_percent, metrics.cpu_percent)
                
                if self.debug and len(self.system_metrics) % 12 == 0:  # Log every minute at 5s intervals
                    logger.debug(f"💻 System: CPU {metrics.cpu_percent:.1f}%, Memory {metrics.memory_mb:.0f}MB ({metrics.memory_percent:.1f}%)")
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.warning(f"System monitoring error: {e}")
                await asyncio.sleep(interval)
    
    def _capture_system_metrics(self) -> SystemMetrics:
        """Capture current system metrics"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return SystemMetrics(
            timestamp=time.time(),
            cpu_percent=process.cpu_percent(),
            memory_percent=process.memory_percent(),
            memory_mb=memory_info.rss / 1024 / 1024,
            disk_usage_percent=psutil.disk_usage('/').percent,
            active_connections=len(process.connections())
        )
    
    def start_operation(self, operation_name: str) -> OperationMetrics:
        """Start tracking an operation with enhanced metrics"""
        metrics = OperationMetrics(
            operation_name=operation_name,
            start_time=time.time()
        )
        self.operation_metrics.append(metrics)
        
        if self.debug:
            logger.debug(f"⏱️ Started: {operation_name}")
        
        return metrics
    
    def complete_operation(self, metrics: OperationMetrics, success: bool = True, 
                          error_message: Optional[str] = None, data_size: int = 0, api_calls: int = 0):
        """Complete an operation and update enhanced metrics"""
        metrics.complete(success=success, error_message=error_message, data_size=data_size, api_calls=api_calls)
        
        # Update counters
        if api_calls > 0:
            self.total_api_calls += api_calls
        
        if data_size > 0:
            self.total_data_processed += data_size
        
        if self.debug:
            status = "✅" if success else "❌"
            logger.debug(f"{status} Completed: {metrics.operation_name} in {metrics.duration:.2f}s")
            if data_size > 0:
                logger.debug(f"  📊 Data processed: {data_size} items")
            if api_calls > 0:
                logger.debug(f"  🔗 API calls: {api_calls}")
    
    def get_enhanced_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive enhanced performance summary"""
        current_time = time.time()
        total_runtime = current_time - self.start_time
        
        # Enhanced operation statistics
        successful_ops = [op for op in self.operation_metrics if op.success and op.duration is not None]
        failed_ops = [op for op in self.operation_metrics if not op.success]
        
        operation_stats = {}
        for op in successful_ops:
            if op.operation_name not in operation_stats:
                operation_stats[op.operation_name] = {
                    'count': 0,
                    'total_duration': 0,
                    'min_duration': float('inf'),
                    'max_duration': 0,
                    'total_data': 0,
                    'total_api_calls': 0
                }
            
            stats = operation_stats[op.operation_name]
            stats['count'] += 1
            stats['total_duration'] += op.duration
            stats['min_duration'] = min(stats['min_duration'], op.duration)
            stats['max_duration'] = max(stats['max_duration'], op.duration)
            stats['total_data'] += op.data_size
            stats['total_api_calls'] += op.api_calls
        
        # Calculate averages
        for stats in operation_stats.values():
            if stats['count'] > 0:
                stats['avg_duration'] = stats['total_duration'] / stats['count']
            if stats['min_duration'] == float('inf'):
                stats['min_duration'] = 0
        
        # System resource statistics
        system_stats = {}
        if self.system_metrics:
            memory_values = [m.memory_mb for m in self.system_metrics]
            cpu_values = [m.cpu_percent for m in self.system_metrics]
            
            system_stats = {
                'avg_memory_mb': sum(memory_values) / len(memory_values),
                'peak_memory_mb': self.peak_memory_mb,
                'avg_cpu_percent': sum(cpu_values) / len(cpu_values),
                'peak_cpu_percent': self.peak_cpu_percent,
                'monitoring_duration': len(self.system_metrics) * 5.0  # Assuming 5s intervals
            }
        
        return {
            'summary': {
                'monitor_name': self.name,
                'total_runtime': total_runtime,
                'total_operations': len(self.operation_metrics),
                'successful_operations': len(successful_ops),
                'failed_operations': len(failed_ops),
                'success_rate': len(successful_ops) / len(self.operation_metrics) if self.operation_metrics else 0,
                'total_api_calls': self.total_api_calls,
                'total_data_processed': self.total_data_processed
            },
            'operation_stats': operation_stats,
            'system_stats': system_stats,
            'api_call_counts': dict(self.api_call_counts),
            'error_counts': dict(self.error_counts),
            'generated_at': datetime.now().isoformat()
        }
    
    def print_performance_report(self):
        """Print human-readable performance report"""
        summary = self.get_enhanced_performance_summary()
        
        print(f"\n{'='*60}")
        print(f"📊 PERFORMANCE REPORT: {self.name}")
        print(f"{'='*60}")
        
        # Overall summary
        overall = summary['summary']
        print(f"⏱️  Total Runtime: {overall['total_runtime']:.1f}s")
        print(f"✅ Success Rate: {overall['success_rate']*100:.1f}% ({overall['successful_operations']}/{overall['total_operations']})")
        print(f"🔗 Total API Calls: {overall['total_api_calls']}")
        print(f"📊 Data Processed: {overall['total_data_processed']} items")
        
        # Operation breakdown
        if summary['operation_stats']:
            print(f"\n📋 OPERATION BREAKDOWN:")
            for op_name, stats in summary['operation_stats'].items():
                print(f"  {op_name}:")
                print(f"    Count: {stats['count']}")
                print(f"    Avg Duration: {stats['avg_duration']:.2f}s")
                print(f"    Range: {stats['min_duration']:.2f}s - {stats['max_duration']:.2f}s")
                if stats['total_data'] > 0:
                    print(f"    Data: {stats['total_data']} items")
                if stats['total_api_calls'] > 0:
                    print(f"    API Calls: {stats['total_api_calls']}")
        
        # System resources
        if summary['system_stats']:
            sys_stats = summary['system_stats']
            print(f"\n💻 SYSTEM RESOURCES:")
            print(f"  Memory: {sys_stats['avg_memory_mb']:.0f}MB avg, {sys_stats['peak_memory_mb']:.0f}MB peak")
            print(f"  CPU: {sys_stats['avg_cpu_percent']:.1f}% avg, {sys_stats['peak_cpu_percent']:.1f}% peak")
        
        # Errors
        if summary['error_counts']:
            print(f"\n❌ ERROR SUMMARY:")
            for error_type, count in summary['error_counts'].items():
                print(f"  {error_type}: {count}")
        
        print(f"{'='*60}\n")


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

# Global enhanced performance monitor instance
_global_enhanced_monitor = None

def get_global_enhanced_monitor(name: str = "ULTRATHINK-AI-PRO", debug: bool = False) -> PerformanceMonitor:
    """Get or create global enhanced performance monitor"""
    global _global_enhanced_monitor
    if _global_enhanced_monitor is None:
        _global_enhanced_monitor = PerformanceMonitor(name=name, debug=debug)
    return _global_enhanced_monitor

async def start_global_monitoring(interval: float = 5.0):
    """Start global performance monitoring"""
    monitor = get_global_enhanced_monitor()
    await monitor.start_monitoring(interval)

async def stop_global_monitoring():
    """Stop global performance monitoring"""
    global _global_enhanced_monitor
    if _global_enhanced_monitor:
        await _global_enhanced_monitor.stop_monitoring()

def get_global_performance_summary() -> Dict[str, Any]:
    """Get global performance summary"""
    monitor = get_global_enhanced_monitor()
    return monitor.get_enhanced_performance_summary()

def print_global_performance_report():
    """Print global performance report"""
    monitor = get_global_enhanced_monitor()
    monitor.print_performance_report()