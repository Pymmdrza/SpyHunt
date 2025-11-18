"""
Main SpyHunt engine for orchestrating reconnaissance operations.
Provides high-level interface for scanning and analysis with advanced performance optimization.
"""

import asyncio
import time
from typing import Dict, List, Any, Optional, Callable, Union, Type
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from .config import Config, get_config
from .logger import get_logger, SpyHuntLogger
from .exceptions import SpyHuntException, ErrorCode, ValidationError


@dataclass
class ScanResult:
    """Container for scan results."""
    module_name: str
    target: str
    status: str
    data: Dict[str, Any]
    execution_time: float
    timestamp: float
    errors: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'module': self.module_name,
            'target': self.target,
            'status': self.status,
            'data': self.data,
            'execution_time': self.execution_time,
            'timestamp': self.timestamp,
            'errors': self.errors
        }


@dataclass
class ScanJob:
    """Container for scan job configuration."""
    module_name: str
    target: str
    parameters: Dict[str, Any]
    priority: int = 0
    
    def __lt__(self, other):
        """Allow priority queue sorting."""
        return self.priority < other.priority


class ModuleRegistry:
    """Registry for scanning modules."""
    
    def __init__(self):
        self._modules: Dict[str, Type] = {}
        self._instances: Dict[str, Any] = {}
        self.logger = get_logger("spyhunt.registry")
    
    def register_module(self, name: str, module_class: Type) -> None:
        """Register a scanning module."""
        self._modules[name] = module_class
        self.logger.info(f"Registered module: {name}")
    
    def get_module(self, name: str) -> Any:
        """Get module instance."""
        if name not in self._modules:
            raise ValidationError(f"Module '{name}' not found", field_name="module_name")
        
        if name not in self._instances:
            self._instances[name] = self._modules[name]()
        
        return self._instances[name]
    
    def list_modules(self) -> List[str]:
        """List available modules."""
        return list(self._modules.keys())
    
    def is_registered(self, name: str) -> bool:
        """Check if module is registered."""
        return name in self._modules


