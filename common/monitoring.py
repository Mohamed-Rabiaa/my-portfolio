"""
Performance monitoring and metrics collection utilities.

This module provides comprehensive monitoring capabilities for the portfolio
application, including performance metrics, error tracking, and system health
monitoring.

Features:
- Request/response time tracking
- Database query monitoring
- Error rate tracking
- System resource monitoring
- Custom metrics collection
- Performance alerts and notifications
"""

import time
import logging
import functools
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.utils import timezone
from django.http import HttpRequest, HttpResponse
import psutil
import threading
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Central metrics collection and storage system.
    
    Collects, aggregates, and stores various performance metrics
    for analysis and monitoring purposes.
    """
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(lambda: deque(maxlen=1000))
        self._lock = threading.Lock()
    
    def increment_counter(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """
        Increment a counter metric.
        
        Args:
            name: Counter name
            value: Value to increment by
            tags: Optional tags for categorization
        """
        with self._lock:
            key = self._build_key(name, tags)
            self.counters[key] += value
            logger.debug(f"Counter {key} incremented by {value}")
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """
        Set a gauge metric value.
        
        Args:
            name: Gauge name
            value: Current value
            tags: Optional tags for categorization
        """
        with self._lock:
            key = self._build_key(name, tags)
            self.gauges[key] = value
            logger.debug(f"Gauge {key} set to {value}")
    
    def record_histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """
        Record a value in a histogram metric.
        
        Args:
            name: Histogram name
            value: Value to record
            tags: Optional tags for categorization
        """
        with self._lock:
            key = self._build_key(name, tags)
            self.histograms[key].append({
                'value': value,
                'timestamp': timezone.now()
            })
            logger.debug(f"Histogram {key} recorded value {value}")
    
    def _build_key(self, name: str, tags: Optional[Dict[str, str]] = None) -> str:
        """Build a metric key with optional tags."""
        if not tags:
            return name
        
        tag_str = ','.join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}[{tag_str}]"
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all collected metrics.
        
        Returns:
            Dict containing metrics summary
        """
        with self._lock:
            return {
                'counters': dict(self.counters),
                'gauges': dict(self.gauges),
                'histograms': {
                    name: {
                        'count': len(values),
                        'latest': values[-1] if values else None,
                        'avg': sum(v['value'] for v in values) / len(values) if values else 0
                    }
                    for name, values in self.histograms.items()
                }
            }


# Global metrics collector instance
metrics = MetricsCollector()


class PerformanceMonitor:
    """
    Performance monitoring decorator and context manager.
    
    Tracks execution time, database queries, and other performance
    metrics for functions and code blocks.
    """
    
    def __init__(self, name: str, tags: Optional[Dict[str, str]] = None):
        self.name = name
        self.tags = tags or {}
        self.start_time = None
        self.start_queries = None
    
    def __enter__(self):
        """Start performance monitoring."""
        self.start_time = time.time()
        self.start_queries = len(connection.queries)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End performance monitoring and record metrics."""
        if self.start_time:
            duration = time.time() - self.start_time
            query_count = len(connection.queries) - self.start_queries
            
            # Record metrics
            metrics.record_histogram(f"{self.name}.duration", duration, self.tags)
            metrics.record_histogram(f"{self.name}.queries", query_count, self.tags)
            
            if exc_type:
                metrics.increment_counter(f"{self.name}.errors", tags=self.tags)
            else:
                metrics.increment_counter(f"{self.name}.success", tags=self.tags)
            
            logger.info(f"Performance: {self.name} took {duration:.3f}s with {query_count} queries")


def monitor_performance(name: str, tags: Optional[Dict[str, str]] = None):
    """
    Decorator for monitoring function performance.
    
    Args:
        name: Metric name
        tags: Optional tags for categorization
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with PerformanceMonitor(name or func.__name__, tags):
                return func(*args, **kwargs)
        return wrapper
    return decorator


