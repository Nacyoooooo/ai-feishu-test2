import time
import functools
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

def performance_monitor(func: Callable) -> Callable:
    """性能监控装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"{func.__name__} 执行时间: {elapsed:.2f}秒")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"{func.__name__} 执行失败，耗时: {elapsed:.2f}秒，错误: {e}")
            raise
    return wrapper

class PerformanceTracker:
    """性能跟踪器"""
    
    def __init__(self):
        self.metrics = {}
    
    def track(self, name: str):
        """跟踪指定名称的操作"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    elapsed = time.time() - start_time
                    
                    if name not in self.metrics:
                        self.metrics[name] = []
                    self.metrics[name].append(elapsed)
                    
                    logger.info(f"{name} 执行时间: {elapsed:.2f}秒")
                    return result
                except Exception as e:
                    elapsed = time.time() - start_time
                    logger.error(f"{name} 执行失败，耗时: {elapsed:.2f}秒，错误: {e}")
                    raise
            return wrapper
        return decorator
    
    def get_average_time(self, name: str) -> float:
        """获取指定操作的平均执行时间"""
        if name in self.metrics and self.metrics[name]:
            return sum(self.metrics[name]) / len(self.metrics[name])
        return 0.0
    
    def get_total_time(self, name: str) -> float:
        """获取指定操作的总执行时间"""
        if name in self.metrics:
            return sum(self.metrics[name])
        return 0.0
    
    def print_summary(self):
        """打印性能摘要"""
        logger.info("=== 性能摘要 ===")
        for name, times in self.metrics.items():
            avg_time = sum(times) / len(times)
            total_time = sum(times)
            count = len(times)
            logger.info(f"{name}: 执行{count}次，平均{avg_time:.2f}秒，总计{total_time:.2f}秒")

# 全局性能跟踪器实例
performance_tracker = PerformanceTracker() 