class SpyHuntEngine:
    """
    Main SpyHunt reconnaissance engine.
    
    Orchestrates scanning operations with advanced performance optimization,
    resource management, and error handling.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize SpyHunt engine.
        
        Args:
            config: Configuration instance (uses global config if None)
        """
        self.config = config or get_config()
        self.logger = get_logger("spyhunt.engine")
        self.registry = ModuleRegistry()
        
        # Performance tracking
        self.start_time = time.time()
        self.operation_count = 0
        self.error_count = 0
        self.results: List[ScanResult] = []
        
        # Resource management
        self._executor: Optional[ThreadPoolExecutor] = None
        self._is_running = False
        
        self.logger.info("SpyHunt engine initialized", extra_fields={
            'version': '4.0.0',
            'config_loaded': True
        })
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
    
    def start(self) -> None:
        """Start the engine."""
        if self._is_running:
            self.logger.warning("Engine is already running")
            return
        
        max_workers = self.config.get('scanning.max_threads', 25)
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._is_running = True
        
        self.logger.info("Engine started", extra_fields={
            'max_workers': max_workers
        })
    
    def stop(self) -> None:
        """Stop the engine."""
        if not self._is_running:
            return
        
        if self._executor:
            self._executor.shutdown(wait=True)
            self._executor = None
        
        self._is_running = False
        
        runtime = time.time() - self.start_time
        self.logger.info("Engine stopped", extra_fields={
            'runtime_seconds': runtime,
            'operations_completed': self.operation_count,
            'errors_encountered': self.error_count,
            'results_count': len(self.results)
        })
    
    def register_module(self, name: str, module_class: Type) -> None:
        """Register a scanning module."""
        self.registry.register_module(name, module_class)
    
    def scan_single(
        self,
        module_name: str,
        target: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ScanResult:
        """
        Execute a single scan operation.
        
        Args:
            module_name: Name of the scanning module
            target: Target to scan
            parameters: Additional parameters for the scan
            
        Returns:
            ScanResult containing the scan results
        """
        start_time = time.time()
        parameters = parameters or {}
        
        self.logger.info(f"Starting scan: {module_name} -> {target}", extra_fields={
            'module': module_name,
            'target': target,
            'parameters': parameters
        })
        
        try:
            # Get module instance
            module = self.registry.get_module(module_name)
            
            # Execute scan
            if hasattr(module, 'scan_async') and asyncio.iscoroutinefunction(module.scan_async):
                # Async module
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result_data = loop.run_until_complete(module.scan_async(target, **parameters))
                finally:
                    loop.close()
            elif hasattr(module, 'scan'):
                # Sync module
                result_data = module.scan(target, **parameters)
            else:
                raise ValidationError(f"Module '{module_name}' missing scan method")
            
            execution_time = time.time() - start_time
            
            result = ScanResult(
                module_name=module_name,
                target=target,
                status='success',
                data=result_data or {},
                execution_time=execution_time,
                timestamp=time.time(),
                errors=[]
            )
            
            self.operation_count += 1
            self.results.append(result)
            
            self.logger.performance.log_performance(
                f"scan_{module_name}",
                execution_time,
                target=target,
                status='success'
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.error_count += 1
            
            error_msg = str(e)
            self.logger.error(f"Scan failed: {module_name} -> {target}", extra_fields={
                'module': module_name,
                'target': target,
                'error': error_msg,
                'execution_time': execution_time
            })
            
            result = ScanResult(
                module_name=module_name,
                target=target,
                status='error',
                data={},
                execution_time=execution_time,
                timestamp=time.time(),
                errors=[error_msg]
            )
            
            self.results.append(result)
            return result
    
    def scan_batch(
        self,
        jobs: List[ScanJob],
        max_concurrent: Optional[int] = None
    ) -> List[ScanResult]:
        """
        Execute multiple scan operations concurrently.
        
        Args:
            jobs: List of scan jobs to execute
            max_concurrent: Maximum concurrent operations (uses config default if None)
            
        Returns:
            List of ScanResult objects
        """
        if not jobs:
            return []
        
        if not self._is_running:
            self.start()
        
        if not self._executor:
            raise SpyHuntException("Executor not available", ErrorCode.MODULE_ERROR)
        
        max_concurrent = max_concurrent or self.config.get('network.max_concurrent_requests', 50)
        
        self.logger.info(f"Starting batch scan", extra_fields={
            'job_count': len(jobs),
            'max_concurrent': max_concurrent
        })
        
        batch_start_time = time.time()
        results = []
        
        # Sort jobs by priority
        sorted_jobs = sorted(jobs, reverse=True)  # Higher priority first
        
        # Submit jobs to executor
        futures = []
        for job in sorted_jobs[:max_concurrent]:  # Limit initial submissions
            future = self._executor.submit(
                self.scan_single,
                job.module_name,
                job.target,
                job.parameters
            )
            futures.append((future, job))
        
        # Process completed jobs and submit new ones
        remaining_jobs = sorted_jobs[max_concurrent:]
        future_list = [f[0] for f in futures]
        
        for future in as_completed(future_list):
            try:
                result = future.result()
                results.append(result)
                
                # Submit next job if available
                if remaining_jobs:
                    next_job = remaining_jobs.pop(0)
                    new_future = self._executor.submit(
                        self.scan_single,
                        next_job.module_name,
                        next_job.target,
                        next_job.parameters
                    )
                    futures.append((new_future, next_job))
                
            except Exception as e:
                self.logger.error(f"Batch job failed: {str(e)}")
                self.error_count += 1
        
        batch_time = time.time() - batch_start_time
        
        self.logger.info("Batch scan completed", extra_fields={
            'total_jobs': len(jobs),
            'successful_jobs': len([r for r in results if r.status == 'success']),
            'failed_jobs': len([r for r in results if r.status == 'error']),
            'batch_time': batch_time
        })
        
        return results
    
    def scan_targets(
        self,
        module_name: str,
        targets: List[str],
        parameters: Optional[Dict[str, Any]] = None,
        max_concurrent: Optional[int] = None
    ) -> List[ScanResult]:
        """
        Scan multiple targets with the same module.
        
        Args:
            module_name: Name of the scanning module
            targets: List of targets to scan
            parameters: Parameters for all scans
            max_concurrent: Maximum concurrent scans
            
        Returns:
            List of ScanResult objects
        """
        jobs = [
            ScanJob(module_name=module_name, target=target, parameters=parameters or {})
            for target in targets
        ]
        
        return self.scan_batch(jobs, max_concurrent)
    
    def get_results(
        self,
        module_name: Optional[str] = None,
        status: Optional[str] = None,
        target: Optional[str] = None
    ) -> List[ScanResult]:
        """
        Get filtered scan results.
        
        Args:
            module_name: Filter by module name
            status: Filter by status ('success', 'error')
            target: Filter by target
            
        Returns:
            List of filtered ScanResult objects
        """
        results = self.results
        
        if module_name:
            results = [r for r in results if r.module_name == module_name]
        
        if status:
            results = [r for r in results if r.status == status]
        
        if target:
            results = [r for r in results if r.target == target]
        
        return results
    
    def clear_results(self) -> None:
        """Clear all stored results."""
        self.results.clear()
        self.logger.info("Results cleared")
    
    def export_results(
        self,
        file_path: str,
        format: str = 'json',
        filter_func: Optional[Callable[[ScanResult], bool]] = None
    ) -> None:
        """
        Export results to file.
        
        Args:
            file_path: Path to output file
            format: Export format ('json', 'csv', 'yaml')
            filter_func: Optional filter function
        """
        import json
        import csv
        
        results = self.results
        if filter_func:
            results = [r for r in results if filter_func(r)]
        
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == 'json':
            with open(path, 'w', encoding='utf-8') as f:
                json.dump([r.to_dict() for r in results], f, indent=2, ensure_ascii=False)
        
        elif format.lower() == 'csv':
            with open(path, 'w', newline='', encoding='utf-8') as f:
                if results:
                    writer = csv.DictWriter(f, fieldnames=results[0].to_dict().keys())
                    writer.writeheader()
                    for result in results:
                        writer.writerow(result.to_dict())
        
        elif format.lower() == 'yaml':
            import yaml
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump([r.to_dict() for r in results], f, default_flow_style=False)
        
        else:
            raise ValidationError(f"Unsupported export format: {format}")
        
        self.logger.info(f"Results exported to {file_path}", extra_fields={
            'format': format,
            'result_count': len(results)
        })
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics."""
        runtime = time.time() - self.start_time
        
        successful_results = [r for r in self.results if r.status == 'success']
        failed_results = [r for r in self.results if r.status == 'error']
        
        avg_execution_time = 0
        if successful_results:
            avg_execution_time = sum(r.execution_time for r in successful_results) / len(successful_results)
        
        return {
            'runtime_seconds': runtime,
            'total_operations': self.operation_count,
            'successful_operations': len(successful_results),
            'failed_operations': len(failed_results),
            'error_rate': len(failed_results) / max(1, self.operation_count),
            'average_execution_time': avg_execution_time,
            'operations_per_second': self.operation_count / max(1, runtime),
            'registered_modules': len(self.registry.list_modules()),
            'is_running': self._is_running
        }