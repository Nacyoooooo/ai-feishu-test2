"""
基于pytest fixture的生命周期管理
避免与pytest系统的冲突
"""

import pytest
import logging
import time
from typing import Dict, Any, List, Optional, Generator
from contextlib import contextmanager
from .test_lifecycle_manager import TestLifecycleManager, TestLifecycleConfig, TestPhase

logger = logging.getLogger(__name__)

@pytest.fixture(scope="function")
def lifecycle_manager():
    """生命周期管理器fixture"""
    return TestLifecycleManager()

@pytest.fixture(scope="function")
def test_lifecycle_context():
    """测试生命周期上下文fixture"""
    @contextmanager
    def _lifecycle_context(test_id: str, config: TestLifecycleConfig):
        manager = TestLifecycleManager()
        manager.register_test(test_id, config)
        
        try:
            yield manager.test_lifecycle_context(test_id)
        finally:
            # 确保清理工作被执行
            if TestPhase.CLEANUP in config.phases:
                manager._cleanup_test_resources(test_id)
    
    return _lifecycle_context

def create_lifecycle_config(
    test_id: str,
    phases: Optional[List[TestPhase]] = None,
    resources: Optional[Dict[str, Any]] = None,
    timeout: int = 300,
    retry_count: int = 3,
    skip_on_failure: bool = False
) -> TestLifecycleConfig:
    """
    创建生命周期配置
    
    Args:
        test_id: 测试用例ID
        phases: 测试阶段列表
        resources: 资源配置
        timeout: 超时时间
        retry_count: 重试次数
        skip_on_failure: 失败时是否跳过
    """
    if phases is None:
        phases = [TestPhase.PREPARATION, TestPhase.EXECUTION, TestPhase.VALIDATION, TestPhase.CLEANUP]
    
    return TestLifecycleConfig(
        test_id=test_id,
        phases=phases,
        dependencies=None,
        resources=resources,
        cleanup_strategy="immediate",
        timeout=timeout,
        retry_count=retry_count,
        skip_on_failure=skip_on_failure
    )

@pytest.fixture(scope="function")
def performance_monitor():
    """性能监控fixture"""
    start_time = time.time()
    
    yield
    
    elapsed = time.time() - start_time
    logger.info(f"测试执行时间: {elapsed:.2f}秒")

@pytest.fixture(scope="function")
def retry_fixture():
    """重试机制fixture"""
    def _retry(func, max_retries: int = 3, delay: float = 1.0):
        for attempt in range(max_retries + 1):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries:
                    logger.error(f"重试 {max_retries} 次后仍然失败: {e}")
                    raise
                else:
                    logger.warning(f"第 {attempt + 1} 次尝试失败: {e}")
                    time.sleep(delay)
    
    return _retry

# 便捷的测试阶段函数
def preparation_phase(func):
    """准备阶段装饰器"""
    def wrapper(*args, **kwargs):
        logger.info(f"进入准备阶段: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"准备阶段完成: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"准备阶段失败: {func.__name__}, 错误: {e}")
            raise
    
    return wrapper

def execution_phase(func):
    """执行阶段装饰器"""
    def wrapper(*args, **kwargs):
        logger.info(f"进入执行阶段: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"执行阶段完成: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"执行阶段失败: {func.__name__}, 错误: {e}")
            raise
    
    return wrapper

def validation_phase(func):
    """验证阶段装饰器"""
    def wrapper(*args, **kwargs):
        logger.info(f"进入验证阶段: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"验证阶段完成: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"验证阶段失败: {func.__name__}, 错误: {e}")
            raise
    
    return wrapper

def cleanup_phase(func):
    """清理阶段装饰器"""
    def wrapper(*args, **kwargs):
        logger.info(f"进入清理阶段: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"清理阶段完成: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"清理阶段失败: {func.__name__}, 错误: {e}")
            raise
    
    return wrapper 