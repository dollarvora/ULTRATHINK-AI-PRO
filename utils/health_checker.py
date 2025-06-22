"""
Comprehensive Health Check System for ULTRATHINK
Monitors all system components and dependencies
"""

import asyncio
import aiohttp
import os
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    component: str
    status: str  # "healthy", "degraded", "unhealthy"
    message: str
    response_time_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None


class HealthChecker:
    """Comprehensive health monitoring for ULTRATHINK"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.last_check = None
        self.check_interval = timedelta(minutes=5)
        
    async def run_full_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check on all components"""
        start_time = datetime.now()
        
        checks = [
            self._check_system_resources(),
            self._check_api_credentials(),
            self._check_external_services(),
            self._check_file_system(),
            self._check_database_connection(),
            self._check_cache_system()
        ]
        
        results = await asyncio.gather(*checks, return_exceptions=True)
        
        # Process results
        health_results = []
        for result in results:
            if isinstance(result, Exception):
                health_results.append(HealthCheckResult(
                    component="unknown",
                    status="unhealthy",
                    message=f"Health check failed: {str(result)}"
                ))
            elif isinstance(result, list):
                health_results.extend(result)
            else:
                health_results.append(result)
        
        # Calculate overall status
        overall_status = self._calculate_overall_status(health_results)
        
        self.last_check = datetime.now()
        
        return {
            "timestamp": start_time.isoformat(),
            "overall_status": overall_status,
            "duration_ms": (datetime.now() - start_time).total_seconds() * 1000,
            "components": [
                {
                    "component": r.component,
                    "status": r.status,
                    "message": r.message,
                    "response_time_ms": r.response_time_ms,
                    "details": r.details
                }
                for r in health_results
            ],
            "summary": self._generate_summary(health_results)
        }
    
    async def _check_system_resources(self) -> List[HealthCheckResult]:
        """Check system resource usage"""
        results = []
        
        # CPU Check
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_status = "healthy" if cpu_percent < 80 else "degraded" if cpu_percent < 95 else "unhealthy"
        results.append(HealthCheckResult(
            component="cpu",
            status=cpu_status,
            message=f"CPU usage: {cpu_percent:.1f}%",
            details={"cpu_percent": cpu_percent, "cpu_count": psutil.cpu_count()}
        ))
        
        # Memory Check
        memory = psutil.virtual_memory()
        memory_status = "healthy" if memory.percent < 80 else "degraded" if memory.percent < 95 else "unhealthy"
        results.append(HealthCheckResult(
            component="memory",
            status=memory_status,
            message=f"Memory usage: {memory.percent:.1f}%",
            details={
                "percent": memory.percent,
                "available_gb": memory.available / (1024**3),
                "total_gb": memory.total / (1024**3)
            }
        ))
        
        # Disk Check
        disk = psutil.disk_usage('/')
        disk_status = "healthy" if disk.percent < 85 else "degraded" if disk.percent < 95 else "unhealthy"
        results.append(HealthCheckResult(
            component="disk",
            status=disk_status,
            message=f"Disk usage: {disk.percent:.1f}%",
            details={
                "percent": disk.percent,
                "free_gb": disk.free / (1024**3),
                "total_gb": disk.total / (1024**3)
            }
        ))
        
        return results
    
    async def _check_api_credentials(self) -> List[HealthCheckResult]:
        """Check API credentials availability"""
        results = []
        
        credentials = {
            "openai": ["OPENAI_API_KEY"],
            "reddit": ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET"],
            "google": ["GOOGLE_API_KEY", "GOOGLE_CSE_ID"],
            "email": ["SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD"]
        }
        
        for service, env_vars in credentials.items():
            missing = [var for var in env_vars if not os.getenv(var)]
            
            if not missing:
                status = "healthy"
                message = f"{service.upper()} credentials configured"
            else:
                status = "unhealthy"
                message = f"{service.upper()} missing: {', '.join(missing)}"
            
            results.append(HealthCheckResult(
                component=f"credentials_{service}",
                status=status,
                message=message,
                details={"missing_vars": missing}
            ))
        
        return results
    
    async def _check_external_services(self) -> List[HealthCheckResult]:
        """Check external service connectivity"""
        results = []
        
        services = {
            "openai": "https://api.openai.com/v1/models",
            "reddit": "https://www.reddit.com/api/v1/me",
            "google": "https://www.googleapis.com/customsearch/v1"
        }
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            for service, url in services.items():
                start_time = datetime.now()
                try:
                    # Add appropriate headers
                    headers = {}
                    if service == "openai" and os.getenv("OPENAI_API_KEY"):
                        headers["Authorization"] = f"Bearer {os.getenv('OPENAI_API_KEY')}"
                    elif service == "reddit":
                        headers["User-Agent"] = "ULTRATHINK/1.0"
                    
                    async with session.get(url, headers=headers) as response:
                        response_time = (datetime.now() - start_time).total_seconds() * 1000
                        
                        if response.status < 500:  # Consider 4xx as "degraded" not "unhealthy"
                            status = "healthy" if response.status < 400 else "degraded"
                            message = f"{service.upper()} API responding (HTTP {response.status})"
                        else:
                            status = "unhealthy"
                            message = f"{service.upper()} API error (HTTP {response.status})"
                        
                        results.append(HealthCheckResult(
                            component=f"api_{service}",
                            status=status,
                            message=message,
                            response_time_ms=response_time,
                            details={"status_code": response.status}
                        ))
                
                except asyncio.TimeoutError:
                    results.append(HealthCheckResult(
                        component=f"api_{service}",
                        status="unhealthy",
                        message=f"{service.upper()} API timeout",
                        details={"error": "timeout"}
                    ))
                except Exception as e:
                    results.append(HealthCheckResult(
                        component=f"api_{service}",
                        status="unhealthy",
                        message=f"{service.upper()} API error: {str(e)}",
                        details={"error": str(e)}
                    ))
        
        return results
    
    async def _check_file_system(self) -> List[HealthCheckResult]:
        """Check file system components"""
        results = []
        
        # Check required directories
        required_dirs = ["cache", "logs", "output", "config"]
        for dir_name in required_dirs:
            dir_path = Path(dir_name)
            if dir_path.exists() and dir_path.is_dir():
                # Check if writable
                test_file = dir_path / ".health_check"
                try:
                    test_file.write_text("test")
                    test_file.unlink()
                    status = "healthy"
                    message = f"Directory {dir_name} accessible and writable"
                except Exception as e:
                    status = "degraded"
                    message = f"Directory {dir_name} not writable: {e}"
            else:
                status = "unhealthy"
                message = f"Directory {dir_name} missing"
            
            results.append(HealthCheckResult(
                component=f"filesystem_{dir_name}",
                status=status,
                message=message
            ))
        
        # Check employees CSV
        employees_csv = Path(self.config.get('email', {}).get('employee_csv', 'config/employees.csv'))
        if employees_csv.exists():
            try:
                import csv
                with open(employees_csv, 'r') as f:
                    reader = csv.DictReader(f)
                    employee_count = sum(1 for row in reader if row.get('active', '').lower() == 'true')
                
                results.append(HealthCheckResult(
                    component="employees_csv",
                    status="healthy",
                    message=f"Employee CSV loaded with {employee_count} active employees",
                    details={"employee_count": employee_count}
                ))
            except Exception as e:
                results.append(HealthCheckResult(
                    component="employees_csv",
                    status="degraded",
                    message=f"Employee CSV error: {e}"
                ))
        else:
            results.append(HealthCheckResult(
                component="employees_csv",
                status="unhealthy",
                message="Employee CSV file not found"
            ))
        
        return results
    
    async def _check_database_connection(self) -> HealthCheckResult:
        """Check database connectivity if configured"""
        # For SQLite, check if file is accessible
        # For PostgreSQL, attempt connection
        try:
            database_url = os.getenv('DATABASE_URL', 'sqlite:///./app.db')
            
            if database_url.startswith('sqlite'):
                # SQLite check
                db_path = database_url.replace('sqlite:///', '')
                if Path(db_path).parent.exists():
                    status = "healthy"
                    message = "SQLite database path accessible"
                else:
                    status = "unhealthy"
                    message = "SQLite database directory not accessible"
            else:
                # For other databases, this would require actual connection test
                status = "degraded"
                message = "Database connection not tested (requires implementation)"
            
            return HealthCheckResult(
                component="database",
                status=status,
                message=message
            )
        
        except Exception as e:
            return HealthCheckResult(
                component="database",
                status="unhealthy",
                message=f"Database check failed: {e}"
            )
    
    async def _check_cache_system(self) -> HealthCheckResult:
        """Check cache system functionality"""
        try:
            cache_dir = Path("cache")
            if not cache_dir.exists():
                cache_dir.mkdir(exist_ok=True)
            
            # Test cache write/read
            test_file = cache_dir / "health_check.json"
            test_data = {"timestamp": datetime.now().isoformat(), "test": True}
            
            import json
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            
            with open(test_file, 'r') as f:
                loaded_data = json.load(f)
            
            test_file.unlink()  # Clean up
            
            if loaded_data.get("test") == True:
                return HealthCheckResult(
                    component="cache",
                    status="healthy",
                    message="Cache system operational"
                )
            else:
                return HealthCheckResult(
                    component="cache",
                    status="degraded",
                    message="Cache write/read test failed"
                )
        
        except Exception as e:
            return HealthCheckResult(
                component="cache",
                status="unhealthy",
                message=f"Cache system error: {e}"
            )
    
    def _calculate_overall_status(self, results: List[HealthCheckResult]) -> str:
        """Calculate overall system health status"""
        statuses = [r.status for r in results]
        
        if "unhealthy" in statuses:
            return "unhealthy"
        elif "degraded" in statuses:
            return "degraded"
        else:
            return "healthy"
    
    def _generate_summary(self, results: List[HealthCheckResult]) -> Dict[str, Any]:
        """Generate summary statistics"""
        total = len(results)
        healthy = sum(1 for r in results if r.status == "healthy")
        degraded = sum(1 for r in results if r.status == "degraded")
        unhealthy = sum(1 for r in results if r.status == "unhealthy")
        
        return {
            "total_components": total,
            "healthy": healthy,
            "degraded": degraded,
            "unhealthy": unhealthy,
            "health_percentage": (healthy / total * 100) if total > 0 else 0
        }