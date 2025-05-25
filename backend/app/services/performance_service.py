from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import psutil
import asyncio
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.performance import PerformanceMetric, SystemResource
from app.core.config import settings

class PerformanceService:
    """Service for handling performance monitoring and optimization."""
    
    def __init__(self):
        self.metrics_interval = settings.METRICS_INTERVAL
        self.resource_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 80.0,
            'disk_percent': 80.0,
            'response_time': 1.0  # seconds
        }
    
    async def collect_system_metrics(self) -> Dict[str, Any]:
        """
        Collect current system resource metrics.
        
        Returns:
            Dict containing system metrics
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used": memory.used,
                "memory_total": memory.total,
                "disk_percent": disk.percent,
                "disk_used": disk.used,
                "disk_total": disk.total,
                "timestamp": datetime.utcnow()
            }
            
            # Store metrics in database
            db = next(get_db())
            system_resource = SystemResource(**metrics)
            db.add(system_resource)
            db.commit()
            
            return metrics
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.utcnow()
            }
    
    async def monitor_endpoint_performance(self, endpoint: str, start_time: datetime) -> Dict[str, Any]:
        """
        Monitor endpoint performance metrics.
        
        Args:
            endpoint: API endpoint path
            start_time: Request start time
            
        Returns:
            Dict containing performance metrics
        """
        try:
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds()
            
            metrics = {
                "endpoint": endpoint,
                "response_time": response_time,
                "timestamp": end_time
            }
            
            # Store metrics in database
            db = next(get_db())
            performance_metric = PerformanceMetric(**metrics)
            db.add(performance_metric)
            db.commit()
            
            return metrics
        except Exception as e:
            return {
                "error": str(e),
                "endpoint": endpoint,
                "timestamp": datetime.utcnow()
            }
    
    async def analyze_performance(self, time_range: timedelta = timedelta(hours=1)) -> Dict[str, Any]:
        """
        Analyze system performance over a time range.
        
        Args:
            time_range: Time range to analyze
            
        Returns:
            Dict containing performance analysis
        """
        try:
            db = next(get_db())
            start_time = datetime.utcnow() - time_range
            
            # Get system resource metrics
            resource_query = text("""
                SELECT 
                    AVG(cpu_percent) as avg_cpu,
                    MAX(cpu_percent) as max_cpu,
                    AVG(memory_percent) as avg_memory,
                    MAX(memory_percent) as max_memory,
                    AVG(disk_percent) as avg_disk,
                    MAX(disk_percent) as max_disk
                FROM system_resources
                WHERE timestamp >= :start_time
            """)
            resource_metrics = db.execute(resource_query, {"start_time": start_time}).first()
            
            # Get endpoint performance metrics
            endpoint_query = text("""
                SELECT 
                    endpoint,
                    AVG(response_time) as avg_response_time,
                    MAX(response_time) as max_response_time,
                    COUNT(*) as request_count
                FROM performance_metrics
                WHERE timestamp >= :start_time
                GROUP BY endpoint
            """)
            endpoint_metrics = db.execute(endpoint_query, {"start_time": start_time}).fetchall()
            
            # Check for performance issues
            issues = []
            if resource_metrics.avg_cpu > self.resource_thresholds['cpu_percent']:
                issues.append("High CPU usage detected")
            if resource_metrics.avg_memory > self.resource_thresholds['memory_percent']:
                issues.append("High memory usage detected")
            if resource_metrics.avg_disk > self.resource_thresholds['disk_percent']:
                issues.append("High disk usage detected")
            
            for metric in endpoint_metrics:
                if metric.avg_response_time > self.resource_thresholds['response_time']:
                    issues.append(f"Slow response time for {metric.endpoint}")
            
            return {
                "system_metrics": {
                    "cpu": {
                        "average": float(resource_metrics.avg_cpu),
                        "maximum": float(resource_metrics.max_cpu)
                    },
                    "memory": {
                        "average": float(resource_metrics.avg_memory),
                        "maximum": float(resource_metrics.max_memory)
                    },
                    "disk": {
                        "average": float(resource_metrics.avg_disk),
                        "maximum": float(resource_metrics.max_disk)
                    }
                },
                "endpoint_metrics": [
                    {
                        "endpoint": metric.endpoint,
                        "average_response_time": float(metric.avg_response_time),
                        "maximum_response_time": float(metric.max_response_time),
                        "request_count": metric.request_count
                    }
                    for metric in endpoint_metrics
                ],
                "issues": issues,
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.utcnow()
            }
    
    async def optimize_database(self) -> Dict[str, Any]:
        """
        Perform database optimization tasks.
        
        Returns:
            Dict containing optimization results
        """
        try:
            db = next(get_db())
            
            # Analyze table statistics
            analyze_query = text("ANALYZE")
            db.execute(analyze_query)
            
            # Vacuum tables
            vacuum_query = text("VACUUM ANALYZE")
            db.execute(vacuum_query)
            
            # Get index usage statistics
            index_query = text("""
                SELECT
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch
                FROM pg_stat_user_indexes
                ORDER BY idx_scan DESC
            """)
            index_stats = db.execute(index_query).fetchall()
            
            return {
                "status": "success",
                "index_statistics": [
                    {
                        "schema": stat.schemaname,
                        "table": stat.tablename,
                        "index": stat.indexname,
                        "scans": stat.idx_scan,
                        "tuples_read": stat.idx_tup_read,
                        "tuples_fetched": stat.idx_tup_fetch
                    }
                    for stat in index_stats
                ],
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.utcnow()
            }
    
    async def get_performance_recommendations(self) -> Dict[str, Any]:
        """
        Generate performance optimization recommendations.
        
        Returns:
            Dict containing recommendations
        """
        try:
            # Get recent performance analysis
            analysis = await self.analyze_performance()
            
            recommendations = []
            
            # System resource recommendations
            if analysis["system_metrics"]["cpu"]["average"] > 70:
                recommendations.append({
                    "type": "system",
                    "component": "CPU",
                    "issue": "High CPU usage",
                    "recommendation": "Consider scaling horizontally or optimizing CPU-intensive operations"
                })
            
            if analysis["system_metrics"]["memory"]["average"] > 70:
                recommendations.append({
                    "type": "system",
                    "component": "Memory",
                    "issue": "High memory usage",
                    "recommendation": "Consider increasing memory allocation or implementing memory caching"
                })
            
            # Endpoint performance recommendations
            for metric in analysis["endpoint_metrics"]:
                if metric["average_response_time"] > 0.5:
                    recommendations.append({
                        "type": "endpoint",
                        "component": metric["endpoint"],
                        "issue": "Slow response time",
                        "recommendation": "Consider implementing caching or optimizing database queries"
                    })
            
            return {
                "recommendations": recommendations,
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            return {
                "error": str(e),
                "recommendations": [],
                "timestamp": datetime.utcnow()
            } 