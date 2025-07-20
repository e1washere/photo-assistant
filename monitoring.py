"""
Performance Monitoring for Photo Assistant

Collects metrics, performance data, and system health information.
"""

import time
import psutil
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    timestamp: float
    processing_time: float
    memory_usage: float
    cpu_usage: float
    api_calls: int
    success_rate: float
    error_count: int


class PerformanceMonitor:
    """Monitor and collect performance metrics."""
    
    def __init__(self, log_file: str = "performance.log"):
        """Initialize performance monitor."""
        self.log_file = log_file
        self.metrics_history = []
        self.start_time = time.time()
        self.api_calls = 0
        self.successful_calls = 0
        self.error_calls = 0
        
        # Setup logging
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def start_operation(self, operation_name: str) -> float:
        """Start timing an operation."""
        start_time = time.time()
        self.logger.info(f"Starting operation: {operation_name}")
        return start_time
    
    def end_operation(self, operation_name: str, start_time: float, success: bool = True):
        """End timing an operation and record metrics."""
        end_time = time.time()
        processing_time = end_time - start_time
        
        self.api_calls += 1
        if success:
            self.successful_calls += 1
        else:
            self.error_calls += 1
        
        # Collect system metrics
        memory_usage = psutil.virtual_memory().percent
        cpu_usage = psutil.cpu_percent(interval=0.1)
        
        # Calculate success rate
        success_rate = (self.successful_calls / self.api_calls) * 100 if self.api_calls > 0 else 0
        
        # Create metrics object
        metrics = PerformanceMetrics(
            timestamp=end_time,
            processing_time=processing_time,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            api_calls=self.api_calls,
            success_rate=success_rate,
            error_count=self.error_calls
        )
        
        # Store metrics
        self.metrics_history.append(metrics)
        
        # Log operation
        status = "SUCCESS" if success else "ERROR"
        self.logger.info(
            f"Operation {operation_name} completed: {status} "
            f"(Time: {processing_time:.2f}s, Memory: {memory_usage:.1f}%, CPU: {cpu_usage:.1f}%)"
        )
        
        return metrics
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get current system health status."""
        try:
            # System metrics
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            health_status = {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'cpu_usage': cpu_percent,
                    'memory_usage': memory.percent,
                    'memory_available': memory.available / 1024 / 1024 / 1024,  # GB
                    'disk_usage': disk.percent,
                    'disk_free': disk.free / 1024 / 1024 / 1024  # GB
                },
                'application': {
                    'process_memory_mb': round(process_memory, 2),
                    'uptime_seconds': time.time() - self.start_time,
                    'api_calls_total': self.api_calls,
                    'success_rate': round((self.successful_calls / self.api_calls) * 100, 2) if self.api_calls > 0 else 0,
                    'error_rate': round((self.error_calls / self.api_calls) * 100, 2) if self.api_calls > 0 else 0
                },
                'status': 'healthy' if memory.percent < 90 and cpu_percent < 90 else 'warning'
            }
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Error getting system health: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e)
            }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics."""
        if not self.metrics_history:
            return {'message': 'No metrics available'}
        
        processing_times = [m.processing_time for m in self.metrics_history]
        memory_usage = [m.memory_usage for m in self.metrics_history]
        cpu_usage = [m.cpu_usage for m in self.metrics_history]
        
        summary = {
            'total_operations': len(self.metrics_history),
            'processing_time': {
                'average': round(sum(processing_times) / len(processing_times), 2),
                'min': round(min(processing_times), 2),
                'max': round(max(processing_times), 2),
                'median': round(sorted(processing_times)[len(processing_times)//2], 2)
            },
            'system_usage': {
                'memory_average': round(sum(memory_usage) / len(memory_usage), 1),
                'cpu_average': round(sum(cpu_usage) / len(cpu_usage), 1)
            },
            'success_rate': round((self.successful_calls / self.api_calls) * 100, 2) if self.api_calls > 0 else 0,
            'uptime_hours': round((time.time() - self.start_time) / 3600, 2)
        }
        
        return summary
    
    def export_metrics(self, filename: str = "metrics_export.json"):
        """Export metrics to JSON file."""
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'summary': self.get_performance_summary(),
                'system_health': self.get_system_health(),
                'metrics_history': [
                    {
                        'timestamp': m.timestamp,
                        'processing_time': m.processing_time,
                        'memory_usage': m.memory_usage,
                        'cpu_usage': m.cpu_usage,
                        'api_calls': m.api_calls,
                        'success_rate': m.success_rate,
                        'error_count': m.error_count
                    }
                    for m in self.metrics_history
                ]
            }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self.logger.info(f"Metrics exported to {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting metrics: {e}")
            return False
    
    def cleanup_old_metrics(self, max_history: int = 1000):
        """Clean up old metrics to prevent memory bloat."""
        if len(self.metrics_history) > max_history:
            self.metrics_history = self.metrics_history[-max_history:]
            self.logger.info(f"Cleaned up metrics history, keeping {max_history} entries")


# Global monitor instance
performance_monitor = PerformanceMonitor()


def monitor_operation(operation_name: str):
    """Decorator to monitor function performance."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = performance_monitor.start_operation(operation_name)
            try:
                result = func(*args, **kwargs)
                performance_monitor.end_operation(operation_name, start_time, success=True)
                return result
            except Exception as e:
                performance_monitor.end_operation(operation_name, start_time, success=False)
                raise e
        return wrapper
    return decorator


def get_health_endpoint():
    """Get health check data for API endpoints."""
    return performance_monitor.get_system_health()


def get_metrics_endpoint():
    """Get performance metrics for API endpoints."""
    return performance_monitor.get_performance_summary() 