class SystemMonitor:
    """
    System resource monitoring utility.
    
    Monitors CPU, memory, disk usage, and other system metrics
    to ensure optimal application performance.
    """
    
    @staticmethod
    def get_system_metrics() -> Dict[str, float]:
        """
        Get current system resource metrics.
        
        Returns:
            Dict containing system metrics
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_mb': memory.available / (1024 * 1024),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024 * 1024 * 1024)
            }
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {}
    
    @staticmethod
    def record_system_metrics():
        """Record current system metrics."""
        system_metrics = SystemMonitor.get_system_metrics()
        
        for metric_name, value in system_metrics.items():
            metrics.set_gauge(f"system.{metric_name}", value)


class DatabaseMonitor:
    """
    Database performance monitoring utility.
    
    Tracks database connection pool status, query performance,
    and connection health.
    """
    
    @staticmethod
    def get_db_metrics() -> Dict[str, Any]:
        """
        Get database performance metrics.
        
        Returns:
            Dict containing database metrics
        """
        try:
            query_count = len(connection.queries)
            
            # Calculate query time if queries exist
            total_time = 0
            if connection.queries:
                total_time = sum(float(q['time']) for q in connection.queries)
            
            return {
                'query_count': query_count,
                'total_query_time': total_time,
                'avg_query_time': total_time / query_count if query_count > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error collecting database metrics: {e}")
            return {}
    
    @staticmethod
    def record_db_metrics():
        """Record current database metrics."""
        db_metrics = DatabaseMonitor.get_db_metrics()
        
        for metric_name, value in db_metrics.items():
            metrics.set_gauge(f"database.{metric_name}", value)


class PerformanceMiddleware:
    """
    Django middleware for automatic performance monitoring.
    
    Tracks request/response times, status codes, and other
    HTTP-related metrics for all requests.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process request and track performance metrics."""
        start_time = time.time()
        start_queries = len(connection.queries)
        
        # Process request
        response = self.get_response(request)
        
        # Calculate metrics
        duration = time.time() - start_time
        query_count = len(connection.queries) - start_queries
        
        # Record metrics
        tags = {
            'method': request.method,
            'status': str(response.status_code),
            'endpoint': request.path
        }
        
        metrics.record_histogram('http.request.duration', duration, tags)
        metrics.record_histogram('http.request.queries', query_count, tags)
        metrics.increment_counter('http.requests', tags=tags)
        
        # Log slow requests
        if duration > getattr(settings, 'SLOW_REQUEST_THRESHOLD', 1.0):
            logger.warning(
                f"Slow request: {request.method} {request.path} "
                f"took {duration:.3f}s with {query_count} queries"
            )
        
        return response


class AlertManager:
    """
    Performance alert management system.
    
    Monitors metrics and triggers alerts when thresholds
    are exceeded or anomalies are detected.
    """
    
    def __init__(self):
        self.thresholds = {
            'http.request.duration': 2.0,  # 2 seconds
            'system.cpu_percent': 80.0,    # 80% CPU
            'system.memory_percent': 85.0,  # 85% memory
            'database.avg_query_time': 0.5  # 500ms average query time
        }
        self.alert_cooldown = {}
    
    def check_alerts(self):
        """
        Check all metrics against thresholds and trigger alerts.
        """
        current_time = timezone.now()
        
        for metric_name, threshold in self.thresholds.items():
            # Check if we're in cooldown period
            if metric_name in self.alert_cooldown:
                if current_time < self.alert_cooldown[metric_name]:
                    continue
            
            # Get current metric value
            current_value = self._get_current_metric_value(metric_name)
            
            if current_value and current_value > threshold:
                self._trigger_alert(metric_name, current_value, threshold)
                # Set cooldown period (5 minutes)
                self.alert_cooldown[metric_name] = current_time + timedelta(minutes=5)
    
    def _get_current_metric_value(self, metric_name: str) -> Optional[float]:
        """Get the current value for a metric."""
        if metric_name in metrics.gauges:
            return metrics.gauges[metric_name]
        
        if metric_name in metrics.histograms:
            values = metrics.histograms[metric_name]
            if values:
                return values[-1]['value']
        
        return None
    
    def _trigger_alert(self, metric_name: str, current_value: float, threshold: float):
        """Trigger an alert for a metric threshold breach."""
        logger.error(
            f"PERFORMANCE ALERT: {metric_name} = {current_value:.3f} "
            f"exceeds threshold of {threshold:.3f}"
        )
        
        # Here you could integrate with external alerting systems
        # like email, Slack, PagerDuty, etc.


# Global alert manager instance
alert_manager = AlertManager()


def get_performance_report() -> Dict[str, Any]:
    """
    Generate a comprehensive performance report.
    
    Returns:
        Dict containing performance metrics and system status
    """
    # Collect current system metrics
    SystemMonitor.record_system_metrics()
    DatabaseMonitor.record_db_metrics()
    
    # Check for alerts
    alert_manager.check_alerts()
    
    return {
        'timestamp': timezone.now().isoformat(),
        'metrics': metrics.get_metrics_summary(),
        'system': SystemMonitor.get_system_metrics(),
        'database': DatabaseMonitor.get_db_metrics()
    }